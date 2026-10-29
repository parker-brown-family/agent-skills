---
name: fancy-pants-brief
description: "The house look for every HTML page an agent makes for a person to read: glass over a random Omarchy wallpaper in that wallpaper's theme, always dark, with gel buttons, a rail of sections and plenty of pictures, built with one tool and passed through one gate. Use whenever you are about to write ANY .html a person will open: a report, a review page, a storyboard, a results or status page, an index, a gallery, a comparison, a preview, a handoff page, a dashboard, a demo page; when a tool you are writing generates HTML for people; when a page came out white, plain or flat; when Parker says \"fancy pants\", \"/fancy-pants-brief\", \"make it look nice\", \"the glass look\", \"Omarchy theme\". A decision brief is one of these pages and keeps its own skill, decision-brief, which wears the same look. NOT for HTML that belongs to another design: a product's or client's own site, an email body, a résumé or invoice that leaves as a PDF, or a scene page a film renders frames from."
license: MIT
---

# Fancy Pants brief

Every HTML page an agent makes for Parker to read wears one look. A blurred Omarchy
wallpaper sits behind everything, in the colours of the theme it came from. Every surface is
glass, the one thing the reader must not miss is milky lit glass, and the buttons are gel. It is
dark every time, and it is built from pictures more than from paragraphs. He reads these pages
for minutes at a time, inside Terminal Delight or a browser, and they should be something good
to look at while he does.

The look was built for decision briefs, and until this skill it lived only inside
`decision-brief`. Pages made any other way, such as film review pages, storyboards, previews
and drafts, were written with their own `<style>`. They painted an opaque ground and came out
flat black or white. Parker, 2026-10-29: *"We're getting white screen plain HTML"*, and then
*"I never want an agent to produce HTML that isn't done in this way."* This skill gives every
other page the same look, and a gate that fails a page without it.

## Build the page on the look

The tool is `scripts/fancy-pants`. Run it through `python3`, because the lean-ctx shell gate
refuses a bare script name.

**A new page** starts from a page that already has the look, a masthead, an empty rail of
sections, one milky card and one pane:

```bash
python3 ~/.claude/skills/fancy-pants-brief/scripts/fancy-pants new page.html --title "Four showcases, retold" --eyebrow "Cinema Delight · review · 2026-10-29"
```

The skeleton gives you structure, not content. Fill it, delete what the material does not
need, and draw what it does. The shape of the page is still yours.

**A page another program writes** (a review page, an index a script regenerates) puts the
look in its `<head>` before its own CSS:

```bash
python3 ~/.claude/skills/fancy-pants-brief/scripts/fancy-pants head --out /tmp/head.html
```

A tool can also read `decision-brief/assets/base.css` and run `decision-brief/scripts/brief-wall`
itself, as Cinema Delight's `ad.py` and `moments.py` already do. Either way, its output goes
through the gate.

**A page that was built without the look** can be dressed in place. The tool adds the look and
then runs the gate, which names whatever in the page's own CSS is still fighting the look:

```bash
python3 ~/.claude/skills/fancy-pants-brief/scripts/fancy-pants dress page.html
```

Fix what it names, or rebuild the page from `new`. Dressing a page does not make it look like
it was designed on the glass.

**A decision brief** is built with `decision-brief`. It wears this look and adds reader notes,
concur stamps and the grill of questions.

## What the look already gives you

`decision-brief/assets/base.css` styles all of the following. Use the components rather than
restyling them. The stylesheet sits in `@layer brief`, so your CSS always wins, and a component
restyled with `background: var(--surface-1)` loses its glass and becomes a flat box.

- **The wall.** Nothing to add. `body::before` carries the wallpaper under the theme's scrim, and
  `body::after` carries the scanlines.
- **Glass** on `.panel`, `.card`, `.finding`, `.tile`, `.callout`, `.facts`, `table`, `figure`,
  `blockquote`, `.stamp`, `dialog`.
- **`.glass`**, the milky card with bright glass and dark ink. Put the headline in it, and use
  one or two per page. A page full of them has no headline.
- **Gel.** `.gel` makes a button or a link look wet on top and glow underneath; a row of them goes in
  `.gels`. `nav.sections` is a rail of gel buttons that stays at the top as the reader scrolls.
  Leave it empty and `assets/sections.js` fills it from the page's `h2`s. A page with three or
  more `h2`s and no rail gets one after its masthead. `section.pane` draws one part of the page as
  its own pane, so the parts separate.
- **The masthead**: `header.top` with `.eyebrow`, `h1`, `.lede` and `.stamps`. Below it come
  `h2` with a `.n` number, `h2.sec`, `.cards` with one `.card.rec`, `.tiles`, `.pair` with
  `.facts`, `figure` with `.lbl` and `figcaption`, `video`, `pre`, `.tag`, `.linkbtn` and
  `dialog`.

**Read `decision-brief/reference/glass.md` before drawing.** It says what the look is for and
what makes it work, and it carries the two figures Parker singled out: the chopped bars, and a
readout that shows two numbers at once. Read `decision-brief/reference/pictures.md` for how
figures colour themselves. A page in this look is drawn. Mockups, SVG diagrams and readouts
carry it, and the prose captions them. A page that is all sentences has missed the point even
when it passes the gate.

## Dark, always

`brief-wall` picks a random Omarchy theme and one of its wallpapers. When the theme is light, it
turns it dark: the ink becomes the ground and the paper becomes the ink. It also lightens the ink
until body text clears 7:1 over the brightest tenth of the wallpaper. Take the random pick, and
never choose a theme to match the subject; the variety is the point. `--theme` and `--image`
exist so that a rebuild keeps the wallpaper a page already has.

Three things in a page's own CSS undo all of that, and the gate fails each one:

- **Painting the ground.** `body`, `main` or `.wrap` with an opaque `background` covers the
  wallpaper. The wall is the ground.
- **Taking over the theme's colours.** `:root { --bg: … }` replaces the wallpaper's palette.
  `brief-wall` owns `--bg --bg2 --bg0 --fg --fg2 --fgb --acc --mut --sel --dim`, the six
  chromatic roles, `--wall` and `--scrim`. Give the page's own colours other names.
- **Asking for light.** A `color-scheme` that includes `light`.

A `@media print` block is exempt, because paper is white.

## One file

Everything is inline: the CSS, the script and the wallpaper, which is baked in as a data URI.
The page must survive being mailed as one file, so a CDN font, a stylesheet or script from the
network, or an `@import` fails the gate. A local `<video src="film.mp4">` beside the page is
fine, because a review page embeds the films it reviews.

## The gate

```bash
python3 ~/.claude/skills/fancy-pants-brief/scripts/fancy-pants check page.html
```

It reads the page's own CSS, ignoring the look's blocks, then photographs the page in headless
Chromium at 1280 × 1800 and measures it. It fails a page:

- that has no `base.css`
- that has no wallpaper
- that paints the ground, takes over the theme's colours, or asks for light
- that loads anything from the network
- whose photograph has a mean luminance above 120 of 255

The glass briefs measure 36–49 and a white page measures 249. It warns, without failing, on
literal light backgrounds and on network images. Exit status 1 means a page failed. Run it
before handing a page over, then open the page in Terminal Delight and look at it. The gate
cannot tell an ugly page from a beautiful one. It only tells a page in the look from a page
outside it.

## When this does not apply

- **A product's or a client's own site**, in its own repository with its own design system. Its
  design wins.
- **An email body.** Mail clients strip most of this.
- **A document that leaves as print or PDF for someone else**, such as a résumé, an invoice or a
  cover letter. Those have their own templates.
- **A scene page a film renders frames from.** The film's own look rules there.

The page Parker reads in order to judge any of these, such as the review page around the film or
the comparison of two résumé drafts, still wears the look.

## Where it lives

The look has one source, `decision-brief/assets/base.css` and `decision-brief/scripts/brief-wall`,
and this skill reads both from the sibling directory. Change the look there and never copy it.
Terminal Delight vendors `decision-brief` byte for byte (its `SOURCE` file names the commit), so
a change to `base.css` reaches the Workbench edition on its next sync. This directory adds only
`assets/sections.js`, the tool, and the tests in `tests/`, which run with
`python3 -m unittest discover fancy-pants-brief/tests`.
