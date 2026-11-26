---
name: web-ux
description: "How a web page should behave, as rules you can test: nothing moves under the reader while they type or read, search finds what a person would actually type, dense results arrive organised, and the keyboard works without the mouse. Each rule names the failure that earned it and the check that catches it, including a script that measures whether an overlay holds still. Use when building or reviewing any interactive web surface — a search box or command palette, a dialog, a results list, a reader, a dashboard, a private project site — and when someone says it \"jumps around\", \"is too snappy\", \"can't find X\", \"is too dense\", \"needs keyboard nav\", \"web UX\", or \"/web-ux\". For how it looks (colour, type, spacing, depth, motion timings), use design-language; this skill is how it acts."
license: MIT
---

# Web UX: how a page behaves

`design-language` decides how a surface looks. This skill decides what it does when someone uses it. Every rule here is a
sentence a script or a reviewer can check, and each one comes from a failure that actually shipped. Read the rules
before building an interactive surface. Before handing it over, run the checks at the bottom.

## 1. Hold still

**H1. An overlay opens where it will sit when it is full.** A dialog, palette or popover that grows with its content is
anchored at the top (`margin: 9vh auto auto`), never centred. Its results grow downward and scroll inside it. A centred
modal re-centres on every keystroke that changes the result count, so the input jumps under the cursor. *Specimen:* a
search dialog whose results went from 0 to 5 to 30 as the reader typed was called "a bit TOO snappy … it jumps around".
Measured, its input sat at 421 px with the box empty and jumped to 115 px on the first letter. Pinned at the top, the input stayed at 104 px through every query.

**H2. Fast is good; moving is not.** Respond on every keystroke, but keep everything already on screen where it was. Space
that will be filled (an image, a count, a results area) is reserved before it fills.

**H3. Background layers never depend on foreground code by accident.** A page that runs as one script shares one scope. Two
`function pick` declarations in the same IIFE hoist, and the later one wins silently: a search feature's `pick` replaced the
wallpaper's, and the wallpaper vanished from every page. Give every function in a shared scope a unique name, and keep a
test that fails on a duplicate declaration (`scripts/dup-functions.sh`).

## 2. Find what a person types

**F1. Index what the reader will search for, not what we wrote about it.** A reading shelf indexed only our one-line note
on each paper, so a search for the university that wrote a paper ("peking") found nothing. Index the title, every
author, the affiliations (from the document's first page when the metadata lacks them) and the abstract. Then test it with
the search a person actually made.

**F2. Never truncate silently.** A per-section cap on indexed text (1,500 characters) cut off most of a long list. Raise
the cap until almost nothing is cut, and measure it: count the entries that hit the cap. When the results are capped, say
so: "185 results, the best 30 shown".

**F3. "Nothing matches" must be true.** It means nothing on the site contains the words, never that the index missed it.
When a search a person reports fails, the fix is in the index, not in how they searched.

## 3. Dense results arrive organised

**O1. One card per result, grouped by where it lives.** Under a page or source label with a count, each card shows its
title, a meta line (author, id, date, size), and at most two excerpts.

**O2. Excerpts are cut around the match**, not from the start of the text: windows around each matched word, merged when
they overlap, snapped to word boundaries, with an ellipsis where they were cut. Strip noise a reader cannot use (URLs,
emails, stamps) before excerpting.

**O3. Mark every searched word** in titles and excerpts, in the accent colour at about 30%, with readable ink on top.

**O4. Build results as text, never as HTML.** Use text nodes and `<mark>` elements. A title or excerpt is data, and
`innerHTML` makes it code.

**O5. Clean what the source encodes.** LaTeX in a title (`$\{\pm1, \pm i\}$`) reads `{±1, ±i}` on the card.

## 4. The keyboard does everything

**K1. Focus stays in the input.** Arrow keys move a highlight through the results while the reader keeps typing. Page
Up/Down moves five. Enter opens the highlighted result. The first result is highlighted from the start.

**K2. Number what can be jumped to.** Show the shortcut on each card (`Alt 1` to `Alt 9`), and make it work from the
input. A bare digit there is typing, so the shortcut needs a modifier.

**K3. Show the keys once, in one line**, beside the result count: `↑ ↓ move · Enter opens · Alt+1–9 opens that card`.

**K4. Opening a result closes the overlay.** A same-page anchor link otherwise leaves the dialog sitting over the place it
just scrolled to. Esc closes, and the shortcut that opened it opens it again, empty.

**K5. Pointer and keyboard agree.** Hovering a card moves the same highlight without scrolling it.

## Check before handing over

Run checks headless (Playwright against a local preview), never on someone's live desktop: focus changes and key
presses there interrupt whoever is typing.

```bash
node scripts/hold-still.mjs http://localhost:8799/ --open Control+k --input '#q' --box '#find' --type 'p,pe,peking,the'
```

It prints the input's and the box's top edge for each query and exits 1 if either moved by more than one pixel. Run it at
desktop and phone width (`--width 390 --height 800`).

```bash
scripts/dup-functions.sh src/app.js
```

It exits 1 and names any function declared twice in a file.

Then do by hand what no script proves: search for the thing a person last failed to find, read the first card aloud, and
reach the third result with the keyboard alone.

## Traps

- `pgrep -f`/`pkill -f` with a pattern that also appears in your own command line matches your own shell. Bracket one
  letter (`"[w]rangler"`).
- A dialog's default `max-width`/`max-height` and an inherited `li { max-width: 68ch }` make cards stop short of the
  dialog's edge. Reset both inside the results list.
