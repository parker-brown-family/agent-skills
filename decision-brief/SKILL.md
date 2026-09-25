---
name: decision-brief
description: Produce a single self-contained HTML brief that Parker annotates in the browser and then prompts back from — an audit, a review, a technology-intake assessment, a findings write-up, any analysis whose point is that a decision gets made. The brief is drawn: hand-built mockups and SVG diagrams carry it and the prose captions them. Reader notes are anchored to elements and export as a token-cheap map, so "read my notes in <file>" replaces pasting the document. Use when asked for an audit, an intake assessment, a review, an analysis, a findings report, a comparison of options, a visual or illustrated write-up, or when Parker says "/decision-brief". NOT for planning docs that end in tickets — that is /tps-report.
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

## Four invariants

Everything else in this skill is a default you may override. These four are not.

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
| **save into file** | downloads the HTML with notes in JSON islands **and** a plain-text comment | localStorage is invisible to an agent; this is what makes the loop work |
| localStorage | live persistence between reloads | |

Every decision in the grill also gets a **concur** space on its right, added by `notes.js`
with no markup from you. Concur is the answer most decisions get and the quickest way for
Parker to say the work was good, so it costs one click: the space shows a grey `?`, throbs
light grey on hover, and takes a green rubber stamp that peels off on a second click. A
concur rides in the map as `[<anchor>] <question>  ✓ concur` and is baked into
`#report-concurs` by save-into-file, so "read my notes" carries agreement as well as
objection. Read a decision with a concur and no note as *approved as recommended*.

Never ship a brief without it.

#### The notes format

Terminal Delight edits a brief's notes in place, so what 💾 save into file writes is a
format another program follows byte for byte. Format 1:

- **Two islands.** `#report-notes` holds `{ anchor: [{text, title, ts}] }`,
  `#report-concurs` holds `{ anchor: ts }`, `ts` in UTC to the minute. The first of each
  is the one read and written. Leave them in the markup, with their `data-format="1"`.
- **Escaping.** Island JSON is `JSON.stringify(map, null, 1)` with `</` written `<\/` and
  `<!` written `\u003c!`, so no note can end the script element. The `READER NOTES`
  comment turns `--!>` into `--! >` and `-->` into `-- >`, and a save replaces the last
  such comment instead of adding another. Its first line and `[anchor] title` lines are
  what agents grep; they do not change.
- **A revision.** Every save stamps `data-rev`, the time of the write, on both islands.
  notes.js remembers the revision it last took in. When a file arrives carrying another
  one, or none, the page shows its stored notes **plus** every note and concur in the file
  it has not seen: a browser never drops a note it holds, and a note the reader deleted
  stays deleted. The price is that a deletion made by another writer does not reach a
  browser that still holds the note.
- **The version.** `data-format` names the format, and a writer refuses one it does not
  know. Bump it when a change alters what a correct writer must put in the file: the
  island shapes or fields, the escaping, where the islands or the mirror go, the mirror's
  lines, or what the revision means. New targets, styling and UI do not bump it.

`fixtures/notes-format/` is the source of truth: fifteen cases, each a brief, its edits
and the exact bytes a correct write leaves, with `writer.mjs` as the reference writer.
Terminal Delight vendors it. Change `notes.js`, `notes.css` or the markup block and the
same commit runs `fixtures/notes-format/build.mjs`, `check.mjs` and
`tests/notes-js.test.mjs` (see the fixtures' README).

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

### 4 · The brief is drawn

Pictures are the medium of this format, and the prose ends up as captions on them. A brief
that could have been an email was not worth the format, and how much of it Parker can *see*
decides whether he reads it or reacts to it.

The 2026-09-15 attention-spine brief carried eleven figures for a plan two earlier prose
briefs had already covered, and it is the standard:
`/home/parker/Work/reports/2026-09-15-attention-spine-groundwork.html`. Mockups of the
surface at the size he would read it, SVG diagrams of the mechanism, an anatomy picture with
numbered pins, a fence, a timeline — all hand-built HTML, CSS and inline SVG, no library, no
image files. **Read `reference/pictures.md` before writing the body**, because the pictures
decide the body.

A brief with a surface in it draws that surface, and a brief with a mechanism in it draws
that mechanism. Where a section's argument really is a list of sentences, leave it as
sentences — a picture of nothing is worse than a paragraph. Everywhere else, when you are
unsure whether to draw one more, draw it.

**When the change touches more than one system, draw the architecture and build it up** —
the same diagram three or four times, each adding a piece, the earlier boxes never moving.
It is the picture Parker asks for by name, and `reference/pictures.md` has the grammar.

## Structure is yours

There are **no section schemas here, deliberately.** The shape comes from the material.

tps-report ships five prescribed schemas and a template you populate; the result is that the
agent picks a schema instead of designing a document. Do not do that here.

Decide the shape by answering these, and let the answers build the page:

- What is the single sentence he needs if he reads nothing else? → that is the headline, and
  it goes first.
- What must he **see** to judge this — a surface, a flow, an order, a boundary? → a figure
  each, and the caption carries the claim. Answer this before you answer the rest; a section
  built around a picture is shaped differently from one built around paragraphs.
- What are the top five things he must look at closely? → Read-first.
- Are there **things being compared**? → some card or tile per thing. Not otherwise.
- Is there **one number** that carries an argument? → a chart, or a stat row. One good chart
  beats four. If nothing is worth plotting, plot nothing.
- What would he ask *"why?"* about? → a modal per answer.
- What decisions are actually his? → a section that asks them, with your recommendation
  attached to each.

Skip any of these that the material does not support. A brief with three sections that
earn their place beats one with eight that fill a template.

## The look

Every brief is built over a random Omarchy wallpaper, in the colours of that wallpaper's
theme, with the glass of the Terminal Delight docs redesign. **Read `reference/glass.md`
before drawing anything**: it says what the look is for, what makes it work, and carries
the two examples Parker singled out (chopped bars, and a readout that shows two numbers at
once). It describes rather than prescribes; the shape of each brief is still yours.

Four blocks go in `<head>`, in this order:

1. `assets/base.css`, inline.
2. The `<style id="brief-wall">` block, straight after it. One run per brief picks a theme,
   then one of its wallpapers, and bakes both in:
   ```bash
   python3 ~/.claude/skills/decision-brief/scripts/brief-wall --out /tmp/brief-wall.html
   ```
   Run it through `python3`; the lean-ctx shell gate refuses the bare script name. It adds
   4–335 KB. Take the random pick, and never choose a theme to match the subject; the
   variety is the point. `--theme` and `--image` exist so a rebuild keeps the wallpaper it
   already has: the block's opening comment names the theme, the wallpaper and the
   contrast it measured.
3. The brief's own `<style>`.
4. `assets/notes.css`.

**Use what `base.css` styles instead of restyling it.** The masthead (`header.top`,
`.eyebrow`, `h1`, `.lede`, `.stamps`), `h2` with a `.n` number, `h2.sec`, `.esc-list`,
`.tiles`, `.cards` with one `.card.rec`, `.finding`, `.grill .ask` with `.rec`, `figure`,
`.pair` with `.facts`, `pre`, `table`, `.callout`, `.tag`, `.linkbtn` and `dialog` are all
done. `base.css` sits in `@layer brief`, so the brief's own CSS always wins, and a component
restyled from an older brief (`background: var(--surface-1)`) replaces its glass with a flat
box. Build what the material needs beyond that list.

**`.glass` is the milky, lit card**: bright glass with dark ink, the element the reader must
not miss. Put the headline verdict in it, and use one or two per page at most.

Colours: the theme owns the ground, the ink and the accent (`--bg`, `--fg`, `--dim`, `--acc`
and the rest of the kiosk role names). The status and categorical colours are fixed in every
theme, so red always means a decision is waiting. Figures colour themselves with classes;
see `reference/pictures.md`.

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
// every svg scales and is described — [hasViewBox, noFixedWidth, hasLabel]
// (an aria-hidden svg is decoration, like a readout's plate, and needs no label)
[...document.querySelectorAll('svg:not([aria-hidden="true"])')].map(s =>
  [!!s.getAttribute('viewBox'), !s.getAttribute('width'), !!s.getAttribute('aria-label')])
// notes COVERAGE — never a bare count. [selector, present, tagged]; present > tagged is a defect
// (tbody, not tr: notes.js skips header rows on purpose, and a check that cries wolf gets ignored)
['.grill .ask, .grill .q, .grill-q', 'figure', '.card', '.finding', '.tile',
 '.esc-list li', 'table.wide tbody tr', '.callout'].map(s => [s,
  document.querySelectorAll(s).length,
  [...document.querySelectorAll(s)].filter(e => e.classList.contains('notable')).length])
// the wallpaper is baked in — empty means the brief-wall block is missing, and the page is
// quietly wearing the fallback glow
getComputedStyle(document.documentElement).getPropertyValue('--wall-label')
```

**A count is not coverage.** `document.querySelectorAll('.notable').length` returning 52 says
nothing about *which* 52, and two briefs shipped with grills nobody could comment on while that
check passed. The grill row is the one to read first: a section asking for a decision that cannot
carry a note has failed at the only job the document has.

Then add a note **on a grill item**, export the map, and confirm the anchors are readable. A map
full of `finding-one-standing-rule-is-wrong-but-the-stack-aro` is a broken map.

Serve it over `http://127.0.0.1:<port>` rather than `file://` — browser automation refuses
`file://`, and the served URL is a second clickable row in the Links table.

## Traps

Named from the tps-report post-mortem, because these are the ways this goes wrong:

- **No theme toggle.** One design, and the palette is never the reader's choice: brief-wall
  picks it when the brief is built. tps-report had four themes, 165 theme rules and a
  switcher nobody used.
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

- `reference/pictures.md` — **read this first**: the figure contract, the repertoire of
  eleven, what colour means, and how to say which parts of a drawing were guessed
- `reference/glass.md` — the look: what it is for, what makes it work, and two examples
- `reference/layout.md` — the disclosure ladder, and which components earn their place
- `reference/evidence.md` — confidence labels, invalidation criteria, recording confounds
- `reference/notes-markup.html` — the markup block the notes system needs
- `scripts/brief-wall` — picks the wallpaper and the palette, measures the contrast, and
  prints the block that follows `base.css`; its docstring says how
- `fixtures/notes-format/README.md` — the notes format in bytes, the cases that pin it,
  and how to run them
