# The rules, as sentences someone can test

These are the example family's rules. Keep the numbers when they suit your family and change
them when they do not; what matters is that each one could be checked against a screenshot or
the DOM.

## Type

- T1 Body text is 16 px on a 24 px line; a sentence a person reads is never smaller than 14 px.
- T2 Under 14 px is for uppercase labels and chips only (example: eyebrows and table headers at
  13 in the display face, chips at 12), never a sentence.
- T3 Text sizes come from 12, 14, 16, 20, 24, 30, 38; the display face's are fitted to its
  x-height (example: 13, 16.5, 19, 27, 34, 43). One screen uses four sizes at most.
- T4 The display face sets the frame only: wordmark, tabs, eyebrows, section and page titles
  (example: Federo). Everything a person reads or types uses the text face (example: IBM Plex
  Sans), every button, number and datum included, and a person's or record's name where a title goes.
- T5 Numbers that line up (a column, a total, a counter, a clock) are in a face whose digits are
  one width (example: Plex as it stands) and align right.
- T6 A paragraph is at most 68 characters wide.
- T7 No digit, price, time, date, count, table cell or form value is set in the display face.
- T8 Nothing is faked: `font-synthesis: none`; a face with one weight is never bold.

## The header

- H1 Where the family takes the glass header, it is 96 px in two rows: the name, the switch and
  the main button; then the tabs ([glass-header.md](glass-header.md)).
- H2 The glow starts in the top right corner, behind the main button, and fades left and down;
  the name sits on clear glass.
- H3 The main button's label reads 4.5:1 over clear glass, not only over the glow.
- H4 The selected tab opens into the page through the header's edge and shadow.

Sources: [modular scale](https://alistapart.com/article/more-meaningful-typography/),
[line length](https://practicaltypography.com/line-length.html),
[Material 3 type scale](https://m3.material.io/styles/typography/type-scale-tokens).

## Spacing and proximity

- S1 Every margin, padding and gap is 4, 8, 12, 16, 24, 32, 48 or 64.
- S2 A label sits 8 above its field; the field's hint sits 4 below it.
- S3 Fields in one group sit 16 apart; groups holding 16 px gaps sit 32 apart at every width; 24
  separates groups only when nothing inside them is more than 12 apart.
- S4 The space between two groups is at least twice the largest space inside either.
- S5 A group gets a border or fill only when space cannot separate it from a neighbour of the
  same kind. A selectable option is always bounded and grows when its name wraps.
- S6 Buttons in one row sit 8 apart; the row sits 32 below the last field.
- S7 Cards and page margins are padded 24 (16 on a phone).
- S8 Everything tapped has a hit area of 44 by 44 px (48 dp on Android). A 36 px visible button
  is allowed on a pointer layout only inside that hit area.

Sources: Nielsen Norman Group on [proximity](https://www.nngroup.com/articles/gestalt-proximity/),
[common region](https://www.nngroup.com/articles/common-region/) and
[similarity](https://www.nngroup.com/articles/gestalt-similarity/); target sizes from
[Apple](https://developer.apple.com/design/human-interface-guidelines/accessibility),
[Material](https://m3.material.io/foundations/designing/structure) and
[WCAG 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).

## Depth and shape

- D1 Four depths above the page: inset, card, raised, float. No component invents a fifth.
- D2 A card never sits inside a card; inside a card is an inset well or a plain list.
- D3 Bars and docks are raised; menus, popovers and dialogs float; only a modal dialog has a scrim.
- D4 Card, raised and float surfaces carry a 1 px lit top edge.
- D5 In dark mode each step up is lighter, not only more shadowed.
- D6 Radius: 8 controls, 12 cards and lists, 16 sheets and dialogs, full chips and avatars.

Sources: [Material elevation](https://m3.material.io/styles/elevation/overview),
[Apple dark mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode).

## Colour

- C1 Components write roles, never hex values.
- C2 Ink on any surface, and a label at the light end of its button's gradient, read at 4.5:1;
  outlines and the focus ring read at 3:1 on every surface, wells included.
- C3 The accent marks four things only: the one primary action, the selected item, focus, and
  live state.
- C4 Statuses mean status only; no product accent sits within 40 degrees of a status hue unless
  it is low in chroma and far enough in colour; any two product accents stay 5.0 apart for
  colour-blind readers.
- C5 Text on a fill uses the on-accent role, never a hard-coded white.

Sources: [WCAG 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html),
[1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html),
[1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).

## States

- St1 A view has at most one filled button, and it is the primary action.
- St2 Selected always adds one mark that is not colour: a check, or a change of shape.
- St3 Focus is a 2 px solid ring in the accent's ink, 2 px outside the control, for keyboard
  focus only ([WCAG 2.4.13](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html)).
- St4 A disabled primary keeps its place, at full opacity, and a line under it says what is missing.
- St5 Every status chip carries an icon and a word.
- St6 A pressed button sinks with an inset shadow, kept under reduced motion.

## Motion

- M1 Hover and press 120 ms, a fold 200 ms, a sheet or dialog 300 ms; leaving takes two thirds.
- M2 Ease on `cubic-bezier(0.2, 0, 0, 1)`, exit on `(0.3, 0, 1, 1)`; nothing bounces.
- M3 Nothing slides farther than 16 px; nothing loops except a live indicator.
- M4 Under reduced motion, durations are 0 and a 100 ms fade remains
  ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)).

Source: [Material easing and duration](https://m3.material.io/styles/motion/easing-and-duration/tokens-specs).

## Patterns every app repeats

- P1 The mark and product name sit top-left and take the person home.
- P2 The bar shows five destinations at most; the rest go under More.
- P3 The current destination is the folio tab ([shapes-and-switch.md](shapes-and-switch.md)).
- P4 The theme switch is one button on the bar; the account menu holds account things only.
- P5 From 1024 px wide a list (300 to 360 px) and its detail sit side by side; below that the
  detail replaces the list and offers Back.
- P6 A list row is 56 tall: title, meta, and the row's next action at its right end.
- P7 Labels sit above fields and are names, not questions.
- P8 The primary ends a form: right-aligned on a laptop, full width on a phone.
- P9 An error sits at its field and says what to do; on submit the first one takes focus
  ([NN/g](https://www.nngroup.com/articles/error-message-guidelines/)).
- P10 Tables: eyebrow headers, 48 px rows, numbers right, no vertical rules, status as a chip.
- P11 An empty region says what will appear and offers the one action that fills it; it never
  explains the system ([NN/g](https://www.nngroup.com/articles/empty-state-interface-design/)).
- P12 Only an action that cannot be undone asks first; its title names the thing and the
  consequence; buttons are verbs; the destructive one is last
  ([NN/g](https://www.nngroup.com/articles/confirmation-dialog/)).
- P13 A page error says what happened in the person's words and what to do, with a retry; never
  an environment variable, host name or stack trace.
