# Tokens version 4: what to change, for the builders

You are on version 2; nobody applied version 3, so this one page takes you to version 4. Copy
`tokens.css` (Piper: regenerate `theme.ts` from `tokens.json`) and work down. `python3
scripts/tokens.py --family examples/head-waters/family.py --check` passes 1,546 checks; `--selftest`
proves twenty-three wrong values fail. Everything here is settled by the owner.

## Breaking

1. **Two faces, both SIL OFL 1.1; Fraunces, Inter and JetBrains Mono leave.** Federo sets the
   frame: the wordmark, eyebrows, tabs, section and page titles, **and every button**. IBM Plex
   Sans sets all content, numbers and data included. Both reserve their names, so self-host each
   file as Google Fonts publishes it, or a `.woff2` that only compresses it (every glyph kept);
   never `next/font/google`, which subsets.
   ```ts
   const federo = localFont({ src: './fonts/Federo-Regular.woff2', variable: '--font-federo', weight: '400',
     display: 'swap', declarations: [{ prop: 'unicode-range', value: RANGE }] })   // RANGE: tokens.json behaviour.type.unicode_range
   const plex = localFont({ src: './fonts/IBMPlexSans-var.woff2', variable: '--font-ibm-plex-sans', weight: '100 700', display: 'swap' })
   ```
   Piper bundles `@expo-google-fonts/federo` and `@expo-google-fonts/ibm-plex-sans` (400, 500,
   600); `native.type.<role>.fontFamily` names the cut for each role.
2. **Buttons are Federo** (`--hw-type-button` 18 px, `-button-small` 16, `-gel` 16; weight 400,
   so a button ranks by fill and size, never bold). **A figure inside a label is Plex:**
   `<button class="hw-btn primary">Pay <span class="hw-fig">$95.00</span></button>`. A control
   whose label is only a number (a stepper, a page number, a count) is data: `.hw-text-data`, its
   plus and minus included. Keep the amount on a pay button. Piper's button splits its label into
   word and figure runs.
3. **Never a number in Federo** anywhere else either. Set text with `.hw-text-<role>`; a person's
   or record's name where a title goes is `.hw-text-title-record`. Run `scripts/frame-digits.js` on
   every screen in Playwright; it returns `[]` or the offending text, a raw "Pay $95.00" included.
4. **Toggles, never checkboxes** (the owner: "I hate checkboxes, TOGGLES"). One toggle per decision, label
   left, toggle right: `<div class="hw-toggle-row"><span id="k">Keep my card on file</span><button
   type="button" role="switch" aria-checked="false" class="hw-toggle" aria-labelledby="k"></button></div>`;
   a form keeps the value in a hidden input. Several choices from a list are selectable rows (the
   selected tint and a check icon). Run `scripts/stray-checkboxes.sh src` (source) and
   `scripts/stray-checkboxes.js` (rendered). Today it finds nine: Scythe's two card consents (they
   become **one** toggle), Stone's booking flow (reminders, policy), manage booking (fee,
   reminders) and calendar scan, Silo's calendar sources, and Surge's recipient picker (selectable
   rows). Piper: `accessibilityRole="switch"`, never `expo-checkbox`.
5. **Every app takes the glass header** (96 px, two rows), Home in its settled colours and each
   other app in its own theme's deep tone, already in the tokens. It replaces `.hw-bar`:
   ```html
   <header class="hw-header">
     <div class="hw-header-row"><span class="hw-word">Stone</span>
       <span class="hw-end"><button class="hw-frost hw-theme-switch">…the three icons…</button><button class="hw-gel">New booking</button></span></div>
     <nav class="hw-header-tabs"><a class="hw-tab hw-folio" aria-current="page">Calendar</a><a class="hw-tab">Bookings</a></nav>
   </header>
   ```
   The selected tab is the folio tab, in the colour of the page below (`--hw-page`: Home's surface,
   every other app's ground); it opens through the header's 1 px edge and soft shadow. The header
   paints its own ground and glow; no backdrop blur of its own. Piper draws the glow with
   `react-native-svg` (`native.header`).
6. **The corner shapes are gone:** Scythe's cut, Stone's groove, Silo's tab rule, Surge's airmail
   stripe, Home's garden strip.
7. **One theme switch replaces each app's ThemeToggle**, in the round frosted button: system,
   light, dark; `data-theme-pref` on `<html>`, class `dark` for what is drawn, saved on the account
   (`theme_preference`), mirrored in a cookie `hw-theme` on the shared domain, decided before paint.
   Spec: `behaviour.theme`.
8. **Piper has a dark mode** and follows the switch. **Silo opens on Today.**

## Type roles (px / line)

| Federo, weight 400 | IBM Plex Sans |
|---|---|
| wordmark 19/28 capitals 0.11em · eyebrow 13/16 capitals 0.10em · tab 16.5/20 | label 14/20 600 · meta 14/20 · body 16/24 · title-card 20/28 600 · lead 20/28 |
| button 18/24 · button-small 16/20 · gel 16/20 | title-record 30/36 600 · figure 38/44 600 · data 16/24 |
| title-section 27/32 · title-page 34/40 · display 43/52 | |

## Colours

| Product | Light accent v2 → v4 | Dark accent v2 → v4 | Folio bar | Corner tone from |
|---|---|---|---|---|
| Home | `#1c2530` → `#18747b` | `#edf1f5` → `#5f9ea2` | `#7A5B3C` / `#B99A70` | old-tree browns (settled) |
| Stone | `#22538d` → `#495a6b` | `#76b4ff` → `#a0b4c7` | accent | Nord slate |
| Silo | `#0e7490` → `#305647` | `#75cbea` → `#87af9e` | accent | Jade Horse jade |
| Scythe | `#2e3947` → `#1f1f1f` | `#c9d9ef` → `#d4d0bf` | `#a18c60` / `#cda369` | Praus gold |
| Surge | `#89396c` → `#006590` | `#eca4ce` → `#3aaae4` | accent | Retro 82 navy |
| Piper | unchanged `#5f4bae` | new `#c8b5f0` | accent | Piper burgundy |

Home's ground, surface and ink are `#EDE6D5` / `#F7F1E2` / `#1B2420` light and `#1E221D` /
`#272C25` / `#DDD7C1` dark. Every other value, the header's included, is in `tokens.json` →
`products.<name>.light|dark`; never write a hex in a component.

## Added

Faces and type: `--hw-font-display`, `--hw-font-ui` (both changed), `--hw-type-wordmark`, `-tab`,
`-button-small`, `-gel`, `-title-record`, `-data`, per-role tracking, `.hw-text-<role>`, `.hw-fig`.
Header: `--hw-header-*`, `--hw-glass-*`, `--hw-glow-*`, `--hw-gel`, `--hw-on-gel`, `--hw-gel-*`,
`--hw-frost-*`, `--hw-page`; `.hw-header`, `.hw-header-row`, `.hw-header-tabs`, `.hw-frost`,
`.hw-gel`. Toggles: `--hw-toggle-width` (44), `-height` (26), `-thumb` (20), `-inset` (3),
`--hw-toggle-on`, `-off`, `-thumb-on`, `-thumb-off`; `.hw-toggle`, `.hw-toggle-row`. Shapes:
`--hw-signature`, `--hw-line*`, `--hw-folio-*`, `.hw-folio`, `.hw-theme-switch`. Checks:
`scripts/frame-digits.js`, `scripts/stray-checkboxes.js`, `scripts/stray-checkboxes.sh`. Drawn:
`screenshots/fig-buttons-toggles.webp`, `screenshots/fig-glass-headers.webp`.
