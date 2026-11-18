# Sources

Every source that changed a number, a rule or a colour in this skill, with the date it was read.
All read on 2026-11-18 unless marked.

## Grouping, layout, patterns

- Nielsen Norman Group, [Proximity principle](https://www.nngroup.com/articles/gestalt-proximity/): spacing groups (S1–S6).
- Nielsen Norman Group, [Common region](https://www.nngroup.com/articles/common-region/): when a box is needed (S5).
- Nielsen Norman Group, [Similarity principle](https://www.nngroup.com/articles/gestalt-similarity/): one filled button per view.
- Nielsen Norman Group, [Confirmation dialogs](https://www.nngroup.com/articles/confirmation-dialog/): P12.
- Nielsen Norman Group, [Error message guidelines](https://www.nngroup.com/articles/error-message-guidelines/): P9, P13.
- Nielsen Norman Group, [Empty states](https://www.nngroup.com/articles/empty-state-interface-design/): P11.

## Accessibility

- W3C, [WCAG 2.2 · 1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): R1–R3, R6.
- W3C, [WCAG 2.2 · 1.4.11 Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html): R4, R11.
- W3C, [WCAG 2.2 · 1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html): St2, St5.
- W3C, [WCAG 2.2 · 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html): S8.
- W3C, [WCAG 2.2 · 2.4.13 Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html): St3, R5.
- Machado, Oliveira, Fernandes, [A physiologically-based model for simulation of color vision deficiency](https://doi.org/10.1109/TVCG.2009.113), IEEE TVCG 2009: R9's simulation matrices.
- Björn Ottosson, [A perceptual color space for image processing (OKLab)](https://bottosson.github.io/posts/oklab/): every hue, chroma and distance.

## Platform guidance

- Apple HIG, [Layout](https://developer.apple.com/design/human-interface-guidelines/layout), [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) (44 pt targets), [Typography](https://developer.apple.com/design/human-interface-guidelines/typography), [Dark mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode), [Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars).
- Material 3, [Elevation](https://m3.material.io/styles/elevation/overview), [Color roles](https://m3.material.io/styles/color/roles), [Type scale tokens](https://m3.material.io/styles/typography/type-scale-tokens), [Corner radius scale](https://m3.material.io/styles/shape/corner-radius-scale), [Easing and duration](https://m3.material.io/styles/motion/easing-and-duration/tokens-specs), [Layout structure](https://m3.material.io/foundations/designing/structure) (48 dp targets).
- MDN, [prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion): M4.
- React Native 0.86, [View style props](https://reactnative.dev/docs/0.86/view-style-props): native shadows and gradients, cited by the review.
- W3C Design Tokens Community Group, [Format draft](https://www.designtokens.org/tr/drafts/format/): the shape of `tokens.json`.

## Type

- Tim Brown, [More meaningful typography](https://alistapart.com/article/more-meaningful-typography/), A List Apart: the modular scale.
- Matthew Butterick, [Line length](https://practicaltypography.com/line-length.html), Practical Typography: T6.
- [Federo](https://github.com/google/fonts/tree/main/ofl/federo), SIL Open Font License 1.1, Copyright (c) 2011, Cyreal, with Reserved Font Name "Federo". Licence read from its OFL file (`examples/head-waters/OFL-Federo.txt`); figures, weight and x-height read from the font with `scripts/font_facts.py`.
- [DM Sans](https://github.com/googlefonts/dm-fonts) 4.004, SIL Open Font License 1.1, © 2014 The DM Sans Project Authors, no reserved name (`OFL-DMSans.txt`). Read from the file: no `tnum` feature.
- [DM Mono](https://github.com/googlefonts/dm-mono), SIL Open Font License 1.1, © 2020 The DM Mono Project Authors, no reserved name (`OFL-DMMono.txt`).
- SIL, [OFL-FAQ 1.1-update8](https://openfontlicense.org/ofl-faq/): 2.1 (a WOFF that only compresses keeps the name), 2.6 (subsetting is modification), 5.1 to 5.9 (Reserved Font Names).
- Chromium, measured through the DevTools protocol (`CSS.getPlatformFontsForNode`): with the unicode-range, the seven number characters of "4 · $95.00" drew in DM Sans and the rest in Federo; without it, Federo drew all eighteen.
- The pages drawn before the type changed embed [Inter](https://github.com/rsms/inter) (© 2016 The Inter Project Authors, `OFL-Inter.txt`) and [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) (© 2020 The JetBrains Mono Project Authors, `OFL-JetBrainsMono.txt`), both SIL OFL 1.1.
- Terminal Delight's Deco skin, [app/skins/deco.toml](https://github.com/parker-brown-family/terminal-delight/blob/main/app/skins/deco.toml) and [app/themes/deco.toml](https://github.com/parker-brown-family/terminal-delight/blob/main/app/themes/deco.toml): no face of its own, so its chrome is the terminal's default, JetBrains Mono, with tracked capitals for labels.

## Themes (colour sources, all MIT)

- [Omarchy](https://github.com/omacom/omarchy) stock themes: [nord](https://github.com/omacom/omarchy/tree/HEAD/themes/nord) (the Nord palette is itself MIT, [nordtheme.com](https://www.nordtheme.com/)), [retro-82](https://github.com/omacom/omarchy/tree/HEAD/themes/retro-82), [miasma](https://github.com/omacom/omarchy/tree/HEAD/themes/miasma), [jade-horse](https://github.com/omacom/omarchy/tree/HEAD/themes/jade-horse).
- [Jade Horse](https://github.com/dhh/omarchy-jade-horse-theme), David Heinemeier Hansson, MIT.
- [Praus](https://github.com/parker-brown-family/omarchy-praus-theme), Parker Brown, MIT.
- Only colour values are used. No theme's wallpapers are redistributed: their licences vary, so
  the example pages are built without one.

## The theme switch

- Terminal Delight documentation site, [docsite/layout.html](https://github.com/parker-brown-family/terminal-delight/blob/main/docsite/layout.html) (the pre-paint script) and [assets/td-shell.js](https://github.com/parker-brown-family/terminal-delight/blob/main/assets/td-shell.js) (the toggle).

## The standard that was measured

- HC VIDEO, [hcvideo.app](https://hcvideo.app): its public site was photographed headless in
  light and dark. Its stylesheet and components (a private repository of the same company) were
  measured with `grep`; the counts are in [method.md](method.md).
