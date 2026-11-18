---
name: design-language
description: "Design, restyle or extend the look of a product screen, an app, or a family of apps so they read as one family while each product stays recognisably its own. Measures a standard you admire in its source, sets colour roles before colours, writes every rule as a sentence someone can test (type, spacing and proximity, depth, states, motion, the patterns every app repeats), takes each product's colour from an Omarchy theme by one fixed rule, and proves contrast at both ends of every gradient, control outlines, status collisions and colour-blind distance with a script whose self-test shows old wrong values fail. Ships the folio tab, a 2 px title line and a light, dark and system switch remembered with the person's account. Use when about to design or restyle a screen, build a design system, tokens or a style guide, theme an app light and dark, add a product to a family, pick product colours, audit an app's UI, or when asked to make a product look nice, modern, consistent or 'like HC VIDEO'. Not for a one-off marketing page that keeps its own brand."
license: MIT
---

# Design language

A product family looks like a family when its products share the things a person feels without
naming them (type, spacing, depth, how primary, selected and focused are marked) and differ in a
few things a person can name from a corner of the screen (a colour, a mark). This skill produces
that as four artifacts: a short page of testable rules drawn as live specimens, tokens a builder
can drop in (CSS variables and a JSON file a native app can read), a script that proves the
colours, and an audit of the current screens with the changes that help most.

The worked example is a six-product suite, Head Waters, in `examples/head-waters/`: its family
file, its tokens, its design-language pages and screenshots. Everything below came out of making
it, with three rounds of review by the product owner and one by a second AI provider.

## The method

1. **Measure a standard you admire, in its source.** Not its screenshots: its stylesheet and
   components. Count what it actually does (sizes in use, radius uses, spacing steps, how many
   files wear its surface classes, what a test enforces) and sort it into *carry over* and
   *belongs to it alone*. [reference/method.md](reference/method.md)
2. **Roles before colours.** Name what a colour is for (ground, surface, raised, float, inset,
   ink in three steps, edge, control edge, accent, accent ink, accent tint, on-accent, signature,
   five statuses) before choosing a single value. Components name roles, never hex values.
3. **Write every rule as a sentence someone could test.** "A label sits 8 above its field; groups
   holding 16 px gaps sit 32 apart", never "generous spacing". Type, spacing and proximity, depth,
   states, motion and seven patterns. [reference/rules.md](reference/rules.md)
4. **Take each product's colour from an Omarchy theme, by the rule.** The theme gives the hue,
   the product's intent gives the chroma, lightness moves only as far as a check needs, and every
   move is recorded. A new product is a lookup. [reference/omarchy-colour.md](reference/omarchy-colour.md)
5. **Prove it with the script.** `scripts/tokens.py --family FAMILY.py` writes the tokens and
   runs the checks: text at both ends of every gradient, outlines on every surface, statuses
   apart from accents, products apart for colour-blind readers, brands on client pages, drift
   between table and files. `--selftest` puts back every value that was once wrong and proves a
   check still fails. [reference/checks.md](reference/checks.md)
6. **Give every app the same shapes.** The folio tab (the selected menu item opening into the
   page, a bar over its words in the product's colour), a 2 px line under the bar, and one theme
   switch, light, dark and system, remembered with the person's account and applied before
   first paint. [reference/shapes-and-switch.md](reference/shapes-and-switch.md)
7. **Use only openly licensed faces, and read the licence from the file.** The example uses
   JetBrains Mono for titles and tracked-caps labels and Inter for everything read or typed,
   both SIL OFL 1.1.
8. **Draw it.** Every token and pattern as live HTML and CSS built from the tokens, light and
   dark, and for an audit a before and after of each app's worst screen at the width it is used
   (phone, iPad, laptop). Drawings beat sentences; captions make a claim.
9. **Get one review from a second provider**, and mark which choices are feel and which are
   measurement, so the reviewer knows where to push. [reference/review.md](reference/review.md)
10. **Hand the builders one page of changes:** every token renamed, added, removed or changed,
    old and new, breaking changes first. `examples/head-waters/05-changes-for-builders-v3.md`.

## Run it

```bash
python3 scripts/tokens.py --family examples/head-waters/family.py --check
python3 scripts/tokens.py --family examples/head-waters/family.py --selftest
```

For a new family, copy `examples/head-waters/family.py`, name your products, their Omarchy
themes and intents, and run without `--check` to write `tokens.css` and `tokens.json` beside it.

## What went wrong on the way, so you do not repeat it

- A theme's accent used raw: Retro 82's is orange, which is the warning hue, and Nord's light
  accent cannot carry white text. The rule exists because of these.
- A white sheen on a button measured at its dark end only: the label failed at the light end.
- A control outline that passed on white and failed on the grey well it also sat in.
- Two products whose colours were fine for most readers and 2.9 apart for deuteranopes, with
  marks of the same silhouette. Separate them in lightness and shape, not hue alone.
- Per-product corner shapes (an engraved groove, a cut corner, a stripe): the owner replaced
  them all with one folio tab. Identity comes from colour and mark; shape is shared.
- Marks drawn by an agent treated as final. Label them placeholders.

## Files

- `scripts/tokens.py`: the generator and checks (standard library Python; 3.11+ to read a theme).
- `reference/`: the method, the rules, the colour rule, the checks, the shapes and switch, the
  review, and [sources.md](reference/sources.md): every source used, linked, with the date read.
- `examples/head-waters/`: `family.py`, `tokens.css`, `tokens.json`, `specimens.css` (every
  pattern built from tokens), two design-language pages, the builders' change sheet,
  screenshots, and the OFL licences of the two embedded faces.
