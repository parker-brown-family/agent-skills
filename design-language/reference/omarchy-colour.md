# Colour from Omarchy themes

[Omarchy](https://github.com/omacom/omarchy) themes each carry a `colors.toml` with a `mode`,
an `accent`, `background`, `foreground` and named colours (`red`, `yellow`, `green`, `cyan`,
`blue`, `magenta`, ...). A product owner who names a theme ("Stone follows Nord") has given you a
palette you can draw from directly, and a rule turns it into a product's light and dark roles.
`scripts/tokens.py` implements the rule; the family file records its inputs.

## The rule

1. **Identity colour.** The theme's `accent`, unless a person named another slot, or the accent
   sits on a status hue (danger about 30°, warning about 70°, success about 150° in OKLCH). Then
   take the slot they named, or the nearest colour of the theme that clears the statuses. Record
   which, and why, in the family file.
2. **Hue and chroma.** Hue is the identity colour's OKLCH hue (or a hue you set, with the reason).
   Chroma comes from the product's *intent*, not the theme: `ink` 0 (black and white), `grey`
   0.035, `gentle` 0.05, `bright` 0.13.
3. **Lightness.** The accent starts at 0.46 in light mode and 0.78 in dark. An `ink` product
   takes 0.24 in light and the theme's foreground in dark. Hover, accent ink, tint and on-accent
   follow at fixed offsets.
4. **Neutrals.** Keep the family's lightness ladder, so depth never changes between products,
   and give each neutral the theme background's hue at a small capped chroma, scaled by how
   coloured that background is. A black theme gives pure greys.
5. **Signature.** The folio bar is the accent, or a named slot (a theme's gold, say), moved in
   lightness until it reads 3:1 on the page and the bar. Use a signature when the colour you
   want for identity cannot be a fill, for example because it sits on the warning hue.
6. **Checks.** Run them. Where a colour fails one, move its lightness in 0.02 steps, never its
   hue, and record the move. A failure lightness cannot fix fails the build.

Out of the sRGB gamut, reduce chroma, never hue: plain channel clipping turned an azure at 236°
into a blue at 245° in the example.

## The example's sources

| Product | Theme | Intent | What the rule did |
|---|---|---|---|
| Stone | Nord (Omarchy, MIT) | grey | accent hue 249°; dark lightness moved to 0.76 |
| Silo | Jade Horse (MIT) | gentle | hue 167°, low chroma so it clears success by distance; moved to 0.42 and 0.72 |
| Scythe | Praus (MIT) | ink | black and linen; the theme's bronze and lamp gold are the signature, never a fill |
| Surge | Retro 82 (Omarchy, MIT) | bright | the theme's accent is orange (warning), so the azure between its navy and teal, 236° |
| Home | Miasma (Omarchy, MIT) | gentle | inferred: the owner named no theme; olive, the one free hue |
| Piper | its own brand | given | a palette given whole; dark mode inferred from its brand sheet |

A seventh product is one entry in `SOURCES`: a theme name and an intent. If the theme is
installed, `tokens.py` reads its colours; record them in the file anyway, so the result does not
change when the theme does, and so the licence and the reason travel with the colour.

## Feel versus measurement

The checks settle contrast and separation. They do not settle the azure point, how gentle
"gentle" is, or whether a gold signature feels like the theme. Say which choices are feel when
you hand the palette to a reviewer.
