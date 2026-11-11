---
name: fancy-pants-brief
description: "The house look for every HTML page an agent makes for a person to read: glass over a random Omarchy wallpaper in that wallpaper's theme, always dark, with gel buttons, a rail of sections and plenty of pictures, and never read-only: every section and figure takes a note, with a copy map and Terminal Delight's one-click send-back to the agent. Built with one tool and passed through one gate. Use whenever you are about to write ANY .html a person will open: a report, a review page, a storyboard, a results or status page, an index, a gallery, a comparison, a preview, a handoff page, a dashboard, a demo page; when a tool you are writing generates HTML for people; when a page came out white, plain or flat; when a page has no notes, no copy map, or \"no commentable sections\"; when the user says \"fancy pants\", \"/fancy-pants-brief\", \"make it look nice\", \"the glass look\", \"Omarchy theme\". A decision brief is one of these pages and keeps its own skill, decision-brief, which wears the same look. NOT for HTML that belongs to another design: a product's or client's own site, an email body, a résumé or invoice that leaves as a PDF, or a scene page a film renders frames from."
license: MIT
---

# Fancy Pants brief

Every HTML page an agent makes for a person to read wears one look. A blurred Omarchy
wallpaper sits behind everything, in the colours of the theme it came from. Every surface is
glass, the one thing the reader must not miss is milky lit glass, and the buttons are gel. It is
dark every time, and it is built from pictures more than from paragraphs. People read these pages
for minutes at a time, inside Terminal Delight or a browser, and they should be something good
to look at while they do.

The look was built for decision briefs, and until this skill it lived only inside
`decision-brief`. Pages made any other way, such as film review pages, storyboards, previews
and drafts, were written with their own `<style>`. They painted an opaque ground and came out
flat black or white. Parker, 2026-10-29: *"We're getting white screen plain HTML"*, and then
*"I never want an agent to produce HTML that isn't done in this way."* This skill gives every
other page the same look, and a gate that fails a page without it.

**Every page also takes notes.** A reader comments on any section or figure, copies the map, and
in Terminal Delight sends the notes straight back to the agent's prompt in one click. The look
was half the job: on 2026-11-02 this skill's own `new` produced a Gate 1 mockups page in perfect
glass that nobody could answer. Parker: *"NO commentable sections --- THIS IS TERRIBLE!!!! ALL
BRIEFS MUST HAVE COMMENTABLE SECIONTS AND THE COPY MAP | ONE-CLICK BACK TO AGENT PROMPT (TD
functionality) --- READ ONLY BRIEFS ARE JUST TRASH!!!!"* So `new` now builds through the
`briefing` skill, and the gate fails a read-only page.

## Build the page on the look

The tool is `scripts/fancy-pants`. Run it through `python3` rather than by its bare name, because
some shell sandboxes refuse a bare script.

**A new page** is a brief, and is built by `briefing`. `new` writes `page.src.html`, a source
with a masthead, numbered sections, a figure and `TODO(brief)` where the writing goes. It then
builds `page.html` from that source, with the look and the notes layer:

```bash
python3 ~/.claude/skills/fancy-pants-brief/scripts/fancy-pants new page.html --title "Four showcases, retold" --eyebrow "Cinema Delight · review · 2026-10-29" --purpose summary
```

Write in the **source**, then rebuild and check it:

```bash
python3 ~/.claude/skills/briefing/scripts/brief.py html page.src.html page.html
```
```bash
python3 ~/.claude/skills/briefing/scripts/brief.py check page.html
```

Never edit the built page. A rebuild keeps the reader's notes and refuses to run over a
hand edit. Give every `h2` and `figure` an `id` equal to its `data-brief-anchor`, the way the
skeleton does. The skeleton gives you structure, not content: fill it, delete what the material
does not need, and draw what it does. The shape of the page is still yours.

**A page already built without notes**, by hand or by an older `new`, is converted in place.
`adopt` keeps the page's own CSS, scripts, drawings and wallpaper. It writes the source beside
the page and rebuilds the page as a commentable brief:

```bash
python3 ~/.claude/skills/briefing/scripts/brief.py adopt page.html --purpose decision
```

**A page another program writes** (a review page, an index a script regenerates) puts the
look in its `<head>` before its own CSS:

```bash
python3 ~/.claude/skills/fancy-pants-brief/scripts/fancy-pants head --out /tmp/head.html
```

A tool can also read `decision-brief/assets/base.css` and run `decision-brief/scripts/brief-wall`
itself, as Cinema Delight's `ad.py` and `moments.py` already do. Either way, its output goes
through the gate, and the gate fails it until the generator emits the notes layer as well. The
simplest way to get that is to write a briefing source and run `brief.py html` over it.

**A page that was built without the look** can be dressed in place. The tool adds the look and
then runs the gate, which names whatever in the page's own CSS is still fighting the look:

```bash
python3 ~/.claude/skills/fancy-pants-brief/scripts/fancy-pants dress page.html
```

Fix what it names, or rebuild the page from `new`. Dressing a page does not make it look like
it was designed on the glass.

**A decision brief** is built with `briefing` (purpose `decision`) or `decision-brief`. Both
wear this look, and both add concur stamps and the grill of questions to the notes.

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
  `.gels`. `nav.sections` is a glass panel docked on the right, 35% of the window tall: the reader drags it by its grip, resizes it from a bottom corner, folds it to its title bar (folded by default on a narrow screen) and double-clicks the grip to dock it again, and the wheel over it scrolls only the panel. In briefing builds it also shows visible time beside sections and entries, and stamped items show in green.
  Leave it empty and `assets/sections.js` fills it from the page's `h2`s. A page with three or
  more `h2`s and no rail gets one after its masthead. `section.pane` draws one part of the page as
  its own pane, so the parts separate.

Keep sections short, and give each enough context to stand alone: a reader may open hundreds of agent briefs in a day. Name the subject, make the claim, and put the evidence behind a link. The rail's times come back through `briefing`'s `attention`, which names the passages a reader scrolled past; what to do about each one is in that skill.
- **The masthead**: `header.top` with `.eyebrow`, `h1`, `.lede` and `.stamps`. Below it come
  `h2` with a `.n` number, `h2.sec`, `.cards` with one `.card.rec`, `.tiles`, `.pair` with
  `.facts`, `figure` with `.lbl` and `figcaption`, `video`, `pre`, `.tag`, `.linkbtn` and
  `dialog`.

**Read `decision-brief/reference/glass.md` before drawing.** It says what the look is for and
what makes it work, and it carries two figures worth copying: the chopped bars, and a
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
- **that is read-only**: no `report-notes` island, or no `notes.js`. The fix it names is
  `brief.py adopt`. On a page built by `briefing`, it also fails an `h2` or `figure` with no
  `data-brief-anchor`, because there the anchors are the targets. A `decision-brief` page has no
  anchors to check: `notes.js` tags its sections and figures itself
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

Such a page can declare itself read-only, and must say why:
`<meta name="fancy-pants-read-only" content="a résumé that leaves as a PDF">`. The gate then
prints the reason as a warning instead of failing the page. A declaration with no reason fails.
No brief, review page, plan, mockup or report is one of these.

The page a person reads in order to judge any of these, such as the review page around the film or
the comparison of two résumé drafts, still wears the look.

## Where it lives

The look has one source, `decision-brief/assets/base.css` and `decision-brief/scripts/brief-wall`,
and this skill reads both from the sibling directory. Change the look there and never copy it.
Terminal Delight vendors `decision-brief` byte for byte (its `SOURCE` file names the commit), so
a change to `base.css` reaches the Workbench edition on its next sync. This directory adds only
`assets/sections.js`, the tool, and the tests in `tests/`, which run with
`python3 -m unittest discover fancy-pants-brief/tests`.
