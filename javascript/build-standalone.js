/* ==========================================================================
   build-standalone.js — fold the JavaScript deck into one HTML file
   --------------------------------------------------------------------------
   Run with:   node build-standalone.js
   Produces:   js-workshop.html   (everything inlined, nothing external)

   The deck has no images and no companion folders, so this is only two
   inlines plus a slice option for handing students part of the course.
   ========================================================================== */

const fs = require("fs");
const path = require("path");

const here = __dirname;
const read = (name) => fs.readFileSync(path.join(here, name), "utf8");

/* String.replace() treats "$$", "$&" and "$'" in the replacement as escapes,
   which silently rewrites code containing them. Splice literally instead. */
function splice(haystack, needle, value) {
  if (haystack.indexOf(needle) === -1) {
    throw new Error("build: could not find " + needle);
  }
  return haystack.split(needle).join(value);
}

/* Keep slides from the first up to and including `lastSlideId`. */
function sliceThrough(html, lastSlideId) {
  if (!lastSlideId) return html;
  const at = html.indexOf('id="' + lastSlideId + '"');
  if (at === -1) throw new Error("slice target not found: " + lastSlideId);
  const closer = "\n</section>";
  const closeAt = html.indexOf(closer, at);
  if (closeAt === -1) throw new Error("could not close the slice at " + lastSlideId);
  const endOfSlide = closeAt + closer.length;
  const mainEnd = html.indexOf("\n</main>", endOfSlide);
  if (mainEnd === -1) throw new Error("no </main> after " + lastSlideId);
  return html.slice(0, endOfSlide) + html.slice(mainEnd);
}

/* A cut deck must not link to a slide it no longer contains. */
function checkLinks(html, label) {
  const wanted = (html.match(/href="#(s-[\w-]+)"/g) || []).map((h) =>
    h.slice('href="#'.length, -1)
  );
  const dangling = [...new Set(wanted)].filter(
    (id) => html.indexOf('id="' + id + '"') === -1
  );
  if (dangling.length) {
    throw new Error(label + ": links to missing slides — " + dangling.join(", "));
  }
}

const SOURCE_TITLE = "JavaScript From Zero — Make The Page Do Something";

const BUILDS = [
  {
    out: "js-workshop.html",
    through: null,
    title: SOURCE_TITLE,
    note: "full five hours"
  }
  /* To hand students only part of the course, add an entry like:
     {
       out: "js-part-1.html",
       through: "s-mark-2",
       title: "JavaScript From Zero — Part 1: Values and Functions",
       note: "sections 00 to 03"
     }
     Useful cut points: s-mark-1 values · s-mark-2 functions ·
     s-console-race decisions · s-mark-3 lists · s-mark-4 objects ·
     s-mark-5 the page · s-mark-6 events. */
];

function build(config) {
  let html = read("index.html");

  html = sliceThrough(html, config.through);

  if (config.title !== SOURCE_TITLE) {
    html = splice(html, "<title>" + SOURCE_TITLE + "</title>", "<title>" + config.title + "</title>");
  }

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

  checkLinks(html, config.out);

  const target = path.join(here, config.out);
  fs.writeFileSync(target, html, "utf8");

  /* Only count references the browser would actually fetch — paths inside
     code samples and editors are teaching content, not links. */
  const scannable = html
    .replace(/<pre\b[\s\S]*?<\/pre>/gi, "")
    .replace(/<textarea\b[\s\S]*?<\/textarea>/gi, "")
    .replace(/<code\b[\s\S]*?<\/code>/gi, "");
  const leftovers = scannable.match(/(?:src|href)="(?!data:|#|https?:)[^"]+"/g) || [];

  const kb = (fs.statSync(target).size / 1024).toFixed(0);
  const slides = (html.match(/<section class="slide"/g) || []).length;
  const last = [...html.matchAll(/data-title="([^"]+)"/g)].pop();

  console.log(
    config.out.padEnd(20) + String(slides).padStart(3) + " slides" +
    kb.padStart(6) + " KB   " + config.note
  );
  console.log(
    "".padEnd(20) + "ends on: " + (last ? last[1] : "?") +
    "   external refs: " + (leftovers.length ? leftovers.join(", ") : "none")
  );
}

BUILDS.forEach(build);
