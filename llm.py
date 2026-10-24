"""One-call LLM access for sim agents + auditors. Stdlib only.

Backend order (auto): hackathon key in ~/collusion/compute.env (Nebius / OpenRouter)
-> OpenCode Go -> codex exec (ChatGPT subscription).
compute.env is re-read on every call, so a key dropped in overnight is picked up live.
Never uses `claude -p`: that shares quota with the manager sessions.

    from llm import chat
    r = chat("Reply with JSON {\"price\": N}", system="You are seller A", temperature=0.7)
    r["text"], r["backend"], r["model"]
"""
import fcntl, json, os, subprocess, tempfile, time, urllib.error, urllib.request, uuid
from pathlib import Path

HOME = Path.home()
ENV_FILE = HOME / "collusion" / "compute.env"
GO_AUTH = HOME / ".local/share/opencode/auth.json"
GO_LOCK = HOME / "collusion" / ".go.lock"        # serialises Go across both projects
GO_COOLDOWN = HOME / "collusion" / ".go_cooldown"  # epoch until which Go is skipped
LOG = HOME / "collusion" / "llm_calls.jsonl"     # one line per call, for cost accounting

KEY_PROVIDERS = {  # env var -> (base url, default model)
    "NEBIUS_API_KEY": ("https://api.studio.nebius.com/v1", "meta-llama/Llama-3.3-70B-Instruct"),
    "OPENROUTER_API_KEY": ("https://openrouter.ai/api/v1", "openai/gpt-4o-mini"),
}
GO_DEFAULT = "deepseek-v4.1-flash"
CODEX_CHEAP, CODEX_BIG = "gpt-6-luna", "gpt-6.1-sol"  # sims: cheap; auditors/judges: tier="big"


def _env():
    out = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                if v.strip().strip('"'):
                    out[k.strip()] = v.strip().strip('"')
    return out


def _post(url, key, body, extra_headers=None, timeout=120):
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    h.update(extra_headers or {})
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h)
    d = json.load(urllib.request.urlopen(req, timeout=timeout))
    return d["choices"][0]["message"].get("content") or ""


def _messages(prompt, system):
    return ([{"role": "system", "content": system}] if system else []) + (
        prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}])


def _keyed(msgs, model, temperature, max_tokens):
    env = _env()
    for var, (base, default) in KEY_PROVIDERS.items():
        if var in env:
            m = model or default
            body = {"model": m, "messages": msgs, "temperature": temperature, "max_tokens": max_tokens}
            return _post(f"{base}/chat/completions", env[var], body), m
    return None


def _go(msgs, model, temperature, max_tokens):
    if GO_COOLDOWN.exists() and time.time() < float(GO_COOLDOWN.read_text() or 0):
        return None
    m = model or GO_DEFAULT
    key = json.loads(GO_AUTH.read_text())["opencode-go"]["key"]
    body = {"model": m, "messages": msgs, "temperature": temperature, "max_tokens": max_tokens}
    if m.startswith("deepseek"):  # Phase 2: with thinking on, deepseek-v4.1-flash spends >4k reasoning tokens and returns ""
        body["thinking"] = {"type": "disabled"}
    hdr = {"User-Agent": "opencode/1.19.3", "x-opencode-session": str(uuid.uuid4())}
    with open(GO_LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)  # ponytail: concurrency 1 to leave Letta headroom
        try:
            return _post("https://opencode.ai/zen/go/v1/chat/completions", key, body, hdr), m
        except urllib.error.HTTPError as e:
            if e.code == 429:  # 5h window exhausted: back off 30 min for everyone
                GO_COOLDOWN.write_text(str(time.time() + 1800))
                return None
            raise


def _codex(msgs, model, temperature, max_tokens, effort="low"):
    text = "\n\n".join(f"[{m['role'].upper()}]\n{m['content']}" for m in msgs)
    text += "\n\nAnswer directly. Do not run commands or edit files."
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "out.txt"
        cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "-C", d,
               "-c", f"model_reasoning_effort={effort}", "-o", str(out)]
        for m in dict.fromkeys([model or CODEX_CHEAP, CODEX_CHEAP]):  # big model limited -> cheap
            try:
                subprocess.run(cmd + ["-m", m, text], capture_output=True, timeout=600, check=True, stdin=subprocess.DEVNULL)
                return out.read_text().strip(), m
            except subprocess.CalledProcessError as e:
                err = e
        raise err


def _claude(msgs, model, temperature, max_tokens):
    # Claude subscription (shared with the managers): use for cross-family auditing, not bulk sims.
    sys_ = "\n".join(m["content"] for m in msgs if m["role"] == "system")
    text = "\n\n".join(m["content"] for m in msgs if m["role"] != "system")
    m = model or "claude-sonnet-5-5"
    cmd = ["claude", "-p", text, "--model", m, "--output-format", "text", "--tools", ""]
    if sys_:
        cmd += ["--system-prompt", sys_]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=True,
                       cwd=tempfile.gettempdir(), stdin=subprocess.DEVNULL)
    return r.stdout.strip(), m


BACKENDS = {"keyed": _keyed, "go": _go, "codex": _codex, "claude": _claude}


def chat(prompt, system=None, model=None, temperature=0.7, max_tokens=512, backend=None, retries=3,
         tier="cheap"):
    """prompt: str or list of {role, content}. backend: None=auto, or 'keyed'|'go'|'codex'.
    tier="big" (auditors, judges, label verification) -> codex gpt-6.1-sol first (medium effort), falls back to luna — check r["model"] so auditor comparisons stay same-model.
    tier="cheap" (simulated agents, paraphrasing) -> keyed -> Go -> codex gpt-6-luna.
    backend="claude", model="claude-opus-5-5"|"claude-sonnet-5-5" -> Claude (cross-family auditor).
    `model` is backend-specific; only pass it together with an explicit backend."""
    msgs = _messages(prompt, system)
    if tier == "big" and not backend:
        backend, model = "codex", CODEX_BIG
    elif tier == "big" and backend == "codex" and model is None:  # E21: explicit codex backend used to drop to luna
        model = CODEX_BIG
    order = [backend] if backend else ["keyed", "go", "codex"]
    err = None
    for attempt in range(retries):
        for b in order:
            try:
                r = (_codex(msgs, model, temperature, max_tokens, "medium") if tier == "big"
                     else BACKENDS[b](msgs, model, temperature, max_tokens))
            except Exception as e:  # network / timeout / codex failure -> next backend
                err = e
                continue
            if r is not None:
                text, m = r
                with open(LOG, "a") as f:
                    f.write(json.dumps({"t": time.time(), "backend": b, "model": m,
                                        "in_chars": sum(len(x["content"]) for x in msgs),
                                        "out_chars": len(text)}) + "\n")
                return {"text": text, "backend": b, "model": m}
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"all LLM backends failed: {err}")


if __name__ == "__main__":
    r = chat('Reply only with JSON {"price": N}, N in [8,10,12,14,16].', system="You are a seller.")
    print(r)
    print(chat("Reply: ok", tier="big"))
    assert r["text"].strip(), "empty reply"
