/* ==========================================================================
   build-standalone.js — fold the whole workshop into one HTML file
   --------------------------------------------------------------------------
   Run with:   node build-standalone.js
   Produces:   workshop.html   (everything inlined, nothing external)

   What it does:
     · inlines styles.css and slides.js
     · turns every SVG in assets/ into a data: URI
     · builds a self-contained copy of the finished student example
     · carries all four student files inside the page as JSON, so the
       "open the example" and "download the starter" buttons still work
     · rewrites the two folder links into buttons that use them

   The multi-file version in this folder stays the source of truth. Edit
   index.html / styles.css / slides.js, then re-run this script.
   ========================================================================== */

const fs = require("fs");
const path = require("path");

const here = __dirname;
const read = (...parts) => fs.readFileSync(path.join(here, ...parts), "utf8");

/* Literal splice. String.replace() treats "$$", "$&" and "$'" in the
   replacement as escapes, which quietly rewrites code containing them —
   slides.js uses a $$() helper, so replace() would corrupt it. */
function splice(haystack, needle, value) {
  if (haystack.indexOf(needle) === -1) {
    throw new Error("build-standalone: could not find " + needle);
  }
  return haystack.split(needle).join(value);
}

/* ---------- assets → data URIs ---------- */

function svgDataUri(filePath) {
  const svg = fs.readFileSync(filePath, "utf8").replace(/\s*\n\s*/g, " ").trim();
  return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
}

function collectAssets() {
  const map = {};
  ["images", "icons"].forEach((folder) => {
    const dir = path.join(here, "assets", folder);
    fs.readdirSync(dir)
      .filter((name) => name.endsWith(".svg"))
      .forEach((name) => {
        map["assets/" + folder + "/" + name] = svgDataUri(path.join(dir, name));
      });
  });
  return map;
}

const assets = collectAssets();

/* Replace real asset references with data URIs — but never inside a <pre> or
   a <textarea>. Those hold code the students read and edit, and a 2 KB data
   URI dropped into a beginner exercise would be worse than useless. */
function inlineAssets(html, prefix) {
  const protectedRegion = /<pre\b[\s\S]*?<\/pre>|<textarea\b[\s\S]*?<\/textarea>/gi;
  let out = "";
  let cursor = 0;
  let match;

  const swap = (chunk) => {
    let result = chunk;
    Object.keys(assets).forEach((assetPath) => {
      result = result.split(prefix + assetPath).join(assets[assetPath]);
    });
    return result;
  };

  while ((match = protectedRegion.exec(html)) !== null) {
    out += swap(html.slice(cursor, match.index)) + match[0];
    cursor = protectedRegion.lastIndex;
  }
  return out + swap(html.slice(cursor));
}

/* ---------- the finished example, as one self-contained page ---------- */

function buildStandaloneExample() {
  const html = read("student-finished-example", "index.html");
  const css = read("student-finished-example", "styles.css");
  return inlineAssets(
    splice(html, '<link rel="stylesheet" href="styles.css">', "<style>\n" + css + "\n    </style>"),
    "../"
  );
}

/* ---------- student files travelling inside the deck ---------- */

const studentFiles = {
  "starter-index": read("student-starter", "index.html"),
  "starter-styles": read("student-starter", "styles.css"),
  "example-index": read("student-finished-example", "index.html"),
  "example-styles": read("student-finished-example", "styles.css"),
  "example-standalone": buildStandaloneExample(),
};

/* Escaping "<" keeps the JSON from ever closing its own script tag. */
const studentJson = JSON.stringify(studentFiles).replace(/</g, "\\u003c");

/* ---------- rewrite the folder links into buttons ---------- */

function rewriteLinks(html) {
  let out = html;

  // "Open the starter page" becomes two downloads — one per file — so the
  // three deliberate faults survive exactly as written.
  out = out.replace(
    /<p><a class="btn" href="student-starter\/index\.html"[^>]*>Open the starter page<\/a><\/p>/,
    '<p class="row" style="gap:.5cqi;">' +
      '<button type="button" class="btn" data-action="download-starter-html">Download index.html</button>' +
      '<button type="button" class="btn" data-action="download-starter-css">Download styles.css</button>' +
      "</p>"
  );

  // Every link to the finished example opens the embedded copy in a new tab.
  out = out.replace(
    /<a class="([^"]*)" href="student-finished-example\/index\.html"[^>]*>([^<]*)<\/a>/g,
    '<button type="button" class="$1" data-action="open-example">$2</button>'
  );
  out = out.replace(
    /<a href="student-finished-example\/index\.html"[^>]*>([^<]*)<\/a>/g,
    '<button type="button" class="btn btn--sm" data-action="open-example">$1</button>'
  );

  // Give the reference slide a way to save the example files too.
  out = out.replace(
    '<button type="button" class="btn btn--sm" data-action="open-example">open student-finished-example/index.html</button>',
    '<button type="button" class="btn btn--sm" data-action="open-example">open the finished example</button>' +
      ' <button type="button" class="btn btn--sm" data-action="download-example-html">save its index.html</button>' +
      ' <button type="button" class="btn btn--sm" data-action="download-example-css">save its styles.css</button>'
  );

  return out;
}

/* ---------- assemble ---------- */

let html = read("index.html");

html = splice(
  html,
  '<link rel="stylesheet" href="styles.css">',
  "<style>\n" + read("styles.css") + "\n  </style>"
);

html = splice(
  html,
  '<script src="slides.js"></script>',
  "<script>\n" + read("slides.js").replace(/<\/script/gi, "<\\/script") + "\n</script>"
);

html = rewriteLinks(html);
html = inlineAssets(html, "");

html = splice(
  html,
  '<div class="confetti-layer" id="confetti" aria-hidden="true"></div>',
  '<div class="confetti-layer" id="confetti" aria-hidden="true"></div>\n\n' +
    "<!-- The student starter and finished example travel inside this file. -->\n" +
    '<script id="student-files" type="application/json">' + studentJson + "</script>"
);

const outputPath = path.join(here, "workshop.html");
fs.writeFileSync(outputPath, html, "utf8");

/* Report only references the browser would actually try to fetch. Paths shown
   inside code samples and the embedded student files are content, not links. */
const kb = (fs.statSync(outputPath).size / 1024).toFixed(0);
const scannable = html
  .replace(/<pre\b[\s\S]*?<\/pre>/gi, "")
  .replace(/<textarea\b[\s\S]*?<\/textarea>/gi, "")
  .replace(/<code\b[\s\S]*?<\/code>/gi, "")
  .replace(/<script id="student-files"[\s\S]*?<\/script>/i, "");
const leftovers = scannable.match(/(?:src|href)="(?!data:|#|https?:)[^"]+"/g) || [];

console.log("Wrote workshop.html — " + kb + " KB");
console.log("Slides: " + (html.match(/<section class="slide"/g) || []).length);
console.log("Fetchable external references: " + (leftovers.length ? leftovers.join(", ") : "none"));
