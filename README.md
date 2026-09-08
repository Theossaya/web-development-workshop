# Web Development From Zero — Instructor Guide

**Build, Inspect and Remix the Web in 2026**

A complete, offline-capable, three-hour HTML and CSS workshop for absolute beginners
aged roughly 15 and up. The deck is a plain web page: no installation, no build step,
no internet connection required.

Students spend about 60% of the session typing, 20% listening and 20% competing,
debugging and explaining. They finish with a one-page website they wrote, broke,
repaired and personalised themselves.

---

## 1. Quick start

Three builds of the same source. Use whichever suits where the class has got to.

### For students right now — `session-1.html`

**183 KB, 32 slides: everything through semantic HTML (slide 28), plus
Assignment 1.** This is the link to hand out after session one. It stops exactly
where the teaching stopped — no CSS, no DevTools, no spoilers — and ends with
the take-home assignment.

Live link: `https://theossaya.github.io/web-development-workshop/session-1.html`

### For you — `workshop.html`

One 394 KB file with **everything** inside it: all 83 slides, the styling, the
behaviour, every illustration as a data URI, and both student projects embedded.
No folder, no assets directory, nothing to go missing.

- Email it, drop it on a USB stick, put it in a shared drive, or host it — see
  “Putting it online” below.
- Double-click it and it runs.
- Students click **Download index.html** / **Download styles.css** on the final
  build slide to get the starter files, and **open the finished example** to
  inspect the reference build in a new tab.

### The folder — `index.html` + `styles.css` + `slides.js`

The editable source. Use this one if you want to change slides, colours or
timings. Copy the whole folder, double-click `index.html`.

Either way: press <kbd>F</kbd> for full screen, <kbd>→</kbd> to advance,
<kbd>N</kbd> for instructor notes. Nothing to install, nothing to serve.

**After editing the folder version, regenerate both single files:**

```bash
node build-standalone.js
```

That is the only step that needs Node, and only you need it — never the
students.

### Growing the student link as the course goes on

`session-1.html` stops at a slide you choose. To extend it after session two,
open `build-standalone.js`, find the `BUILDS` list near the bottom, and change
one line:

```js
{
  out: "session-2.html",
  through: "s-checkpoint-7",       // the last slide students should see
  title: "Web Development From Zero — Session 2: CSS and Layout",
  note: "session two — students",
},
```

Add it to the list, run the build, push. The slide counter, progress bar,
section markers and navigator all rebuild themselves from whatever slides
survive the cut. The build refuses to write a file that links to a slide it has
just removed, so a bad cut point fails loudly instead of shipping a dead link.

Useful cut points:

| Ends after | `through:` | Covers |
| --- | --- | --- |
| Semantic HTML + assignment | `s-assignment-submit` | Sections 0–5 (current session-1) |
| DevTools | `s-devtools-rebuild` | + inspecting real sites |
| Styled cards | `s-checkpoint-5` | + CSS, selectors and classes |
| Responsive page | `s-checkpoint-7` | + box model, Flexbox, media queries |
| Everything | `null` | the full deck |

### Running it locally

**You do not need a server to present.** Double-click any deck file and it runs:
`session-1.html`, `workshop.html`, or `javascript/js-workshop.html`. The single
files carry everything inside them, and the JavaScript deck's code runners work
with no server at all.

The one thing that needs a server: **local storage**. Team scores, the theme and
your last slide are remembered in the browser, and some browsers block storage on
`file://` paths. If the scoreboard forgets itself between refreshes, that is why.

Run a server when you want scores to persist, or when you want the class on their
own laptops with no internet:

**Double-click `serve.bat`.** It serves this folder on port 8000 and prints both
addresses — the one for your laptop and the one for the classroom wifi.

Or by hand, from this folder:

```bash
python -m http.server 8000 --bind 0.0.0.0
```

Then:

| Who | Address |
| --- | --- |
| You | `http://localhost:8000/javascript/js-workshop.html` |
| Students on the same wifi | `http://YOUR-IP:8000/javascript/js-workshop.html` |

Find your IP with `ipconfig`, or just read it off the `serve.bat` window.

Windows will ask to allow Python through the firewall the first time. Say **yes
for Private networks** — decline it and students cannot connect. School wifi that
isolates clients from each other will also block this; if so, fall back to the
GitHub Pages link or a USB stick.

### Putting it online

`workshop.html` is a static page with no dependencies, so any host will serve
it. The two easiest:

**GitHub Pages**

1. Create a repository and upload `workshop.html`.
2. Rename it to `index.html` if you want the bare repo URL to open it —
   otherwise leave the name and link straight to the file.
3. Repository → **Settings → Pages** → Source: *Deploy from a branch* →
   branch `main`, folder `/ (root)` → **Save**.
4. Wait about a minute. Your link is:
   - `https://YOUR-NAME.github.io/YOUR-REPO/` (if you renamed it), or
   - `https://YOUR-NAME.github.io/YOUR-REPO/workshop.html` (if you did not).

**Anything else** — Netlify Drop, Cloudflare Pages, a school web folder, or
Google Drive with link sharing. Drag the file in; there is nothing to configure
and no build step to run.

Students only need the link. The deck works the same over HTTPS as it does from
a USB stick, and it keeps working if the wifi drops mid-session once the page
has loaded.

---

## 2. File tree

```text
web-development-workshop/
│
├── session-1.html                 ★ HAND THIS OUT — slides 1–28 + Assignment 1
├── workshop.html                  the full deck as one file — for you
│
├── index.html                     the presentation source (83 slides)
├── styles.css                     presentation styling only
├── slides.js                      presentation behaviour only
├── build-standalone.js            rebuilds both single files from the above
├── assignment-1.md                printable assignment sheet for the LMS
├── README.md                      this instructor guide
│
├── student-starter/               hand this to students for the final build
│   ├── index.html                 scaffold + 3 deliberate faults (Level 3)
│   └── styles.css
│
├── student-finished-example/      reference build AND the offline DevTools target
│   ├── index.html
│   └── styles.css
│
└── assets/
    ├── images/                    local SVG illustrations — no remote assets
    │   ├── event-hero.svg
    │   ├── workshop-build.svg
    │   ├── talk-code-poetry.svg
    │   ├── talk-first-robot.svg
    │   └── talk-design-jam.svg
    └── icons/
        ├── html.svg
        ├── css.svg
        ├── devtools.svg
        ├── bug.svg
        └── trophy.svg
```

---

## 3. Deck controls

### Keyboard

| Key | Action |
| --- | --- |
| <kbd>→</kbd> <kbd>Space</kbd> <kbd>PageDown</kbd> | Next slide |
| <kbd>←</kbd> <kbd>PageUp</kbd> | Previous slide |
| <kbd>Home</kbd> / <kbd>End</kbd> | First / last slide |
| <kbd>O</kbd> | Slide navigator (jump anywhere) |
| <kbd>N</kbd> | Instructor notes on/off |
| <kbd>T</kbd> | Timer panel |
| <kbd>S</kbd> | Team scoreboard |
| <kbd>B</kbd> | Bright-room / dark-room mode |
| <kbd>F</kbd> | Full screen |
| <kbd>R</kbd> | Reset the interactive exercises on this slide |
| <kbd>Esc</kbd> | Close open panels |
| <kbd>?</kbd> | Shortcut list |

Shortcuts are ignored while the cursor is inside a code editor or text field, so
students typing in a playground never trigger a slide change.

### On screen

Every keyboard action also has a button in the toolbar along the bottom: previous,
slide counter, next, all-slides navigator, notes, timer, scores, reset exercises,
bright room, full screen and help. The progress bar sits along the very bottom edge
with a tick mark at the start of each section.

### Timers

Open with <kbd>T</kbd> or the **Timer** button. Presets: 30s prediction, 60s speed
edit, 3-minute mini challenge, 5-minute pair challenge, 15-minute build. Start,
pause and reset are always available; the display turns amber for the final ten
seconds and red at zero. **Sound on / Sound off** toggles the end chime and the
choice is remembered.

Most challenge slides carry their own **Start** button that opens the timer with
the right duration and starts it in one click.

### Team scoreboard

Open with <kbd>S</kbd>. Choose 2–6 teams, rename any team by typing in its field,
add or subtract points, reset all scores, or hide the panel. Scores and names are
kept in the browser's local storage and survive a refresh or an accidental tab
close. If local storage is blocked, the scoreboard still works for the session —
it simply will not persist.

Points across the deck reward correct predictions, clear explanations, finding
bugs, helping another team, readable code and optional extensions. Speed alone is
never the sole route to points, and the highest-value item in the whole deck is
Level 5: helping somebody else understand their problem.

### Playgrounds

Every playground has an editable HTML pane, usually an editable CSS pane, a live
preview, and **Run**, **Reset** and **Copy** buttons. Hints and solutions are
collapsed panels that only open on a deliberate click. The preview renders inside
a sandboxed `iframe` using `srcdoc`, so student code can never affect the deck.
Nothing students type is sent anywhere.

**Reset exercises** (toolbar, or <kbd>R</kbd>) restores the current slide's
playgrounds to their starting code, closes any opened hints and solutions, clears
quiz answers and returns the box-model and Flexbox labs to their defaults.

---

## 4. Before class

### Required software

- Any Chromium browser (Chrome or Edge) on the teaching machine and on student
  laptops. Firefox and Safari also work; DevTools shortcuts differ slightly.
- VS Code on student machines, if possible. If it is not available, the deck's
  Route B browser editor covers the whole workshop — see slide **Route B**.
- Nothing else. No Node, no npm, no extensions, no accounts.

### Projector check (do this the day before)

1. Open `index.html` on the teaching machine and press <kbd>F</kbd>.
2. Walk to the back of the room and read a code panel — for example the slide
   **Anatomy of a CSS rule**. If you cannot read it, the room needs the bright-room
   mode (<kbd>B</kbd>), which raises contrast considerably on washed-out projectors.
3. Advance five slides and confirm nothing is cut off at the edges.
4. Open the timer and confirm the end chime is audible, or turn sound off.

### File distribution

Pick one, in order of preference:

1. **A link to `workshop.html`.** Nothing to copy. Students get the starter
   files from the download buttons on the final build slide, and open the
   finished example from any of the “open the finished example” buttons.
2. **USB stick or shared drive.** Copy `workshop.html` on its own, or the whole
   folder if you want students to have the loose starter files directly.
3. **Zip by email or LMS.** Warn students to *extract* the zip before editing —
   editing files inside a zip preview is the single most common setup failure.

If you hand out the folder rather than the single file, students only need
`student-starter/`. Give them `student-finished-example/` at the DevTools
section so they have a small, real page to inspect offline.

### Offline preparation

The deck has no remote fonts, no CDN, no analytics and no network calls of any
kind. All illustrations are local SVG files. It works with the network cable
unplugged. Verify by opening it in aeroplane mode once before class.

### Resetting between classes

- **Scores:** open the scoreboard and press **Reset scores**, or rename the teams.
- **Playgrounds:** press <kbd>R</kbd> on any slide you used, or simply reload the
  page — playgrounds always start from their original code on load.
- **Everything:** reload with <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>R</kbd>. Only
  the theme, notes visibility, sound setting, team scores and the last slide you
  viewed are remembered; nothing else persists.

### Team arrangement

Four teams of 4–7 works well for a class of 12–30. Mix confidence levels
deliberately. Seat students in pairs at one laptop where numbers allow — pair
work produces noticeably more explaining out loud, which is where the learning is.

Name the teams after things they will learn: Team Tag, Team Selector, Team Flexbox,
Team Inspect. The scoreboard is pre-filled with these.

### Optional printed materials

Print these slides one-sided, one per pair:

- **Reference · Keyboard shortcuts and scavenger sheet** — the right-hand column is
  the scavenger hunt worksheet.
- **Reference · Project checklist and rubric** — hand out at the start of the final
  build, not at the end.
- **Debugging · Reference — the usual suspects** — the nineteen-bug table.
- **Reference · HTML tag reference** and **Reference · CSS property reference**.

Use <kbd>Ctrl</kbd>+<kbd>P</kbd>. The deck has a print stylesheet that lays every
slide out as a flowing document with the instructor notes included, one slide per
page. For student handouts, print only the page ranges you need.

For the Human DOM activity, write these nine labels on index cards:
`header`, `nav`, `main`, `section "About"`, `section "Schedule"`,
`section "Sessions"`, `article "Card 1"`, `article "Card 2"`, `footer`.

---

## 5. During class — the full route

### Timing at a glance

| Time | Section | Slides | Mode |
| --- | --- | --- | --- |
| 0–10 | Opening hook | Title → You have already changed a web page | Demo + all type |
| 10–18 | What the browser is doing | Two files in, one page out → Sorting activity | Demo + teams |
| 18–28 | Prepare the workspace | A website is a folder → Setup checkpoint | All type |
| 28–45 | First HTML document | Anatomy of an element → Checkpoint 1 | All type + pairs |
| 45–65 | Add useful content | Attributes → Checkpoint 2 | All type + teams |
| 65–80 | Semantic HTML | div soup → Checkpoint 3 | Discussion + whole class |
| 80–90 | **Break** | Ten-minute countdown | — |
| 90–110 | Inspect a live website | DevTools → Reconstruct a card | Demo + teams + pairs |
| 110–120 | Connect CSS | Linking the stylesheet → Teacher Trap | All type |
| 120–135 | Selectors and classes | Element/class/id → Checkpoint 5 | All type + pairs |
| 135–150 | Box model | Box model → CSS Target Match | All experiment + pairs |
| 150–165 | Flexbox | Flex intro → Checkpoint 6 | All experiment |
| 165–175 | Responsive design | Media queries → Checkpoint 7 | All type + pairs |
| 175–185 | Accessibility | Nine habits → Spot the problem | Teams |
| 185–190 | Debugging + AI | Do Not Start Again → Simplify | Demo + pairs |
| 190–220 | Final build | The brief → Checkpoint 8 | Individual |
| 220–235 | Closing | Showcase → Final message | Whole class |

The core workshop is the 0–190 block plus a 15–20 minute build. The extended
version runs the full final build and the showcase, adding 45–60 minutes.

### Slide types

**Demonstration slides — you drive, students watch:**
the reveal (`That is all of it`), the browser diagram, both semantic-HTML slides,
all four DevTools slides, Teacher Trap, and `Do Not Start Again`.

**Typing slides — every student types along:**
Route A and Route B setup, both build steps, the content tags slide, checkpoint 3
(wrapping in semantic regions), the CSS link slide, and all eight checkpoints.

**Individual activities:**
the micro-challenge (About block), the Flexbox challenge, the final build,
the exit challenge.

**Paired activities:**
Bug Hunt #1, the reconstruction challenge, three cards / one class, the wide-card
diagnosis, CSS Target Match, Responsive Rescue, and the AI simplification.

**Team activities (scoreboard on):**
the sorting activity, Predict the Output, Tag Relay, Human DOM, the DevTools
scavenger hunt, Mystery Property, Spot the problem, and Teacher Trap.

### Questions worth asking repeatedly

- “What do you think will happen before I press refresh?”
- “Why did that work?” — worth more points than the fix itself.
- “Is that structure or appearance?”
- “If the CSS file disappeared, would this page still make sense?”
- “Which step of the debugging routine are you on?”
- “Show me on your screen.”

### Common beginner misunderstandings

| Misunderstanding | Where it appears | Counter it with |
| --- | --- | --- |
| The `head` is the top of the page | Build step 1 | Save and refresh — the page is blank |
| `h1` means “big text” | Predict the Output | It means most important; CSS decides the size |
| Indentation changes the page | Nesting | It changes whether *you* can read the file |
| `href="#schedule"` searches for the word | Micro-challenge | It looks for a matching `id` |
| A `div` is a beginner mistake | Semantic HTML | It is correct when no named element fits |
| DevTools edits the real website | DevTools step 13 | Refresh — everything vanishes |
| The dot goes in the HTML | Selectors | The dot lives in the CSS only |
| `width: 300px` means 300px of space | Box model lab | Read the live readout while dragging |
| `display: flex` goes on the children | Flexbox | Say “flex goes on the parent” three times |
| Media queries can go anywhere | Responsive | Later rules win — put queries last |
| A clickable `div` is basically a button | Spot the problem | Try to reach it with <kbd>Tab</kbd> |
| More code means better code | AI simplification | Seven elements become three |

### Pace signals

**Going too fast** — hands stop going up; students stop typing and start watching;
two or more people ask you to go back a slide; a checkpoint takes more than double
its budget; students copy your code without changing the words.

*Fix:* stop, go to the nearest checkpoint slide, let everyone catch up, and cut the
next optional activity.

**Going too slow** — students finish challenges with a third of the time left;
side conversations start; people begin styling things you have not taught yet.

*Fix:* skip to the extension task on the current challenge slide, or move the final
build earlier and make it longer. Fast rooms benefit far more from extra build time
than from extra content.

### Where to pause for catch-up

The eight checkpoint slides exist for exactly this. Never skip them:

1. **Checkpoint 1** — a valid HTML page
2. **Checkpoint 2** — content and links
3. **Checkpoint 3** — semantic structure
4. **Checkpoint 4** — first stylesheet
5. **Checkpoint 5** — styled cards
6. **Checkpoint 6** — Flexbox layout
7. **Checkpoint 7** — responsive page
8. **Checkpoint 8** — the finished project

A student who has fallen behind can copy the checkpoint code, change the words to
their own, and rejoin the class in ninety seconds.

### What to shorten first

In order, if you are running late:

1. The reconstruction challenge (DevTools).
2. CSS Target Match — the box-model lab already teaches it.
3. Mystery Property — keep only mystery A.
4. The AI segment — say rule 3 out loud and move on.
5. Human DOM — run it as a 90-second discussion using the on-screen chips.
6. The scavenger hunt — run four items instead of nine.

Never shorten: the opening remix, the setup checkpoint, the checkpoints, the
DevTools refresh moment (step 13), or the final build.

---

## 6. After class

### Saving and submitting projects

- **Simplest:** students zip their project folder and upload it to the LMS.
- **Route B students:** press **Copy** in the playground, paste into a text file,
  save as `index.html` and `styles.css` in one folder, and check it opens.
- **Keeping it:** the folder is the website. It opens on any machine, forever, with
  no dependencies. Say this — students find it genuinely surprising.
- **Publishing (optional homework):** GitHub Pages or Netlify Drop will host the
  folder for free. This is deliberately left out of the workshop itself.

### Assessment rubric — 20 points

**HTML structure — 5**
valid skeleton · logical heading order · semantic regions · useful content ·
correct nesting

**CSS — 5**
external stylesheet · reusable classes · readable spacing · consistent styling ·
no major broken rules

**Layout and responsiveness — 4**
Flexbox used appropriately · cards wrap or stack · readable on narrow screens ·
no significant horizontal overflow

**Usability and accessibility — 3**
useful link wording · alt text on meaningful images · readable contrast and
visible focus

**Independence and explanation — 3**
can explain their own code · made meaningful personal changes · debugged at least
one issue themselves

**Do not grade visual taste.** There is no single correct design. A page you would
not have designed is not a page that loses points. Deduct only for things that are
unreadable, broken or copied wholesale.

### Practice tasks (homework)

1. Build the same page shape for a completely different subject, from an empty
   folder, with no starter file.
2. Take a page you built and give it a second colour scheme without touching the
   HTML at all.
3. Find a website you like, inspect one component, and rebuild that component's
   principle with your own words and colours.
4. Break your own page on purpose in three ways, hand it to a classmate, and see how
   fast they find the faults.
5. Make one page work well at 320px wide. Just one page, just that one goal.

### Suggested next lesson

**Session two: layout in depth.** More Flexbox (`flex-grow`, `align-self`), then a
first look at CSS Grid for two-dimensional layouts, then a multi-page site with
links between pages and a shared stylesheet.

### Moving into JavaScript without jumping too far

Do not start with syntax, loops or data types. Start where this workshop ended:

1. **One button, one line.** A button that toggles a class on an element. Everything
   visual still comes from the CSS they already know.
2. **Reading the page.** `document.querySelector` using the exact same selectors
   they wrote in Section 8 — that continuity is the whole point.
3. **Responding to a click.** One event listener, one function.
4. **Changing content.** Updating text, then updating a class.
5. *Only then* variables, conditions and loops — introduced because a real feature
   needs them, not as a topic in their own right.

The bridge is the selector. Students who wrote `.card` in CSS already understand
what `document.querySelector('.card')` is pointing at, and that makes JavaScript
feel like an extension rather than a new subject.

---

## 7. Three delivery routes

### Route 1 — 90-minute introduction

Hook · basic HTML · links and lists · basic CSS · one mini project · DevTools preview.

Use these slides:

`s-title` → `s-hook-card` → `s-hook-reveal` → `s-hook-remix` → `s-hook-message` →
`s-browser-job` → `s-route-b` → `s-element-anatomy` → `s-skeleton-1` →
`s-skeleton-2` → `s-checkpoint-1` → `s-attributes` → `s-content-tags` →
`s-micro-challenge` → `s-css-link` → `s-css-anatomy` → `s-css-predict` →
`s-checkpoint-4` → `s-devtools-why` → `s-devtools-edit` → `s-final-message`

Everyone uses Route B (the in-deck editor) — do not spend 20 minutes on file setup
in a 90-minute session. Skip semantic HTML, the box model, Flexbox and responsive
design entirely rather than rushing them.

### Route 2 — three-hour core workshop

The full deck as written, with the final build cut to 15–20 minutes. Skip the
reconstruction challenge, CSS Target Match and the AI segment if you are behind at
the break. Take the ten-minute break exactly on time.

### Route 3 — two sessions

**Session one (2 hours) — structure**
Opening hook → workspace → first HTML document → content → semantic HTML →
**Assignment 1** (four slides, ends at slide 32).
End with: “Next time we make it look like something. Bring your folder.”

This is exactly what `session-1.html` contains, so the link you hand out and the
deck you present are the same thing.

Homework: **Assignment 1 — Structure Something Real.** A two-page HTML-only site
on a subject of their choosing. Full brief on the last four slides and in
`assignment-1.md` for printing or uploading to the LMS. Marked out of 20 on
structure, semantics, nesting, working links and content — never on looks, since
there is no CSS in it.

If you have time to spare in session one, DevTools (`s-devtools-why` through
`s-devtools-rebuild`) fits neatly at the end and needs no CSS. Set the build's
`through:` to `s-devtools-rebuild` if you do.

**Session two (2 hours) — appearance and layout**
Quick recap of checkpoint 3 → connect CSS → selectors and classes → box model →
Flexbox → responsive design → accessibility → final build → showcase → exit
challenge → where this leads.

This split is the strongest of the three routes for a school timetable. The
natural break between “what things are” and “how they look” is a real conceptual
boundary, and sleeping on it helps.

---

## 8. Student support materials in the deck

| Material | Slide |
| --- | --- |
| Glossary in plain words | `s-glossary` |
| HTML tag reference | `s-ref-html` |
| CSS property reference | `s-ref-css` |
| Keyboard shortcut reference | `s-ref-shortcuts` |
| DevTools scavenger-hunt sheet | `s-ref-shortcuts` (right column) |
| Project checklist | `s-ref-checklists` |
| Debugging checklist | `s-ref-checklists` |
| Assessment rubric | `s-ref-checklists` |
| “Finished early” extension list | `s-final-build` |
| Common bugs table | `s-debug-common` |
| Catch-up checkpoints | eight slides, listed above |
| Hint cards | collapsed panels on every challenge slide |
| Starter files | `student-starter/` |
| Finished reference files | `student-finished-example/` |

Jump straight to any of them with <kbd>O</kbd>, or by typing the slide id into the
address bar after the `#`.

---

## 9. The three hidden faults in the starter files

For **Level 3: Debugger**. Do not tell students what they are; these are for you.

| # | File | Fault | Symptom students see |
| --- | --- | --- | --- |
| 1 | `student-starter/index.html` | `<link rel="stylesheet" href="style.css">` — the file is `styles.css` | The page has no styling at all |
| 2 | `student-starter/index.html` | `<a href="#shedule">` — the section id is `schedule` | The Schedule nav link does nothing when clicked |
| 3 | `student-starter/styles.css` | `card { ... }` — missing the dot before the class name | The cards stay unstyled while everything else works |

Fault 1 is intentionally the loudest: students meet it first and it teaches the
"stylesheet not linked" lesson immediately. If a struggling student is blocked by
it, point them at the debugging checklist rather than telling them the answer —
"is the CSS reaching the page at all?" is enough of a nudge.

Award 2 points per fault found, plus 2 more for describing the symptom before the
fix.

---

## 10. Customisation

Everything below is a small, safe edit. None of it requires touching `slides.js`
logic.

### Change the example project name

The default project is **Nova Student Tech Day**. To rebrand the deck, search
`index.html` for `Nova` and replace. The same name appears in
`student-finished-example/index.html`. Nothing depends on it.

### Change the accent colours

Top of `styles.css`, in `:root` (dark mode) and `[data-theme="light"]`:

```css
--html: #ffab6a;        /* HTML concepts — warm */
--css: #64d3ff;         /* CSS concepts — cool */
--challenge: #cdf75c;   /* challenges — bright */
--devtools: #e58cff;    /* DevTools — magenta */
--debug: #ffd45c;       /* debugging — warning */
```

Change both blocks so bright-room mode keeps its contrast. The `-soft` and `-ink`
variants beside each one are the tinted background and the light text version.

### Change the default classroom mode

`slides.js`, in `start()`:

```js
applyTheme(store.get("theme", "dark"));   // change "dark" to "light"
applyNotes(store.get("notes", false));    // change false to true to start with notes on
```

### Change the timer presets

`index.html`, in the timer panel. Each button is one line:

```html
<button type="button" class="icon-btn" data-timer-preset="180" data-timer-label="3 min mini challenge">3m</button>
```

`data-timer-preset` is seconds. The per-slide **Start** buttons use
`data-timer-start="180"` in exactly the same way.

### Change the default team names or count

`slides.js`:

```js
const DEFAULT_TEAMS = ["Team Tag", "Team Selector", "Team Flexbox", "Team Inspect", "Team Semantic", "Team Remix"];
let teams = store.get("scores", null) || DEFAULT_TEAMS.slice(0, 4).map(...);   // 4 = default team count
```

The scoreboard's dropdown supports 2–6 either way.

### Turn the end-of-timer sound off permanently

Press **Sound off** in the timer panel once — the choice is stored. Or set the
default in `slides.js`: `let soundEnabled = store.get("sound", false);`

### Turn off the celebration effect

It already respects `prefers-reduced-motion` at the operating-system level. To
disable it outright, make `celebrate()` in `slides.js` return immediately:

```js
function celebrate(count) {
  return;   // celebrations disabled
  ...
}
```

### After any customisation

Re-run `node build-standalone.js` so `workshop.html` picks up the change. The
folder version is the source of truth; the single file is generated from it and
is overwritten every time you build.

### Remove a slide

Delete the whole `<section class="slide">…</section>` block. The counter, progress
bar, section markers and navigator all rebuild themselves from whatever is left. If
another slide links to the one you removed, update that link — the internal links
live in `s-final-build` and `s-final-message`.

### Add a slide

Copy any existing slide block, change the `id`, `data-section` and `data-title`,
and drop it where you want it. `data-accent` accepts `html`, `css`, `challenge`,
`devtools` or `debug`.

### Change the reading level

The deck uses British spelling and short sentences throughout. The instructor notes
are written as things you can say out loud verbatim — edit them freely to match how
you actually speak.

---

## 11. Technical notes

- **No dependencies.** No frameworks, no fonts, no CDN, no network requests.
  Fonts come from the operating system's own stack.
- **Sandboxed previews.** Every playground preview is an `iframe` with a `sandbox`
  attribute and no `allow-scripts`, populated via `srcdoc`. Student code cannot run
  scripts, reach the parent page, or leave the machine.
- **Local storage.** Only five harmless classroom preferences are stored: theme,
  notes visibility, sound on/off, team scores and the last slide viewed. Every read
  and write is wrapped so that a browser blocking storage degrades silently instead
  of breaking.
- **Accessibility.** All controls are real `button`, `a`, `input` and `select`
  elements — there are no clickable `div`s anywhere in the deck. Focus outlines are
  visible, the slide counter is a live region, and every image and icon has either
  alt text or `alt=""` where decorative.
- **Reduced motion.** Slide transitions, hover lifts and the confetti effect are all
  suppressed when the operating system requests reduced motion.
- **Narrow screens.** Below 900px the deck stops pretending to be a projector and
  becomes a scrolling document, so students can read it on a phone or a half-width
  window.
- **Printing.** `Ctrl+P` produces one slide per page with the instructor notes
  included and all deck chrome removed.

---

## 12. Troubleshooting

| Problem | Cause | Fix |
| --- | --- | --- |
| Deck opens unstyled | `styles.css` was not copied alongside `index.html` | Copy the whole folder, not just the HTML file |
| Playground previews are blank | The browser is blocking `srcdoc` iframes | Use Chrome or Edge; check any content-blocking extension |
| Scores do not survive a refresh | Local storage is blocked or the browser is in private mode | Normal browsing window; scores still work for the session |
| Illustrations are missing | The `assets/` folder was not copied | Copy the whole folder |
| Timer chime does not sound | Sound is toggled off, or the browser needs a user gesture first | Press **Sound on**, then click once anywhere in the page |
| Code is too small on the projector | Room lighting, not font size | Press <kbd>B</kbd> for bright-room mode and <kbd>F</kbd> for full screen |
| Full screen does nothing | Some browsers block it from `file://` in rare configurations | Use the browser's own full-screen key (<kbd>F11</kbd>) |
| A student's page is completely unstyled | Almost always the stylesheet filename | Have them read the filename and the `href` out loud, letter by letter |

---

## 13. Verification checklist

Run through this once on the machine you will present from.

**Deck**
- [ ] `index.html` opens by double-clicking, with no server
- [ ] Every one of the 83 slides is reachable from the navigator (<kbd>O</kbd>)
- [ ] Previous and next buttons work
- [ ] <kbd>→</kbd> <kbd>←</kbd> <kbd>Space</kbd> <kbd>Home</kbd> <kbd>End</kbd> all work
- [ ] Full screen works
- [ ] The slide counter updates correctly
- [ ] The progress bar and section markers update correctly
- [ ] Instructor notes toggle on and off with <kbd>N</kbd>
- [ ] Bright-room mode is readable on the projector

**Interactivity**
- [ ] Timers start, pause and reset; the display turns amber in the last ten seconds
- [ ] Per-slide **Start** buttons open the timer with the right duration
- [ ] Team names can be edited and points added and subtracted
- [ ] Team scores survive a page refresh
- [ ] Playground previews render on load and after **Run**
- [ ] **Reset** restores the original starter code
- [ ] **Copy** puts both files on the clipboard
- [ ] Hints open on click; solutions stay closed until clicked
- [ ] The box-model sliders and readout update live
- [ ] The Flexbox dropdowns move the boxes and update the generated CSS
- [ ] The viewport tester resizes the miniature page and its media query fires

**Session build (`session-1.html`)**
- [ ] Ends on “Assignment 1 — check, mark, submit”, 32 slides
- [ ] Contains no CSS, DevTools or Flexbox material
- [ ] Counter reads “x / 32” and the navigator lists 32 slides
- [ ] No link points at a slide that was cut

**Single file (`workshop.html`)**
- [ ] Opens from a folder containing nothing else
- [ ] All illustrations appear (they are data URIs, not files)
- [ ] “Open the finished example” opens the reference build in a new tab
- [ ] “Download index.html” and “Download styles.css” save the starter files
- [ ] The downloaded starter still contains the three deliberate faults

**Content**
- [ ] Both student project links open (`student-starter/`, `student-finished-example/`)
- [ ] Internal links on `s-final-build` jump to the right reference slides
- [ ] Every image has alt text, or `alt=""` where decorative
- [ ] The deck is usable at narrow widths (drag the window to phone width)
- [ ] No code example is cut off horizontally
- [ ] No slide contains unreadably small text at the back of the room
- [ ] The finished example uses only techniques taught in the deck
- [ ] The starter project contains the scaffold and three faults, not the answers
- [ ] The browser console shows no errors

---

## 14. A note on how this is meant to feel

The deck is built around one loop, repeated about twenty times:

**See → Predict → Type → Run → Remix → Explain**

If you find yourself talking for more than five minutes without the students
touching a keyboard, something has gone wrong with the pacing — jump to the next
challenge slide and come back to the explanation afterwards. The explanation always
lands better after the attempt.

The competition exists to make people talk out loud, not to make them anxious.
Points for explaining are worth more than points for finishing. Points for helping
somebody else are worth the most of all. If a team is behind on the scoreboard,
give them a question to explain rather than a task to race.

And when something breaks in front of the whole room — and it will — say so,
open DevTools, and debug it live. That single unplanned moment teaches more than
any slide in here.
