---
name: web-ux
description: "How a web page should behave, as rules you can test: nothing moves under the reader while they type or read, search finds what a person would actually type, dense results arrive organised, the keyboard works without the mouse from the moment anything opens, a page turn lands on the page it names, a page switch changes the page but never the ground behind it, and a document shown inside a themed site wears the theme with the original one click away. Each rule names the failure that earned it and the check that catches it, including scripts that measure whether an overlay holds still, whether its keys work the moment it opens, and what a page switch looks like frame by frame. Use when building or reviewing any interactive web surface — a search box or command palette, a dialog, a results list, a reader, a dashboard, a private project site — and when someone says it \"jumps around\", \"is too snappy\", \"snaps\" or \"throbs\" between pages, the wallpaper or background \"keeps changing\", view transitions, \"can't find X\", \"is too dense\", \"needs keyboard nav\", \"the arrow keys do nothing\", a PDF or document reader, a PDF that \"looks too white\" in a dark theme, keyboard shortcuts, \"web UX\", or \"/web-ux\". For how it looks (colour, type, spacing, depth, motion timings), use design-language; this skill is how it acts."
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

**H4. A layer drawn over the page never takes the page's input.** An effect laid over the content (a CRT bend, a
canvas, a glass sheen) passes every click through to what is under it, mapped through any distortion it draws, and the
page under it stays see-through while the layer waits for its first frame, so the page never flashes flat in between.
Where the effect cannot run (no WebGL2, a page taller than the GPU's largest texture, a narrow screen), a flat stand-in
takes its place and the page still works.

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

**O6. What the reader reaches for is open; the rest is folded, with a count.** A list that mixes the reader's own items
with other people's leads with theirs and puts the rest in a closed `<details>` that says how many it holds. *Specimen:* a
repositories flyout listed eight other people's repositories open beneath ours, and the flyout grew long when the ones
reached for are ours. Opening the fold must not close the flyout that holds it.

## 4. The keyboard does everything

**K1. Focus stays in the input.** Arrow keys move a highlight through the results while the reader keeps typing. Page
Up/Down moves five. Enter opens the highlighted result. The first result is highlighted from the start.

**K2. Number what can be jumped to.** Show the shortcut on each card (`Alt 1` to `Alt 9`), and make it work from the
input. A bare digit there is typing, so the shortcut needs a modifier.

**K3. Show the keys once, in one line**, beside the result count: `↑ ↓ move · Enter opens · Alt+1–9 opens that card`.

**K4. Opening a result closes the overlay.** A same-page anchor link otherwise leaves the dialog sitting over the place it
just scrolled to. Esc closes, and the shortcut that opened it opens it again, empty.

**K5. Pointer and keyboard agree.** Hovering a card moves the same highlight without scrolling it.

**K6. Whatever opens takes the focus, and gives it back.** An overlay with no input of its own (a reader, a viewer, a
lightbox) makes its scroller focusable (`tabindex="-1"`, no outline) and focuses it on open; Esc returns focus to the
control that opened it. *Specimen:* with a paper open in a PDF reader, "the arrow key navigation is shut down". Focus had
stayed on the shelf button hidden behind the reader, and the body's `overflow: hidden` left Up and Down nothing to scroll.
Handle the overlay's keys wherever focus sits inside it, except in its own text fields and under Ctrl, Alt or Meta.

**K7. A page turn lands on the page it names.** When a key turns the page with a smooth scroll, record where the scroll is
headed, and keep the scroll watcher from recomputing the current page until the scroll ends there (`scrollend`, with a
fallback of about 1.5 s). Otherwise a second press mid-scroll leaves the page number and the position disagreeing. Jump
instantly when the distance is more than a few screens. When the scroller is at the bottom, the current page is the
last, because a short last page never reaches the middle of the view.

**K8. Single keys for a site you read; they rest while anything else wants the keys.** A reading site earns one-key
shortcuts (`/` search, `[` `]` turn, `j` `k` sections, `?` the sheet of every key) and lists them all on the `?` sheet.
They do nothing while focus is in a text field, under a modifier, or while an overlay with keys of its own is open. A
site built on another site's shell brings that shell's keys with it, or the reader's habits from the first site fail on
the second.

## 5. Pages change; the ground does not

**M1. A page switch never puts the page behind anything.** In a cross-document view transition (`@view-transition {
navigation: auto }`), every element with a `view-transition-name` becomes its own group, drawn *above* the root
snapshot. Name a full-screen background and it covers the page for the whole of its animation; when that ends, the live
page is drawn again at full strength and the text snaps forward. *Specimen:* a wallpaper named with a 1.1 s fade, over a
0.55 s page fade, read as "a slow fade in and a snap… the snap needs to be much smoother". Leave background layers
unnamed so they fade inside the root snapshot. Do not push a named background under the page with `z-index: -1`
instead: the root snapshot carries the canvas's opaque ground, so the background vanishes for the whole switch and pops in
at the end, a snap of its own.

**M2. An ambient layer is a setting, not content.** A wallpaper, a tint or a drifting backdrop does not change because
the reader moved to another page or scrolled past a section heading. It changes only when the reader acts on it: a picker,
or a deliberate reload. *Specimen:* a "Flow" mode that swapped the painting by section and by page was judged against
"a big refresh, not switching between sections, headings or otherwise navigating should change the wallpaper". Keep what
is on screen in `localStorage`. Read `performance.getEntriesByType('navigation')[0].type`: on `reload` choose anew, and on
`navigate` or `back_forward` put the same layer straight back with its transition switched off for that one frame. Run
its slow animation on the clock (`animation-delay: -(Date.now() / 1000 % period)s`) so it carries on across pages
instead of restarting.

**M3. What changes slowly does so on purpose.** A background that fades up from black on every page load reads as a throb
behind the text. Fade only when something new was chosen, and then slowly: about 4 s for a full-screen painting, eased in
and out.

## 6. A document shown inside the site wears the site

**D1. A PDF opened in a themed site takes the theme, and the original is one click away.** A dark, glassy site that
opens every paper as a white page drops a white slab in front of the reader ("the PDF colors are too white"). Eight
treatments were rendered from real pages and compared; the one chosen flips each colour's lightness into the theme's
ground-to-ink range and keeps its hue, so a diagram's colour coding survives, and puts photographs back as printed. The
built-in alternatives fail on colour: PDF.js `pageColors` and every "night mode" that maps to one ink and one ground turn
each figure and photo grey, and inverting turns photos into negatives. A Paper button prints the pages white again and
is remembered per device; Download is always the original file. In a light look, multiply the page by the theme's paper
colour instead.

**D2. Recolour on the graphics card, never per pixel per page.** A JavaScript pass over the pixels costs 50–115 ms a page,
and a reader that draws every page on open pays it for every page. An SVG filter on the page canvas does the same work
for nothing: `feColorMatrix` invert, `hueRotate 180`, alpha from the inverted lightness (paper 0.65, ink 1.0, for glass),
then `feComponentTransfer` stretched onto the theme's ground and ink. Rebuild the filter whenever the theme repaints. For
photos, render with PDF.js `recordImages: true`: `page.imageCoordinates` then holds six numbers per image, three corners
as fractions of the canvas, recorded once on the first render and unrotated. Copy those rectangles from the unfiltered
canvas onto a layer above it, rotated to match.

**D3. Marks drawn on a recoloured page change how they blend.** A highlighter that multiplies shows on white and vanishes
on a dark page; there it screens. Ink chosen for paper (near-black) draws in the theme's ink. Decide at draw time, so the
stored marks never change and switching back to Paper shows them as they were made.

**D4. Measure contrast on the live surface, for every theme and every background.** A mock-up of a see-through page
measured 4.2 : 1 over a bright painting; the built reader, where its own dimming layer sits under the glass, measured
8.7 : 1 at worst across five themes and seven wallpapers. Only the live number decides. Sample the ground beside the text
in a headless screenshot and compute it against the theme's ink.

**D6. A cited source opens on the page, and its origin stays in plain sight.** A source list of outbound links sends
the reader to someone else's site at the moment they wanted to check a claim, and most of them do not come back. Make the
citation's main link open the source as a PDF in a dialog on the page, about four-fifths of the window (nearly all of a
phone), with the original source and a download one click away in the dialog's header. Under each entry in the list,
print the origin in italics as an ordinary visible link (*Source: pubmed.ncbi.nlm.nih.gov/…*), so the credit and the
backlink are never hidden behind the dialog. Without JavaScript the main link's `href` is the PDF itself. Host a
source's own PDF only where its licence allows a copy on your site (CC BY, CC0, public domain; *not* non-commercial
licences on a business's site, and never a paywalled publisher PDF). For everything else, generate a short PDF of your own:
what the source is, what you took from it, the exact lines you quoted, and where to read it, labelled as your summary.
The dialog follows K6 (focus in on open, back to the link on close, Esc and the backdrop close it), H1 (every page's box
is sized before it is drawn, so nothing moves while pages render) and a scroll lock on the page behind.

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

```bash
node scripts/page-switch.mjs http://localhost:8799/ideas/ --click 'nav a[href="/hypotheses/"]' --layer '.wall i' --out /tmp/switch
```

It clicks through to another page, scrolls, then reloads, and prints which background layer is showing after each. It
exits 1 if the background changed on the switch or the scroll. It also records the screen as frames, with every
`animation-duration` slowed tenfold (`--slow`), so you can look for the snap yourself. Lay the frames out in a contact sheet
and read them in order: through the switch the text should never sit behind the background.

```bash
node scripts/overlay-keys.mjs http://localhost:8799/library/ --click '.book button.gel' --box '#rd-box' --scroller '#rd-scroll' --next ArrowRight --target '.rd-wrap:nth-of-type(2)' --offset 18
```

It clicks the opener and checks that focus is inside the overlay, that ↓ scrolls it, that → comes to rest on the next
page, and that Esc puts focus back on the opener (rules K6 and K7). It exits 1 on any failure. Checked against a
reader before and after the K6 fix: the old build exits 1 (focus on the button behind it, ↓ scrolls 0 px), the new one 0.

Then do by hand what no script proves: search for the thing a person last failed to find, read the first card aloud, and
reach the third result with the keyboard alone. Open every overlay with a click and press ↓ without touching the mouse
again: if nothing scrolls, focus was left behind it. In a paged reader, press → twice quickly and check that the page
number and the page on screen agree.

## Traps

- `pgrep -f`/`pkill -f` with a pattern that also appears in your own command line matches your own shell. Bracket one
  letter (`"[w]rangler"`).
- Playwright's default headless shell draws nothing during a view transition: every frame and screenshot is the blank
  ground, so a snap is invisible to it. Launch full Chromium with software GL (`channel: 'chromium'`,
  `--use-angle=swiftshader --enable-unsafe-swiftshader --enable-gpu`) and record with the CDP screencast;
  `page.screenshot` also stalls mid-transition.
- Two `wrangler dev` servers on one machine collide on an internal socket as well as on `--port` ("Address already in use
  (socket direct:1:default)"). Give the second its own `--inspector-port`.
- Two agents in one working tree share one git index. Staging your own hunks with `git update-index` while another agent
  commits puts your change into their commit. Say before you stage, or work in a separate worktree.
- Killing `workerd` by name stops every local Cloudflare preview on the machine, other agents' included. Stop your own
  `wrangler dev` by its port (`pkill -f "[w]rangler@4 dev --port 8799"`).
- Smooth scrolling over a reader's large canvases can take well over a second in headless Chromium. Wait for `scrollend`
  or a generous timeout before reading the position, or a correct page turn reads as a failure.
- Drawing a canvas that has transparent pixels (made with `willReadFrequently`) onto another canvas wiped what was beneath
  instead of blending over it, in headless Chromium. `drawImage(await createImageBitmap(src, x, y, w, h), …)` blends.
- A dialog's default `max-width`/`max-height` and an inherited `li { max-width: 68ch }` make cards stop short of the
  dialog's edge. Reset both inside the results list.
