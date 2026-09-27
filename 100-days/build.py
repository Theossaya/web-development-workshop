"""
Builds 100-days-of-web-dev.pdf.

    python build.py

The words live in content/*.txt, in a small plain-text format described at the
bottom of this file. Edit those, run this again, and the PDF is rebuilt. Chrome
or Edge does the printing, so no PDF library is needed.
"""

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTENT = HERE / "content"
OUT_PDF = HERE / "100-days-of-web-dev.pdf"

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

DEVICE_LABELS = {
    "phone": ("Phone", "phone"),
    "preview": ("Phone + server", "phone"),
    "laptop": ("Laptop recommended", "laptop"),
}

# --------------------------------------------------------------------------
# Syntax colouring for code blocks
# --------------------------------------------------------------------------

JS_TOKENS = re.compile(
    r"(//[^\n]*|/\*[\s\S]*?\*/)"
    r"|(`[^`]*`|\"[^\"\n]*\"|'[^'\n]*')"
    r"|\b(const|let|var|function|return|if|else|for|of|in|while|new|async|await|"
    r"import|export|from|default|try|catch|throw|class|typeof)\b"
    r"|\b(true|false|null|undefined|\d+(?:\.\d+)?)\b"
)


def paint_js(src):
    def swap(m):
        comment, string, keyword, literal = m.groups()
        if comment:
            return f'<span class="c">{comment}</span>'
        if string:
            return f'<span class="s">{string}</span>'
        if keyword:
            return f'<span class="k">{keyword}</span>'
        if literal:
            return f'<span class="n">{literal}</span>'
        return m.group(0)

    esc = src.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return JS_TOKENS.sub(swap, esc)


def paint_css(src):
    esc = html.escape(src, quote=False)
    esc = re.sub(r"(/\*[\s\S]*?\*/)", r'<span class="c">\1</span>', esc)
    esc = re.sub(r"^([ \t]+)([a-z-]+)(\s*:)", r'\1<span class="k">\2</span>\3', esc, flags=re.M)
    esc = re.sub(r"^([^\s{}][^{}\n]*)(\{)", r'<span class="t">\1</span>\2', esc, flags=re.M)
    return esc


def paint_html(src):
    esc = html.escape(src, quote=False)
    esc = re.sub(r"(&lt;!--[\s\S]*?--&gt;)", r'<span class="c">\1</span>', esc)
    esc = re.sub(r'(=)("[^"]*")', r'\1<span class="s">\2</span>', esc)
    esc = re.sub(r"(&lt;/?)([a-z0-9]+)", r'\1<span class="t">\2</span>', esc)
    return esc


PAINTERS = {"js": paint_js, "css": paint_css, "html": paint_html, "json": paint_js}


def code_block(lang, src):
    src = "\n".join(src).strip("\n")
    painter = PAINTERS.get(lang, lambda s: html.escape(s, quote=False))
    names = {"js": "script.js", "css": "styles.css", "html": "index.html",
             "json": "data/games.json", "terminal": "terminal", "text": "text"}
    return (f'<div class="code"><div class="file">{names.get(lang, lang)}</div>'
            f"<pre>{painter(src)}</pre></div>")


def inline(text):
    """Escape a line of prose, then allow `code` and **bold**."""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", out)
    return out


# --------------------------------------------------------------------------
# Parsing the content files
# --------------------------------------------------------------------------

SECTION_WORDS = {"LEARN", "BUILD", "DONE", "STRETCH", "STUCK", "MUST", "NICE",
                 "PLAN", "TEXT", "BY-THE-END", "DEVICE"}


def parse_body(lines):
    """Turn the lines of one block into {section: [html fragments]}."""
    sections = {}
    current = "TEXT"
    para, items, ordered = [], [], []
    code_lang, code_lines = None, []

    def flush():
        nonlocal para, items, ordered
        bucket = sections.setdefault(current, [])
        if para:
            bucket.append(f"<p>{inline(' '.join(para))}</p>")
            para = []
        if items:
            bucket.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
            items = []
        if ordered:
            bucket.append("<ol>" + "".join(f"<li>{inline(i)}</li>" for i in ordered) + "</ol>")
            ordered = []

    for raw in lines:
        line = raw.rstrip("\n")
        if code_lang is not None:
            if line.strip() == "```":
                sections.setdefault(current, []).append(code_block(code_lang, code_lines))
                code_lang, code_lines = None, []
            else:
                code_lines.append(line)
            continue
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            code_lang = stripped[3:].strip() or "text"
            continue
        if stripped in SECTION_WORDS:
            flush()
            current = stripped
            continue
        if not stripped:
            flush()
            continue
        if stripped.startswith("### "):
            flush()
            sections.setdefault(current, []).append(f'<h4 class="sub">{inline(stripped[4:])}</h4>')
            continue
        if stripped.startswith("- "):
            if para:
                flush()
            items.append(stripped[2:])
            continue
        m = re.match(r"^\d+\.\s+(.*)", stripped)
        if m and current != "PLAN":
            if para:
                flush()
            ordered.append(m.group(1))
            continue
        if current == "PLAN" and "|" in stripped:
            flush()
            day, text = [part.strip() for part in stripped.split("|", 1)]
            sections.setdefault("PLAN", []).append(
                f'<div class="plan-row"><span>Day {html.escape(day)}</span><div>{inline(text)}</div></div>')
            continue
        para.append(stripped)
    flush()
    return sections


def parse_file(path):
    blocks, header, body = [], None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("@@ "):
            if header is not None:
                blocks.append((header, body))
            header = [part.strip() for part in line[3:].split("|")]
            body = []
        elif header is not None:
            body.append(line)
    if header is not None:
        blocks.append((header, body))
    return blocks


# --------------------------------------------------------------------------
# Rendering each kind of block
# --------------------------------------------------------------------------

def join(sections, key):
    return "".join(sections.get(key, []))


def render_page(fields, sections):
    title = fields[1] if len(fields) > 1 else ""
    klass = "page" + (" " + fields[2] if len(fields) > 2 else "")
    return f'<section class="{klass}"><h2>{inline(title)}</h2>{join(sections, "TEXT")}</section>'


def render_level(fields, sections):
    _, number, name, subject, span = fields[:5]
    end = join(sections, "BY-THE-END")
    end_html = f'<div class="level-end"><h4>By the end of this level</h4>{end}</div>' if end else ""
    return (f'<section class="level"><p class="level-no">Level {number}</p>'
            f'<h2>{inline(name)}</h2><p class="level-sub">{inline(subject)} &middot; {inline(span)}</p>'
            f'{join(sections, "TEXT")}{end_html}</section>')


def device_tag(key):
    label, kind = DEVICE_LABELS.get(key, (key, "phone"))
    return f'<span class="device device-{kind}">{label}</span>'


def render_day(fields, sections):
    _, number, title, device = (fields + ["", "", "", "phone"])[:4]
    head = (f'<div class="day-head"><span class="day-no">Day {int(number):02d}</span>'
            f'<h3>{inline(title)}</h3>{device_tag(device)}</div>')
    learn = join(sections, "LEARN")
    device_note = join(sections, "DEVICE")
    if device_note:
        learn += f'<div class="device-note">{device_note}</div>'
    task = join(sections, "BUILD")
    done = join(sections, "DONE")
    stretch = join(sections, "STRETCH")
    stuck = join(sections, "STUCK")

    task_html = f'<div class="task"><div class="label">Your task</div>{task}'
    if done:
        task_html += f'<div class="label">Done when</div><div class="checks">{done}</div>'
    task_html += "</div>"
    extra = ""
    if stuck:
        extra += f'<div class="aside stuck"><span>If you are stuck</span>{stuck}</div>'
    if stretch:
        extra += f'<div class="aside stretch"><span>Push further</span>{stretch}</div>'

    return (f'<section class="day" id="day-{int(number)}">'
            f'<div class="unit">{head}<div class="learn">{learn}</div></div>'
            f'<div class="unit">{task_html}{extra}</div></section>')


def render_boss(fields, sections):
    _, number, span, title, device = (fields + ["", "", "", "", "phone"])[:5]
    parts = [f'<section class="boss"><div class="boss-band">'
             f'<p class="boss-no">Boss week {number} &middot; days {inline(span)}</p>'
             f'<h2>{inline(title)}</h2>{device_tag(device)}</div>']
    if sections.get("TEXT"):
        parts.append(f'<div class="unit"><h4>The brief</h4>{join(sections, "TEXT")}</div>')
    if sections.get("MUST"):
        parts.append(f'<div class="unit"><h4>Must have</h4><div class="checks">{join(sections, "MUST")}</div></div>')
    if sections.get("NICE"):
        parts.append(f'<div class="unit"><h4>Nice to have</h4>{join(sections, "NICE")}</div>')
    if sections.get("PLAN"):
        parts.append(f'<div class="unit"><h4>Day by day</h4><div class="plan">{join(sections, "PLAN")}</div></div>')
    if sections.get("LEARN"):
        parts.append(f'<div class="unit"><h4>New ideas this week</h4>{join(sections, "LEARN")}</div>')
    if sections.get("DONE"):
        parts.append(f'<div class="unit"><h4>Done when</h4><div class="checks">{join(sections, "DONE")}</div></div>')
    if sections.get("STUCK"):
        parts.append(f'<div class="unit aside stuck"><span>If you are stuck</span>{join(sections, "STUCK")}</div>')
    parts.append("</section>")
    return "".join(parts)


RENDERERS = {"page": render_page, "level": render_level, "day": render_day, "boss": render_boss}


# --------------------------------------------------------------------------
# Generated pages: contents, laptop table, tracker
# --------------------------------------------------------------------------

def collect(all_blocks):
    days, bosses, levels = {}, [], []
    for fields, _ in all_blocks:
        kind = fields[0]
        if kind == "day":
            days[int(fields[1])] = (fields[2], fields[3] if len(fields) > 3 else "phone")
        elif kind == "boss":
            lo, hi = [int(x) for x in re.findall(r"\d+", fields[2])[:2]]
            bosses.append((fields[1], lo, hi, fields[3], fields[4] if len(fields) > 4 else "phone"))
        elif kind == "level":
            levels.append((fields[1], fields[2], fields[3], fields[4]))
    return days, bosses, levels


def render_contents(days, bosses, levels):
    rows = []
    for number, name, subject, span in levels:
        rows.append(f'<div class="toc-level"><b>Level {number}</b><span>{inline(name)}</span>'
                    f'<em>{inline(span)}</em></div>')
        lo, hi = [int(x) for x in re.findall(r"\d+", span)[:2]]
        for boss_no, b_lo, b_hi, title, _ in bosses:
            if lo <= b_lo <= hi:
                rows.append(f'<div class="toc-boss"><b>Boss week {boss_no}</b><span>{inline(title)}</span>'
                            f'<em>days {b_lo} to {b_hi}</em></div>')
    return f'<section class="page toc"><h2>Contents</h2>{"".join(rows)}</section>'


def render_laptop_table(days, bosses):
    rows = [(n, t) for n, (t, d) in sorted(days.items()) if d == "laptop"]
    rows += [(f"{lo} to {hi}", f"Boss week {no}: {t}")
             for no, lo, hi, t, d in bosses if d == "laptop"]
    body = "".join(f"<tr><td>Day {n}</td><td>{inline(t)}</td></tr>" for n, t in rows)
    return (f'<table class="laptop-table"><tr><th>Day</th><th>Topic</th></tr>'
            f"{body}</table>")


def render_tracker(bosses):
    boss_days = set()
    for _, lo, hi, _, _ in bosses:
        boss_days.update(range(lo, hi + 1))
    cells = "".join(
        f'<div class="cell{" boss-cell" if d in boss_days else ""}"><span>{d}</span></div>'
        for d in range(1, 101)
    )
    return (f'<section class="page tracker"><h2>Progress tracker</h2>'
            f"<p>Tick a box when you finish a day's task, not when you read it. Shaded boxes are boss "
            f"week days. Missing a day is fine. Just pick up where you stopped.</p>"
            f'<div class="grid">{cells}</div></section>')


# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------

CSS = """
@page {
  size: A4;
  margin: 16mm 16mm 17mm;
  @bottom-left { content: "100 days of web development"; font: 8.2pt "Segoe UI", Arial, sans-serif; color: #85857c; }
  @bottom-right { content: counter(page); font: 8.2pt "Segoe UI", Arial, sans-serif; color: #85857c; }
}
@page :first { @bottom-left { content: none; } @bottom-right { content: none; } }

:root {
  --ink: #15150f;
  --ink-2: #44443c;
  --ink-3: #7c7c73;
  --rule: #d8d8ce;
  --green: #0a7a52;
  --green-soft: #eaf5ef;
  --boss: #b3124f;
  --boss-soft: #fbeef3;
  --warn: #9a5a00;
  --warn-soft: #fdf5e7;
  --code-bg: #f3f3ee;
}

* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Segoe UI", Arial, sans-serif; font-size: 10.2pt; line-height: 1.5; color: var(--ink); }

p { margin: 0 0 2.6mm; }
ul, ol { margin: 0 0 2.6mm; padding-left: 5.5mm; }
li { margin-bottom: 1mm; }
h2, h3, h4 { margin: 0; }
b { font-weight: 600; }

code {
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 8.9pt;
  color: #5a2a86;
}

.code, .unit, table, .plan-row, .cell { break-inside: avoid; }

.code { margin: 1mm 0 3mm; border: 1px solid var(--rule); background: var(--code-bg); }
.code .file {
  font-family: "Cascadia Mono", Consolas, monospace; font-size: 7.4pt; color: var(--ink-3);
  padding: 1mm 2.8mm; border-bottom: 1px solid var(--rule); background: #ebebe3;
}
.code pre {
  margin: 0; padding: 2.6mm 3.2mm;
  font-family: "Cascadia Mono", Consolas, monospace; font-size: 8.7pt; line-height: 1.48;
  white-space: pre-wrap; color: var(--ink);
}
.c { color: #7c7c73; font-style: italic; }
.s { color: #0b5c38; }
.k { color: #5a2a86; font-weight: 600; }
.n { color: #9a4a00; }
.t { color: #9a4a00; }

/* ---------- cover ---------- */

.cover { height: 262mm; display: flex; flex-direction: column; justify-content: space-between; break-after: page; }
.cover-top { border-top: 6px solid var(--ink); padding-top: 8mm; }
.cover .kicker { font-family: "Cascadia Mono", Consolas, monospace; font-size: 9.5pt; color: var(--green); margin-bottom: 20mm; }
.cover h1 {
  font-family: Georgia, "Times New Roman", serif; font-size: 52pt; line-height: .98;
  letter-spacing: -0.025em; margin: 0 0 7mm;
}
.cover .sub { font-size: 14pt; color: var(--ink-2); max-width: 30ch; line-height: 1.35; margin: 0; }
.cover-levels { display: flex; border-top: 1px solid var(--ink); }
.cover-levels div { flex: 1; padding: 4mm 3mm 0 0; }
.cover-levels b { display: block; font-family: "Cascadia Mono", Consolas, monospace; font-size: 8.5pt; color: var(--green); font-weight: 400; }
.cover-levels span { font-size: 10pt; }
.cover-foot { font-size: 9pt; color: var(--ink-3); border-top: 1px solid var(--rule); padding-top: 3mm; }

/* ---------- generic pages ---------- */

.page { break-before: page; }
.page h2, .level h2, .boss h2 {
  font-family: Georgia, "Times New Roman", serif; font-size: 22pt; line-height: 1.1; letter-spacing: -0.01em;
}
.page > h2 { border-bottom: 2px solid var(--ink); padding-bottom: 2.4mm; margin-bottom: 5mm; }
h4.sub { font-size: 11.5pt; font-weight: 700; margin: 5mm 0 1.6mm; break-after: avoid; }
.day h4.sub, .boss h4.sub { font-size: 10pt; margin: 3mm 0 1.2mm; }
.flow { break-before: auto; margin-top: 10mm; }

.toc-level, .toc-boss { display: flex; gap: 4mm; padding: 2.2mm 0; border-bottom: 1px solid var(--rule); align-items: baseline; }
.toc-level b { color: var(--green); min-width: 22mm; }
.toc-level span { font-weight: 600; flex: 1; }
.toc-boss { padding-left: 8mm; }
.toc-boss b { color: var(--boss); min-width: 26mm; font-weight: 600; font-size: 9.2pt; }
.toc-boss span { flex: 1; }
.toc em, .toc-boss em { font-style: normal; color: var(--ink-3); font-size: 9pt; }

/* ---------- levels ---------- */

.level { break-before: page; padding-top: 30mm; }
.level-no { font-family: "Cascadia Mono", Consolas, monospace; font-size: 11pt; color: var(--green); margin: 0 0 2mm; }
.level h2 { font-size: 36pt; margin-bottom: 2mm; }
.level-sub { font-size: 12pt; color: var(--ink-3); margin-bottom: 9mm; border-bottom: 2px solid var(--ink); padding-bottom: 4mm; }
.level > p { font-size: 11pt; max-width: 150mm; }
.level-end { margin-top: 7mm; padding: 4mm 5mm 2mm; background: var(--green-soft); border: 1px solid #bfdccb; }
.level-end h4 { font-size: 10pt; color: var(--green); margin-bottom: 2mm; }

/* ---------- days ---------- */

.day { margin: 0 0 7mm; padding-top: 4mm; border-top: 2px solid var(--ink); }
.day-head { display: flex; align-items: baseline; gap: 3.5mm; margin-bottom: 2.4mm; flex-wrap: wrap; }
.day-no { font-family: "Cascadia Mono", Consolas, monospace; font-size: 10pt; color: var(--green); white-space: nowrap; }
.day-head h3 { font-family: Georgia, "Times New Roman", serif; font-size: 15pt; line-height: 1.15; flex: 1; min-width: 60mm; }

.device { font-size: 7.8pt; font-weight: 600; white-space: nowrap; padding: .4mm 2mm; border: 1px solid; }
.device-phone { color: var(--green); border-color: #bfdccb; }
.device-laptop { color: var(--warn); border-color: #efd3a8; background: var(--warn-soft); }
.boss-band .device { background: #fff; }

.device-note { font-size: 9.2pt; color: var(--warn); background: var(--warn-soft); border: 1px solid #efd3a8; padding: 2mm 3mm; margin: 1mm 0 3mm; }
.device-note p { margin: 0; }

.task { border: 1px solid var(--rule); padding: 3mm 3.6mm 1mm; margin-bottom: 2.5mm; }
.label { font-size: 8.2pt; font-weight: 700; color: var(--green); margin-bottom: 1mm; }
.task .label + p { font-size: 10.2pt; }
.task .label:not(:first-child) { margin-top: 2mm; }

.checks ul { list-style: none; padding-left: 0; }
.checks li { position: relative; padding-left: 5.5mm; }
.checks li::before {
  content: ""; position: absolute; left: 0; top: 1.3mm;
  width: 2.8mm; height: 2.8mm; border: 1.2px solid var(--ink-3);
}

.aside { font-size: 9.4pt; padding: 2mm 3.2mm .6mm; margin-bottom: 2mm; }
.aside > span { display: block; font-size: 8pt; font-weight: 700; margin-bottom: .6mm; }
.aside p { margin-bottom: 1.4mm; }
.stretch { background: #f4f4ef; }
.stretch > span { color: var(--ink-2); }
.stuck { background: var(--warn-soft); }
.stuck > span { color: var(--warn); }

/* ---------- boss weeks ---------- */

.boss { break-before: page; break-after: page; }
.boss-band { border-top: 6px solid var(--boss); padding: 4mm 0 4mm; margin-bottom: 4mm; border-bottom: 1px solid var(--rule); }
.boss-no { font-family: "Cascadia Mono", Consolas, monospace; font-size: 9.5pt; color: var(--boss); margin: 0 0 1.5mm; }
.boss h2 { margin-bottom: 2.5mm; }
.boss h4 { font-size: 10.5pt; color: var(--boss); margin: 3mm 0 1.6mm; }
.plan-row { display: flex; gap: 4mm; padding: 1.6mm 0; border-bottom: 1px solid var(--rule); }
.plan-row span { font-family: "Cascadia Mono", Consolas, monospace; font-size: 8.8pt; color: var(--boss); min-width: 16mm; padding-top: .3mm; }
.plan-row div { flex: 1; }

/* ---------- tables and tracker ---------- */

table { border-collapse: collapse; width: 100%; margin: 1mm 0 4mm; font-size: 9.6pt; }
td, th { text-align: left; vertical-align: top; padding: 1.7mm 3mm 1.7mm 0; border-bottom: 1px solid var(--rule); }
th { font-weight: 600; border-bottom: 1.5px solid var(--ink); }
.laptop-table td:first-child { width: 34mm; white-space: nowrap; font-family: "Cascadia Mono", Consolas, monospace; font-size: 8.8pt; }

.tracker .grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 1.6mm; margin-top: 5mm; }
.cell { border: 1.2px solid var(--ink-3); aspect-ratio: 1 / 1; position: relative; }
.cell span { position: absolute; top: 1mm; left: 1.4mm; font-family: "Cascadia Mono", Consolas, monospace; font-size: 7.5pt; color: var(--ink-3); }
.boss-cell { background: var(--boss-soft); border-color: #e3a3bb; }
.boss-cell span { color: var(--boss); }
"""


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

COVER = """
<section class="cover">
  <div class="cover-top">
    <p class="kicker">html &middot; css &middot; javascript</p>
    <h1>100 days of web development</h1>
    <p class="sub">One assignment a day, building a gaming community website from the first tag to launch day.</p>
  </div>
  <div>
    <div class="cover-levels">
      <div><b>Level 1</b><span>Structure</span></div>
      <div><b>Level 2</b><span>Style</span></div>
      <div><b>Level 3</b><span>Behaviour</span></div>
      <div><b>Level 4</b><span>The platform</span></div>
    </div>
  </div>
  <div class="cover-foot">Most of it works on a phone. The days where a laptop makes a real difference are marked, and listed on one page near the front.</div>
</section>
"""


def build_html():
    files = sorted(CONTENT.glob("*.txt"))
    all_blocks = []
    for f in files:
        all_blocks.extend(parse_file(f))

    days, bosses, levels = collect(all_blocks)

    missing = [d for d in range(1, 101)
               if d not in days and not any(lo <= d <= hi for _, lo, hi, _, _ in bosses)]
    if missing:
        print(f"warning: no content for days {missing}")

    body = [COVER, render_contents(days, bosses, levels)]
    for fields, lines in all_blocks:
        kind = fields[0]
        sections = parse_body(lines)
        rendered = RENDERERS[kind](fields, sections)
        body.append(rendered.replace("{{LAPTOP_TABLE}}", render_laptop_table(days, bosses)))
    body.append(render_tracker(bosses))

    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            "<title>100 days of web development</title>"
            f"<style>{CSS}</style></head><body>{''.join(body)}</body></html>")


def find_browser():
    for path in BROWSERS:
        if os.path.exists(path):
            return path
    sys.exit("Could not find Chrome or Edge. Install one, or add its path to BROWSERS.")


def main():
    page = build_html()
    work = Path(tempfile.mkdtemp(prefix="100-days-"))
    try:
        html_file = work / "guide.html"
        html_file.write_text(page, encoding="utf-8")
        if "--html" in sys.argv:
            shutil.copy(html_file, HERE / "guide-preview.html")
        subprocess.run([
            find_browser(), "--headless=new", "--disable-gpu", "--no-first-run",
            "--no-pdf-header-footer", f"--user-data-dir={work / 'profile'}",
            f"--print-to-pdf={OUT_PDF}", html_file.as_uri(),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"Wrote {OUT_PDF.name}  ({OUT_PDF.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------
# The content format
# --------------------------------------------------------------------------
#
# Every block starts with a line beginning "@@ ", fields separated by "|":
#
#   @@ page | Title                          a plain page of prose
#   @@ level | 1 | Name | Subject | Days 1 to 14
#   @@ day | 5 | Title | phone              phone, preview or laptop
#   @@ boss | 1 | 11-14 | Title | phone
#
# Inside a block, a line holding only one of these words starts a section:
#   LEARN  BUILD  DONE  STRETCH  STUCK  DEVICE  TEXT  BY-THE-END
#   MUST  NICE  PLAN (boss weeks; plan lines look like "57 | what to do")
#
# Blank lines separate paragraphs. "- " starts a bullet, "1. " a numbered item.
# ```html / ```css / ```js ... ``` is a code block.
# `code` and **bold** work inside sentences.
# {{LAPTOP_TABLE}} inside a page is replaced with the list of laptop days.
