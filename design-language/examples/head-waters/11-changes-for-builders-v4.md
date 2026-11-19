## 4.2, values only: copy tokens.css again (Piper: regenerate theme.ts)

No markup changes. Text on a header button must pass on the header's weakest ground at any width,
not only where the corner glow lends it light: Surge's account name read 3.89 over bare dark ground.
Every dark gel is lifted until its label passes there at the button's top and foot; a new check
(R18) measures text on the header's buttons over the bare ground in both modes and every product.
`--check` passes 1,582, `--selftest` 25. Light mode is unchanged.

| Product | Role that changed (dark) |
|---|---|
| Head Waters | `gel` `#3fa6ac` → `#51b6bc` |
| Stone | `gel` `#8a9eb1` → `#9cb1c4` |
| Silo | `gel` `#7ea595` → `#90b8a8` |
| Surge | `gel` `#5ea5cd` → `#6db4de` (no longer held at version 4's value) |
| Piper | `gel` `#a896cf` → `#bba9e3` |
| Scythe | none (its linen gel already passed) |

## 4.2, added: the alert and the sign-in page (copy tokens.css again)

Two patterns every app now shares, drawn for all six in `screenshots/fig-sign-in.webp`. New in `tokens.css`:
`--hw-type-alert-title` (Federo 18/24), `.hw-alert` with `-icon`, `-title`, `-text`;
`.hw-header.single`, `.hw-signin`, `.hw-signin-card`, `-title`, `-lead`, `-or`. Check R19 holds the
alert: its words 4.5:1 on its tint, the icon's mark 4.5:1, its edge 3:1. 1,658 checks, 25 self-test values.

**The alert is the one error pattern.** Every error in every app (a refused sign-in, a failed save, a
lost connection) is one block:
`<div class="hw-alert" role="alert" aria-live="assertive"><span class="hw-alert-icon" aria-hidden="true">!</span><div><p class="hw-alert-title">What happened</p><p class="hw-alert-text">One sentence saying what to do.</p></div></div>`.
It sits under the button that was pressed, or at the top of the panel the error belongs to, and
stays until the next attempt. The heading is Federo and names what happened (no figures); the
sentence is Plex and says what to do (a time or a count goes here). Never red helper text, a toast
or a modal for an error. Piper's `ErrorBlock` is this pattern; native draws the same block.

**The sign-in page is the same in every app.** Today four apps draw four layouts, each with an
email and password form on an instance where only Google works. Replace them with:
- `.hw-header.single`: one row, the wordmark (the product named in Federo, on a phone too) and the
  theme switch. No tabs, no gel.
- One `.hw-signin-card` (400 px wide at most, 14% of the window from the top; full width on a
  phone): `<h1 class="hw-signin-title">Sign in to Stone</h1>` in Federo, one Plex line
  `Use your practice's Google account.`, then the primary button, full width, "Continue with Google".
- **Google only** (every instance today): nothing else. No field, no "or", no "Forgot password?", no
  "Create account" unless that instance can create one.
- **Password sign-in on** (an instance setting): under the Google button, "or", Email and Password
  (labels above), an outlined "Sign in" (Google stays the one filled button), and "Forgot password?"
  only where reset works.
- **A refusal** is the alert under the button that was pressed. Google's causes, in Piper's words:
  "Nothing came back from Google" / Press Continue with Google to try again; "<Product>'s server
  refused the sign-in" / try again, and if it happens again tell the owner the time (the time is
  in the sentence); "This Google account is not on <Product>'s list" / ask the practice's owner to
  add it (naming it), or choose another; "No connection to <Product>" / check the Wi-Fi, then try
  again; "Too many attempts" / wait a minute, then try again. A closed Google sheet says nothing.
  A wrong password: "That email and password do not match" / Check both, then press Sign in again.
- Light and dark, in each product's colours, come from the tokens; the card's top bar is the
  product's signature, the folio tab's bar.

## 4.1, values only: copy tokens.css again (Piper: regenerate theme.ts)

No markup changes. A second provider's review of the header on the five other products, all ten
changes taken. Head Waters, the faces and the toggles are unchanged.

| Product | Roles that changed |
|---|---|
| Stone | `glow-core`, `glow-mid` (light and dark): slate; glow reach `--hw-glow-reach-x` 32% |
| Silo | `glow-core`, `glow-mid` (light and dark): grey-jade |
| Scythe | dark `ground` `#0e0e0e` (ink-black) and `page`; glow reach 28% × 92% |
| Surge | `glow-core`, `glow-mid` (light and dark): navy to azure; dark `ground` `#0c192b` and `page`; glow reach 46% × 122%; dark `gel` stays `#5ea5cd` |
| Piper | dark neutrals become dark earth from the brand brown: `ground`, `surface`, `surface-top`, `surface-bottom`, `raised`, `raised-bottom`, `float`, `inset`, `field`, `edge`, `neutral-tint`, `neutral-edge`, with `page`, `assist-surface`, `avatar-bg`, `done-tint`, `line`, `toggle-off`; `glow-core`, `glow-mid` (dark), `glow-mid` (light): deeper burgundy |

The reach is emitted per product in `tokens.css` (`--hw-glow-reach-x`, `-y` in each `[data-product]`
block) and in `tokens.json` under `products.<name>.header_glow`; Piper's native glow reads it there.

# Tokens version 4: what to change, for the builders

You are on version 2; nobody applied version 3, so this one page takes you to version 4. Copy
`tokens.css` (Piper: regenerate `theme.ts` from `tokens.json`) and work down. `python3
scripts/tokens.py --family examples/head-waters/family.py --check` passes the checks; `--selftest`
proves the wrong values fail. Everything here is settled by the owner.

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
`screenshots/fig-buttons-toggles.webp`, `screenshots/fig-glass-headers.webp`, `screenshots/fig-sign-in.webp`.
