# JavaScript From Zero — Instructor Guide

**Make The Page Do Something** · five hours · 61 slides

For students who have already done the HTML and CSS sessions and have a page of
their own. They arrive able to build something that looks right and does nothing.
They leave having made it respond.

---

## 1. Quick start

**Hand students this:** `js-workshop.html` — one 244 KB file with the whole
course inside it. No folder, no assets, nothing to go missing. Double-click it,
or host it and share the link.

**Present from:** the same file, or the folder version if you want to edit.

Press <kbd>F</kbd> for full screen, <kbd>→</kbd> to advance, <kbd>N</kbd> for
teacher notes. Nothing to install.

After editing the folder version, regenerate the single file:

```bash
node build-standalone.js
```

Node is needed only by you, never by students.

---

## 2. Files

```text
javascript/
├── js-workshop.html      ★ the single file — hand this out
│
├── index.html            source deck (61 slides)
├── styles.css            the "Signal" design system
├── slides.js             deck behaviour + the sandboxed code runner
├── build-standalone.js   rebuilds js-workshop.html
└── README.md             this guide
```

---

## 3. The five hours

| Time | Part | Slides | What happens |
| --- | --- | --- | --- |
| 0:00–0:15 | 00 hook | 5 | Their own dead button, then three lines that wake it up |
| 0:15–0:35 | 01 where it lives | 4 | Console, `<script>` tag, catch-up 00 |
| 0:35–1:05 | 02 values | 7 | Types, `let`/`const`, template literals, type detective, bug hunt |
| 1:05–1:40 | 03 functions | 7 | Declare, call, parameters, **return vs log**, predict, build three |
| 1:40–2:05 | 04 decisions | 4 | `if`/`else`, `===`, truthiness, console race |
| 2:05–2:20 | break | 1 | Ten-minute countdown |
| 2:20–2:55 | 05 lists | 5 | Arrays, index, `for...of`, `forEach`, array workout |
| 2:55–3:20 | 06 objects | 4 | Objects, dot access, arrays of objects |
| 3:20–3:50 | 07 the page | 6 | `querySelector`, `textContent`, `classList`, null guard |
| 3:50–4:25 | 08 events | 6 | `addEventListener`, callbacks, inputs, the build-off |
| 4:25–4:50 | 09 build | 3 | Their own component, on their own page |
| 4:50–5:00 | 10 close | 5 | Debugging routine, errors, where next |
| — | reference | 4 | Glossary, syntax, errors, keys — printable |

Seven catch-up slides (`s-mark-0` … `s-mark-6`) let anyone who falls behind copy
a known-good state and rejoin in ninety seconds. Never skip them.

---

## 4. The code runner

Every playground has its own `<iframe sandbox="allow-scripts">` — **with
`allow-same-origin` deliberately left off**. That combination gives the frame an
opaque origin: student code executes normally, but it cannot read this document,
its storage or its cookies. Output comes back by `postMessage` only.

What that buys you in a classroom:

- `console.log` output is captured and printed under the editor, formatted —
  arrays print as `[1, 2, 3]`, objects as `{ a: 1 }`, elements as `<button>`.
- Errors are caught and shown in red **with the line number corrected** to match
  what the student typed, not the wrapper.
- A DOM playground gets a visible white panel, so `querySelector` and
  `addEventListener` work against a real page.

### If a student freezes their preview

Writing `while (true)` is a rite of passage. The deck checks for the obvious
shapes before running and refuses once, printing:

> that loop never stops. press Run again if you meant it, then Stop.

Pressing Run a second time honours the request — because watching an infinite
loop actually happen is a lesson. **Stop** kills the frame. If the whole tab
locks up, reloading the page loses nothing but that one editor's edits.

---

## 5. Competitions

Nine `.ask` prediction rows and six timed team challenges, all on the scoreboard.

| Slide | Competition | Scoring bias |
| --- | --- | --- |
| `s-hook-remix` | One-minute remix | anything that still runs |
| `s-typeof` | Type detective | **reason worth double the answer** |
| `s-bugs-1` | Bug hunt (four faults) | naming all four out loud |
| `s-fn-predict` | Predict the output | spotting the unreachable line |
| `s-fn-build` | Write three functions | clean names, helping others |
| `s-console-race` | Console race | explaining `===` vs `==` |
| `s-array-workout` | Array workout | one loop, not three |
| `s-event-race` | The build-off | one function used by both buttons |

Points reward reasons, mentoring and readable code — never speed alone. Open the
scoreboard with <kbd>S</kbd>; names and scores survive a refresh.

---

## 6. What they will get wrong

| Misconception | Where it bites | Counter |
| --- | --- | --- |
| `=` means equals | `score = score + 10` | Say "gets", out loud, every time |
| `"5"` and `5` are the same | `"24" + 1` → `"241"` | Bug hunt slide, then point back all day |
| Writing a function runs it | `s-fn-call` | "A recipe in a drawer" — delete the call, run it |
| `console.log` returns a value | `s-fn-return` | **"log is a window, return is a door"** |
| Code after `return` runs | `s-fn-predict` | It never prints. Let them predict wrong first |
| `==` is fine | `s-console-race` | Teach `===` only; mention `==` once, as a trap |
| Loop variable is the item | `for...of` vs index | Teach `for...of` first for exactly this reason |
| `querySelector("card")` | `s-query` | The dot and hash are part of the selector |
| Passing `fn()` to a listener | `s-event-bugs` | It runs immediately and passes the result. Drop the brackets |
| `null` element errors | `s-query-null` | Script above the element, or a typo'd selector |

The **return vs log** confusion is the single biggest one, and it takes three
encounters to shift. Slides 21, 22 and the function challenge are all aimed at
it. Budget the time and do not cut them.

### Pace signals

**Too fast:** hands stop going up; people stop typing and start watching; two or
more ask you to go back. Go to the nearest catch-up slide and cut the next
optional challenge.

**Too slow:** challenges finish with a third of the time left. Skip to the
"extra" line on the challenge card, or start the build earlier and make it longer.

**Best things to cut** if you are behind, in order: the array workout extension,
`s-object-model`, the AI-free-form part of the build, the reference tour.

**Never cut:** the hook remix, catch-up 00, return vs log, or the build.

---

## 7. After class

**Homework:** finish the interactive component on their own page. One button,
one thing that changes, and they must be able to explain every line.

**Rubric — 20 points**

| Area | Points |
| --- | --- |
| Values and variables used correctly (`const` by default, sensible names) | 4 |
| A function that takes something in and returns something out | 4 |
| A list or an object holding real data | 4 |
| The page actually changes in response to a click or a keystroke | 4 |
| Can explain any line, and debugged at least one error themselves | 4 |

Not marked: how it looks. They already did that unit.

**Next:** arrays of objects → rendering a list to the page from data. That one
step turns everything today into something that feels like a real application,
and it needs nothing new.

---

## 8. Why the deck looks like this

The design brief was to avoid the current AI-generated house style, so these are
deliberately absent: Inter, indigo-to-purple gradients, rounded cards, soft
shadows, thin-line icons, three-card rows, the coloured left-border strip, status
badges, cream light mode and blue-slate dark mode.

What it uses instead:

- **Print language, not app language.** Hairline rules, flat colour fields and
  crop marks at the corners. Zero border-radius anywhere in the stylesheet.
- **Three type voices with fixed jobs.** A heavy grotesque for display, Georgia
  for prose, monospace for anything structural — labels, numbers, captions,
  the toolbar. If it is a machine speaking, it is monospace.
- **The chrome is written in JavaScript comment syntax.** Running heads read
  `// 03 functions · new syntax`. On-theme, and it doubles as a reminder that
  comments are for humans.
- **An asymmetric 7/5 grid**, not halves and not thirds.
- **A riso-ish palette**: stone ground, warm near-black ink, vermilion,
  chartreuse, ochre. Colour is used as flat blocks and highlighter marks, never
  as a gradient.
- **Slide kind is signalled by the running head and the dot field**, not a badge.

Sources for the conventions avoided:
[925 Studios](https://www.925studios.co/blog/ai-slop-design-tells) ·
[SmoothUI](https://smoothui.dev/blog/ai-design-slop) ·
[Impeccable](https://impeccable.style/slop/)

---

## 9. Customisation

**Palette** — top of `styles.css`, in `:root` and `[data-theme="light"]`. Change
`--red`, `--lime` and `--ochre` in both blocks so the light mode keeps its
contrast.

**Default theme** — in `slides.js`: `setTheme(store.get("theme", "dark"))`.

**Timer presets** — in `index.html`, each is one line:
`data-preset="180" data-label="…"`. Per-slide start buttons use `data-start`.

**Team names** — in `slides.js`: `var NAMES = ["callback", "closure", …]`.

**Hand out only part of the course** — `build-standalone.js` has a `BUILDS` list
and a commented example. Set `through:` to a slide id and it cuts there,
refusing to write a file that links to a slide it just removed. Useful cut
points: `s-mark-1` (values), `s-mark-2` (functions), `s-mark-3` (lists),
`s-mark-5` (the page), `s-mark-6` (events).

**Remove a slide** — delete the whole `<section class="slide">…</section>`. The
counter, ruler, section ticks and navigator all rebuild from what is left.

---

## 10. Verification checklist

Run this on the machine you will present from.

**Deck**
- [ ] Opens by double-clicking, no server
- [ ] All 61 slides reachable from the navigator (<kbd>O</kbd>)
- [ ] Arrows / Space / Home / End / full screen work
- [ ] Counter, ruler and the 15 section ticks update
- [ ] Teacher notes toggle with <kbd>N</kbd>
- [ ] Light mode readable on the projector (<kbd>L</kbd>)

**The runner** — the part that matters
- [ ] A playground prints `console.log` output under the editor
- [ ] Arrays and objects print readably, not `[object Object]`
- [ ] A deliberate error shows in red with a line number
- [ ] A DOM playground renders its white panel and responds to clicks
- [ ] `while (true)` is refused once before running
- [ ] **Stop** clears a running frame
- [ ] **Reset** restores the original code

**Classroom kit**
- [ ] Timer starts, pauses, resets; goes amber in the last ten seconds
- [ ] Team scores editable and survive a refresh
- [ ] Prediction rows mark right and wrong
- [ ] All 19 reveals start closed
- [ ] No console errors
- [ ] No sideways scrolling at phone width
