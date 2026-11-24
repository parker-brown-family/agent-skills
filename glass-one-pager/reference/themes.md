# Themes

A theme is one JSON file beside its two pictures. Copy `themes/deep-quiet.json`, or start one from an image:

```bash
python3 scripts/onepager.py theme my-look --wallpaper picture.jpg --dir my-page
```

That crops the picture to 1920 × 1200, makes the blurred copy the glass shows, and writes `my-page/my-look.json` with the base theme's colours.
`--base bright-future` starts from the other one.

## Colours, by role

| Key | Where it shows |
|---|---|
| `accent` | the window's frame, the tube's rim, the prompt |
| `good`, `waiting`, `building` | the marks; a state in the content file names one of these, or any other key here |
| `text`, `bright`, `dim` | words on the glass and in the sidebar; names; owners and the legend |
| `heart`, `heart_text` | what the person loves |
| `link` | the links at the top |
| `panel`, `shade`, `edge`, `line` | the sidebar's glass, the tube's tint, its darkest rim, hairlines |
| `note`, `note_ink`, `glare` | the sticky note and the light on the glass |
| `projects` | one dot per project, in order. A project's own `colour` in the content file wins |

Every colour is six hex digits. Keep `text` light: it sits on glass over a picture.

## The glass

| Key | Turn it up and | Deep Quiet |
|---|---|---|
| `tint` | the screen gets darker and less see-through | 0.40 |
| `panel_tint`, `frame_tint` | the same, for the sidebar and the frame around the tube | 0.50, 0.40 |
| `smoke`, `vignette` | the middle, then the corners, darken | 0.20, 0.82 |
| `phosphor` | the accent colour glows from the centre | 0.05 |
| `scanlines`, `glare` | stronger lines, more light at the top left | 0.30, 0.20 |
| `bend` | lines of text curve more; 0 is a flat screen | 0.018 |
| `bulge`, `corner` | the tube's sides and corners round out | 0.035, 0.09 |
| `wallpaper_dim` | the picture behind everything darkens | 0.16 |

**More see-through:** lower `tint` and `panel_tint`, then look at the brightest part of the picture. If words wash out there, darken the
blurred copy (`magick my-look-blur.jpg +level 0,60% my-look-blur.jpg`) rather than raising the tint.
