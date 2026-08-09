/* ==========================================================================
   Web Development From Zero — presentation behaviour
   --------------------------------------------------------------------------
   No dependencies, no build step. Everything here is plain browser JS.

   Sections:
     1.  Small helpers (storage, DOM, sound)
     2.  Syntax highlighting for the code panels
     3.  Deck navigation, progress, overview
     4.  Presenter notes, theme, fullscreen
     5.  Timers
     6.  Team scoreboard
     7.  Live playgrounds (sandboxed iframe previews)
     8.  Box model lab, Flexbox lab, viewport tester
     9.  Quizzes and sorting activities
     10. Celebration + exercise reset
     11. Keyboard shortcuts and start-up
   ========================================================================== */

(function () {
  "use strict";

  /* ---------- 1. Helpers ---------- */

  const $ = (selector, scope) => (scope || document).querySelector(selector);
  const $$ = (selector, scope) =>
    Array.from((scope || document).querySelectorAll(selector));

  /** localStorage that never throws — private mode and file:// may block it. */
  const store = {
    get(key, fallback) {
      try {
        const raw = window.localStorage.getItem("wdz." + key);
        return raw === null ? fallback : JSON.parse(raw);
      } catch (error) {
        return fallback;
      }
    },
    set(key, value) {
      try {
        window.localStorage.setItem("wdz." + key, JSON.stringify(value));
      } catch (error) {
        /* Preferences are a convenience, never a requirement. */
      }
    },
  };

  const prefersReducedMotion = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let soundEnabled = store.get("sound", true);

  /** Short two-tone chime used when a timer finishes. */
  function playChime() {
    if (!soundEnabled) return;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    try {
      const ctx = new AudioCtx();
      [660, 880].forEach((frequency, index) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.value = frequency;
        gain.gain.setValueAtTime(0.0001, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.22, ctx.currentTime + 0.02 + index * 0.18);
        gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.35 + index * 0.18);
        osc.connect(gain).connect(ctx.destination);
        osc.start(ctx.currentTime + index * 0.18);
        osc.stop(ctx.currentTime + 0.45 + index * 0.18);
      });
      setTimeout(() => ctx.close(), 1200);
    } catch (error) {
      /* Sound is optional. */
    }
  }

  /* ---------- 2. Syntax highlighting ---------- */

  const ENTITIES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
  const escapeHtml = (text) => text.replace(/[&<>"]/g, (ch) => ENTITIES[ch]);

  function colourTag(rawTag) {
    return escapeHtml(rawTag)
      .replace(/^(&lt;[!/]?)([\w-]+)/, '<span class="t-punct">$1</span><span class="t-tag">$2</span>')
      .replace(
        /([\w-]+)(=)(&quot;[^&]*?&quot;)/g,
        '<span class="t-attr">$1</span><span class="t-punct">$2</span><span class="t-str">$3</span>'
      )
      .replace(/(&gt;)$/, '<span class="t-punct">$1</span>');
  }

  function highlightMarkup(source) {
    const tagPattern = /<!--[\s\S]*?-->|<[!/]?[a-zA-Z][^>]*>/g;
    let out = "";
    let cursor = 0;
    let match;
    while ((match = tagPattern.exec(source)) !== null) {
      out += escapeHtml(source.slice(cursor, match.index));
      out += match[0].startsWith("<!--")
        ? '<span class="t-comment">' + escapeHtml(match[0]) + "</span>"
        : colourTag(match[0]);
      cursor = tagPattern.lastIndex;
    }
    return out + escapeHtml(source.slice(cursor));
  }

  function colourValues(value) {
    return value.replace(
      /(#[0-9a-fA-F]{3,8}\b|\b\d+(?:\.\d+)?(?:px|rem|em|%|s|ms|ch|vw|vh|deg)?\b)/g,
      '<span class="t-num">$1</span>'
    );
  }

  function highlightStyles(source) {
    const escaped = escapeHtml(source);
    // One pass, ordered alternatives: comment | at-rule | declaration | selector.
    const pattern =
      /(\/\*[\s\S]*?\*\/)|(@[\w-]+)|(^[ \t]+)([-\w]+)(\s*:\s*)([^;\n]*)(;?)|(^[ \t]*[^\n{}]+)(?=\{)/gm;
    return escaped.replace(
      pattern,
      (whole, comment, atRule, indent, prop, colon, value, semi, selector) => {
        if (comment) return '<span class="t-comment">' + comment + "</span>";
        if (atRule) return '<span class="t-at">' + atRule + "</span>";
        if (prop) {
          return (
            indent +
            '<span class="t-prop">' + prop + "</span>" +
            colon +
            '<span class="t-val">' + colourValues(value) + "</span>" +
            semi
          );
        }
        if (selector) return '<span class="t-sel">' + selector + "</span>";
        return whole;
      }
    );
  }

  const highlightFor = (lang, source) =>
    lang === "css" ? highlightStyles(source) : highlightMarkup(source);

  /** Diff blocks keep their "+" / "-" markers and colour each line separately. */
  function highlightDiff(lang, source) {
    return source
      .split("\n")
      .map((line) => {
        const marker = line.charAt(0);
        if (marker === "+" || marker === "-") {
          const cls = marker === "+" ? "dline add" : "dline del";
          return '<span class="' + cls + '">' + highlightFor(lang, line.slice(1)) + "</span>";
        }
        return '<span class="dline">' + highlightFor(lang, line) + "</span>";
      })
      .join("\n");
  }

  function paintCodeBlocks() {
    $$("pre[data-lang]").forEach((block) => {
      const lang = block.getAttribute("data-lang");
      const source = block.textContent.replace(/^\n/, "").replace(/\s+$/, "");
      block.innerHTML = block.hasAttribute("data-diff")
        ? highlightDiff(lang, source)
        : highlightFor(lang, source);
    });
  }

  /* ---------- 3. Deck navigation ---------- */

  const deck = $(".deck");
  const slides = $$(".slide");
  const counter = $("#counter");
  const progressFill = $("#progressFill");
  const toolbarSection = $("#toolbarSection");
  const toolbarTitle = $("#toolbarTitle");
  let currentIndex = 0;

  function slideIndexFromHash() {
    const id = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (!id) return -1;
    return slides.findIndex((slide) => slide.id === id);
  }

  function goTo(index, options) {
    const settings = options || {};
    const target = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, i) => {
      const active = i === target;
      slide.classList.toggle("is-active", active);
      slide.setAttribute("aria-hidden", active ? "false" : "true");
    });
    currentIndex = target;

    const slide = slides[target];
    counter.textContent = target + 1 + " / " + slides.length;
    progressFill.style.width = ((target + 1) / slides.length) * 100 + "%";
    toolbarSection.textContent = slide.dataset.section || "";
    toolbarTitle.textContent = slide.dataset.title || "";

    if (!settings.silent) {
      const newHash = "#" + slide.id;
      if (window.location.hash !== newHash) {
        history.replaceState(null, "", newHash);
      }
    }
    store.set("slide", slide.id);
    markOverviewCurrent();
    const inner = slide.querySelector(".slide-inner");
    if (inner) inner.scrollTop = 0;
  }

  const next = () => goTo(currentIndex + 1);
  const previous = () => goTo(currentIndex - 1);

  /* Section markers on the progress bar */
  function buildSectionMarks() {
    const marks = $("#sectionMarks");
    let lastSection = null;
    slides.forEach((slide, index) => {
      if (slide.dataset.section === lastSection) return;
      lastSection = slide.dataset.section;
      const mark = document.createElement("span");
      mark.className = "section-mark";
      mark.style.left = (index / slides.length) * 100 + "%";
      mark.title = lastSection;
      marks.appendChild(mark);
    });
  }

  /* Slide navigator */
  function buildOverview() {
    const grid = $("#overviewGrid");
    const fragment = document.createDocumentFragment();
    slides.forEach((slide, index) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "overview-item";
      item.dataset.action = "goto";
      item.dataset.index = String(index);
      item.innerHTML =
        '<b>' + String(index + 1).padStart(2, "0") + "</b>" +
        '<span class="ov-sec"></span><span class="ov-title"></span>';
      item.querySelector(".ov-sec").textContent = slide.dataset.section || "";
      item.querySelector(".ov-title").textContent = slide.dataset.title || "";
      fragment.appendChild(item);
    });
    grid.appendChild(fragment);
  }

  function markOverviewCurrent() {
    $$(".overview-item").forEach((item, index) => {
      item.classList.toggle("is-current", index === currentIndex);
      item.setAttribute("aria-current", index === currentIndex ? "true" : "false");
    });
  }

  function togglePanel(id, force) {
    const panel = document.getElementById(id);
    if (!panel) return;
    const show = typeof force === "boolean" ? force : panel.hidden;
    panel.hidden = !show;
    const trigger = $('[data-panel-toggle="' + id + '"]');
    if (trigger) trigger.setAttribute("aria-pressed", String(show));
    if (show) {
      const focusable = panel.querySelector("button, input, select");
      if (focusable) focusable.focus();
    }
  }

  /* ---------- 4. Notes, theme, fullscreen ---------- */

  function applyNotes(on) {
    document.body.classList.toggle("notes-on", on);
    const button = $('[data-action="toggle-notes"]');
    if (button) button.setAttribute("aria-pressed", String(on));
    store.set("notes", on);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const button = $('[data-action="toggle-theme"]');
    if (button) {
      button.setAttribute("aria-pressed", String(theme === "light"));
      button.textContent = theme === "light" ? "Dark room" : "Bright room";
    }
    store.set("theme", theme);
  }

  function toggleFullscreen() {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(() => {});
    }
  }

  /* ---------- 5. Timers ---------- */

  const timerPanel = $("#timer");
  const timerDisplay = $("#timerDisplay");
  const timerLabel = $("#timerLabel");
  let timerTotal = 180;
  let timerRemaining = 180;
  let timerHandle = null;

  const formatTime = (seconds) =>
    Math.floor(seconds / 60) + ":" + String(seconds % 60).padStart(2, "0");

  function renderTimer() {
    timerDisplay.textContent = formatTime(Math.max(0, timerRemaining));
    timerPanel.classList.toggle("is-final", timerRemaining <= 10 && timerRemaining > 0);
    timerPanel.classList.toggle("is-done", timerRemaining <= 0);
    const toggleButton = $("#timerToggle");
    toggleButton.textContent = timerHandle ? "Pause" : "Start";
    toggleButton.dataset.timer = timerHandle ? "pause" : "start";
  }

  function stopTimer() {
    if (timerHandle) {
      clearInterval(timerHandle);
      timerHandle = null;
    }
  }

  function startTimer() {
    if (timerHandle || timerRemaining <= 0) return;
    timerHandle = setInterval(() => {
      timerRemaining -= 1;
      if (timerRemaining <= 0) {
        timerRemaining = 0;
        stopTimer();
        playChime();
      }
      renderTimer();
    }, 1000);
    renderTimer();
  }

  function setTimer(seconds, label, autoStart) {
    stopTimer();
    timerTotal = seconds;
    timerRemaining = seconds;
    timerLabel.textContent = label || formatTime(seconds) + " round";
    togglePanel("timer", true);
    renderTimer();
    if (autoStart) startTimer();
  }

  /* ---------- 6. Team scoreboard ---------- */

  const DEFAULT_TEAMS = ["Team Tag", "Team Selector", "Team Flexbox", "Team Inspect", "Team Semantic", "Team Remix"];
  let teams = store.get("scores", null) || DEFAULT_TEAMS.slice(0, 4).map((name) => ({ name: name, score: 0 }));

  function saveTeams() {
    store.set("scores", teams);
  }

  function renderTeams() {
    const holder = $("#teamRows");
    holder.innerHTML = "";
    teams.forEach((team, index) => {
      const row = document.createElement("div");
      row.className = "team-row";
      row.innerHTML =
        '<input type="text" value="" aria-label="Team name">' +
        '<button type="button" class="score-btn" data-score="-1" aria-label="Subtract a point">&minus;</button>' +
        '<span class="team-score">0</span>' +
        '<button type="button" class="score-btn" data-score="1" aria-label="Add a point">+</button>';
      row.dataset.team = String(index);
      row.querySelector("input").value = team.name;
      row.querySelector(".team-score").textContent = String(team.score);
      holder.appendChild(row);
    });
    $("#teamCount").value = String(teams.length);
  }

  function changeTeamCount(count) {
    const wanted = Number(count);
    while (teams.length < wanted) {
      teams.push({ name: DEFAULT_TEAMS[teams.length] || "Team " + (teams.length + 1), score: 0 });
    }
    teams = teams.slice(0, wanted);
    saveTeams();
    renderTeams();
  }

  /* ---------- 7. Live playgrounds ---------- */

  const PREVIEW_SHELL =
    '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
    "<style>html{font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#172033;background:#fff}" +
    "body{margin:0;padding:14px}img{max-width:100%;display:block}</style>";

  function renderPlayground(playground) {
    const htmlArea = $("[data-pg-html]", playground);
    const cssArea = $("[data-pg-css]", playground);
    const frame = $("[data-pg-preview]", playground);
    if (!frame) return;
    const css = cssArea ? cssArea.value : "";
    const markup = htmlArea ? htmlArea.value : "";
    // Student code only ever runs inside a sandboxed frame, never in this page.
    frame.srcdoc = PREVIEW_SHELL + "<style>" + css + "</style></head><body>" + markup + "</body></html>";
  }

  function resetPlayground(playground) {
    $$("[data-pg-html], [data-pg-css]", playground).forEach((area) => {
      area.value = area.dataset.initial || "";
    });
    $$("details.reveal", playground).forEach((reveal) => {
      reveal.open = false;
    });
    renderPlayground(playground);
  }

  function copyPlayground(playground, button) {
    const htmlArea = $("[data-pg-html]", playground);
    const cssArea = $("[data-pg-css]", playground);
    const parts = [];
    if (htmlArea) parts.push("<!-- index.html -->\n" + htmlArea.value);
    if (cssArea) parts.push("/* styles.css */\n" + cssArea.value);
    const text = parts.join("\n\n");
    const done = () => {
      const original = button.textContent;
      button.textContent = "Copied";
      setTimeout(() => {
        button.textContent = original;
      }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, () => legacyCopy(text, done));
    } else {
      legacyCopy(text, done);
    }
  }

  function legacyCopy(text, done) {
    const scratch = document.createElement("textarea");
    scratch.value = text;
    scratch.setAttribute("aria-hidden", "true");
    scratch.style.position = "fixed";
    scratch.style.opacity = "0";
    document.body.appendChild(scratch);
    scratch.select();
    try {
      document.execCommand("copy");
      done();
    } catch (error) {
      /* Clipboard blocked — students can still select the text by hand. */
    }
    document.body.removeChild(scratch);
  }

  function setUpPlaygrounds() {
    $$("[data-playground]").forEach((playground) => {
      $$("[data-pg-html], [data-pg-css]", playground).forEach((area) => {
        area.dataset.initial = area.value;
      });
      renderPlayground(playground);
    });
  }

  /* Typing runs the preview shortly after the student stops typing. */
  let liveRunTimer = null;
  document.addEventListener("input", (event) => {
    const area = event.target.closest("[data-pg-html], [data-pg-css]");
    if (!area) return;
    const playground = area.closest("[data-playground]");
    clearTimeout(liveRunTimer);
    liveRunTimer = setTimeout(() => renderPlayground(playground), 450);
  });

  /* Tab inside a code textarea should indent, not jump to the next control. */
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Tab" || event.shiftKey) return;
    const area = event.target.closest("[data-pg-html], [data-pg-css]");
    if (!area) return;
    event.preventDefault();
    const start = area.selectionStart;
    area.value = area.value.slice(0, start) + "  " + area.value.slice(area.selectionEnd);
    area.selectionStart = area.selectionEnd = start + 2;
  });

  /* ---------- 8. Box model lab, Flexbox lab, viewport tester ---------- */

  function updateBoxLab(lab) {
    const target = $("[data-box-target]", lab);
    const outer = $("[data-box-outer]", lab);
    const values = {};
    $$("[data-box]", lab).forEach((input) => {
      values[input.dataset.box] = Number(input.value);
      const output = $('output[for="' + input.id + '"]', lab);
      if (output) output.textContent = input.value + "px";
    });
    const borderBox = $("[data-box-toggle]", lab).checked;
    outer.style.setProperty("--m", values.margin + "px");
    target.style.setProperty("--p", values.padding + "px");
    target.style.setProperty("--b", values.border + "px");
    target.style.setProperty("--w", values.width + "px");
    target.style.setProperty("--bs", borderBox ? "border-box" : "content-box");

    const painted = borderBox
      ? values.width
      : values.width + values.padding * 2 + values.border * 2;
    $("[data-box-readout]", lab).textContent =
      "box-sizing: " + (borderBox ? "border-box" : "content-box") +
      "  →  space used across the page: " + painted + "px" +
      " (+ " + values.margin * 2 + "px margin)";
  }

  function updateFlexLab(lab) {
    const stage = $("[data-flex-stage]", lab);
    const declarations = ["display: flex"];
    $$("[data-flex]", lab).forEach((control) => {
      const property = control.dataset.flex;
      const value = control.value;
      stage.style.setProperty(property, value);
      declarations.push(property + ": " + value);
    });
    const output = $("[data-flex-css]", lab);
    if (output) {
      output.textContent = ".cards {\n  " + declarations.join(";\n  ") + ";\n}";
      output.innerHTML = highlightStyles(output.textContent);
    }
  }

  function setViewportWidth(tester, width) {
    const frame = $("[data-viewport-frame]", tester);
    frame.style.width = width === "full" ? "100%" : width + "px";
    $$("[data-viewport-width]", tester).forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.viewportWidth === width));
    });
    const label = $("[data-viewport-label]", tester);
    if (label) {
      label.textContent =
        width === "full" ? "Full width" : width + "px — " + (Number(width) <= 420 ? "phone" : Number(width) <= 820 ? "tablet" : "laptop");
    }
  }

  /* ---------- 9. Quizzes ---------- */

  function answerQuiz(option) {
    const row = option.closest(".quiz-row");
    const correct = option.dataset.value === row.dataset.answer;
    $$(".opt", row).forEach((other) => {
      other.classList.remove("is-right", "is-wrong");
      other.setAttribute("aria-pressed", "false");
    });
    option.setAttribute("aria-pressed", "true");
    option.classList.add(correct ? "is-right" : "is-wrong");
    row.classList.toggle("is-right", correct);
    row.classList.toggle("is-wrong", !correct);
    const feedback = $(".quiz-feedback", row);
    if (feedback) {
      feedback.textContent = correct
        ? "Correct — " + (row.dataset.because || "")
        : "Not quite. Try again, then say out loud why.";
    }
    if (correct) celebrate(6);
  }

  function resetQuizzes(scope) {
    $$(".quiz-row", scope).forEach((row) => {
      row.classList.remove("is-right", "is-wrong");
      $$(".opt", row).forEach((option) => {
        option.classList.remove("is-right", "is-wrong");
        option.setAttribute("aria-pressed", "false");
      });
      const feedback = $(".quiz-feedback", row);
      if (feedback) feedback.textContent = "";
    });
  }

  /* ---------- 9b. Student files carried inside the single-file build ----------

     The multi-file deck links to student-starter/ and student-finished-example/
     on disk. The standalone build has no folders to link to, so those files
     travel inside the page as JSON and are handed out as downloads or opened
     from a blob URL. Both builds share this code; in the multi-file deck the
     JSON block is simply absent and none of these buttons exist. */

  function embeddedFiles() {
    const node = document.getElementById("student-files");
    if (!node) return null;
    try {
      return JSON.parse(node.textContent);
    } catch (error) {
      return null;
    }
  }

  function downloadEmbedded(filename, key) {
    const files = embeddedFiles();
    if (!files || !files[key]) return;
    const blob = new Blob([files[key]], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 8000);
  }

  function openEmbeddedPage(key) {
    const files = embeddedFiles();
    if (!files || !files[key]) return;
    const blob = new Blob([files[key]], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank", "noopener");
    setTimeout(() => URL.revokeObjectURL(url), 120000);
  }

  /* ---------- 10. Celebration + reset ---------- */

  const CONFETTI_COLOURS = ["#ffab6a", "#64d3ff", "#cdf75c", "#e58cff", "#6df0bb"];

  function celebrate(count) {
    if (prefersReducedMotion()) return;
    const layer = $("#confetti");
    const total = count || 40;
    for (let i = 0; i < total; i += 1) {
      const bit = document.createElement("span");
      bit.className = "confetti-bit";
      bit.style.left = Math.random() * 100 + "vw";
      bit.style.background = CONFETTI_COLOURS[i % CONFETTI_COLOURS.length];
      bit.style.animationDelay = Math.random() * 0.4 + "s";
      bit.style.transform = "rotate(" + Math.random() * 180 + "deg)";
      layer.appendChild(bit);
      setTimeout(() => bit.remove(), 2400);
    }
  }

  /** Put every interactive widget on the current slide back to its start. */
  function resetExercises() {
    const slide = slides[currentIndex];
    $$("[data-playground]", slide).forEach(resetPlayground);
    resetQuizzes(slide);
    $$("details.reveal", slide).forEach((reveal) => {
      reveal.open = false;
    });
    $$("[data-boxlab]", slide).forEach((lab) => {
      $$("[data-box]", lab).forEach((input) => {
        input.value = input.dataset.initial || input.defaultValue;
      });
      $("[data-box-toggle]", lab).checked = false;
      updateBoxLab(lab);
    });
    $$("[data-flexlab]", slide).forEach((lab) => {
      $$("[data-flex]", lab).forEach((control) => {
        control.value = control.dataset.initial || control.options[0].value;
      });
      updateFlexLab(lab);
    });
    $$("[data-viewport-tester]", slide).forEach((tester) => setViewportWidth(tester, "full"));
  }

  /* ---------- 11. Events, shortcuts, start-up ---------- */

  /* One delegated click handler for the whole deck. */
  document.addEventListener("click", (event) => {
    const option = event.target.closest(".opt");
    if (option && option.closest(".quiz-row")) {
      answerQuiz(option);
      return;
    }

    const scoreButton = event.target.closest(".score-btn");
    if (scoreButton) {
      const row = scoreButton.closest(".team-row");
      const index = Number(row.dataset.team);
      const delta = Number(scoreButton.dataset.score);
      teams[index].score += delta;
      // Update just this number so repeated clicks keep keyboard focus.
      row.querySelector(".team-score").textContent = String(teams[index].score);
      saveTeams();
      if (delta > 0) celebrate(10);
      return;
    }

    const timerButton = event.target.closest("[data-timer]");
    if (timerButton) {
      const mode = timerButton.dataset.timer;
      if (mode === "start") startTimer();
      if (mode === "pause") {
        stopTimer();
        renderTimer();
      }
      if (mode === "reset") {
        stopTimer();
        timerRemaining = timerTotal;
        renderTimer();
      }
      return;
    }

    const preset = event.target.closest("[data-timer-preset]");
    if (preset) {
      setTimer(Number(preset.dataset.timerPreset), preset.dataset.timerLabel, false);
      return;
    }

    const starter = event.target.closest("[data-timer-start]");
    if (starter) {
      setTimer(Number(starter.dataset.timerStart), starter.dataset.timerLabel, true);
      return;
    }

    const pgButton = event.target.closest("[data-pg-action]");
    if (pgButton) {
      const playground = pgButton.closest("[data-playground]");
      const action = pgButton.dataset.pgAction;
      if (action === "run") {
        renderPlayground(playground);
        pgButton.textContent = "Run ▸";
      }
      if (action === "reset") resetPlayground(playground);
      if (action === "copy") copyPlayground(playground, pgButton);
      return;
    }

    const viewportButton = event.target.closest("[data-viewport-width]");
    if (viewportButton) {
      setViewportWidth(viewportButton.closest("[data-viewport-tester]"), viewportButton.dataset.viewportWidth);
      return;
    }

    const actionButton = event.target.closest("[data-action]");
    if (!actionButton) return;
    const action = actionButton.dataset.action;

    switch (action) {
      case "next": next(); break;
      case "prev": previous(); break;
      case "first": goTo(0); break;
      case "last": goTo(slides.length - 1); break;
      case "goto":
        goTo(Number(actionButton.dataset.index));
        togglePanel("overview", false);
        break;
      case "toggle-notes": applyNotes(!document.body.classList.contains("notes-on")); break;
      case "toggle-theme":
        applyTheme(document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light");
        break;
      case "fullscreen": toggleFullscreen(); break;
      case "toggle-panel": togglePanel(actionButton.dataset.panelToggle); break;
      case "close-panel": togglePanel(actionButton.closest(".panel-float").id, false); break;
      case "reset-exercises": resetExercises(); break;
      case "reset-scores":
        teams.forEach((team) => {
          team.score = 0;
        });
        saveTeams();
        $$(".team-score").forEach((cell) => {
          cell.textContent = "0";
        });
        break;
      case "toggle-sound":
        soundEnabled = !soundEnabled;
        store.set("sound", soundEnabled);
        actionButton.setAttribute("aria-pressed", String(soundEnabled));
        actionButton.textContent = soundEnabled ? "Sound on" : "Sound off";
        break;
      case "celebrate": celebrate(70); break;
      case "print": window.print(); break;
      case "open-example": openEmbeddedPage("example-standalone"); break;
      case "download-starter-html": downloadEmbedded("index.html", "starter-index"); break;
      case "download-starter-css": downloadEmbedded("styles.css", "starter-styles"); break;
      case "download-example-html": downloadEmbedded("index.html", "example-index"); break;
      case "download-example-css": downloadEmbedded("styles.css", "example-styles"); break;
      default: break;
    }
  });

  document.addEventListener("change", (event) => {
    if (event.target.matches("[data-box], [data-box-toggle]")) {
      updateBoxLab(event.target.closest("[data-boxlab]"));
    }
    if (event.target.matches("[data-flex]")) {
      updateFlexLab(event.target.closest("[data-flexlab]"));
    }
    if (event.target.id === "teamCount") {
      changeTeamCount(event.target.value);
    }
  });

  document.addEventListener("input", (event) => {
    if (event.target.matches("[data-box]")) {
      updateBoxLab(event.target.closest("[data-boxlab]"));
    }
    if (event.target.closest(".team-row") && event.target.matches("input[type='text']")) {
      const index = Number(event.target.closest(".team-row").dataset.team);
      teams[index].name = event.target.value;
      saveTeams();
    }
  });

  const TYPING_TAGS = ["INPUT", "TEXTAREA", "SELECT"];

  document.addEventListener("keydown", (event) => {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    if (TYPING_TAGS.indexOf(event.target.tagName) !== -1 || event.target.isContentEditable) return;

    switch (event.key) {
      case "ArrowRight":
      case "PageDown":
        event.preventDefault(); next(); break;
      case " ":
        event.preventDefault(); next(); break;
      case "ArrowLeft":
      case "PageUp":
        event.preventDefault(); previous(); break;
      case "Home": event.preventDefault(); goTo(0); break;
      case "End": event.preventDefault(); goTo(slides.length - 1); break;
      case "n": case "N": applyNotes(!document.body.classList.contains("notes-on")); break;
      case "o": case "O": togglePanel("overview"); break;
      case "t": case "T": togglePanel("timer"); break;
      case "s": case "S": togglePanel("scoreboard"); break;
      case "b": case "B":
        applyTheme(document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light");
        break;
      case "f": case "F": toggleFullscreen(); break;
      case "r": case "R": resetExercises(); break;
      case "?": togglePanel("help"); break;
      case "Escape":
        $$(".panel-float").forEach((panel) => {
          if (panel.id !== "timer") panel.hidden = true;
        });
        break;
      default: break;
    }
  });

  window.addEventListener("hashchange", () => {
    const index = slideIndexFromHash();
    if (index >= 0 && index !== currentIndex) goTo(index, { silent: true });
  });

  function start() {
    paintCodeBlocks();
    buildSectionMarks();
    buildOverview();
    setUpPlaygrounds();
    renderTeams();
    renderTimer();

    $$("[data-boxlab]").forEach((lab) => {
      $$("[data-box]", lab).forEach((input) => {
        input.dataset.initial = input.value;
      });
      updateBoxLab(lab);
    });
    $$("[data-flexlab]").forEach((lab) => {
      $$("[data-flex]", lab).forEach((control) => {
        control.dataset.initial = control.value;
      });
      updateFlexLab(lab);
    });
    $$("[data-viewport-tester]").forEach((tester) => setViewportWidth(tester, "full"));

    applyTheme(store.get("theme", "dark"));
    applyNotes(store.get("notes", false));
    const soundButton = $('[data-action="toggle-sound"]');
    if (soundButton) {
      soundButton.setAttribute("aria-pressed", String(soundEnabled));
      soundButton.textContent = soundEnabled ? "Sound on" : "Sound off";
    }

    const fromHash = slideIndexFromHash();
    const storedId = store.get("slide", null);
    const fromStore = storedId ? slides.findIndex((slide) => slide.id === storedId) : -1;
    goTo(fromHash >= 0 ? fromHash : Math.max(0, fromStore), { silent: fromHash >= 0 });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
