# Mechanism

How the register tabs and the copy button actually work. Framework-agnostic —
the markup and CSS below work in a static export, a React app, or hand-written
HTML.

## Six rules

1. **Every register in the DOM, inactive ones hidden.** All registers stay
   crawlable and findable with the browser's own find. Registers behind a fetch
   are invisible to search and to anyone reading with scripting off.
2. **Tabs are radio inputs plus CSS sibling selectors.** No JavaScript needed
   for the swap, so it survives a blocked hydration and a strict CSP, and it
   works on a statically prerendered page before anything boots.
3. **Full tablist semantics.** `role`, `aria-selected`, `aria-controls`, and
   left/right arrow traversal between tabs.
4. **One URL per article; registers are hash fragments.** `#tldr`, `#eli5`,
   `#technical`. Not separate slugs — several URLs for one finding compete with
   each other to rank for it.
5. **Copy is scoped to the visible register.** See below.
6. **No tab bar when only the default register exists.**

## The tab component

Radios come first so the sibling selectors can reach both the tab labels and the
panels.

```html
<div class="register-dossier">
  <input type="radio" name="register" id="r-tldr" checked>
  <input type="radio" name="register" id="r-eli5">
  <input type="radio" name="register" id="r-technical">

  <div class="folder-tabs" role="tablist" aria-label="Registers">
    <label for="r-tldr">tl;dr</label>
    <label for="r-eli5">ELI5</label>
    <label for="r-technical">Technical</label>
  </div>

  <div class="folder-body">
    <section class="register-panel" id="tldr" role="tabpanel">…</section>
    <section class="register-panel" id="eli5" role="tabpanel">…</section>
    <section class="register-panel" id="technical" role="tabpanel">…</section>
  </div>
</div>
```

```css
.register-dossier > input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.register-panel { display: none; }

#r-tldr:checked      ~ .folder-body .register-panel:nth-child(1),
#r-eli5:checked      ~ .folder-body .register-panel:nth-child(2),
#r-technical:checked ~ .folder-body .register-panel:nth-child(3) { display: block; }

.folder-tabs label { border-bottom: 2px solid transparent; cursor: pointer; }

#r-tldr:checked      ~ .folder-tabs label:nth-of-type(1),
#r-eli5:checked      ~ .folder-tabs label:nth-of-type(2),
#r-technical:checked ~ .folder-tabs label:nth-of-type(3) { border-bottom-color: currentColor; }

/* The inputs keep keyboard focus, so the focus ring has to be drawn on the label. */
#r-tldr:focus-visible      ~ .folder-tabs label:nth-of-type(1),
#r-eli5:focus-visible      ~ .folder-tabs label:nth-of-type(2),
#r-technical:focus-visible ~ .folder-tabs label:nth-of-type(3) { outline: 2px solid; outline-offset: -3px; }
```

Two things that bite:

- **`opacity: 0` and not `display: none`.** A hidden-by-display input is not
  focusable, and the tabs stop working from the keyboard.
- **Source order decides overrides at equal specificity.** If a later rule sets
  `display: none` on the panels or the rail, it beats an earlier media query
  with the same specificity. Put the overriding rules last.

## Progressive enhancement

About twenty lines, and everything it adds is optional:

- Read `location.hash` on load and check the matching radio, so a deep link
  opens its register. With scripting off the reader lands on the default, which
  is the intended default anyway.
- Update the hash when a tab is chosen, so the URL is shareable.
- Maintain `aria-selected` on the labels and move focus with the arrow keys.

## Copy, scoped

The copy button hands a register to someone who will paste it elsewhere —
increasingly into another agent — so it needs a metadata header:

```
<title>
Written by: <byline>
Date: <date>
Register: <register label>
Category: <category>
Source URL: <canonical article url>

<the register's text, structure preserved, links inlined as: label (href)>
```

Convert the register's own HTML: headings become their own lines with blank
lines around them, list items get a leading `- `, table rows join with ` | `,
and anchors collapse to `label (href)` so the reference survives the paste.

### The defect worth not copying

There is a live implementation of this on the BFS articles that collects copy
sections by walking *up* to the article root and then querying *down* for every
marked section:

```js
const root = button.closest('[data-copy-root]');
const parts = [...root.querySelectorAll('[data-copy-section]')]
  .map((s) => s.textContent.trim());
```

On a multi-register page that root contains every register, so pressing Copy
inside one register returns all of them concatenated, unlabelled, including the
two the reader can't see.

**Pass the register's content in, don't go looking for it.** A copy button that
receives one register's HTML as a parameter cannot reach the others — the bug is
impossible by construction rather than avoided by care. That's the shape to
build.

## Theme discipline

Where the property ships more than one theme, every article component takes its
colours from that property's tokens and never a literal. A hard-coded accent —
`linear-gradient(135deg, #0E6E78, #123A4F)` on a call-to-action, say — reads as
a foreign object the moment the reader picks a light theme.

Decorative graphics that must survive every ground use `currentColor`, which is
also the reason to inline an SVG rather than reference it with `<img>`: an
embedded SVG can't inherit the page's colour.

Give each register one token so its kicker, its active tab, and its lead callout
agree, and keep those hues low-saturation — they have to sit on both a near-black
and a near-white ground.
