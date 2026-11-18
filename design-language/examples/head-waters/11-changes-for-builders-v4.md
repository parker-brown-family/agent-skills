# Tokens version 4: what to change, for the builders

Nobody applied version 3, so this page replaces its list: it takes an app from version 2 to
version 4 in one pass. Copy `tokens.css` (Piper: regenerate `theme.ts` from `tokens.json`) and
work down. `python3 scripts/tokens.py --family examples/head-waters/family.py --check` passes
1,324 checks; `--selftest` proves seventeen
wrong values fail, six of them type. Unchanged from version 2: spacing, depth, radius, motion,
states, status colours.

**Two things are still the owner's:** Home's colour (Miasma is a holding value, marked PENDING in
both files; the pick replaces that one entry) and the face of buttons (DM Sans until chosen).

## Breaking

1. **Three faces, all SIL OFL 1.1.** Fraunces, Inter and JetBrains Mono leave.

   | Face | Sets | Web (next/font) |
   |---|---|---|
   | Federo | the frame: wordmark, eyebrows, tabs, section and page titles | `localFont({ src: './fonts/Federo-Regular.ttf', variable: '--font-federo', weight: '400', display: 'swap', declarations: [{ prop: 'unicode-range', value: RANGE }] })`, where `RANGE` is `tokens.json` → `behaviour.type.unicode_range` |
   | DM Sans | everything read or typed | `DM_Sans({ subsets: ['latin'], axes: ['opsz'], variable: '--font-dm-sans' })` |
   | DM Mono | figures that line up; code | `DM_Mono({ subsets: ['latin'], weight: ['400', '500'], variable: '--font-dm-mono' })` |

   Federo's file is the one Google Fonts publishes (`ofl/federo` in github.com/google/fonts), with
   its `OFL.txt`. Ship it as it is:
   Federo reserves its name, so a subset or converted copy may not be called Federo. Piper bundles
   `@expo-google-fonts/federo` (`Federo_400Regular`), `/dm-sans` (400, 500, 600) and `/dm-mono`
   (400, 500); `native.type.<role>.fontFamily` names the cut for each role.
2. **Never a number in Federo:** no digit, price, time, date, count, table cell or form value.
   Set text with the role classes `.hw-text-<role>`, which carry face, size, case and tracking.
   Frame: `wordmark`, `eyebrow`, `tab`, `title-section`, `title-page`, `display`. Everything else
   is DM Sans. A person's or record's name where a title goes is `.hw-text-title-record`.
   Add `scripts/frame-digits.js` to your Playwright tests on every screen; it returns `[]` or the
   offending text. Piper's frame text component throws in development on a digit.
3. **Figures that line up are DM Mono, not `tabular-nums`.** DM Sans has no tabular figures, so
   `font-variant-numeric: tabular-nums` changes nothing: at 16 px, 111.11 measures 28 px and
   888.88 measures 53 px. Amount columns, ledgers, totals, schedule times and counters take
   `.hw-text-data`. A number inside a sentence, or one big number alone (`.hw-text-figure`),
   stays DM Sans.
4. **No bold or italic Federo.** It has one weight. `tokens.css` sets `:root { font-synthesis:
   none }`; rank frame strings by size and ink (`ink`, `ink-2`, `ink-3`), never weight.
5. **The selected menu item is the folio tab.** `class="hw-folio"` and `aria-current="page"`.
   `.hw-bar` draws its own 2 px line; remove any border of your own under the bar.
6. **The corner shapes are gone:** Scythe's cut, Stone's groove, Silo's tab rule, Surge's airmail
   stripe, Home's garden strip.
7. **One theme switch replaces each app's ThemeToggle:** system, light, dark. `data-theme-pref` on
   `<html>`, class `dark` for what is drawn, the choice saved on the account
   (`theme_preference`) and mirrored in a cookie `hw-theme` on the shared domain, rendered on the
   server, `system` decided in a head script before paint. Spec: `behaviour.theme`.
8. **Piper has a dark mode** and follows the switch: deep green ground, parchment ink, lavender
   accent, burgundy reed.

## Type roles (sizes px / line)

| Federo, weight 400 | DM Sans | DM Mono |
|---|---|---|
| wordmark 19/28 caps 0.10em · eyebrow 13/16 caps 0.10em · tab 16/20 caps 0.08em | label 14/20 600 · meta 14/20 · body 16/24 · button 16/24 600 · title-card 20/28 600 · lead 20/28 | data 16/24 |
| title-section 28/32 · title-page 34/40 · display 44/52 | **title-record 30/36 600 (new)** · figure 38/44 600 | |

Federo runs small (x-height 0.46 em against DM Sans's 0.53), so its titles are one step up and
still narrower: "Today at the clinic" is 205 px at 28, against 274 px in version 3's mono at 24.

## Changed colours (no markup change)

| Product (theme) | Light accent v2 → v4 | Dark accent v2 → v4 | Folio bar (`--hw-signature`) |
|---|---|---|---|
| Stone (Nord) | `#22538d` → `#495a6b` | `#76b4ff` → `#a0b4c7` | accent |
| Silo (Jade Horse) | `#0e7490` → `#305647` | `#75cbea` → `#87af9e` | accent |
| Scythe (Praus) | `#2e3947` → `#1f1f1f` | `#c9d9ef` → `#d4d0bf` | bronze `#a18c60` / gold `#cda369` |
| Surge (Retro 82) | `#89396c` → `#006590` | `#eca4ce` → `#3aaae4` | accent |
| Home (holding value) | `#1c2530` → `#5b6241` | `#edf1f5` → `#b4bc98` | accent |
| Piper (its brand) | unchanged `#5f4bae` | new `#c8b5f0` | accent |

Every product's neutrals now come from its theme too: read `tokens.json` →
`products.<name>.light|dark`, never a hex in a component.

## Added

`--hw-font-figures`; `--hw-type-wordmark`, `-tab`, `-title-record`, `-data`; per-role tracking
(`--hw-tracking-wordmark`, `-tab`; `-eyebrow` is now 0.10em); classes `.hw-text-<role>`; `--hw-signature`,
`--hw-line`, `--hw-line-width`, `--hw-folio-radius` (4), `--hw-folio-chip` (10), `--hw-folio-bar`
(3); classes `.hw-folio`, `.hw-theme-switch`. In `tokens.json`: `behaviour.type` (which face sets
what, the unicode-range, licences), `shared.fonts` (each face's licence, reserved name and
figures, read from its files), `products.<name>.source`, `behaviour.theme`, `native.font`,
`native.type.<role>.fontFamily`, `native.folio`, `native.line`, Piper dark.
