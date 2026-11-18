# Tokens version 3: what breaks, for the builders

Copy `tokens.css` (Piper: regenerate `theme.ts` from `tokens.json`) and work down this page.
`python3 build_tokens.py --check` passes 1,262 checks; `--selftest` proves eleven wrong values fail.
Unchanged: spacing, depth, radius, motion, states, status colours, every pattern Parker ticked.

## Breaking

1. **Faces.** Fraunces is gone. Load **JetBrains Mono** as `--font-jetbrains-mono` and **Inter** as
   `--font-inter` (next/font: `JetBrains_Mono({ variable: '--font-jetbrains-mono' })`,
   `Inter({ variable: '--font-inter' })`). Piper bundles `@expo-google-fonts/jetbrains-mono`
   (500, 600) and `@expo-google-fonts/inter` (400, 600). Both are SIL OFL 1.1.
2. **Labels are tracked capitals.** `--hw-type-eyebrow` and the new `--hw-type-tab` need
   `text-transform: uppercase; letter-spacing: var(--hw-tracking-label)`.
   `--hw-tracking-eyebrow` is **removed**; use `--hw-tracking-label` (0.12em).
3. **The selected menu item is the folio tab.** Give it `class="hw-folio"` and
   `aria-current="page"`. `.hw-bar` now draws its own 2 px line (`--hw-line-width`, `--hw-line`);
   remove any border of your own under the bar.
4. **The corner shapes are gone:** `--hw-cut` and `.hw-cut` (Scythe), `--hw-bar-edge-shadow`
   (Stone's groove), Silo's `.hw-tab[aria-current]` rule, Surge's airmail stripe and Home's garden strip.
5. **The theme switch replaces each app's ThemeToggle.** One button, three states (system, light,
   dark). Put `data-theme-pref` on `<html>`, keep the `dark` class for what is drawn, store the
   choice in the person's account (`theme_preference`), mirror it in a cookie `hw-theme` on the
   suite's shared domain, render it on the server, and for `system` decide in a head script before
   paint. Signed-out pages: this device's cookie, else system, switch in the footer. Full spec:
   `tokens.json` → `behaviour.theme`. The account menu loses its theme row.
6. **Piper has a dark mode.** Its block no longer forces light under `.dark`; Piper follows the
   switch like every app. Dark: deep green ground, parchment ink, lavender accent, burgundy reed.

## Changed values (no markup change; every product's neutrals now come from its theme too)

| Product (theme) | Light accent v2 → v3 | Dark accent v2 → v3 | Folio bar (`--hw-signature`) |
|---|---|---|---|
| Stone (Nord) | `#22538d` → `#495a6b` grey | `#76b4ff` → `#a0b4c7` | accent |
| Silo (Jade Horse) | `#0e7490` → `#305647` grey-green | `#75cbea` → `#87af9e` | accent |
| Scythe (Praus) | `#2e3947` → `#1f1f1f` black | `#c9d9ef` → `#d4d0bf` linen | bronze `#a18c60` / gold `#cda369` |
| Surge (Retro 82) | `#89396c` → `#006590` azure | `#eca4ce` → `#3aaae4` | accent |
| Home (Miasma, inferred) | `#1c2530` → `#5b6241` olive | `#edf1f5` → `#b4bc98` | accent |
| Piper (its brand) | unchanged `#5f4bae` | new `#c8b5f0` | accent |

Grounds: Stone `#f6f8fd`, Silo `#f3faf7`, Surge `#f5f9fe`, Scythe and Home `#f8f8f8`; dark grounds
follow the same hues. Read every value from `tokens.json` → `products.<name>.light|dark`.

## Added

`--hw-signature`, `--hw-line`, `--hw-line-width`, `--hw-folio-radius` (4), `--hw-folio-chip` (10),
`--hw-folio-bar` (3), `--hw-type-tab`, `--hw-tracking-label`; classes `.hw-folio`, `.hw-theme-switch`.
`tokens.json` gains `products.<name>.source` (theme, licence, colours read, every lightness the rule
moved), `behaviour.theme`, `shared.fonts` (licences), and `native.folio`, `native.line`, Piper dark.
