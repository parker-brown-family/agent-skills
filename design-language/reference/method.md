# The method, in order

## 1 · Measure a standard you admire

Pick the product whose look the family should live near and read its source, not its
screenshots. In the example the standard was HC VIDEO, a web app by the same company. What was
measured, with `grep` over its components:

| Measure | What it showed | Verdict |
|---|---|---|
| Surface classes | nine named roles; 98 of 179 component files wear one; a unit test fails a hand-painted surface | carry the mechanism: roles as tokens, and a guard test |
| Depth | inset, surface, float: a gradient darkening 1 to 2 percent, a lit 1 px top edge, a two-part shadow | carry, as four steps |
| Primary vs selected | primary a solid gradient fill; selected a tint with an edge, a separate class | carry the split |
| Radius | 8 px 375 uses, 12 px 80, full 72 | carry 8 / 12 / full, add 16 for sheets |
| Body size | 14 px 516 uses, 16 px 14 uses | leave: body 16 |
| Phone buttons | the medium button shrinks to 28 px tall on phones | leave: 44 px minimum |
| Focus ring | 3 px turquoise at 35 percent: 1.3:1 on white | leave: solid 2 px ring at 3:1 |

The habit: every claim about the standard is a count or a value from its source, and every
verdict is *carry* or *leave*. Paint usually lives in shared classes and layout lives page by
page; say which, because it decides what the family must standardise.

## 2 · Roles before colours

Write the role table first. The example's roles: `ground` (the page), `surface` (cards and
lists), `raised` (bar, dock), `float` (menus, popovers, dialogs), `inset` (wells, tracks,
disabled), `field`, `ink`, `ink-2`, `ink-3`, `edge` (decoration), `edge-control` (an outline that
identifies a control), `accent` (fills), `accent-ink` (text and icons in the product colour,
the focus ring), `accent-tint` (a selected item's background), `on-accent` (text on a fill),
`signature` (the folio bar), and statuses: `danger`, `warning`, `success`, `neutral` (no
judgement: scheduled, idle), `done` (a finished step: signed, settled). Only then pick values.

The accent marks four things only: the one primary action in a view, the selected item, focus,
and live state. Headings, body and icons are ink. Statuses never stand in for an accent.

## 3 · Testable rules

See [rules.md](rules.md). Each rule is a sentence with a number in it. If two builders could
follow the page and produce different screens, the rule is not finished.

## 4 · Colour from themes

See [omarchy-colour.md](omarchy-colour.md).

## 5 · Checks

See [checks.md](checks.md). Treat the checks as the definition of done for colour, and add one
whenever a review finds a failure the checks missed, together with a `--selftest` entry that
puts the failing value back.

## 6 · Shapes and the switch

See [shapes-and-switch.md](shapes-and-switch.md).

## 7 · Type

Use faces whose licence allows embedding and redistribution, and read the licence from the
font's own licence file, not a web page. The example asked for the face of a terminal skin the
owner liked; the skin set no face, so its chrome used the terminal's default, JetBrains Mono.
Check that sort of claim in the source before building on it.

## 8 · Draw it

The page that carries the language is drawn: every token and pattern as live HTML and CSS built
from the token file itself, so the page cannot drift from the tokens. Light and dark side by
side. In an audit, the worst screen of each app before and after at the width it is used, as real
markup, not a picture. Workflows count: where a task takes more steps than it should, draw the
flow before and after with the step count.

## 9 · Review, then hand over

One round from a second provider ([review.md](review.md)), then one page of changes for the
builders: renamed, added, removed, changed, breaking first, each with old and new value.
