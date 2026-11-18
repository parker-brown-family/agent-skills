# The glass header and the corner glow

A header of smoked glass, with a glow of the product's deep tone starting in the top right
corner, behind its main button, and fading left and down. The product's name sits on clear glass
on the left. The example's owner settled it for the suite's front page after asking for a header
that was "a little fuzzy at the edges with some fade and some depth", and moved the glow until
it started in "the TOP RIGHT CORNER and fade[d] along two dimensions (left and down)".

## Credit

The glass is Terminal Delight's documentation site's recipe
([docsite/redesign/redesign.css](https://github.com/parker-brown-family/terminal-delight/blob/main/docsite/redesign/redesign.css)):
a blur, a faint lit gradient over the ground, a hairline edge and a soft shadow below in place of
a hard line, and a gel button of the accent at partial opacity with a white sheen. The corner glow,
the two rows and the folio tab inside it are this family's.

## The recipe (`tokens.json` → `shared.header`)

| Part | Value |
|---|---|
| Height | 96 px, two rows: the name, the switch and the gel button; then the tabs |
| Glass | the ground at 26% over the glow, a white sheet fading from 7% to 2%, a 1 px edge of white at 12%, a shadow `0 14px 34px` at 33% black |
| Glow | an ellipse centred on the top right corner, 38% of the header's width to the left and 112% of its height down; the core colour solid to 14%, the mid tone (at about 65% opacity) by 46%, gone at 100%; softened by the glass's 20 px blur and clipped to the header |
| Gel button | 34 px tall, 44 px to the hand; the gel colour at 62% with a white sheen from 28% to 5%, an edge of the gel mixed 55% with white, a shadow `0 8px 20px` |
| Frosted button | 34 px round, 44 px to the hand; the theme switch lives here |

The header paints its own ground under the glass, so it looks the same over any page and needs no
backdrop blur of its own; the frosted controls blur the glow behind them. In CSS only the last
layer of a `background` may be a plain colour, so the ground's tint is drawn as a one-colour
gradient: the first version put a `color-mix()` mid-stack, and browsers dropped the whole header.

## Each product's corner tone

A settled product's values are used as given. For the others the rule is: hue and chroma from a
named colour of the product's theme (chroma at most 0.07), and the settled product's lightness for
the core, the mid tone and its opacity, so every glow weighs the same. The gel takes the product's
dark accent's hue and chroma at the settled gel's lightness; a product whose accent is ink takes
its dark accent as it stands, because a gold fill would sit on the warning colour. In the example,
the five tones are Nord slate, Jade Horse jade, Praus gold, Retro 82 navy and Piper's burgundy.
That is a rule for a starting point; the tones themselves are a judgement for the eye.

## Keep the folio tab joined

The shadow under the glass runs under the selected tab too, and the tab then sits on the page
instead of opening into it. The tab therefore takes the colour of the page beneath the header
(`--hw-page`), covers the 1 px edge, and carries that colour down into the shadow, fading out by
the page's padding (24 px) so it can never lie over content.

## What the script checks (R16)

- The header's ink, and its ink at 82% for a tab not selected, at 4.5:1 on the glass.
- The folio bar at 3:1 on the glass.
- The gel's label at 4.5:1 at the top and bottom of its line box, both over the glow's core and
  over clear glass, which is where a narrow header puts the button, past the glow's reach. In the
  example every dark gel failed this at first (3.8 to 4.2) and was lifted in lightness, the owner's
  settled one included, and recorded.
- The switch's icon at 3:1 on the frosted button.
- An advisory reports how far each glow's core stands from the ground, since in dark mode a
  glow close to the ground in brightness barely shows.

## Native

No radial gradient or backdrop blur in plain React Native: draw the glow with
`react-native-svg`'s `RadialGradient` from the same numbers, make the glass opaque, and use
`expo-blur` only for the frosted controls (`tokens.json` → `native.header`).
