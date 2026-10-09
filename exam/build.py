"""
Builds exam.pdf (for students) and marking-guide.pdf (for the instructor).

    python build.py

The words live in exam.html and marking-guide.html. Inside those files, code in
<pre> is written as-is and escaped here, [[lines N]] becomes N ruled answer
lines, and questions number themselves. Chrome or Edge does the printing.
"""

import html
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

CSS = """
@page {
  size: A4;
  margin: 17mm 18mm 18mm;
  @bottom-left { content: "%(footer)s"; font: 8pt Georgia, serif; color: #666; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font: 8pt Georgia, serif; color: #666; }
}
* { box-sizing: border-box; }
html { font: 10.5pt/1.5 Georgia, "Times New Roman", serif; color: #111; background: #fff; }
body { margin: 0; counter-reset: q; }
p { margin: 0 0 2.4mm; }
code, pre { font-family: Consolas, "Courier New", monospace; }
code { font-size: 0.9em; }

.paper-head { border-bottom: 1.5px solid #111; padding-bottom: 4mm; margin-bottom: 5mm; }
.course { font-size: 9.5pt; letter-spacing: 0.04em; text-transform: uppercase; margin: 0 0 1mm; }
h1 { font-size: 17pt; font-weight: normal; margin: 0 0 4mm; }
.for { font-style: italic; margin: 0; }
.who { display: flex; gap: 10mm; }
.who span { display: flex; flex: 1; align-items: flex-end; gap: 2mm; }
.who span:last-child { flex: 0 0 55mm; }
.who i { flex: 1; border-bottom: 1px solid #111; height: 5mm; }
.blank { display: inline-block; width: 38mm; border-bottom: 1px solid #111; }

table { border-collapse: collapse; width: 100%%; margin: 0 0 4mm; font-size: 9.6pt; }
th, td { text-align: left; vertical-align: top; padding: 1.4mm 2.5mm 1.4mm 0; border-bottom: 1px solid #bbb; }
th { font-weight: bold; border-bottom: 1px solid #111; }
td:last-child, th:last-child { padding-right: 0; }
.overview td:first-child { width: 14mm; }
.overview td:nth-child(3) { width: 14mm; }
.overview td:nth-child(2) { width: 62mm; }
.overview td:nth-child(4) { white-space: nowrap; }
.overview .blank { width: 30mm; }
.marking { break-inside: avoid; margin-top: 3mm; }
.marking td:last-child, .marking th:last-child { width: 38mm; text-align: right; }

h2 { font-size: 13.5pt; margin: 7mm 0 2mm; padding-bottom: 1.5mm; border-bottom: 1px solid #111;
     display: flex; justify-content: space-between; align-items: baseline; break-after: avoid; }
h2.new-page { break-before: page; margin-top: 0; }
h3 { font-size: 11pt; text-transform: uppercase; letter-spacing: 0.06em; margin: 6mm 0 3mm; break-after: avoid; }
h3.brief-title { text-transform: none; letter-spacing: 0; font-size: 12.5pt; margin-top: 3mm; }
h4 { font-size: 10.5pt; margin: 5mm 0 2mm; display: flex; justify-content: space-between; break-after: avoid; }
.marks { font-weight: normal; font-size: 9.5pt; }
.note { font-style: italic; }

.q { position: relative; padding-left: 8mm; margin: 0 0 5mm; break-inside: avoid; counter-increment: q; }
.q::before { content: counter(q) "."; position: absolute; left: 0; top: 0; font-weight: bold; }
.q.a { margin-bottom: 3.5mm; }

pre { font-size: 8.8pt; line-height: 1.45; margin: 1.5mm 0 2.6mm; padding: 1.5mm 0 1.5mm 3.5mm;
      border-left: 2px solid #999; white-space: pre-wrap; break-inside: avoid; }
pre.tree, pre.sample { border-left-color: #ccc; }

ol.opts { list-style: none; padding: 0; margin: 1mm 0 0; counter-reset: opt; }
ol.opts li { counter-increment: opt; padding-left: 7mm; position: relative; margin-bottom: 1mm; }
ol.opts li::before { content: "(" counter(opt, lower-alpha) ")"; position: absolute; left: 0; }
ol.opts.two { display: grid; grid-template-columns: 1fr 1fr; column-gap: 6mm; }
ol.opts.four { display: grid; grid-template-columns: repeat(4, 1fr); column-gap: 6mm; }

h3 { display: flex; justify-content: space-between; align-items: baseline; }
h3 .marks { text-transform: none; letter-spacing: 0; }
h3.part-two { margin-top: 8mm; }
h3.page-break { break-before: page; margin-top: 0; }
.key { break-inside: auto; font-size: 9.2pt; }
.key td { padding-top: 1mm; padding-bottom: 1mm; }
.key tr { break-inside: avoid; }
.key td:nth-child(1) { width: 9mm; }
.key td:nth-child(2) { width: 16mm; font-weight: bold; }

ul, ol { margin: 0 0 3mm; padding-left: 6mm; }
li { margin-bottom: 1.2mm; }
ul.checks { list-style: none; padding-left: 0; }
ul.checks li { padding-left: 7mm; position: relative; }
ul.checks li::before { content: ""; position: absolute; left: 0; top: 1.1mm; width: 3.2mm; height: 3.2mm; border: 1px solid #111; }

.lines { margin-top: 1mm; }
.lines div { height: 7.5mm; border-bottom: 1px solid #aaa; }
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>%(title)s</title>
<style>%(css)s</style>
</head>
<body>
%(body)s
</body>
</html>
"""

DOCS = [
    ("exam.html", "exam.pdf", "Final exam", ""),
    ("marking-guide.html", "marking-guide.pdf", "Final exam marking guide", "Final exam: marking guide (instructor only)"),
]


def prepare(source):
    body = re.sub(r"<!--.*?-->", "", source, flags=re.S)
    body = re.sub(r"(<pre[^>]*>)(.*?)(</pre>)",
                  lambda m: m.group(1) + html.escape(m.group(2), quote=False) + m.group(3),
                  body, flags=re.S)
    body = re.sub(r"\[\[lines (\d+)\]\]",
                  lambda m: '<div class="lines">' + "<div></div>" * int(m.group(1)) + "</div>",
                  body)
    return body


def find_browser():
    for path in BROWSERS:
        if os.path.exists(path):
            return path
    raise SystemExit("Could not find Chrome or Edge. Add its path to BROWSERS in build.py.")


def main():
    browser = find_browser()
    work = Path(tempfile.mkdtemp(prefix="exam-"))
    try:
        for source, pdf, title, footer in DOCS:
            body = prepare((HERE / source).read_text(encoding="utf-8"))
            page = PAGE % {"title": title, "css": CSS % {"footer": footer}, "body": body}
            html_file = work / source
            html_file.write_text(page, encoding="utf-8")
            out = HERE / pdf
            subprocess.run([
                browser, "--headless=new", "--disable-gpu", "--no-first-run",
                "--no-pdf-header-footer", f"--user-data-dir={work / 'profile'}",
                f"--print-to-pdf={out}", html_file.as_uri(),
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            print(f"Wrote {pdf}  ({out.stat().st_size // 1024} KB)")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
