# The review by a second provider

The agent that drew the language should not be the last to judge it. Get one review from a model
of a different provider, one round, and treat its findings the way a build treats a failing test.

## Brief the reviewer

- Point it at the pages, the token files and the script, not at your conclusions.
- Ask it to measure: contrast at the light ends of gradients and on the actual label positions,
  outlines on every surface, colour-blind distance between products, and the marks at 16 px
  with the names covered.
- Ask it to name states the mockups leave out (untouched, edited, submitting, empty) and flows
  that take more steps than they should.
- Ask what a builder applying the tokens to a native app would be missing.
- Tell it which choices are feel and which are measurement, so it pushes on the right ones.

## Answer every item

Tick each item with what changed, or mark it *not taken* with the reason: a number, a rendered
pair, or a decision the product owner already made (the owner's words win). For every accepted
measurement, add a check and a self-test entry, so the failure cannot return.

In the example the review found a 4.12:1 label at a button's light end, outlines at 2.78:1 on
wells, two products 2.91 apart for deuteranopes with marks of the same silhouette, a spacing rule
that two builders could read two ways, and no numbers a native theme could be generated from.
All became checks or tokens. One item was not taken: a time-zone label the owner had decided.
