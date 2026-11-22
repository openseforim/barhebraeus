"""Build the reader (GitHub Pages, docs/): each page of Bedjan's text line by line, the Syriac (as Kraken read it) and
a transliteration into Hebrew letters, with a link to the scan.
  uv run build_site.py
The transliteration is the deterministic table of the Bochart project (bochart-hierozoicon/translate.py,
syriac_to_hebrew): one Hebrew letter per Syriac consonant, final forms at the end of a word, vowel points and other
marks left out. Added here: ܤ (final semkath of the East Syriac type) = ס. Digits and punctuation are kept.
"""
import html
import json
import re
import sys
from pathlib import Path

from segments import segments

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent
TEXT = ROOT / "data" / "text"
DOCS = ROOT / "docs"
ITEM = "ketabademadatbez00barhuoft"
SYRIAC_TO_HEBREW = dict(zip("ܐܒܓܕܗܘܙܚܛܝܟܠܡܢܣܥܦܨܩܪܫܬܤ", "אבגדהוזחטיכלמנסעפצקרשתס"))
FINALS = dict(zip("כמנפצ", "ךםןףץ"))
MARK = re.compile(r"[̀-ͯܰ-ܑ݊]")  # vowel points, seyame and other marks (and superscript alaph)


def to_hebrew(line: str) -> str:
    out = []
    for w in MARK.sub("", line).split():
        h = "".join(SYRIAC_TO_HEBREW.get(c, c) for c in w)
        # final form for the last Hebrew letter of the word (before any trailing punctuation)
        m = re.search(r"([כמנפצ])([^א-ת]*)$", h)
        if m and re.search(r"[א-ת]", h[:m.start()]):
            h = h[:m.start()] + FINALS[m.group(1)] + m.group(2)
        out.append(h)
    return " ".join(out)


def leaf(page: int) -> int:
    return 605 - page  # Bedjan's pages run from the back of the scan


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1b18;--muted:#6b665e;--line:#e4e0d8;--accent:#7a3b12;--card:#fff}
@media (prefers-color-scheme: dark){:root{--bg:#161513;--fg:#ece8e1;--muted:#a49d92;--line:#33302b;--accent:#e2a06b;--card:#1e1c19}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 Georgia,"Times New Roman",serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.6rem;margin:0 0 .3rem} h2{font-size:1.2rem;margin:2.2rem 0 .6rem;border-bottom:1px solid var(--line);padding-bottom:.3rem}
p,li{max-width:46rem} .muted{color:var(--muted)} a{color:var(--accent)}
nav.pages{display:flex;flex-wrap:wrap;gap:.4rem;margin:1rem 0} nav.pages a{padding:.15rem .5rem;border:1px solid var(--line);border-radius:4px;text-decoration:none}
table.lines{width:100%;border-collapse:collapse;background:var(--card)}
table.lines td{border-bottom:1px solid var(--line);padding:.35rem .6rem;vertical-align:top}
td.n{color:var(--muted);font:12px/1.9 system-ui,sans-serif;width:2.5rem;text-align:left}
td.syr{font-family:"Noto Sans Syriac Eastern","Noto Sans Syriac",serif;font-size:1.35rem;line-height:2.1;direction:rtl;text-align:right;width:52%;border-left:1px solid var(--line)}
td.en{font-size:1rem;line-height:1.6;width:30%;color:var(--fg)}
td.heb{font-family:"Noto Serif Hebrew","SBL Hebrew",serif;font-size:1.15rem;line-height:2.1;direction:rtl;text-align:right;color:var(--fg)}
tr.hl td{background:rgba(226,160,107,.12)}
.cap{font:13px/1.5 system-ui,sans-serif;color:var(--muted);margin:.3rem 0 .8rem}
@media (max-width:640px){table.lines,table.lines tbody{display:block;width:100%}table.lines tr{display:flex;flex-direction:column;border-bottom:1px solid var(--line)}table.lines td{display:block;width:100%;border:none}td.n{order:0;text-align:right;width:auto;padding-bottom:0}td.syr{order:1;border-left:none}td.heb{order:2;padding-top:0;color:var(--muted)}td.en{order:3;width:100%;padding-top:0}}
"""


HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="OCR of Bedjan's edition of Barhebraeus' Chronicon Syriacum (1890), with a transliteration into Hebrew letters.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Syriac+Eastern&family=Noto+Serif+Hebrew&display=swap" rel="stylesheet">
<style>{css}</style></head><body><main>"""


def page_html(p: int, prev: int | None, nxt: int | None) -> str:
    lines = [ln for ln in (TEXT / f"p{p:03d}.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    # The archive.org viewer skips leaf 0 (the cover), so its index is leaf - 1 (checked 20-Nov-2026: n604 = leaf 605,
    # the preface). The image link gives the leaf itself.
    scan = f"https://archive.org/details/{ITEM}/page/n{leaf(p) - 1}/mode/1up"
    img = (f"https://archive.org/download/{ITEM}/{ITEM}_jp2.zip/{ITEM}_jp2%2F{ITEM}_{leaf(p):04d}.jp2"
           f"&ext=jpg&reduce=1")
    rows = []
    tr_file = ROOT / "data" / "translation" / f"p{p:03d}.json"
    tr = json.loads(tr_file.read_text(encoding="utf-8")) if tr_file.exists() else None
    if tr and len(segments(p)[0]) != len(tr["segments"]):
        print(f"p. {p}: {len(segments(p)[0])} segments but {len(tr['segments'])} translations: shown without English")
        tr = None  # the text changed after the translation, or the model lost the alignment
    if tr:
        # the page split at its punctuation (segments.py), with an English translation per segment
        segs, notes = segments(p)
        by = tr.get("by", "a pilot translation by Claude from the OCR text (not checked by a Syriacist)")
        for i, (s, en) in enumerate(list(zip(segs, tr["segments"])) + list(zip(notes, tr.get("notes", []))), 1):
            rows.append(f'<tr><td class="en">{html.escape(en)}</td><td class="heb" lang="he">{html.escape(to_hebrew(s))}</td>'
                        f'<td class="syr" lang="syr">{html.escape(s)}</td><td class="n">{i if i <= len(segs) else "note"}</td></tr>')
        lines = segs
        unit = (f"{len(segs)} segments, split at the punctuation (. and :), with an English translation: {html.escape(by)}; "
                f"Bedjan&#39;s notes at the end")
    else:
        # every page (20-Nov-2026): split at the punctuation, Hebrew letters on the left, the Syriac on the right
        segs, notes = segments(p)
        unit = (f"{len(segs)} segments, split at the punctuation (. and :); the page header is in the first segment, "
                f"Bedjan&#39;s notes at the end")
        on = False
        for i, s in enumerate(segs + notes, 1):
            key = MARK.sub("", s)
            if p == 128 and "ܐܨܗ" in key:
                on = True  # the plague of locusts of AG 1095 (the check of the pilot)
            hl = ' class="hl"' if on else ""
            if p == 128 and "ܠܡܥܪܒܐ" in key:
                on = False
            rows.append(f'<tr{hl}><td class="heb" lang="he">{html.escape(to_hebrew(s))}</td>'
                        f'<td class="syr" lang="syr">{html.escape(s)}</td><td class="n">{i if i <= len(segs) else "note"}</td></tr>')
    nav = (f'<a href="p{prev:03d}.html">&larr; p. {prev}</a>' if prev else "") + ' <a href="index.html">contents</a> ' +           (f'<a href="p{nxt:03d}.html">p. {nxt} &rarr;</a>' if nxt else "")
    return (HEAD.format(title=f"Barhebraeus Chronography, p. {p}", css=CSS) +
            f'<p class="muted"><a href="index.html">Barhebraeus, <i>Chronography</i> (ed. Bedjan, 1890)</a></p>'
            f'<nav class="pages">{nav}</nav><h2 id="p{p}">Page {p}</h2>'
            f'<div class="cap">As read by Kraken, not proofread: {unit} · <a href="{scan}">scan in the viewer</a> · <a href="{img}">page image (leaf {leaf(p)})</a></div>'
            f'<table class="lines"><tbody>{"".join(rows)}</tbody></table><nav class="pages">{nav}</nav></main></body></html>')


def build() -> None:
    DOCS.mkdir(exist_ok=True)
    pages = sorted(int(p.stem[1:]) for p in TEXT.glob("p*.txt"))
    for k, p in enumerate(pages):
        prev = pages[k - 1] if k else None
        nxt = pages[k + 1] if k + 1 < len(pages) else None
        (DOCS / f"p{p:03d}.html").write_text(page_html(p, prev, nxt), encoding="utf-8")
    links = " ".join(f'<a href="p{p:03d}.html">{p}</a>' for p in pages)
    index = HEAD.format(title="Barhebraeus Chronography", css=CSS) + f"""
<h1>Barhebraeus, <i>Chronography</i> (ed. Bedjan, 1890)</h1>
<p class="muted">{len(pages)} of 599 pages · machine reading, not proofread · 20-Nov-2026</p>
<p>The secular part of the history of Gregory Barhebraeus (1226–1286), in Paul Bedjan's vocalised edition, <i>Gregorii
Barhebraei Chronicon Syriacum</i> (Paris 1890), from the <a href="https://archive.org/details/{ITEM}">University of Toronto scan</a>.
The Syriac was read by <a href="https://github.com/mittagessen/kraken">Kraken</a> with Beth Mardutho's
<a href="https://bethmardutho.org/qoruyo/">Qoruyo</a> models for printed East Syriac (CC BY 4.0). On each page the Syriac is on the
right, and on the left are the same words in Hebrew letters, by a fixed letter table (one letter for one consonant; vowels left out),
for readers of Hebrew and Aramaic. A third column gives an English machine translation of each segment (Gemini 3.8 Flash,
chosen in a test of six models; p. 1 by Claude; pp. 59, 583 and 593–599 by Gemini 4 Argon), made from the uncorrected OCR text:
a guide to the content, not a scholarly translation. {{OCR?}} marks a place where the OCR text is doubtful.</p>
<p>How good is it? On <a href="p128.html">p. 128</a> (highlighted: the plague of locusts of the year 1095 of the Greeks, AD 784) the
reading was compared with a text of the same passage made from two other prints in another script: 55 of 58 words were the same. The
vowel points, the page headers and the notes have not been checked. Method and code:
<a href="https://github.com/openseforim/barhebraeus">github.com/EzraBrand/barhebraeus-chronography</a>.</p>
<h2>Pages</h2><nav class="pages">{links}</nav>
</main></body></html>"""
    (DOCS / "index.html").write_text(index, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print("wrote docs/index.html and", len(pages), "page files")


if __name__ == "__main__":
    build()
