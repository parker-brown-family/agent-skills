# The folio tab, the line, and the theme switch

Every app in a family draws these three the same way. They are where the family is most
visible, so they are shared, and identity comes from the colour in them.

## The folio tab

The selected menu item is a tab that opens into the page below it, like a folder's tab.

- A bar over its words, 3 px, in the product's signature colour (`--hw-folio-bar`). Not an underline.
- A chip cut from its right corner, 10 px at 45 degrees (`--hw-folio-chip`).
- A slight rounding on its left corner, a third of a card's radius: 4 px against 12 (`--hw-folio-radius`).
- No line under it: its fill is the page ground, so it joins the content.
- `class="hw-folio"` and `aria-current="page"`. Unselected tabs are text on the bar.
- Labels in the display face, tracked capitals.

`tokens.css` (section 3) implements it with a `clip-path` for the chip and a `::after` for the
chip's edge; the screenshot `examples/head-waters/screenshots/fig-folio.webp` shows it at 100 and
300 percent.

## The line under the bar

One line, `--hw-line-width` 2 px, in the edge colour (`--hw-line`), not an accent. The example
drew 2 and 3 px side by side and chose 2: 3 px begins to read as a border. The folio tab
interrupts it where it opens into the page.

## The theme switch: light, dark and system

After the Terminal Delight documentation site
([layout.html](https://github.com/parker-brown-family/terminal-delight/blob/main/docsite/layout.html)
and [td-shell.js](https://github.com/parker-brown-family/terminal-delight/blob/main/assets/td-shell.js)),
whose switch has two states and follows the system until a choice is saved. The family adds the
third state so a person can go back to following the system.

- **One button** at the right of the bar. Each press moves system → light → dark → system. The
  icon shows the current state (a half-filled circle, a sun, a moon); its label says the next.
- **Remembered with the person's account** (one field, for example `theme_preference`), so the
  choice follows them to every device and every app in the family.
- **No flash.** Mirror the account value in a cookie on the family's shared parent domain. The
  server renders `data-theme-pref` and the `dark` class from it. For `system`, a few lines in the
  `<head>` read `matchMedia('(prefers-color-scheme: dark)')` before the body paints and follow
  the device while it changes:

  ```html
  <script>(function(){var r=document.documentElement,p=r.dataset.themePref||'system',
  m=matchMedia('(prefers-color-scheme: dark)');function a(){r.classList.toggle('dark',
  p==='dark'||(p==='system'&&m.matches))}a();if(p==='system')m.addEventListener('change',a);})();</script>
  ```
- **Signed out** (a client on a public page): this device's cookie if there is one, else system;
  the switch sits in the footer and its choice stays on the device.
- **Native apps** read the same account field after sign-in and follow the device before it.

`tokens.json` carries this as `behaviour.theme`, so a builder reads one place.
