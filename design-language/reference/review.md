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
- Ask whether any two products could be mistaken for each other where colour is all that
  differs: put the same words in every product's header and look.

## Answer every item

Tick each item with what changed, or mark it *not taken* with the reason: a number, a rendered
pair, or a decision the product owner already made (the owner's words win). For every accepted
measurement, add a check and a self-test entry, so the failure cannot return.

In the example the review found a 4.12:1 label at a button's light end, outlines at 2.78:1 on
wells, two products 2.91 apart for deuteranopes with marks of the same silhouette, a spacing rule
that two builders could read two ways, and no numbers a native theme could be generated from.
All became checks or tokens. One item was not taken: a time-zone label the owner had decided.

A later round, in the same example, looked at how the settled skin carried to the five products
whose header colours came from a rule: hue from a named theme colour, lightness and opacity copied
from the settled product's glow. Every value passed every check. The rule did what it was built
to do, giving each glow the same weight, and that is where the palettes were dry. Surge's navy
corner read as Stone's slate. Piper's green-black dark ground sat close to Silo's. Stone's slate
was faint at night and heavy by day, Silo's jade was louder than patient records want, and
Scythe's gold spread wider than the button it belongs to. The checks could not see any of this:
colour-blind distance is measured between accents, not between corners and grounds, and contrast
says a palette is legible, not that it belongs to anybody. The reviewer proposed ten value changes
(glow colours, two dark grounds, three reaches, and dark-earth neutrals for Piper from its brand
brown), ran each in a scratch copy of the generator against every check, and all ten were taken
unchanged. Piper's turned out to be a rule, the brand brown at a fixed chroma on the old lightness
steps, and went in as one. The round cost one review and no markup. It earned that cost by
catching two identity collisions that the derivation had produced by design. Later the owner chose
the dictation app's colours himself in a workshop, and that choice replaced the reviewer's dark
earth and burgundy glow for that product. An owner's settled choice outranks a reviewer's proposal,
as it outranks the agent's; it still goes through the checks, and the one value that failed (a
button label at 4.02:1) was lifted by the generator, not by bending the approved colours.
