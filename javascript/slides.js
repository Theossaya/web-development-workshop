/* ==========================================================================
   JavaScript workshop — deck behaviour
   --------------------------------------------------------------------------
   Plain browser JS, no dependencies, runs from a file:// path.

   The one genuinely new piece compared with the HTML/CSS deck is the runner:
   student code has to actually execute, so each playground owns a sandboxed
   iframe with `allow-scripts` but NOT `allow-same-origin`. That combination
   gives the frame an opaque origin — it can run code and postMessage back,
   but it cannot reach into this document, its storage or its cookies.

     1  helpers and storage
     2  syntax highlighting
     3  navigation, ruler, navigator
     4  notes, theme, fullscreen
     5  timer
     6  scoreboard
     7  the runner: sandbox, console capture, watchdog
     8  ask/predict rows
     9  cheer and reset
     10 keys and start-up
   ========================================================================== */

(function () {
  "use strict";

  /* ---------- 1. helpers ---------- */

  var $ = function (sel, scope) { return (scope || document).querySelector(sel); };
  var $$ = function (sel, scope) {
    return Array.prototype.slice.call((scope || document).querySelectorAll(sel));
  };

  var store = {
    get: function (key, fallback) {
      try {
        var raw = window.localStorage.getItem("jsdeck." + key);
        return raw === null ? fallback : JSON.parse(raw);
      } catch (e) { return fallback; }
    },
    set: function (key, value) {
      try { window.localStorage.setItem("jsdeck." + key, JSON.stringify(value)); } catch (e) {}
    }
  };

  var calm = function () {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  };

  var soundOn = store.get("sound", true);

  function chime() {
    if (!soundOn) return;
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    try {
      var ctx = new Ctx();
      [520, 780].forEach(function (hz, i) {
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = "square";
        osc.frequency.value = hz;
        gain.gain.setValueAtTime(0.0001, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.15, ctx.currentTime + 0.02 + i * 0.16);
        gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.3 + i * 0.16);
        osc.connect(gain).connect(ctx.destination);
        osc.start(ctx.currentTime + i * 0.16);
        osc.stop(ctx.currentTime + 0.4 + i * 0.16);
      });
      setTimeout(function () { ctx.close(); }, 1200);
    } catch (e) {}
  }

  /* ---------- 2. syntax highlighting ---------- */

  var ENT = { "&": "&amp;", "<": "&lt;", ">": "&gt;" };
  function esc(text) { return text.replace(/[&<>]/g, function (c) { return ENT[c]; }); }

  var TOKENS = new RegExp(
    [
      "(\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/)",                 // 1 comment
      "(`[^`]*`|\"[^\"\\n]*\"|'[^'\\n]*')",                     // 2 string
      "\\b(const|let|var|function|return|if|else|for|of|in|while|do|break|continue|new|typeof|class|this|try|catch|throw)\\b", // 3 keyword
      "\\b(true|false|null|undefined|NaN|\\d+(?:\\.\\d+)?)\\b",  // 4 literal
      "\\b([A-Za-z_$][\\w$]*)(?=\\s*\\()"                        // 5 call
    ].join("|"),
    "g"
  );

  function paintJs(source) {
    return esc(source).replace(TOKENS, function (whole, comment, str, kw, lit, call) {
      if (comment) return '<span class="c">' + comment + "</span>";
      if (str) return '<span class="s">' + str + "</span>";
      if (kw) return '<span class="k">' + kw + "</span>";
      if (lit) return '<span class="n">' + lit + "</span>";
      if (call) return '<span class="f">' + call + "</span>";
      return whole;
    });
  }

  /* Markup blocks keep the simpler treatment — tags only. */
  function paintHtml(source) {
    return esc(source)
      .replace(/(&lt;\/?)([\w-]+)/g, '<span class="p">$1</span><span class="k">$2</span>')
      .replace(/([\w-]+)(=)(&quot;[^&]*?&quot;|"[^"]*")/g,
        '<span class="n">$1</span><span class="p">$2</span><span class="s">$3</span>')
      .replace(/(&gt;)/g, '<span class="p">$1</span>');
  }

  function paintBlocks() {
    $$("pre[data-lang]").forEach(function (block) {
      var lang = block.getAttribute("data-lang");
      var src = block.textContent.replace(/^\n/, "").replace(/\s+$/, "");
      var paint = lang === "html" ? paintHtml : paintJs;
      if (!block.hasAttribute("data-diff")) {
        block.innerHTML = paint(src);
        return;
      }
      block.innerHTML = src.split("\n").map(function (line) {
        var m = line.charAt(0);
        if (m === "+") return '<span class="ln ln--add">' + paint(line.slice(1)) + "</span>";
        if (m === "-") return '<span class="ln ln--del">' + paint(line.slice(1)) + "</span>";
        return '<span class="ln">' + paint(line) + "</span>";
      }).join("\n");
    });
  }

  /* ---------- 3. navigation ---------- */

  var slides = $$(".slide");
  var count = $("#count");
  var rulerFill = $("#rulerFill");
  var barId = $("#barId");
  var here = 0;

  function indexFromHash() {
    var id = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (!id) return -1;
    for (var i = 0; i < slides.length; i += 1) if (slides[i].id === id) return i;
    return -1;
  }

  function show(index, opts) {
    var settings = opts || {};
    var target = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach(function (slide, i) {
      var on = i === target;
      slide.classList.toggle("is-on", on);
      slide.setAttribute("aria-hidden", on ? "false" : "true");
    });
    here = target;
    var slide = slides[target];

    count.textContent = pad(target + 1) + " / " + pad(slides.length);
    rulerFill.style.width = ((target + 1) / slides.length) * 100 + "%";
    barId.innerHTML = "// " + (slide.dataset.part || "") + " &middot; <b>" +
      (slide.dataset.title || "") + "</b>";

    if (!settings.quiet) {
      var hash = "#" + slide.id;
      if (window.location.hash !== hash) history.replaceState(null, "", hash);
    }
    store.set("at", slide.id);
    markHere();
    var pane = slide.querySelector(".pane");
    if (pane) pane.scrollTop = 0;
  }

  function pad(n) { return n < 10 ? "0" + n : String(n); }
  function next() { show(here + 1); }
  function prev() { show(here - 1); }

  function buildMarks() {
    var holder = $("#marks");
    var last = null;
    slides.forEach(function (slide, i) {
      if (slide.dataset.part === last) return;
      last = slide.dataset.part;
      var tick = document.createElement("i");
      tick.style.left = (i / slides.length) * 100 + "%";
      tick.title = last;
      holder.appendChild(tick);
    });
  }

  function buildNavigator() {
    var grid = $("#navGrid");
    var frag = document.createDocumentFragment();
    slides.forEach(function (slide, i) {
      var item = document.createElement("button");
      item.type = "button";
      item.className = "nav-item";
      item.dataset.act = "go";
      item.dataset.i = String(i);
      var meta = document.createElement("span");
      meta.textContent = pad(i + 1) + "  " + (slide.dataset.part || "");
      var name = document.createElement("em");
      name.style.fontStyle = "normal";
      name.textContent = slide.dataset.title || "";
      item.appendChild(meta);
      item.appendChild(name);
      frag.appendChild(item);
    });
    grid.appendChild(frag);
  }

  function markHere() {
    $$(".nav-item").forEach(function (item, i) {
      item.classList.toggle("is-here", i === here);
      item.setAttribute("aria-current", i === here ? "true" : "false");
    });
  }

  function sheet(id, force) {
    var el = document.getElementById(id);
    if (!el) return;
    var open = typeof force === "boolean" ? force : el.hidden;
    el.hidden = !open;
    var trigger = $('[data-sheet="' + id + '"]');
    if (trigger) trigger.setAttribute("aria-pressed", String(open));
    if (open) {
      var first = el.querySelector("button, input, select");
      if (first) first.focus();
    }
  }

  /* ---------- 4. notes, theme, fullscreen ---------- */

  function setNotes(on) {
    document.body.classList.toggle("notes-on", on);
    var b = $('[data-act="notes"]');
    if (b) b.setAttribute("aria-pressed", String(on));
    store.set("notes", on);
  }

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var b = $('[data-act="theme"]');
    if (b) {
      b.setAttribute("aria-pressed", String(theme === "light"));
      b.textContent = theme === "light" ? "dark" : "light";
    }
    store.set("theme", theme);
  }

  function fullscreen() {
    if (document.fullscreenElement) document.exitFullscreen();
    else if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(function () {});
    }
  }

  /* ---------- 5. timer ---------- */

  var timerBox = $("#timer");
  var clock = $("#clock");
  var clockLabel = $("#clockLabel");
  var total = 180;
  var left = 180;
  var ticking = null;

  function mmss(s) { return Math.floor(s / 60) + ":" + (s % 60 < 10 ? "0" : "") + (s % 60); }

  function drawClock() {
    clock.textContent = mmss(Math.max(0, left));
    timerBox.classList.toggle("is-last", left <= 10 && left > 0);
    timerBox.classList.toggle("is-out", left <= 0);
    var b = $("#clockGo");
    b.textContent = ticking ? "pause" : "start";
    b.dataset.clock = ticking ? "pause" : "start";
  }

  function haltClock() { if (ticking) { clearInterval(ticking); ticking = null; } }

  function runClock() {
    if (ticking || left <= 0) return;
    ticking = setInterval(function () {
      left -= 1;
      if (left <= 0) { left = 0; haltClock(); chime(); }
      drawClock();
    }, 1000);
    drawClock();
  }

  function setClock(seconds, label, go) {
    haltClock();
    total = seconds;
    left = seconds;
    clockLabel.textContent = label || "";
    sheet("timer", true);
    drawClock();
    if (go) runClock();
  }

  /* ---------- 6. scoreboard ---------- */

  var NAMES = ["callback", "closure", "scope", "array", "object", "event"];
  var teams = store.get("teams", null) ||
    NAMES.slice(0, 4).map(function (n) { return { name: n, score: 0 }; });

  function saveTeams() { store.set("teams", teams); }

  function drawTeams() {
    var holder = $("#teams");
    holder.innerHTML = "";
    teams.forEach(function (team, i) {
      var row = document.createElement("div");
      row.className = "team";
      row.dataset.i = String(i);
      row.innerHTML =
        '<input type="text" aria-label="Team name">' +
        '<button type="button" class="pm" data-pts="-1" aria-label="Subtract a point">&minus;</button>' +
        '<span class="pts">0</span>' +
        '<button type="button" class="pm" data-pts="1" aria-label="Add a point">+</button>';
      row.querySelector("input").value = team.name;
      row.querySelector(".pts").textContent = String(team.score);
      holder.appendChild(row);
    });
    $("#teamN").value = String(teams.length);
  }

  function setTeamCount(n) {
    var want = Number(n);
    while (teams.length < want) {
      teams.push({ name: NAMES[teams.length] || "team " + (teams.length + 1), score: 0 });
    }
    teams = teams.slice(0, want);
    saveTeams();
    drawTeams();
  }

  /* ---------- 7. the runner ---------- */

  /* Runs inside the sandboxed frame. Reports back by postMessage only. */
  var RUNTIME = [
    "(function(){",
    "  function fmt(v, d){",
    "    d = d || 0;",
    "    if (d > 3) return '…';",
    "    if (typeof v === 'string') return d ? JSON.stringify(v) : v;",
    "    if (v === null) return 'null';",
    "    if (v === undefined) return 'undefined';",
    "    if (typeof v === 'number' || typeof v === 'boolean') return String(v);",
    "    if (typeof v === 'function') return 'function ' + (v.name || 'anonymous') + '()';",
    "    if (v && v.nodeType === 1) return '<' + v.tagName.toLowerCase() + '>';",
    "    if (Array.isArray(v)) return '[' + v.map(function(x){ return fmt(x, d+1); }).join(', ') + ']';",
    "    try {",
    "      var out = [];",
    "      for (var k in v) if (Object.prototype.hasOwnProperty.call(v, k)) out.push(k + ': ' + fmt(v[k], d+1));",
    "      return '{ ' + out.join(', ') + ' }';",
    "    } catch (e) { return String(v); }",
    "  }",
    "  window.__say = function(kind, args){",
    "    var text = Array.prototype.map.call(args, function(a){ return fmt(a, 0); }).join(' ');",
    "    parent.postMessage({ jsdeck: 1, kind: kind, text: text }, '*');",
    "  };",
    "  ['log','info','warn','error'].forEach(function(name){",
    "    var original = console[name];",
    "    console[name] = function(){ window.__say(name === 'info' ? 'log' : name, arguments); original.apply(console, arguments); };",
    "  });",
    "  window.onerror = function(msg, src, line){",
    "    var own = line - __OFFSET__;",
    "    window.__say('error', [msg + (own > 0 ? '  (your line ' + own + ')' : '')]);",
    "    return true;",
    "  };",
    "  window.addEventListener('unhandledrejection', function(e){ window.__say('error', ['Unhandled promise rejection: ' + e.reason]); });",
    "  window.__done = function(){ parent.postMessage({ jsdeck: 1, kind: 'done' }, '*'); };",
    "})();"
  ].join("\n");

  var SHELL_CSS =
    "html{font-family:Georgia,'Times New Roman',serif;color:#14140f;background:#fff}" +
    "body{margin:0;padding:14px;font-size:15px;line-height:1.4}" +
    "button{font:inherit;padding:6px 14px;cursor:pointer;border:1px solid #14140f;background:#fff}" +
    "input{font:inherit;padding:5px 8px;border:1px solid #14140f}" +
    "ul,ol{margin:.4em 0;padding-left:1.3em}" +
    "*{box-sizing:border-box}";

  /* Built line by line so the error line numbers can be translated back into
     the line the student actually typed. The student's line 1 lands on
     document line offset+1, so onerror subtracts offset. */
  function runnerDoc(markup, code) {
    var open = "<scr" + "ipt>";
    var close = "</scr" + "ipt>";
    var preamble = [
      '<!doctype html><html><head><meta charset="utf-8"><style>' + SHELL_CSS + "</style></head><body>",
      markup,
      open,
      RUNTIME,
      close,
      open
    ].join("\n");
    var offset = preamble.split("\n").length;
    return preamble.replace("__OFFSET__", String(offset)) +
      "\n" + code +
      "\n;window.__done && window.__done();\n" + close +
      "</body></html>";
  }

  var LOOPY = /while\s*\(\s*(?:true|1)\s*\)|for\s*\(\s*;\s*;\s*\)/;

  function say(pg, kind, text) {
    var out = $("[data-console]", pg);
    if (!out) return;
    var line = document.createElement("span");
    line.className = "console-line" +
      (kind === "error" ? " is-err" : kind === "warn" ? " is-warn" : kind === "sys" ? " is-sys" : "");
    line.textContent = text;
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
  }

  function runPlayground(pg) {
    var jsArea = $("[data-js]", pg);
    var htmlArea = $("[data-html]", pg);
    var frame = $("[data-frame]", pg);
    var out = $("[data-console]", pg);
    if (!frame || !jsArea) return;

    var code = jsArea.value;
    if (LOOPY.test(code) && pg.dataset.loopOk !== "1") {
      out.innerHTML = "";
      say(pg, "sys", "that loop never stops. press Run again if you meant it, then Stop.");
      pg.dataset.loopOk = "1";
      return;
    }
    pg.dataset.loopOk = "";

    out.innerHTML = "";
    clearTimeout(pg.__watch);
    frame.srcdoc = runnerDoc(htmlArea ? htmlArea.value : "", code);
    pg.__watch = setTimeout(function () {
      if (!pg.__finished) say(pg, "sys", "still running — press Stop if it is stuck.");
    }, 2500);
    pg.__finished = false;
  }

  function stopPlayground(pg) {
    var frame = $("[data-frame]", pg);
    if (!frame) return;
    clearTimeout(pg.__watch);
    frame.srcdoc = "<!doctype html><title>stopped</title>";
    say(pg, "sys", "stopped.");
  }

  function resetPlayground(pg) {
    $$("[data-js], [data-html]", pg).forEach(function (area) {
      area.value = area.dataset.start || "";
    });
    $$("details.rev", pg).forEach(function (d) { d.open = false; });
    var out = $("[data-console]", pg);
    if (out) out.innerHTML = "";
    var frame = $("[data-frame]", pg);
    if (frame) frame.srcdoc = "";
    pg.dataset.loopOk = "";
  }

  function copyPlayground(pg, button) {
    var parts = [];
    var htmlArea = $("[data-html]", pg);
    var jsArea = $("[data-js]", pg);
    if (htmlArea) parts.push("<!-- index.html -->\n" + htmlArea.value);
    if (jsArea) parts.push("// script.js\n" + jsArea.value);
    var text = parts.join("\n\n");
    var done = function () {
      var was = button.textContent;
      button.textContent = "copied";
      setTimeout(function () { button.textContent = was; }, 1300);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
    } else { fallbackCopy(text, done); }
  }

  function fallbackCopy(text, done) {
    var pad = document.createElement("textarea");
    pad.value = text;
    pad.setAttribute("aria-hidden", "true");
    pad.style.position = "fixed";
    pad.style.opacity = "0";
    document.body.appendChild(pad);
    pad.select();
    try { document.execCommand("copy"); done(); } catch (e) {}
    document.body.removeChild(pad);
  }

  window.addEventListener("message", function (event) {
    var data = event.data;
    if (!data || data.jsdeck !== 1) return;
    var pg = null;
    $$("[data-pg]").forEach(function (candidate) {
      var frame = $("[data-frame]", candidate);
      if (frame && frame.contentWindow === event.source) pg = candidate;
    });
    if (!pg) return;
    if (data.kind === "done") {
      pg.__finished = true;
      clearTimeout(pg.__watch);
      return;
    }
    say(pg, data.kind, data.text);
  });

  function setUpPlaygrounds() {
    $$("[data-pg]").forEach(function (pg) {
      $$("[data-js], [data-html]", pg).forEach(function (area) {
        area.dataset.start = area.value;
      });
    });
  }

  /* Tab indents inside a code area instead of leaving it. */
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Tab" || event.shiftKey) return;
    var area = event.target.closest && event.target.closest("[data-js], [data-html]");
    if (!area) return;
    event.preventDefault();
    var at = area.selectionStart;
    area.value = area.value.slice(0, at) + "  " + area.value.slice(area.selectionEnd);
    area.selectionStart = area.selectionEnd = at + 2;
  });

  /* ---------- 8. ask rows ---------- */

  function answer(opt) {
    var ask = opt.closest(".ask");
    var right = opt.dataset.v === ask.dataset.a;
    $$(".opt", ask).forEach(function (o) { o.classList.remove("is-yes", "is-no"); });
    opt.classList.add(right ? "is-yes" : "is-no");
    var why = $(".ask-why", ask);
    if (why) {
      why.textContent = right
        ? "// " + (ask.dataset.why || "correct")
        : "// not that one. try again, then say why out loud.";
    }
    if (right) cheer(8);
  }

  function resetAsks(scope) {
    $$(".ask", scope).forEach(function (ask) {
      $$(".opt", ask).forEach(function (o) { o.classList.remove("is-yes", "is-no"); });
      var why = $(".ask-why", ask);
      if (why) why.textContent = "";
    });
  }

  /* ---------- 9. cheer and reset ---------- */

  var CHEER = ["#ff5c2e", "#d7f43a", "#f0b429"];

  function cheer(n) {
    if (calm()) return;
    var layer = $("#cheer");
    var total = n || 26;
    for (var i = 0; i < total; i += 1) {
      var bit = document.createElement("i");
      bit.style.left = Math.random() * 100 + "vw";
      bit.style.background = CHEER[i % CHEER.length];
      bit.style.animationDelay = Math.random() * 0.35 + "s";
      layer.appendChild(bit);
      (function (el) { setTimeout(function () { el.remove(); }, 2200); })(bit);
    }
  }

  function resetSlide() {
    var slide = slides[here];
    $$("[data-pg]", slide).forEach(resetPlayground);
    resetAsks(slide);
    $$("details.rev", slide).forEach(function (d) { d.open = false; });
  }

  /* ---------- 10. events, keys, start ---------- */

  document.addEventListener("click", function (event) {
    var t = event.target;

    var opt = t.closest(".opt");
    if (opt && opt.closest(".ask")) { answer(opt); return; }

    var pm = t.closest(".pm");
    if (pm) {
      var row = pm.closest(".team");
      var i = Number(row.dataset.i);
      var d = Number(pm.dataset.pts);
      teams[i].score += d;
      row.querySelector(".pts").textContent = String(teams[i].score);
      saveTeams();
      if (d > 0) cheer(8);
      return;
    }

    var clockBtn = t.closest("[data-clock]");
    if (clockBtn) {
      var mode = clockBtn.dataset.clock;
      if (mode === "start") runClock();
      if (mode === "pause") { haltClock(); drawClock(); }
      if (mode === "reset") { haltClock(); left = total; drawClock(); }
      return;
    }

    var preset = t.closest("[data-preset]");
    if (preset) { setClock(Number(preset.dataset.preset), preset.dataset.label, false); return; }

    var starter = t.closest("[data-start]");
    if (starter) { setClock(Number(starter.dataset.start), starter.dataset.label, true); return; }

    var pgBtn = t.closest("[data-pgact]");
    if (pgBtn) {
      var pg = pgBtn.closest("[data-pg]");
      var act = pgBtn.dataset.pgact;
      if (act === "run") runPlayground(pg);
      if (act === "stop") stopPlayground(pg);
      if (act === "reset") resetPlayground(pg);
      if (act === "copy") copyPlayground(pg, pgBtn);
      return;
    }

    var btn = t.closest("[data-act]");
    if (!btn) return;
    switch (btn.dataset.act) {
      case "next": next(); break;
      case "prev": prev(); break;
      case "first": show(0); break;
      case "last": show(slides.length - 1); break;
      case "go": show(Number(btn.dataset.i)); sheet("nav", false); break;
      case "notes": setNotes(!document.body.classList.contains("notes-on")); break;
      case "theme":
        setTheme(document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light");
        break;
      case "full": fullscreen(); break;
      case "sheet": sheet(btn.dataset.sheet); break;
      case "close": sheet(btn.closest(".sheet").id, false); break;
      case "reset": resetSlide(); break;
      case "zero":
        teams.forEach(function (team) { team.score = 0; });
        saveTeams();
        $$(".pts").forEach(function (cell) { cell.textContent = "0"; });
        break;
      case "sound":
        soundOn = !soundOn;
        store.set("sound", soundOn);
        btn.setAttribute("aria-pressed", String(soundOn));
        btn.textContent = soundOn ? "sound on" : "sound off";
        break;
      case "cheer": cheer(46); break;
      case "print": window.print(); break;
      default: break;
    }
  });

  document.addEventListener("change", function (event) {
    if (event.target.id === "teamN") setTeamCount(event.target.value);
  });

  document.addEventListener("input", function (event) {
    var row = event.target.closest && event.target.closest(".team");
    if (row && event.target.matches("input[type='text']")) {
      teams[Number(row.dataset.i)].name = event.target.value;
      saveTeams();
    }
  });

  var TYPING = ["INPUT", "TEXTAREA", "SELECT"];

  document.addEventListener("keydown", function (event) {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    if (TYPING.indexOf(event.target.tagName) !== -1 || event.target.isContentEditable) return;
    switch (event.key) {
      case "ArrowRight": case "PageDown": case " ":
        event.preventDefault(); next(); break;
      case "ArrowLeft": case "PageUp":
        event.preventDefault(); prev(); break;
      case "Home": event.preventDefault(); show(0); break;
      case "End": event.preventDefault(); show(slides.length - 1); break;
      case "n": case "N": setNotes(!document.body.classList.contains("notes-on")); break;
      case "o": case "O": sheet("nav"); break;
      case "t": case "T": sheet("timer"); break;
      case "s": case "S": sheet("score"); break;
      case "l": case "L":
        setTheme(document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light");
        break;
      case "f": case "F": fullscreen(); break;
      case "r": case "R": resetSlide(); break;
      case "?": sheet("help"); break;
      case "Escape":
        $$(".sheet").forEach(function (s) { if (s.id !== "timer") s.hidden = true; });
        break;
      default: break;
    }
  });

  window.addEventListener("hashchange", function () {
    var i = indexFromHash();
    if (i >= 0 && i !== here) show(i, { quiet: true });
  });

  function start() {
    paintBlocks();
    buildMarks();
    buildNavigator();
    setUpPlaygrounds();
    drawTeams();
    drawClock();

    setTheme(store.get("theme", "dark"));
    setNotes(store.get("notes", false));
    var sBtn = $('[data-act="sound"]');
    if (sBtn) {
      sBtn.setAttribute("aria-pressed", String(soundOn));
      sBtn.textContent = soundOn ? "sound on" : "sound off";
    }

    var fromHash = indexFromHash();
    var savedId = store.get("at", null);
    var fromStore = -1;
    if (savedId) {
      for (var i = 0; i < slides.length; i += 1) if (slides[i].id === savedId) fromStore = i;
    }
    show(fromHash >= 0 ? fromHash : Math.max(0, fromStore), { quiet: fromHash >= 0 });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
