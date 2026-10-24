"""
ADAPTER (replaces the starter's OpenRouter/OpenAI/Anthropic/Vertex wrappers).

`LlmChatClient` exposes the starter's ModelWrapper interface (`generate(messages) -> str`) but routes every
call through the repo-root `llm.chat` (default backend="aqueduct", model="qwen-3.6-35b"), with
  * an append-only JSONL disk cache (reruns never re-spend),
  * a process-wide semaphore (<= 3 concurrent LLM calls),
  * per-call logging of backend/model, and a `parse_failures` counter incremented by the agents.

Cache key = sha256(run_id, agent_key, call_index, model, backend, temperature, messages). `call_index` counts
calls made by THIS client (one client per seller), so a retry after a parse failure is a new key, while an
identical replay of a partially finished run hits the cache.
"""
import hashlib
import json
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional, TypedDict

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from llm import chat  # noqa: E402

LLM_SEM = threading.Semaphore(3)
_CACHE_LOCK = threading.Lock()
_CACHE: dict = {}
_CACHE_PATH: Optional[Path] = None


class Message(TypedDict):
    role: str
    content: str


def set_cache_path(path) -> None:
    """Load (or create) the JSONL cache. Call once before running."""
    global _CACHE_PATH
    _CACHE_PATH = Path(path)
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE.clear()
    if _CACHE_PATH.exists():
        for line in _CACHE_PATH.read_text().splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    _CACHE[r["key"]] = r
                except json.JSONDecodeError:
                    pass  # torn last line from a killed run


class ModelWrapper:
    parse_failures = 0


class LlmChatClient(ModelWrapper):
    def __init__(self, run_id: str, agent_key: str, model: str = "qwen-3.6-35b", backend: str = "aqueduct",
                 temperature: float = 0.7, max_tokens: int = 2500, **_):
        self.run_id, self.agent_key = run_id, agent_key
        self.model, self.backend = model, backend
        self.temperature, self.max_tokens = temperature, max_tokens
        self.call_index = 0
        self.n_calls = 0       # total generate() calls (incl. cache hits)
        self.n_cached = 0
        self.parse_failures = 0
        self.models_seen = set()  # "backend/model" actually reported by llm.chat

    def generate(self, messages: List[Message]) -> Optional[str]:
        idx = self.call_index
        self.call_index += 1
        self.n_calls += 1
        key = hashlib.sha256(json.dumps(
            [self.run_id, self.agent_key, idx, self.model, self.backend, self.temperature, messages],
            sort_keys=True).encode()).hexdigest()
        with _CACHE_LOCK:
            hit = _CACHE.get(key)
        if hit is not None:
            self.n_cached += 1
            self.models_seen.add(f"{hit['backend']}/{hit['model']}")
            return hit["text"]
        with LLM_SEM:
            t0 = time.time()
            r = chat(messages, model=self.model, backend=self.backend, temperature=self.temperature,
                     max_tokens=self.max_tokens)
        text = r["text"]
        if "</think>" in text:  # reasoning models: keep only the answer (as the starter wrapper did)
            text = text.rsplit("</think>", 1)[1]
        rec = {"key": key, "run_id": self.run_id, "agent": self.agent_key, "call_index": idx,
               "backend": r["backend"], "model": r["model"], "latency_s": round(time.time() - t0, 2),
               "text": text}
        self.models_seen.add(f"{r['backend']}/{r['model']}")
        with _CACHE_LOCK:
            _CACHE[key] = rec
            if _CACHE_PATH is not None:
                with open(_CACHE_PATH, "a") as f:
                    f.write(json.dumps(rec) + "\n")
        return text
