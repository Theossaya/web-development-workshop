# Assignment 1 — Structure Something Real

**Two pages. HTML only. No CSS.**

Due: next session. Bring the folder with you — we build straight on top of it.

---

## What to build

A small two-page website about something you actually care about.

A club you are in · a game you play · a band · a sport · a place you know well ·
a person you admire · a thing you collect · a cause you care about.

Pick something you have opinions about. If you would not read it, do not write it.

```text
my-project/
├── index.html
└── about.html
```

Two files, one folder. No `styles.css` this time — you would only be tempted.

### The one hard rule: no CSS

No `style` attributes, no `<style>` block, no stylesheet.

Your page will look plain — black text, blue links, Times New Roman. **That is
correct.** Styling comes next session, and it is far easier on top of good
structure. Everything you are marked on this week is invisible in a screenshot
and obvious in the code.

### Roughly how long

| Part | Time |
| --- | --- |
| Page one | 40 minutes |
| Page two | 25 minutes |
| Checking and fixing | 15 minutes |

If it is taking three hours you are writing too much text. The structure is the
assignment, not the essay.

---

## What must be in it

### Both pages

- [ ] `<!doctype html>` on line one
- [ ] `<html lang="en">`
- [ ] `charset` and `viewport` meta tags in the head
- [ ] A `<title>` that names the page — not "Document"
- [ ] A `<header>` containing a `<nav>`
- [ ] One `<main>`
- [ ] Exactly one `<h1>`
- [ ] A `<footer>` with your name
- [ ] Tidy indentation

### Page one — `index.html`

- [ ] At least **three** `<section>` elements
- [ ] Each section has an `id` and an `<h2>`
- [ ] A nav link that jumps to each section
- [ ] At least **two** `<article>` elements inside one section
- [ ] A list of at least three items
- [ ] One `<img>` with real `alt` text
- [ ] One `<strong>` where the emphasis is genuine
- [ ] A link to page two

### Page two — `about.html`

- [ ] At least **two** `<section>` elements
- [ ] A nav link back to page one
- [ ] At least one element from "A little more" below
- [ ] Something that could not just live on page one — give it a reason to exist

Page two ideas: a timeline, a set of rules, a list of people, a how-to, or
answers to the questions people always ask.

---

## A little more — five things you have not used yet

Use **at least one**, and be ready to say why that element and not a different one.

### `<ol>` — an ordered list

Use it when the order carries meaning: steps, rankings, a timetable. The numbers
come free.

```html
<ol>
  <li>Toss for ends</li>
  <li>Two halves of forty minutes</li>
  <li>Handshakes, then chips</li>
</ol>
```

### `<figure>` and `<figcaption>` — a picture with a caption

Ties the caption to the image so a browser knows they belong together. The `alt`
describes the picture; the caption comments on it. They are not the same job.

```html
<figure>
  <img src="team.jpg" alt="Our team lined up before kickoff">
  <figcaption>The squad, twenty minutes before the whistle.</figcaption>
</figure>
```

### `<blockquote>` — a quotation from somewhere else

Put a `<p>` inside it. Say who said it.

```html
<blockquote>
  <p>We lost every game and learned every rule.</p>
</blockquote>
```

### A nested list — a list inside a list *item*

Look carefully at where the inner `<ul>` opens. It goes **inside** the `<li>`,
before that item's closing tag — not between the items.

```html
<ul>
  <li>Equipment
    <ul>
      <li>Boots</li>
      <li>Shin pads</li>
    </ul>
  </li>
  <li>Snacks</li>
</ul>
```

### A link to another file

No `#`. Same folder, exact spelling, exact capitals.

```html
<a href="about.html">Read about the club</a>
```

---

## Before you hand it in — check these ten

- [ ] Both pages open in a browser
- [ ] Every nav link goes somewhere real
- [ ] Page one links to page two, and page two links back
- [ ] Every jump link lands on a section
- [ ] The image loads — or you know exactly why it does not
- [ ] The `alt` text describes the picture
- [ ] No link says "click here"
- [ ] One `h1` per page, and no skipped heading levels
- [ ] Every tag you opened, you closed
- [ ] Nothing visible sits outside `<body>`

### The five most likely faults

1. The link to page two is spelled differently from the file. `About.html` is
   not `about.html`.
2. A jump link with no matching `id` to land on.
3. An image path pointing somewhere that does not exist.
4. A missing closing tag, so half the page goes strange.
5. `alt=""` left on a photograph that actually matters.

Fault 1 is the big one. Your own computer forgives capital letters; almost
nothing else does. Close your editor, open both files fresh from the folder, and
click every single link.

---

## How it is marked — 20 points

| Area | Points | What earns them |
| --- | --- | --- |
| Valid document structure | 4 | Doctype, `lang`, charset, viewport and a real title, on **both** pages |
| Semantic regions | 4 | `header`, `nav`, `main`, `section`, `footer` used honestly; `article` where it genuinely fits |
| Headings and nesting | 4 | One `h1` per page, levels in order, correct nesting, readable indentation |
| Links and images | 4 | Nav works, both pages link to each other, jump links land, image loads with real alt text |
| Content and personalisation | 4 | Your own subject and your own words, plus at least one stretch element |

**No marks for looks.** There is no CSS, so there is nothing to judge. Marks are
for structure, working links, and words worth reading.

**Be ready to explain any line.** If a line is in your file, you should be able
to say what it does and why it is there.

---

## Submitting

Put both files in one folder, zip the folder, upload it.

Name the zip with your own name, not `assignment.zip`.

---

## Stuck?

- The skeleton is on **Checkpoint 1** in the slides — copy it and change the words.
- The full page shape is on **Checkpoint 3**.
- The debugging routine: read what the browser shows, say out loud how it differs
  from what you expected, then change **one** thing and look again.
- Do not delete your file and start again. Find the fault.
