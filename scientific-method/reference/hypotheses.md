# Competing hypotheses

The matrix is Richards Heuer's Analysis of Competing Hypotheses, from his CIA monograph
*Psychology of Intelligence Analysis* (1999), with three changes from the first run: cells
on four described levels rather than plus and minus, rows weighted by how the evidence
itself stands, and a second tally over the record alone.

## Writing the set

- **Four or more, written before any evidence is weighed.** The ordinary account; the
  ordinary account plus a smaller concealment; a variant short of the claimant's; the
  claimant's. Add any account a serious person actually holds.
- **Each in the words its holders would use, as strongly as they would put it.** A weakened
  version of someone's account is a different hypothesis, and beating it shows nothing.
- **Record who holds each one**, and tell the grader that who holds it is no reason to
  believe it.
- **Keep them exclusive enough to disagree.** Two accounts that predict the same thing on
  every row are one account, and splitting them only halves its tally.

## Writing the rows

- **One fact per row.** Two signs that a row bundles facts that pull different ways: it
  contradicts both the official account and the claimant's, or the grader's answer for one
  cell splits between *predicted* and *strained* with little in between. Split it. On the
  first run the second sign fired on 8 cells, and one of the traps turned out to bundle two
  facts and was split before the full run.
- **Standing is set by research and stored as data**: *established*, a primary public
  record no party disputes; *reported*, stated by prosecutors, police or an official
  report and not yet tested at trial; *disputed*, reported and contradicted by another
  credible source; *claimed*, asserted by a party and not independently confirmed. The
  grader is told the standing and never decides it.
- **Mark rows that relay a claim** ("the investigator has said…"). The sentence is true; its
  content is only a claim, and its standing is the claim's.
- **Include what each side cites and what neither side cites.** Record which side cites each
  row. A matrix built from what everyone already agrees on has no diagnostic rows and can say
  nothing. On the first run, a falsifier was set on that in advance: more than half of a
  case's rows non-diagnostic means the evidence was chosen badly.

## Levels

| Level | Meaning |
|---|---|
| 0 predicted | the hypothesis leads one to expect this; had it been missing, that would count against it |
| 1 comfortable | the hypothesis sits with it without any added assumption, though it does not particularly predict it |
| 2 strained | the hypothesis accommodates it only by adding an assumption it does not otherwise need: a coincidence, an error, someone hiding or planting something |
| 3 contradicted | the hypothesis is contradicted by it |

A grader returns a distribution over the four. Code reads its expected level for the
spread, P(strained) for strain, and P(contradicted) for contradiction.

## Reading the tallies

- **Diagnosticity is the spread**: highest expected level minus lowest. Rows under 0.75 are
  consistent with every hypothesis and stay out of the tally. Show them greyed in the matrix
  so the reader can see what was left out and why.
- **Least contradicted survives.** Rank by weighted contradiction, break ties on strain, and
  report an exact tie as a tie.
- **Strain is where immunisation shows.** An account with no contradiction and heavy strain is
  surviving one assumption at a time. Say how many assumptions it needed.
- **The record-only retally tests whether the ordering leans on the weaker rows.** Drop
  disputed and claimed rows and every row that relays a claim. If the ordering holds, say so. If two accounts become a near tie,
  say that instead; on the first run one case's two single-shooter accounts became a near
  tie on the record alone, and the page reported the tie.
- **A ranking is a ranking.** The least contradicted account is the one the evidence gathered
  so far strains least. It is not proved, and new evidence enters as new rows.
- **Unknown cells stay unknown.** A row with an unscored cell is shown and left out of the
  tally, never filled with a level.

## Known leanings of a model grader

The first run's matrix grader leaned in two ways, both caught by its traps and recorded as
known failures rather than tuned away. An exotic hypothesis drew about half a level of
strain on a row that was neutral to it; the 0.75 diagnosticity cut keeps such a row out of
the tally, so it moves no conclusion. And the claimant's account was under-credited on its
own claimed evidence, so read those cells as a floor on its fit rather than a measurement of
it. Check both in your own run before reading a tally.

`tools/ach_tally.py` implements all of this over a JSON matrix.
`tools/examples/marston-fair.matrix.json` is a worked example where the ordering changes on
the record alone.
