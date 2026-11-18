# Tokens version 4: what to change, for the builders

You are on version 2; nobody applied version 3, so this one page takes you to version 4. Copy
`tokens.css` (Piper: regenerate `theme.ts` from `tokens.json`) and work down. `python3
scripts/tokens.py --family examples/head-waters/family.py --check` passes 1,420 checks; `--selftest`
proves twenty-one wrong values fail.

**Settled by the owner:** the two faces, Home's colours, Home's glass header.
**Waiting on the owner:** whether Stone, Silo, Scythe, Surge and Piper take the glass header too. Until
that is answered, only Home uses `.hw-header`; the others keep `.hw-bar`. Their header colours are in the
tokens already, marked proposed.

## Breaking

1. **Two faces, both SIL OFL 1.1; Fraunces, Inter and JetBrains Mono leave.** Federo sets the
   frame (wordmark, eyebrows, tabs, section and page titles); IBM Plex Sans sets everything else,
   numbers, data and every button included. Both reserve their names ("Federo", "Plex"), so
   self-host each file as Google Fonts publishes it, or a `.woff2` that only compresses it
   (39 KB and 230 KB, every glyph kept). Do not use
   `next/font/google` for either: it subsets, and a subset may not carry the name.

   ```ts
   const federo = localFont({ src: './fonts/Federo-Regular.woff2', variable: '--font-federo', weight: '400',
     display: 'swap', declarations: [{ prop: 'unicode-range', value: RANGE }] })   // RANGE: tokens.json behaviour.type.unicode_range
   const plex = localFont({ src: './fonts/IBMPlexSans-var.woff2', variable: '--font-ibm-plex-sans', weight: '100 700', display: 'swap' })
   ```
   Piper bundles `@expo-google-fonts/federo` (`Federo_400Regular`) and `@expo-google-fonts/ibm-plex-sans`
   (400, 500, 600); `native.type.<role>.fontFamily` names the cut for each role.
2. **Never a number in Federo:** no digit, price, time, date, count, table cell or form value.
   Set text with the role classes `.hw-text-<role>`. A person's or record's name where a title goes
   is `.hw-text-title-record`. Add `scripts/frame-digits.js` to your Playwright tests on every screen;
   it returns `[]` or the offending text. Piper's frame text component throws in development on a digit.
3. **Numbers line up in Plex as it stands** (every digit 0.60 em). Columns of amounts, totals and
   clocks use `.hw-text-data`. Never switch on old-style figures (`onum`) for data.
4. **No bold or italic Federo.** `tokens.css` sets `:root { font-synthesis: none }`; rank frame
   strings by size and ink, never weight. Every button is Plex 600.
5. **Home's header is the glass header** (96 px, two rows). The page below it is `--hw-page`
   (Home: the surface colour), which the selected tab opens into:
   ```html
   <header class="hw-header">
     <div class="hw-header-row"><span class="hw-word">Head Waters</span>
       <span class="hw-end"><button class="hw-frost hw-theme-switch">…the three icons…</button><a class="hw-gel" href="/signup">Start free</a></span></div>
     <nav class="hw-header-tabs"><a class="hw-tab hw-folio" aria-current="page">Pieces</a><a class="hw-tab">Pricing</a></nav>
   </header>
   ```
   The header paints its own ground, the corner glow and the glass; it needs no backdrop blur of
   its own. Its edge is a 1 px hairline with a soft shadow, in place of the 2 px line.
6. **The selected menu item is the folio tab** in every app: `class="hw-folio"`, `aria-current="page"`.
   In a `.hw-bar`, the bar draws its own 2 px line; remove any border of your own under it.
7. **The corner shapes are gone:** Scythe's cut, Stone's groove, Silo's tab rule, Surge's airmail
   stripe, Home's garden strip.
8. **One theme switch replaces each app's ThemeToggle:** system, light, dark; in Home's header it is
   the round frosted button. `data-theme-pref` on `<html>`, class `dark` for what is drawn, saved on
   the account (`theme_preference`), mirrored in a cookie `hw-theme` on the shared domain, rendered
   on the server, `system` decided in a head script before paint. Spec: `behaviour.theme`.
9. **Piper has a dark mode** and follows the switch.

## Type roles (px / line)

| Federo, weight 400 | IBM Plex Sans |
|---|---|
| wordmark 19/28 capitals 0.11em · eyebrow 13/16 capitals 0.10em · tab 16.5/20 | label 14/20 600 · meta 14/20 · body 16/24 · button 16/24 600 · gel 14/20 600 · title-card 20/28 600 · lead 20/28 |
| title-section 27/32 · title-page 34/40 · display 43/52 | title-record 30/36 600 · figure 38/44 600 · data 16/24 |

## Home's colours (settled; three moved to pass the checks)

| Role | Light | Dark |
|---|---|---|
| ground / surface (= page) / ink | `#EDE6D5` / `#F7F1E2` / `#1B2420` | `#1E221D` / `#272C25` / `#DDD7C1` |
| accent (button, link fill) | `#18747b` (settled `#0C6E75`: 3.0 from Stone for colour-blind readers) | `#5f9ea2` (settled `#6BAAAE`: 3.5 from Silo) |
| folio bar / header ink | `#7A5B3C` / `#241A10` | `#B99A70` / `#EAE2CC` |
| corner glow core / mid | `#2C1F15` / `#4E3927b0` | `#6E553C` / `#3D2C1Ea0` |
| gel / its label | `#2F9AA0` / `#061416` | `#3fa6ac` (settled `#2F9AA0`: label 4.2 on clear glass) / `#061416` |

## The other products' colours (v2 → v4; no markup change)

| Product (theme) | Light accent | Dark accent | Folio bar |
|---|---|---|---|
| Stone (Nord) | `#22538d` → `#495a6b` | `#76b4ff` → `#a0b4c7` | accent |
| Silo (Jade Horse) | `#0e7490` → `#305647` | `#75cbea` → `#87af9e` | accent |
| Scythe (Praus) | `#2e3947` → `#1f1f1f` | `#c9d9ef` → `#d4d0bf` | bronze `#a18c60` / gold `#cda369` |
| Surge (Retro 82) | `#89396c` → `#006590` | `#eca4ce` → `#3aaae4` | accent |
| Piper (its brand) | unchanged `#5f4bae` | new `#c8b5f0` | accent |

Every product's neutrals now come from its theme; read `tokens.json` → `products.<name>.light|dark`.

## Added

Faces and type: `--hw-font-display`, `--hw-font-ui` (both changed), `--hw-type-wordmark`, `-tab`,
`-gel`, `-title-record`, `-data`, per-role tracking, classes `.hw-text-<role>`. Header:
`--hw-header-height`, `--hw-header-control`, `--hw-glass-*`, `--hw-glow-*` and `--hw-glow`,
`--hw-gel`, `--hw-on-gel`, `--hw-gel-*`, `--hw-frost-*`, `--hw-header-ink`, `--hw-header-tint`,
`--hw-page`; classes `.hw-header`, `.hw-header-row`, `.hw-header-tabs`, `.hw-frost`, `.hw-gel`.
Shapes: `--hw-signature`, `--hw-line`, `--hw-line-width`, `--hw-folio-*`, `.hw-folio`,
`.hw-theme-switch`. In `tokens.json`: `behaviour.type`, `behaviour.theme`, `shared.fonts`,
`shared.header`, `products.<name>.source` and `.header` (settled or proposed), `native.font`,
`native.header`, `native.type.<role>.fontFamily`, Piper dark.
