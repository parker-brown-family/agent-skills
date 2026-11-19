# The checks

`scripts/tokens.py` runs these on every product palette, light and dark. Contrast is the WCAG 2
ratio. Every gradient is checked at both ends: a two-stop lightness ramp is monotonic, so its
ends bound every label position between them.

| Rule | What it requires |
|---|---|
| R1 | `ink`, `ink-2`, `ink-3` at 4.5:1 or more on every surface and both ends of every surface gradient |
| R2 | text on a fill (accent, accent hover, danger) at 4.5:1 at the fill's light end; the sheen is computed per product to keep 4.6:1 |
| R3 | accent ink at 4.5:1 on every surface and on its own tint |
| R4 | control outlines at 3:1 on every surface they can sit on, wells included ([WCAG 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)) |
| R5 | the focus ring at 3:1 on every surface ([WCAG 2.4.13](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html)) |
| R6 | status text at 4.5:1 on its tint and on surfaces; neutral and done marks at 3:1 |
| R7 | chromatic light accents at OKLCH lightness 0.38 to 0.55 |
| R8 | an accent 40 degrees of hue from each status colour, or low in chroma (0.06 or less) and 8 apart in OKLab |
| R9 | any two product accents 5.0 apart (100 × OKLab) after deuteranopia and protanopia simulation, in each mode |
| R10 | a brand a client page wears passes R2 and R3 with its own colours; an advisory names a subtitle that fails |
| R11 | the folio bar (signature) at 3:1 on the page and the bar |
| R12 | the display face on frame roles only, and on every one; no frame role asks for figures; its web unicode-range leaves out every character of a number |
| R13 | every type role at a weight its face has, and a native cut bundled for it |
| R14 | every role that asks for tabular figures is in a face whose figures line up |
| R15 | each face's licence file present and OFL 1.1, with the copyright and reserved name the family file records, read from the file |
| R18 | text on the header's buttons over the header's bare ground (no glow, the faint end of its sheet), in both modes: the gel's label at its top and foot, words in a frosted button; 4.5:1. A control must pass on the weakest ground it can meet at any width |
| R19 | the notice levels in the page (failed, attention, worked): heading and sentence 4.5:1 on the level's tint, the icon's mark 4.5:1, the left edge in the level's ink 3:1 on the tint, surface, ground, raised and float |
| R21 | the mode strip: its words 7:1 on the band; the band 3:1 against the page ground and against the header's bare ground |
| R22 | status in a row (waiting, done, held, refused, unknown): the word 4.5:1 and the icon 3:1 on its tint |
| R17 | toggles: the on track 3:1 on surface, ground, raised and float; the off outline 3:1 on the same; each thumb 3:1 on its track |
| R16 | the glass header: its ink (and at 82%) 4.5:1 on the glass, the folio bar 3:1, the gel's label 4.5:1 at both edges of its line over the glow and over clear glass, the switch icon 3:1 on the frosted button |

Colour-blind simulation follows Machado, Oliveira and Fernandes, *A physiologically-based model
for simulation of color vision deficiency*, IEEE TVCG 2009
([doi](https://doi.org/10.1109/TVCG.2009.113)), at severity 1, applied in linear sRGB. The 5.0
threshold is a judgement: it clears every pair a reviewer called too close in the example (2.91)
and the closest pair they accepted (3.91), with room.

## Drift and the self-test

- `--check` regenerates both files in memory and fails if either differs from the file on disk,
  so a hand edit to `tokens.css` cannot pass.
- `--selftest` puts back, one at a time, every value in the family's `OLD_VALUES`: values that were
  once wrong, and theme colours used raw. Each must make at least one check fail. Add an entry
  whenever a review finds a failure, so it can never come back unnoticed.

In the example, the self-test restores twenty-seven values: three outlines that failed on wells, a
heavy sheen, a translucent brand subtitle, four theme accents used raw, two accents at the rule's
starting lightness before step 6 moved them, six type values (the big number in the display face,
DM Sans as the text face, a semibold Federo title, meta in Federo, a face recorded with no
reserved name, a unicode-range that leaves out only the digits), the three values the owner
settled by eye that a check then moved (two accents too close for colour-blind readers, a gel
whose label fell under 4.5 on clear glass), buttons put back in the text face, a pale toggle
whose on and off differ only by a faint colour, and two dark gels whose label failed over the
header's bare ground (one measured at 3.89 in a live app, where it had passed only over the glow), a mode strip as dark
as the dark page it sits on, and white on the amber attention mark.
