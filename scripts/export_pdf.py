"""Export REPORT.md and PRESENTATION.md for offline reading (no results recomputed).

uv run --group export playwright install chromium   # once
uv run --group export python scripts/export_pdf.py

Writes REPORT.html (single file, figures embedded), REPORT.pdf (A4) and PRESENTATION.pdf
(one landscape page per slide; slides are separated by '---' lines in PRESENTATION.md).
Checks that every table cell, heading and slide title survives into the PDF text.
"""
import base64
import html
import re
import unicodedata
from pathlib import Path

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent

CSS = """
:root { font-family: system-ui, sans-serif; color: #17243b }
body { margin: 0 } main { max-width: 1000px; margin: 24px auto; padding: 0 32px }
h1 { font-size: 26px; line-height: 1.25 } h2 { font-size: 21px; margin-top: 30px } h3 { font-size: 18px }
h1, h2, h3, h4 { break-after: avoid }
p, li { font-size: 15px; line-height: 1.5 }
img { display: block; max-width: 100%; height: auto; margin: 12px auto; break-inside: avoid }
pre { padding: 12px; background: #f2f5f9; white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12px }
code { font-size: .88em; overflow-wrap: anywhere }
table { border-collapse: collapse; font-size: 12px; margin: 12px 0; font-variant-numeric: tabular-nums }
th, td { padding: 5px 7px; border: 1px solid #d7dfeb; text-align: left; vertical-align: top }
th { background: #f2f5f9 }
.note { font-size: 12px; color: #53647a }
@media print {
  @page { size: A4 portrait; margin: 15mm 13mm }
  main { margin: 0; padding: 0; max-width: none }
  p, li { font-size: 9.5pt; line-height: 1.35 } h1 { font-size: 17pt } h2 { font-size: 14pt } h3, h4 { font-size: 11pt }
  table { font-size: 7.5pt } tr { break-inside: avoid } thead { display: table-header-group }
  img { max-height: 115mm; object-fit: contain }
}
"""

SLIDE_CSS = """
:root { font-family: system-ui, sans-serif; color: #17243b }
body { margin: 0 }
@page { size: 297mm 167mm; margin: 0 }
section { width: 297mm; height: 167mm; padding: 9mm 13mm; box-sizing: border-box; overflow: hidden;
          page-break-after: always; break-after: page; font-size: 14pt }
h1 { font-size: 1.7em; margin: 0 0 .35em } h2 { font-size: 1.6em; margin: 0 0 .35em }
p, li { font-size: 1em; line-height: 1.3; margin: .2em 0 }
img { display: block; max-height: 82mm; max-width: 100%; margin: 2mm auto }
table { border-collapse: collapse; font-size: .8em; margin: 2mm 0 } th, td { padding: 2pt 5pt; border: 1px solid #d7dfeb }
th { background: #f2f5f9 } code { font-size: .88em }
"""

# shrink each slide's base font until it fits its page
FIT_JS = """() => [...document.querySelectorAll('section')].map(s => {
  let pt = 14;
  while (s.scrollHeight > s.clientHeight + 1 && pt > 8) { pt -= 0.5; s.style.fontSize = pt + 'pt'; }
  return [pt, s.scrollHeight > s.clientHeight + 1];
})"""


def md():
    return MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")


def embed_images(body):
    def repl(m):
        src = m.group(1)
        path = ROOT / src
        if not path.is_file():
            return m.group(0)
        data = base64.b64encode(path.read_bytes()).decode()
        return f'src="data:image/png;base64,{data}"'
    return re.sub(r'src="(figures/[^"]+\.png)"', repl, body)


def page(title, css, body):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>'
            f'<style>{css}</style></head><body>{body}</body></html>\n')


def plain(s):
    """Markdown cell/heading -> text as it appears in the PDF (approx.)."""
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = s.replace("**", "").replace("*", "")
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return s.strip()


def norm(s):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s)).replace("−", "-").replace("–", "-")


def check_pdf(pdf, needles, label):
    text = norm("".join(p.extract_text() or "" for p in PdfReader(pdf).pages))
    missing = [n for n in needles if norm(n) and norm(n) not in text]
    if missing:
        print(f"[warn] {label}: {len(missing)}/{len(needles)} fragments not found verbatim in PDF text: {missing}")
    else:
        print(f"[ok] {label}: all {len(needles)} fragments found in PDF text")
    return missing


def main():
    report_md = (ROOT / "REPORT.md").read_text()
    body = embed_images(md().render(report_md))
    note = ('<p class="note">Export of REPORT.md (scripts/export_pdf.py); no results recomputed. '
            'Source paths refer to the repository.</p>')
    (ROOT / "REPORT.html").write_text(page("REPORT", CSS, f"<main>{note}{body}</main>"))

    slides_md = (ROOT / "PRESENTATION.md").read_text()
    slides = [s for s in re.split(r"(?m)^---\s*$", slides_md) if s.strip()]
    slide_html = "".join(f"<section>{embed_images(md().render(s))}</section>" for s in slides)
    slides_file = ROOT / "results" / "_slides_tmp.html"
    slides_file.write_text(page("PRESENTATION", SLIDE_CSS, slide_html))

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto((ROOT / "REPORT.html").as_uri(), wait_until="load")
        pg.pdf(path=str(ROOT / "REPORT.pdf"), prefer_css_page_size=True, print_background=True)
        pg.goto(slides_file.as_uri(), wait_until="load")
        fit = pg.evaluate(FIT_JS)
        print("slide base font (pt):", [f[0] for f in fit])
        overflow = [f[1] for f in fit]
        pg.pdf(path=str(ROOT / "PRESENTATION.pdf"), prefer_css_page_size=True, print_background=True)
        b.close()
    slides_file.unlink()

    # checks: headings + table cells of the report, slide titles + page count of the deck
    heads = [plain(h) for h in re.findall(r"(?m)^#{2,4} (.+)$", report_md)]
    cells = []
    for line in report_md.splitlines():
        if line.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", line):
            cells += [plain(c.replace("\\|", "|")) for c in re.split(r"(?<!\\)\|", line.strip().strip("|")) if plain(c)]
    check_pdf(ROOT / "REPORT.pdf", heads, "REPORT headings")
    check_pdf(ROOT / "REPORT.pdf", cells, "REPORT table cells")
    n = len(PdfReader(ROOT / "PRESENTATION.pdf").pages)
    titles = [plain(re.search(r"(?m)^#{1,2} (.+)$", s).group(1)) for s in slides if re.search(r"(?m)^#{1,2} ", s)]
    print(f"[{'ok' if n == len(slides) else 'FAIL'}] deck: {n} PDF pages for {len(slides)} slides")
    if any(overflow):
        print(f"[FAIL] slides overflowing their page: {[i + 1 for i, o in enumerate(overflow) if o]}")
    check_pdf(ROOT / "PRESENTATION.pdf", titles, "slide titles")
    print(f"REPORT.pdf pages: {len(PdfReader(ROOT / 'REPORT.pdf').pages)}")


if __name__ == "__main__":
    main()
