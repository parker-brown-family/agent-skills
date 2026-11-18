# Type: four rules, and the example that tested them

A family's type is three decisions and one chore. Make the decisions per role, not per screen,
and do the chore from the font files themselves.

## The rules

1. **A display face for the frame.** The frame is the words the product ships: the wordmark, tab
   names, eyebrows, section and page titles. List those roles (`FRAME_ROLES` in the family file)
   and give the display face to nothing else. A string that came from a person or a record, such
   as a client's name or an appointment's title, is content even where a title goes; the example
   gives it a role of its own, `title-record`, in the text face.
2. **A text face for content.** Everything a person reads or types: body, fields, buttons, meta
   lines (dates, times, counts), names, and one number standing alone.
3. **Digits only in a face whose figures line up.** A number in a sentence stays in the text face.
   Figures that must line up (an amount column, a total, a counter, a clock) need digits of one
   width: a `tnum` feature, or a face whose digits are all one width. Read which from the file
   (`scripts/font_facts.py FONT` prints each digit's width and whether `tnum` exists), never from
   `font-variant-numeric`, which silently does nothing when the feature is missing. The display
   face never sets a digit at all.
4. **Every font's licence read from its file.** The OFL.txt beside the font, not a web page. It
   says who holds the copyright and whether the name is reserved, and a reserved name changes how
   the face may ship: the file as published, or a WOFF2 that only compresses it, keeps the name; a
   subset or any other conversion is a modified version and may not use it
   ([OFL-FAQ 2.1 and 2.6](https://openfontlicense.org/ofl-faq/)).

## Fitting a display face

- **Size by x-height, not by the number.** Two faces at 16 px can differ by a fifth in how big they
  look. Scale the display face so its x-height matches the text face's at the step the role would
  take: x-height of the text face ÷ x-height of the display face.
- **Measure the real strings** at the new size against the old ones. A face chosen for being
  narrower can lose its saving once it is sized up to read.
- **One weight means no bold.** Set `font-synthesis: none` on the root so a browser draws the face
  as it is instead of smearing a fake bold or italic. Rank frame strings by size and ink level.
  A word that needs emphasis inside a title is content, so it takes the text face.
- **Put the text face second in the display face's stack.** Then a glyph the display face lacks
  (an arrow, the ellipsis) falls to the text face, not to a system font.
- **On the web, add a net for digits.** Give the display face's `@font-face` a `unicode-range`
  that leaves out every character a number is made of (digits, currency and number signs, the
  separators). A number that reaches a frame string is then drawn by the next face in the stack.
  `tokens.json` → `behaviour.type.unicode_range` carries the range; with next/font it goes in
  `localFont({ declarations: [{ prop: 'unicode-range', value }] })`. Native has no such net, so a
  native frame-text component refuses a digit in development.
- **Check the rendered screens too.** `scripts/frame-digits.js`, run in a page (Playwright:
  `page.evaluate`), returns every piece of visible text set in the display face that holds a
  digit or number sign. The net hides such a mistake on screen; this finds it.

## The example: Federo, DM Sans and DM Mono

The suite's titles were first set in JetBrains Mono, after a terminal skin the owner liked. He
found it "a little space hoggy" and asked to see Federo, a narrow display face with one weight. On
the sample he wrote: "can't use it for numbers or data... but the title and headers look really
nice", and Federo for "the surrounding elements, the meta elements, the headers, the titles, the
folders, maybe even buttons", with DM Sans "for all of the body content".

The plan that came back said numbers would be "DM Sans with lined-up figures". `font_facts.py`
said otherwise: DM Sans 4.004 has no `tnum` feature and its digits differ in width (a 1 is 0.34 em,
a 0 is 0.66 em). In Chromium, with `tabular-nums` set, 111.11 measured 28 px and 888.88 measured
53 px at 16 px. So figures that line up went to DM Mono, the same family's monospace, whose digits
are all 0.60 em and whose capitals are the height of DM Sans's. Meta lines hold dates and times,
so they stayed in DM Sans, the owner's "meta elements" read as the frame's labels (eyebrows).

| Face | Sets | Fitted |
|---|---|---|
| Federo | wordmark 19, eyebrow 13, tab 16 (tracked capitals); titles 28, 34, 44 | x-height 0.46 em against DM Sans's 0.526, so titles are the step × 1.14; "Today at the clinic" is 205 px at 28 where the mono title took 274 at 24 |
| DM Sans | label, meta, body, button, card title, lead, record title, a figure alone | the 12 to 38 scale; its optical-size axis follows the font size |
| DM Mono | `data`: amounts, totals, counters, clocks; code | the same step as the text beside it |

Federo's OFL.txt reserves the name "Federo", so the example ships the file as published, with
`next/font/local` on the web and `@expo-google-fonts/federo` on native, and never a subset of its
own. DM Sans and DM Mono reserve no name. Buttons were still undecided when this was written; the
tokens keep them in DM Sans, and if Federo wins the net still draws a button's price in DM Sans.

## What the script holds

R12 to R15 in [checks.md](checks.md): the display face on frame roles only and on every frame
role, and its unicode-range missing no character of a number; every role at a weight its face has
and that a native app bundles; every role asking for tabular figures in a face whose figures line
up; each licence, copyright and reserved name as the family file records them, read from the
OFL.txt. The self-test restores six wrong type values, among them the big number in the display
face and tabular figures asked of DM Sans, and each must fail.
