---
name: decision-brief
description: Produce a single self-contained HTML brief that Parker annotates in the browser and then prompts back from — an audit, a review, a technology-intake assessment, a findings write-up, any analysis whose point is that a decision gets made. Reader notes are anchored to elements and export as a token-cheap map, so "read my notes in <file>" replaces pasting the document. Use when asked for an audit, an intake assessment, a review, an analysis, a findings report, a comparison of options, or when Parker says "/decision-brief". NOT for planning docs that end in tickets — that is /tps-report.
license: MIT
---

# Decision brief

A brief exists to get a decision made by someone with less time than the material deserves.
Everything below serves that.

**The loop this skill exists for:**

```
you write the brief  →  Parker annotates it in the browser  →  💾 save into file
                     →  "read my notes in <file>"           →  you act on the notes
```

That loop is the reason for the notes system. Without it a report is a dead end: he reads it,
forms opinions, and then has to retype them into a prompt.

## Three invariants

Everything else in this skill is a default you may override. These three are not.

### 1 · Notes on every element

Copy `assets/notes.js`, `assets/notes.css` and the markup block from
`reference/notes-markup.html` into the file. Inline them — a brief must survive being
emailed as one file, so no external `src`.

> **Inlining trap.** An HTML parser ends a `<script>` element at the first literal closing
> script tag it sees — including one inside a JS comment or string. If any lands in the JS
> you inline, everything after it silently becomes page content and the notes system never
> runs, with **no console error**. This bit the first brief built from this skill: the
> smoke test loaded the JS with `src` and passed; the real brief inlined it and broke.
> After assembling, verify with `document.querySelectorAll('.notable').length` — zero
> means you hit this.

`notes.js` tags elements itself and gives each a stable anchor id. Three outputs:

| Output | What it does | Why |
|---|---|---|
| **copy map** | `[anchor] Title` + notes, in document order | ~1% of the tokens of the full document, and still tethered to the passage |
| **save into file** | downloads the HTML with notes in a JSON island **and** a plain-text comment | localStorage is invisible to an agent; this is what makes the loop work |
| localStorage | live persistence between reloads | |

Never ship a brief without it.

### 2 · The reading budget drives the structure

Ask, or infer: *how long does he have?* One hour to decide means roughly twenty minutes to
read. Then build to that number.

The consequence is **progressive disclosure**: the main page is the brief; depth lives in
modals. A reader who stops at the bottom of the page must already have enough to decide.
A reader with more time opens the sub-reports.

The **Read-first block** is where the budget bites. Ranked items, **hard cap of five**, each
one three lines: *what it is · why it matters · what it would take.* The cap is load-bearing —
at seven it becomes a list nobody finishes and the ranking stops meaning anything. If
something is sixth, it goes in the body and waits its turn.

### 3 · Every claim carries its confidence

`measured` · `inferred` · `hunch` · `contradicted`. The `.tag` classes in `base.css` render them.
A claim you have not tested is not a finding, and saying so costs nothing.

Anything you assert as a defect also carries an **invalidation criterion**: the check that
would prove it wrong, which the picker-upper runs *first*. See `reference/evidence.md`.

## Structure is yours

There are **no section schemas here, deliberately.** The shape comes from the material.

tps-report ships five prescribed schemas and a template you populate; the result is that the
agent picks a schema instead of designing a document. Do not do that here.

Decide the shape by answering these, and let the answers build the page:

- What is the single sentence he needs if he reads nothing else? → that is the headline, and
  it goes first.
- What are the top five things he must look at closely? → Read-first.
- Are there **things being compared**? → some card or tile per thing. Not otherwise.
- Is there **one number** that carries an argument? → a chart, or a stat row. One good chart
  beats four. If nothing is worth plotting, plot nothing.
- What would he ask *"why?"* about? → a modal per answer.
- What decisions are actually his? → a section that asks them, with your recommendation
  attached to each.

Skip any of these that the material does not support. A brief with three sections that
earn their place beats one with eight that fill a template.

## Verify before you deliver

Screenshots lie — they crop, and they return blank frames at deep scroll positions. **Check the
DOM**, then look at it:

```js
// horizontal overflow — the most common silent break
document.documentElement.scrollWidth > document.documentElement.clientWidth
// every modal trigger resolves
[...document.querySelectorAll('[data-dlg]')].filter(b => !document.getElementById(b.dataset.dlg))
// every dialog actually has content
[...document.querySelectorAll('dialog')].map(d => [d.id, d.querySelector('.dlg-body')?.innerText.length])
// notes wired
document.querySelectorAll('.notable').length
```

Then add a note, export the map, and confirm the anchors are readable. A map full of
`finding-one-standing-rule-is-wrong-but-the-stack-aro` is a broken map.

Serve it over `http://127.0.0.1:<port>` rather than `file://` — browser automation refuses
`file://`, and the served URL is a second clickable row in the Links table.

## Traps

Named from the tps-report post-mortem, because these are the ways this goes wrong:

- **No theme system.** One palette. tps-report has four themes and 165 theme rules; nobody
  switches. Style is not where the value is.
- **No template to populate.** Ship components and constraints. The moment there is a
  `body.html` with slots, the agent stops designing.
- **No prescribed sections.** See above.
- **Do not explain a title with a subtitle.** "Tokens", not "Tokens — what they are and why
  one of our rules is wrong". The gloss breaks the heading.
- **Do not announce honesty.** "stated honestly", "the honest position". Serious material
  already reads as serious; use a confidence label instead.
- **No superlatives about things you have not exhaustively tested.** "the single best thing in
  this repo" tells the reader to stop looking, which is worse than saying nothing.
- **Long prose sections belong in a modal.** If a section runs past a screen or two on the
  main page, it is competing with the brief. Move it and leave a one-line entry point.
- The full writing rules live in `~/.claude/writing/house-style.md` and the
  `avoid-ai-writing` skill. Run that skill as a final pass.

## Deliver

Write to a `reports/` directory in the relevant project, named
`<YYYY-MM-DD>-<topic-slug>.html` — never date-only, since several agents may tie off the same
project on the same day.

Send the file with `SendUserFile`, and end with the Links table: the brief first, the served
URL second.

## Reference

- `reference/layout.md` — the disclosure ladder, and which components earn their place
- `reference/evidence.md` — confidence labels, invalidation criteria, recording confounds
- `reference/notes-markup.html` — the markup block the notes system needs
