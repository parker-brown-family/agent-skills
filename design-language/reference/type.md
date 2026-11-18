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
   lines (dates, times, counts), names, numbers and data.
3. **Digits only in a face whose figures line up.** Figures that must line up (an amount column,
   a total, a counter, a clock) need digits of one width: by default, or through a `tnum`
   feature. Read which from the file (`scripts/font_facts.py FONT` prints each digit's width and
   whether `tnum` exists), never from `font-variant-numeric`, which silently does nothing when the
   feature is missing. Choose a text face that has them and numbers need no third face. The
   display face never sets a digit at all.
4. **Every font's licence read from its file.** The OFL.txt beside the font, not a web page and
   not the font's own name table. It says who holds the copyright and whether the name is
   reserved, and a reserved name changes how the face may ship: the file as published, or a WOFF2
   that only compresses it, keeps the name; a subset or any other conversion is a modified version
   and may not use it ([OFL-FAQ 2.1 and 2.6](https://openfontlicense.org/ofl-faq/)).

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

## The example: Federo and IBM Plex Sans

The suite's titles were first set in JetBrains Mono, after a terminal skin the owner liked. He
found it "a little space hoggy" and asked to see Federo, a narrow display face with one weight. On
the sample he wrote: "can't use it for numbers or data... but the title and headers look really
nice". The first text face tried beside it was DM Sans, and `font_facts.py` showed it has no `tnum`
feature and digits of different widths: with `tabular-nums` set, 111.11 measured 28 px and 888.88
measured 53 px at 16 px in Chromium. Then he saw IBM Plex Sans on a billing report: "let's keep it
simple ... Still fedora for all the STYLE stuff... and then IBM for all the CONTENT". Plex's digits
are all 0.60 em by default, so numbers stay in the text face, and the family has two faces.

| Face | Sets | Fitted |
|---|---|---|
| Federo | wordmark 19 (capitals, 0.11 em), eyebrow 13 (capitals), tab 16.5; titles 27, 34, 43 | x-height 0.46 em against Plex's 0.516, so titles are the step × 1.12; wordmark and tabs are the settled header's |
| IBM Plex Sans | label, meta, body, every button, card title, lead, record title, a figure alone, data | the 12 to 38 scale, at 400, 500 and 600 |

Both faces reserve their names. Federo's OFL.txt reserves "Federo"; Plex's reserves "Plex", though
its own name table states no reserved name, which is why rule 4 says to read the OFL.txt. The
example ships each as a WOFF2 that only compresses the published file (39 KB and 230 KB, every
glyph kept) with `next/font/local`, and `@expo-google-fonts/federo` and `/ibm-plex-sans` on native,
never a subset of its own.

## What the script holds

R12 to R15 in [checks.md](checks.md): the display face on frame roles only and on every frame
role, and its unicode-range missing no character of a number; every role at a weight its face has
and that a native app bundles; every role asking for tabular figures in a face whose figures line
up; each licence, copyright and reserved name as the family file records them, read from the
OFL.txt. The self-test restores the wrong type values, among them the big number in the display
face, DM Sans as the text face, and Plex recorded with no reserved name; each must fail.
