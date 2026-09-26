"""
Builds javascript-from-zero.pdf, the student handout for the JavaScript session.

    python build.py

Edit the text in SECTIONS below, then run this again. The script writes an HTML
page to a temporary folder and asks Chrome (or Edge) to print it to PDF, so no
PDF library is needed to build it.
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
OUT_PDF = HERE / "javascript-from-zero.pdf"

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

# --------------------------------------------------------------------------
# Small helpers for writing the content
# --------------------------------------------------------------------------

JS_TOKENS = re.compile(
    r"(//[^\n]*)"                                  # 1 comment
    r"|(`[^`]*`|\"[^\"\n]*\"|'[^'\n]*')"           # 2 string
    r"|\b(const|let|function|return|if|else|for|of|new)\b"  # 3 keyword
    r"|\b(true|false|undefined|null|\d+(?:\.\d+)?)\b"      # 4 literal
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

    escaped = src.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return JS_TOKENS.sub(swap, escaped)


def paint_html(src):
    escaped = html.escape(src, quote=False)
    escaped = re.sub(r'(=)("[^"]*")', r'\1<span class="s">\2</span>', escaped)
    escaped = re.sub(r"(&lt;/?)([a-z0-9]+)", r'\1<span class="t">\2</span>', escaped)
    return escaped


def code(src, lang="js", label=None):
    src = src.strip("\n")
    body = paint_html(src) if lang == "html" else paint_js(src)
    name = label or ("index.html" if lang == "html" else "script.js")
    return f'<div class="code"><div class="file">{name}</div><pre>{body}</pre></div>'


def prints(*lines):
    rows = "".join(f"<div>{html.escape(line)}</div>" for line in lines)
    return f'<div class="out"><div class="out-label">Prints</div>{rows}</div>'


def watch(text):
    return f'<div class="box watch"><div class="box-label">Watch out</div><p>{text}</p></div>'


def tryit(text):
    return f'<div class="box try"><div class="box-label">Try it</div><p>{text}</p></div>'


def p(text):
    return f"<p>{text}</p>"


def h3(text):
    return f"<h3>{text}</h3>"


def c(text):
    """Inline code inside a sentence."""
    return f"<code>{html.escape(text)}</code>"


# --------------------------------------------------------------------------
# The content
# --------------------------------------------------------------------------

SECTIONS = []

SECTIONS.append(("1", "Where JavaScript goes", [
    p("Your page already has two files. HTML says what things are: a heading, a button, a "
      "paragraph. CSS says how they look. JavaScript is the third file, and it decides what "
      "happens when someone clicks, types or scrolls."),
    p(f"Link it at the bottom of the body, just before {c('</body>')}. The browser reads your "
      "page from top to bottom, so putting the script last means every element already exists "
      "by the time your code runs."),
    code("""
    <footer>Made in Lagos</footer>
    <script src="script.js"></script>
  </body>
</html>
""", "html"),
    p(f"To see what your code is doing, open the console. Press {c('F12')} and click the "
      f"Console tab. Anything you pass to {c('console.log')} shows up there."),
    code("""
console.log("Hello from Lagos");
console.log(2 + 2);
"""),
    prints("Hello from Lagos", "4"),
    watch("Nothing in the console? Check that the file name in <code>src</code> matches the real "
          "file exactly (<code>script.js</code> is not <code>Script.js</code>), that both files "
          "sit in the same folder, and that you saved before refreshing."),
    tryit("Log your name and your state of origin on two separate lines."),
]))

SECTIONS.append(("2", "Values and variables", [
    p("Almost everything you work with is one of three kinds of value. A <b>number</b> has no "
      f"quotes and you can do sums with it: {c('1500')}, {c('0')}, {c('-20')}. A <b>string</b> is "
      f"text inside quotes: {c('\"Chiamaka\"')}, {c('\"Yaba\"')}. A <b>boolean</b> is only ever "
      f"{c('true')} or {c('false')}."),
    p("A variable is a name you give a value so you can use it again later."),
    code("""
const name = "Chiamaka";    // string
let dataLeft = 1500;        // number: MB of data left
const hasLight = true;      // boolean

dataLeft = dataLeft - 200;  // after watching football highlights

console.log(name, dataLeft, hasLight);
"""),
    prints("Chiamaka 1300 true"),
    p(f"Use {c('const')} by default. Switch to {c('let')} only when the value will change, like "
      "a data balance that keeps going down."),
    p(f"Read {c('=')} as <i>gets</i>. The line {c('dataLeft = dataLeft - 200')} means "
      "\"dataLeft gets dataLeft minus 200\". JavaScript works out the right side first, then "
      "stores the answer in the name on the left."),
    p(f"Give variables names that explain themselves: {c('dataLeft')}, not {c('d')} or "
      f"{c('x')}. Start with a small letter, use no spaces, and put a capital letter where each "
      "new word starts."),
    watch("Change a <code>const</code> and the console says <i>Assignment to constant "
          "variable.</i> That message tells you exactly what happened. If the value really needs "
          "to change, use <code>let</code>."),
    tryit("Make a variable for your airtime balance, spend ₦100 on a call, then log what is left."),
]))

SECTIONS.append(("3", "Text, numbers and the + trap", [
    p("Join text with backticks. Anything inside <code>${ }</code> gets worked out and dropped "
      "into the sentence. On most keyboards the backtick key sits to the left of the 1 key."),
    code("""
const customer = "Tunde";
const total = 3500;

console.log(`Thank you ${customer}, your total is ₦${total}.`);
"""),
    prints("Thank you Tunde, your total is ₦3500."),
    p("Now the trap. The + sign adds numbers, but if either side is text it glues them together "
      "instead. Anything a person types into a form reaches your code as text, even when it "
      "looks like a number."),
    code("""
const amount = "2000";   // typed into a form
const charge = 50;

console.log(amount + charge);          // glued
console.log(Number(amount) + charge);  // added
"""),
    prints("200050", "2050"),
    p(f"Wrap text in {c('Number()')} before you do sums with it."),
    p("Some numbers should stay as text. You will never add two phone numbers together, and if "
      "you turn one into a number the zero at the front disappears:"),
    code("""
console.log(Number("08031234567"));
"""),
    prints("8031234567"),
    p(f"To check what kind of value you have, use {c('typeof')}:"),
    code("""
console.log(typeof "5");     // string
console.log(typeof 5);       // number
console.log(typeof false);   // boolean
"""),
    watch("<code>${ }</code> only works inside backticks. Inside ordinary quotes you get "
          "<code>${customer}</code> printed exactly as you typed it."),
    tryit("Print <i>Aisha scored 280 in JAMB</i> using one variable for the name and one for "
          "the score."),
]))

SECTIONS.append(("4", "Functions", [
    p("A function is a set of steps with a name. You write the steps once, then run them as "
      "many times as you need, with different inputs each time."),
    code("""
function greet(name) {
  console.log(`Good morning, ${name}`);
}

greet("Emeka");
greet("Zainab");
"""),
    prints("Good morning, Emeka", "Good morning, Zainab"),
    p("Writing the function does nothing on its own. Think of a recipe in a drawer: nothing "
      f"gets cooked until somebody uses it. The brackets in {c('greet(\"Emeka\")')} are what "
      "run it."),
    p(f"{c('name')} is the <b>parameter</b>, a blank in the recipe. {c('\"Emeka\"')} is the "
      "<b>argument</b>, whatever fills that blank this time."),
    h3("return versus console.log"),
    p(f"Most people get stuck here, so go slowly. {c('console.log')} only shows you a value. "
      f"{c('return')} hands the value back, so the rest of your code can use it."),
    p("You and three friends eat at a buka and the bill comes to ₦12,000:"),
    code("""
function splitBill(total, people) {
  return total / people;
}

const each = splitBill(12000, 4);
console.log(`Everybody pays ₦${each}`);
"""),
    prints("Everybody pays ₦3000"),
    p(f"Here is the same function with {c('console.log')} where {c('return')} should be:"),
    code("""
function splitBill(total, people) {
  console.log(total / people);
}

const each = splitBill(12000, 4);  // prints 3000
console.log(each);                 // prints undefined
"""),
    p(f"The function showed you 3000 and then threw it away. A function without {c('return')} "
      f"always hands back {c('undefined')}. To remember it: <b>console.log is a window, return "
      "is a door.</b> You look through a window. You carry things out through a door."),
    p(f"{c('return')} also ends the function straight away. Any line after it never runs."),
    watch("<code>splitBill</code> on its own, without brackets, runs nothing. You need "
          "<code>splitBill(12000, 4)</code>."),
    tryit("Write <code>addDelivery(price)</code> that returns the price plus ₦1,500 for "
          "delivery. <code>addDelivery(8000)</code> should give you 9500."),
]))

SECTIONS.append(("5", "Making decisions", [
    p(f"{c('if')} lets your code choose between two paths. The condition goes in round brackets, "
      "and the code for each path goes in curly braces."),
    code("""
const jambScore = 245;
const cutOff = 200;

if (jambScore >= cutOff) {
  console.log("You made the cut-off. Apply!");
} else {
  console.log("Below the cut-off for this school.");
}
"""),
    prints("You made the cut-off. Apply!"),
    p(f"For more than two paths, add {c('else if')}. JavaScript checks each condition in order "
      "and runs the first one that is true:"),
    code("""
const hasLight = false;
const hasFuel = true;

if (hasLight) {
  console.log("Up NEPA! Charge everything.");
} else if (hasFuel) {
  console.log("Generator time.");
} else {
  console.log("Candle and early sleep.");
}
"""),
    prints("Generator time."),
    """<table class="signs">
      <tr><td><code>===</code></td><td>equal</td><td><code>!==</code></td><td>not equal</td></tr>
      <tr><td><code>&gt;</code></td><td>greater than</td><td><code>&gt;=</code></td><td>greater than or equal to</td></tr>
      <tr><td><code>&lt;</code></td><td>less than</td><td><code>&lt;=</code></td><td>less than or equal to</td></tr>
    </table>""",
    p("Always compare with three equals signs. Two equals signs change the types before "
      "comparing, and that causes surprises:"),
    code("""
console.log("5" == 5);   // true, surprising
console.log("5" === 5);  // false, correct
"""),
    p(f"Join conditions with {c('&&')} (and) or {c('||')} (or). Flip one with {c('!')} (not):"),
    code("""
const age = 16;
const hasPaid = true;

console.log(age >= 13 && age <= 19);  // true: a teenager
console.log(hasPaid || age < 12);     // true: one of them is true
console.log(!hasPaid);                // false
"""),
    watch("One <code>=</code> puts a value into a variable. <code>===</code> compares two "
          "values. <code>if (score = 200)</code> is a bug that looks almost right."),
    tryit("Make a variable <code>dataLeft</code>. If it is below 100, log a warning to buy data. "
          "Otherwise, log that you are fine for now. Write the messages in Pidgin if you like."),
]))

SECTIONS.append(("6", "Lists and loops", [
    p("An array keeps a list of values under one name. Use square brackets, with commas "
      "between the items."),
    code("""
const stops = ["Ojota", "Maryland", "Anthony"];

console.log(stops[0]);       // Ojota
console.log(stops.length);   // 3

stops.push("Palmgrove");
console.log(stops.length);   // 4
"""),
    p(f"Counting starts at 0, so {c('stops[0]')} is the first stop. The last one is always "
      f"{c('stops[stops.length - 1]')}."),
    p(f"A loop runs the same code once for every item in the list. Learn {c('for...of')} "
      "first:"),
    code("""
for (const stop of stops) {
  console.log(`${stop}! ${stop}! Enter with your change.`);
}
"""),
    prints("Ojota! Ojota! Enter with your change.",
           "Maryland! Maryland! Enter with your change.",
           "Anthony! Anthony! Enter with your change.",
           "Palmgrove! Palmgrove! Enter with your change."),
    p("Add a fifth stop to the array and the loop picks it up without any other change. You "
      "write the instruction once, however long the list gets."),
    h3("Adding up a list"),
    p("Make the total before the loop starts, then add to it inside the loop:"),
    code("""
const prices = [2000, 1500, 500];   // jollof, chicken, zobo
let total = 0;

for (const price of prices) {
  total = total + price;
}

console.log(`Your bill: ₦${total}`);
"""),
    prints("Your bill: ₦4000"),
    h3("Two loops you will see in other people's code"),
    code("""
for (let i = 1; i <= 3; i++) {
  console.log(`Round ${i}`);
}

stops.forEach(function (stop) {
  console.log(stop);
});
"""),
    p(f"Both work. Stick with {c('for...of')} in your own code until you have a reason not to."),
    watch("<code>stops[4]</code> on a list of four items gives <code>undefined</code>, not an "
          "error. If a value is mysteriously <code>undefined</code>, check whether you counted "
          "from 1 instead of 0."),
    tryit("Make a list of five test scores. Log how many there are, the first and the last "
          "score, every score on its own line, and the total. Then work out the average."),
]))

SECTIONS.append(("7", "Objects", [
    p("An array numbers its items. An object names them. Use an object when one thing has "
      "several details."),
    code("""
const student = {
  name: "Ifeoma",
  state: "Enugu",
  jambScore: 268,
  hasLaptop: true
};

console.log(student.name);        // Ifeoma
console.log(student.jambScore);   // 268

student.hasLaptop = false;        // change a value
"""),
    p("Read a value with a dot and the property name. Change it the same way."),
    h3("A list of objects"),
    p("Put objects inside an array and you have the shape of most real data: a menu, a class "
      "list, a playlist, a bank statement."),
    code("""
const menu = [
  { food: "Jollof rice", price: 2000 },
  { food: "Fried plantain", price: 700 },
  { food: "Pepper soup", price: 2500 }
];

const budget = 2000;

for (const item of menu) {
  if (item.price <= budget) {
    console.log(`You can afford ${item.food}`);
  }
}
"""),
    prints("You can afford Jollof rice", "You can afford Fried plantain"),
    p("That one loop uses an array, objects, a loop, a comparison and a template literal. "
      "Most of what you build from here is some mix of those."),
    watch("Write <code>student.name</code>. Not <code>student.\"name\"</code>, and not "
          "<code>student[name]</code>. A dot, then the property name, no quotes."),
    tryit("Model four players from your favourite team as objects with a name, a position and "
          "a number of goals. Loop through them and log only the players with more than 2 goals."),
]))

SECTIONS.append(("8", "Changing the page", [
    p("When the browser loads your HTML, it turns every element into an object your code can "
      f"grab and change. {c('document.querySelector')} finds one element, using the same "
      "selectors you already write in CSS."),
    code("""
<h1 class="shop-name">Mama Put</h1>
<p class="status">Checking...</p>
""", "html"),
    code("""
const shopName = document.querySelector(".shop-name");
const status = document.querySelector(".status");

shopName.textContent = "Iya Basira Kitchen";
status.textContent = "Open now. Jollof is ready.";
status.classList.add("open");
"""),
    p("A few properties do most of the work:"),
    """<table class="props">
      <tr><td><code>textContent</code></td><td>The words inside an element. Read it, or replace it.</td></tr>
      <tr><td><code>classList.add("x")</code><br><code>classList.remove("x")</code></td><td>Switch a CSS class on or off. Keep the styling in your CSS file and let JavaScript flip the class.</td></tr>
      <tr><td><code>style.color</code></td><td>Set one style directly. Handy while testing, but classes are neater.</td></tr>
    </table>""",
    p(f"{c('querySelector')} gives you the first match. {c('querySelectorAll')} gives you every "
      "match, as a list:"),
    code("""
const items = document.querySelectorAll(".menu li");
console.log(items.length);
"""),
    watch("<i>Cannot read properties of null</i> means <code>querySelector</code> found nothing. "
          "Look for a typo in the selector (<code>.stauts</code>), a missing dot before a class "
          "name, or a script tag that sits above the element it is looking for."),
    tryit("On your own page, change the main heading and add a class to one element, using "
          "only JavaScript. Do not touch the HTML file."),
]))

SECTIONS.append(("9", "Responding to clicks and typing", [
    p(f"{c('addEventListener')} tells an element: when this happens, run that function."),
    code("""
<button class="vote-naija">Naija jollof</button>
<button class="vote-ghana">Ghana jollof</button>
<p class="score">No votes yet</p>
""", "html"),
    code("""
let naija = 0;
let ghana = 0;

const score = document.querySelector(".score");

function showScore() {
  score.textContent = `Naija ${naija} : ${ghana} Ghana`;
}

document.querySelector(".vote-naija").addEventListener("click", function () {
  naija = naija + 1;
  showScore();
});

document.querySelector(".vote-ghana").addEventListener("click", function () {
  ghana = ghana + 1;
  showScore();
});
"""),
    p(f"Both buttons call the same {c('showScore')} function, so the paragraph always reads the "
      "same way. Make that a habit: one function updates the page, and everything that changes "
      "something calls it."),
    p(f"Other events follow the same shape. Only the word in quotes changes: {c('\"input\"')} "
      f"fires on every key pressed in a text box, and {c('\"submit\"')}, {c('\"keydown\"')} and "
      f"{c('\"mouseover\"')} work the same way."),
    h3("The brackets bug"),
    code("""
button.addEventListener("click", showScore());  // wrong
button.addEventListener("click", showScore);    // right
"""),
    p(f"With brackets, {c('showScore')} runs once, straight away, and the button does nothing "
      "after that. Without brackets, you hand the function over so it can run on every click."),
    h3("Reading what someone typed"),
    p(f"The text in an input box lives in {c('.value')}, and it is always a string."),
    code("""
<input class="bill" placeholder="Bill total">
<input class="people" placeholder="Number of people">
<button class="split">Split it</button>
<p class="answer"></p>
""", "html"),
    code("""
document.querySelector(".split").addEventListener("click", function () {
  const bill = Number(document.querySelector(".bill").value);
  const people = Number(document.querySelector(".people").value);

  document.querySelector(".answer").textContent =
    `Each person pays ₦${bill / people}`;
});
"""),
    watch("Dividing text happens to work without <code>Number()</code>. Adding does not: "
          "<code>\"2000\" + 50</code> is still <code>\"200050\"</code>. Use <code>Number()</code> "
          "on every <code>.value</code> and you never have to remember which is which."),
    tryit("Build a light switch. A button flips a variable <code>hasLight</code> between "
          "<code>true</code> and <code>false</code> (<code>hasLight = !hasLight</code> does it). "
          "When it is true, a paragraph reads <i>Up NEPA! Light don come.</i> When it is false, "
          "it reads <i>Light don go again.</i> Put the <code>if</code> inside your update "
          "function."),
]))

SECTIONS.append(("10", "When it breaks", [
    p("Every programmer reads error messages all day. The message tells you what went wrong "
      "and which line to look at."),
    """<ol class="routine">
      <li>Read the red error in the console. All of it, including the line number.</li>
      <li>Say out loud what you expected, and what actually happened.</li>
      <li><code>console.log</code> any value you are not sure about.</li>
      <li>Change one thing, save, refresh and check again.</li>
      <li>Do not delete your work and start again. Starting over hides the mistake instead of teaching you what it was.</li>
    </ol>""",
    h3("Errors you will see this week"),
    """<table class="errors">
      <tr><th>The console says</th><th>It usually means</th></tr>
      <tr><td><code>jolof is not defined</code></td><td>A typo in a name, or you used the name before creating it.</td></tr>
      <tr><td><code>Cannot read properties of null</code></td><td><code>querySelector</code> found nothing.</td></tr>
      <tr><td><code>Assignment to constant variable</code></td><td>You tried to change a <code>const</code>.</td></tr>
      <tr><td><code>Unexpected token</code></td><td>A missing bracket, brace, comma or quote nearby.</td></tr>
      <tr><td><code>showScore is not a function</code></td><td>A typo in the name, or the thing you called is not a function.</td></tr>
      <tr><th colspan="2">No error, but it is still wrong</th></tr>
      <tr><td>200050 instead of 2050</td><td>You added text and a number. Use <code>Number()</code>.</td></tr>
      <tr><td>A function gives back <code>undefined</code></td><td>It uses <code>console.log</code> where it needs <code>return</code>.</td></tr>
      <tr><td>The button does nothing</td><td>You passed <code>showScore()</code> instead of <code>showScore</code>, or the selector is wrong.</td></tr>
    </table>""",
]))

CHEAT_JS_LEFT = """
// values
const name = "Chiamaka";
let balance = 1500;
const isOpen = true;

// join text
`Hi ${name}, you have ₦${balance}`

// text to number
Number("2000")

// decide
if (balance > 1000) {
  // ...
} else {
  // ...
}

// compare    ===  !==  >  <  >=  <=
// combine    &&  ||  !
"""

CHEAT_JS_RIGHT = """
// function
function addDelivery(price) {
  return price + 1500;
}

// list
const stops = ["Ojota", "Maryland"];
stops[0]
stops.length
stops.push("Yaba");

// loop
for (const stop of stops) {
  console.log(stop);
}

// object
const student = {
  name: "Ifeoma",
  score: 268
};
student.score
"""

# Page code has long lines, so it gets the full width instead of a column,
# where it would wrap mid-statement and look like the break mattered.
CHEAT_JS_PAGE = """
// find something on the page
const status = document.querySelector(".status");

// change it
status.textContent = "Open now";
status.classList.add("open");
status.classList.remove("closed");

// run code when something happens
button.addEventListener("click", function () {
  // ...
});

// what someone typed is always a string, so use Number() before sums
const amount = Number(input.value);
"""

PRACTICE = [
    ("Data balance tracker",
     "Start with 2000 MB. One button spends 150 (watching a video), one spends 5 (sending a "
     "WhatsApp message), and one adds 1000 (buying data). Show the balance on the page. When "
     "it drops below 200, add a warning class to it."),
    ("Bill splitter",
     "Build the splitter from section 9, then add a third box for a delivery fee that gets added "
     "to the bill before it is split."),
    ("Jollof war",
     "Take the vote counter from section 9. Add a Reset button and a line that says who is "
     "winning, or that it is a draw."),
    ("Cut-off checker",
     "Two boxes: a JAMB score and a school's cut-off mark. A button tells the student whether "
     "they made it. If either box is empty, show a message asking them to fill it in."),
    ("Buka menu",
     "An array of at least five meals as objects, each with a name and a price. A budget box and "
     "a button that logs every meal you can afford, then the cheapest meal on the menu."),
]

# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------

CSS = """
@page {
  size: A4;
  margin: 17mm 17mm 18mm;
  @bottom-left { content: "JavaScript from zero"; font: 8.5pt "Segoe UI", Arial, sans-serif; color: #7a7a72; }
  @bottom-right { content: counter(page); font: 8.5pt "Segoe UI", Arial, sans-serif; color: #7a7a72; }
}
@page :first {
  @bottom-left { content: none; }
  @bottom-right { content: none; }
}

:root {
  --ink: #16160f;
  --ink-2: #45453d;
  --ink-3: #7a7a72;
  --rule: #d6d6cc;
  --green: #007a4a;
  --green-dark: #0a5c38;
  --red: #b3261e;
  --code-bg: #f3f3ee;
}

* { box-sizing: border-box; }

html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

body {
  margin: 0;
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 10.6pt;
  line-height: 1.5;
  color: var(--ink);
}

/* ---------- cover ---------- */

.cover {
  height: 255mm;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  break-after: page;
}
.cover-top { border-top: 5px solid var(--green); padding-top: 9mm; }
.cover .class { font-size: 10pt; color: var(--ink-3); margin: 0 0 22mm; }
.cover h1 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 46pt;
  line-height: 1.02;
  letter-spacing: -0.02em;
  margin: 0 0 6mm;
  max-width: 13ch;
}
.cover .sub { font-size: 14pt; color: var(--ink-2); margin: 0; max-width: 34ch; line-height: 1.35; }
.cover-code {
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 11pt;
  line-height: 1.6;
  background: var(--code-bg);
  border: 1px solid var(--rule);
  padding: 6mm 7mm;
  margin: 0;
  white-space: pre;
}
.cover-foot { font-size: 9.5pt; color: var(--ink-3); border-top: 1px solid var(--rule); padding-top: 3mm; }

/* ---------- how to use ---------- */

.intro h2, .topic h2, .cheat h2, .practice h2 {
  font-family: Georgia, "Times New Roman", serif;
  font-weight: 700;
  font-size: 22pt;
  line-height: 1.1;
  letter-spacing: -0.01em;
  margin: 0 0 4mm;
}
.intro { break-after: page; }
.intro ol { padding-left: 5mm; margin: 0 0 6mm; }
.intro li { margin-bottom: 1.6mm; }
.contents { border-top: 1px solid var(--ink); margin-top: 8mm; }
.contents div {
  display: flex; gap: 5mm;
  padding: 2mm 0;
  border-bottom: 1px solid var(--rule);
}
.contents b { color: var(--green); font-weight: 600; min-width: 7mm; }

/* ---------- topics ---------- */

/* Topics flow on from each other instead of each forcing a fresh page, which
   left several pages a quarter full. Units keep text with its example. */
.topic + .topic { margin-top: 11mm; }
.unit { break-inside: avoid; }
.topic-num {
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 9.5pt;
  color: var(--green);
  margin: 0 0 1mm;
}
.topic h2 { border-bottom: 2px solid var(--ink); padding-bottom: 2.5mm; margin-bottom: 5mm; }

h3 {
  font-size: 12.5pt;
  font-weight: 700;
  margin: 6mm 0 2mm;
  break-after: avoid;
}

p { margin: 0 0 3mm; }

code {
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 9.2pt;
  color: #5a2a86;
  white-space: nowrap;
}

.code, .out, .box, table, ol.routine { break-inside: avoid; }

.code { margin: 0 0 3mm; border: 1px solid var(--rule); background: var(--code-bg); }
.code .file {
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 7.8pt;
  color: var(--ink-3);
  padding: 1.2mm 3mm;
  border-bottom: 1px solid var(--rule);
  background: #ebebe4;
}
.code pre {
  margin: 0;
  padding: 3mm 3.5mm;
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 9.2pt;
  line-height: 1.5;
  white-space: pre-wrap;
  color: var(--ink);
}
.c { color: #7a7a72; font-style: italic; }
.s { color: var(--green-dark); }
.k { color: #5a2a86; font-weight: 600; }
.n { color: #9a4a00; }
.t { color: #9a4a00; }

.out {
  margin: -1.5mm 0 4mm;
  border: 1px dashed #b9b9ae;
  border-top: 0;
  padding: 2mm 3.5mm 2.2mm;
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 9.2pt;
}
.out-label {
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 7.8pt;
  font-weight: 600;
  color: var(--ink-3);
  margin-bottom: .8mm;
}

.box { margin: 4mm 0 3mm; padding: 2.6mm 3.5mm 1mm; border: 1px solid var(--rule); }
.box-label { font-size: 8.4pt; font-weight: 700; margin-bottom: 1mm; }
.box p { margin-bottom: 2mm; }
.watch { background: #fbf3f2; border-color: #e8c4c1; }
.watch .box-label { color: var(--red); }
.try { background: #eef6f1; border-color: #bfdccb; }
.try .box-label { color: var(--green); }

table { border-collapse: collapse; width: 100%; margin: 1mm 0 4mm; font-size: 9.8pt; }
td, th { text-align: left; vertical-align: top; padding: 1.8mm 3mm 1.8mm 0; border-bottom: 1px solid var(--rule); }
th { font-weight: 600; border-bottom: 1.5px solid var(--ink); }
table.signs td:nth-child(odd) { width: 13mm; }
table.props td:first-child { width: 48mm; }
table.errors td:first-child { width: 72mm; }
table.errors th[colspan] { padding-top: 4mm; color: var(--ink-2); }
table.errors code { white-space: normal; }

ol.routine { padding-left: 5.5mm; margin: 0 0 5mm; }
ol.routine li { margin-bottom: 1.8mm; padding-left: 1mm; }

/* ---------- cheat sheet ---------- */

.cheat { break-before: page; }
.cheat-cols { display: flex; gap: 5mm; }
.cheat-cols .code { flex: 1; min-width: 0; }
.cheat pre { font-size: 9pt; line-height: 1.5; white-space: pre; }

/* ---------- practice ---------- */

.practice { break-before: page; }
.task { padding: 3mm 0; border-bottom: 1px solid var(--rule); break-inside: avoid; }
.task b { display: block; font-size: 11pt; margin-bottom: .8mm; }
.task span { font-family: "Cascadia Mono", Consolas, monospace; color: var(--green); font-size: 9pt; margin-right: 2mm; }
.last { margin-top: 6mm; font-weight: 600; }
"""


def kind_of(block):
    head = block.lstrip()[:24]
    if head.startswith('<div class="code"'):
        return "code"
    if head.startswith('<div class="out"'):
        return "out"
    if head.startswith("<h3"):
        return "h3"
    if head.startswith("<p"):
        return "p"
    return "other"


def group_units(blocks):
    """Keep each explanation with the code and output that follow it.

    A sentence like "use typeof:" is useless at the foot of one page with its
    example on the next, so a paragraph plus the code and output after it
    becomes one unit that the printer is not allowed to split. A sub-heading
    also pulls in the paragraph after it, so it never ends a page alone.
    """
    units, current, sticky = [], None, False
    for block in blocks:
        kind = kind_of(block)
        if kind in ("code", "out") and current is not None:
            current.append(block)
            continue
        if kind == "p" and sticky and current is not None:
            current.append(block)
            sticky = False
            continue
        current = [block]
        units.append(current)
        sticky = kind == "h3"
    return units


def build_html():
    parts = []

    parts.append("""
<section class="cover">
  <div class="cover-top">
    <p class="class">Web dev class &middot; session three notes</p>
    <h1>JavaScript from zero</h1>
    <p class="sub">How to make your web page respond when someone clicks, types or votes.</p>
  </div>
  <pre class="cover-code">""" + paint_js("""let naija = 0;

button.addEventListener("click", function () {
  naija = naija + 1;
  score.textContent = `Naija ${naija}`;
});""") + """</pre>
  <div class="cover-foot">Keep these notes next to your laptop. Every example is short enough to type in under a minute.</div>
</section>
""")

    contents = "".join(
        f'<div><b>{num}</b><span>{title}</span></div>' for num, title, _ in SECTIONS
    )
    contents += '<div><b>11</b><span>Cheat sheet</span></div>'
    contents += '<div><b>12</b><span>Practice at home</span></div>'

    parts.append(f"""
<section class="intro">
  <h2>How to use these notes</h2>
  <ol>
    <li>Read the short explanation first.</li>
    <li>Type the example yourself. Do not copy and paste it; typing it out is how your fingers learn where the brackets go.</li>
    <li>Run it and check that your console shows what the <b>Prints</b> box says.</li>
    <li>Do the <b>Try it</b> task without looking back at the example. Look back only if you get stuck.</li>
  </ol>
  <p>The red <b>Watch out</b> boxes are the mistakes that catch almost everybody. Read them even when your code works.</p>
  <div class="contents">{contents}</div>
</section>
""")

    for num, title, blocks in SECTIONS:
        header = f'<p class="topic-num">{num.zfill(2)}</p><h2>{title}</h2>'
        units = group_units(blocks)
        # The section heading rides with its first unit, so a title can never
        # sit alone at the bottom of a page.
        units[0].insert(0, header)
        body = "".join(f'<div class="unit">{"".join(u)}</div>' for u in units)
        parts.append(f'<section class="topic">{body}</section>')

    parts.append(f"""
<section class="cheat">
  <p class="topic-num">11</p>
  <h2 style="border-bottom:2px solid var(--ink);padding-bottom:2.5mm;margin-bottom:5mm;">Cheat sheet</h2>
  <div class="cheat-cols">
    <div class="code"><div class="file">values and decisions</div><pre>{paint_js(CHEAT_JS_LEFT.strip(chr(10)))}</pre></div>
    <div class="code"><div class="file">functions, lists and objects</div><pre>{paint_js(CHEAT_JS_RIGHT.strip(chr(10)))}</pre></div>
  </div>
  <div class="code"><div class="file">the page</div><pre>{paint_js(CHEAT_JS_PAGE.strip(chr(10)))}</pre></div>
</section>
""")

    tasks = "".join(
        f'<div class="task"><b><span>{i:02d}</span>{name}</b>{text}</div>'
        for i, (name, text) in enumerate(PRACTICE, start=1)
    )
    parts.append(f"""
<section class="practice">
  <p class="topic-num">12</p>
  <h2 style="border-bottom:2px solid var(--ink);padding-bottom:2.5mm;margin-bottom:5mm;">Practice at home</h2>
  <p>Each project uses only what is in these notes. Build them in a new folder with an <code>index.html</code> and a <code>script.js</code>.</p>
  {tasks}
  <p class="last">Pick one, bring it to the next class working, and be ready to explain every line.</p>
</section>
""")

    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        "<title>JavaScript from zero</title>"
        f"<style>{CSS}</style></head><body>{''.join(parts)}</body></html>"
    )


def find_browser():
    for path in BROWSERS:
        if os.path.exists(path):
            return path
    sys.exit("Could not find Chrome or Edge. Install one, or add its path to BROWSERS.")


def main():
    page = build_html()
    browser = find_browser()
    work = Path(tempfile.mkdtemp(prefix="js-handout-"))
    try:
        html_file = work / "handout.html"
        html_file.write_text(page, encoding="utf-8")
        profile = work / "profile"
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={OUT_PDF}",
            html_file.as_uri(),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    if not OUT_PDF.exists():
        sys.exit("The browser ran but no PDF appeared.")
    print(f"Wrote {OUT_PDF.name}  ({OUT_PDF.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
