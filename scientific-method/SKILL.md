---
name: scientific-method
description: "Put a claim, a theory or a whole argument to the test, and hand back which steps the record confirms, which it contradicts, which an ordinary explanation already covers, which rest on a weak move, and which are reasonable conjecture still worth pursuing. Pulls every claim out word for word, writes the competing hypotheses before weighing anything, writes traps that would embarrass the grading, gathers the record apart from the argument, grades each claim's reasoning and its record in two passes that never see each other, weighs the hypotheses only on evidence that tells them apart, checks every striking coincidence against how often chance would produce it, and tests the grader before trusting it. Use on a podcast, video, article, thread or pitch that makes contested claims ('put this to the test', 'fact-check this episode', 'is this conspiracy theory any good', 'stress-test this theory', 'what would refute this', 'competing hypotheses', 'is this a coincidence'), and on our own conjectures: a bug's root cause, a product bet, a surprising result ('are we sure', 'what else could explain this', 'scientific method', '/scientific-method'). Never decides anyone's guilt, honesty or motives."
license: MIT
---

# Scientific method

Someone has made a case. It might be a guest on a three-hour podcast, a thread, a colleague
in a design review, or us, explaining why a test fails. A case is a chain of claims of very
different strength, and a few of them carry the rest. This skill sorts the chain. For each
claim it reports how much ground it stands on, and for the case as a whole it reports which
of the competing accounts the evidence actually separates. It never reports what happened,
and it never reports what anyone intended.

The method was assembled on its first full run: a long podcast episode arguing that a
public shooting was carried out by a hidden actor, with 85 claims, three cases and four
competing accounts for each, two sets of Jev calls, and an aircraft's movements rebuilt from
public flight-tracking archives. Each stage below carries what that run taught. Where a
stage names a tool, `tools/` has a version that runs anywhere Python 3 does, and
`reference/` has the detail.

## Size it before starting

| Pass | When | What runs |
|---|---|---|
| Quick | one claim, one coincidence, a question in chat | stages 1, 2, 4 and 7 by hand, answered in chat |
| Full | an episode, a report, a body of claims, anything someone will be shown | every stage, delivered as an annotatable page |

A quick pass that finds a load-bearing claim it cannot settle becomes a full pass. Say which
pass you ran.

## 1. The ledger

Pull every claim out **verbatim**, with who said it and where (a timestamp, a page, a
line). Keep the speaker's wording and the captioner's errors; a paraphrase is already an
interpretation. For each claim, record:

- **A one-sentence restatement, written before any research.** Written first, research cannot
  bend it. After the first grading run, check every restatement against its quote again: on
  the first run one restatement merged two moments the speaker had kept apart, and the record
  then contradicted something he never said. Correct it, and log the correction.
- **Whether it is load-bearing**: does the case fall without it? The page leads with these.
- **Which hypothesis it serves**, as the auditor's reading, stored as data.
- **Floated or asserted.** "Here's an idea, and it's insane" is floated. A floated idea is shown
  as floated and never counted against the speaker.

Keep three other lists beside the claims. The **method statements** record what the speakers
say good reasoning looks like, and what they say would settle the question. The strongest
test of a case is the one its own author set, so grade against it and quote it. The
**pushbacks** record each place one speaker challenged another, and what became of the
challenge. **Track records** come from a dossier on each source: their past contested claims
and the evidence those met later, the expertise they claim beside what independent sources
confirm, how the work is paid for, and named critics and defenders. A pen name stays a pen
name; never try to establish who is behind it.

## 2. The hypotheses, before the evidence

Write at least four accounts for each question before weighing anything, and record who
holds each one:

1. the ordinary or official account;
2. the ordinary account plus a smaller concealment, such as an agency hiding its own failure;
3. a variant short of the claimant's, such as a second actor without a conspiracy;
4. the claimant's account, stated as strongly as they state it.

With only two accounts, every awkward fact for one reads as support for the other. The
middle accounts catch the facts that embarrass the official version without needing the
grand one. When a piece of evidence contradicts every account on the list, the list is
missing one: add it rather than forcing the row. See `reference/hypotheses.md`.

## 3. Traps first

Before grading anything, write the cases that would embarrass the grader, in matched pairs:
the same input with one part changed. The changes come from guide words: *no*, *more*,
*less*, *as well as*, *part of*, *reverse*, *other than*. A claim supported by a missing
release, beside the same claim supported by a released log. Fingerprints recast as a
frame-up, beside fingerprints accepted as contrary evidence. Set every trap at a **fictional
event**, so that a right answer can only come from reading the input and never from what the
grader knows about the real case. Add positive controls, plain facts that must come back
confident and unflagged.

Write one trap for **the missing deciding fact**: a claim whose truth turns on a fact the grader
has not been shown. On the first run that trap failed. A claim about the timing of a shot was
graded without the shot's time in the grader's state, so it could be neither confirmed nor
contradicted, and the case timeline was added to every record the grader sees.

## 4. The record, gathered apart from the argument

Research each claim against primary sources, and let the research see the restatement, never
the speaker's framing.

- **Cite or flag.** Every fact carries its source, the kind of source, and a date.
- **Facts are neutral.** Verdict words ("debunked", "confirms") go in the researcher's note and
  never in a fact the grader will read.
- **Unknown is not zero.** A claim nobody researched has *unknown* record answers, never
  "unsupported". "Research looked and found nothing" is its own finding, flagged, and it
  differs from "nobody looked".
- **What is not public is listed as not public**: a sealed report, unreleased footage. That
  absence is a fact about the record, and it is no evidence for any account.
- **Rebuild primary data where it exists** instead of quoting someone's reading of it. On the
  first run the aircraft's own position reports, pulled from three public archives and
  plotted, decided more than any article about them.
- **Count independent sources.** Five outlets repeating the speaker are one source.
- **Gather the ordinary explanations on purpose**: what accounts for the observation with no
  concealment at all, from the record.

## 5. Grade every claim twice, blind

Two passes, and neither sees the other's evidence.

- **The reasoning pass** sees the speaker's words and the restatement, and never the record.
  Does the speaker assert it or float it? Does the support rest on an absence, on a private
  conversation nobody can check, or on the speaker's own standing? Is contrary evidence recast
  as part of the concealment? Does the speaker name what would refute it? Could public
  material check it? How far does it leap beyond the observation offered, from 0 to 3?
- **The record pass** sees the restatement, the facts, the ordinary explanations, what is not
  public and the case timeline, and never the speaker's words. Does the record confirm it?
  Contradict it? Does an ordinary explanation cover the observation as well as the claim does?

They are kept apart because an argument inside a grader's state is a thumb on the scale. A
confident speaker moves the reading of a record, and a damning record moves the reading of
a speaker's words. Each question is a yes-or-no or a placement on a described scale, and
answers come back as probabilities. Code combines them into a tier, in this order:

| Tier | When |
|---|---|
| floated | the speaker does not assert it |
| contradicted | the record contradicts it and does not confirm it |
| contested | the record leans both ways |
| solid | the record confirms it and does not contradict it |
| explained | an ordinary explanation fits as well |
| shaky | carried by a weak move, or a hidden-actor leap |
| unverifiable | public material could not check it |
| solid conjecture | a modest leap the record does not contradict |
| open | the rest |
| not graded | a deciding answer is unknown. It is never put in *open* |

Some combinations mean something on their own and get routed rather than tiered. When the
record cuts both ways, a person reads it. Immunised and contradicted together means the claim
*explains away the record*: it cannot lose on the evidence as argued. A private-source claim
that came back confirmed probably had only its public part confirmed. A hidden-actor claim
that came back confirmed means the record packet needs checking first. Any answer within
0.05 of a cut-off could flip between identical runs, so it is marked. The weak moves, each
with a matched example, are in `reference/missteps.md`. The calls themselves, written for
Jev, are in `reference/grading-with-jev.md`.

## 6. Weigh the hypotheses on the evidence that separates them

Lay the evidence out as rows and the hypotheses as columns (Heuer's Analysis of Competing
Hypotheses). Each row carries its **standing**: established, reported, disputed, or claimed.
Place every cell on four levels:

- 0, predicted: had this been missing, it would count against the hypothesis;
- 1, comfortable;
- 2, strained: it fits only with an added assumption, such as a coincidence, an error, or
  someone hiding or planting something;
- 3, contradicted.

Then let code do three things:

- **Throw out rows that cannot discriminate.** A row's diagnosticity is the spread between
  its highest and lowest cell. A row every hypothesis sits comfortably with says nothing
  about which is true, however striking it sounds. Only rows with a spread of 0.75 or more
  enter the tally. On the first run, every anomaly the episode leaned on was in this
  non-diagnostic pile, and the rows that did discriminate all pointed the same way.
- **Tally contradiction and strain per hypothesis, weighted by standing** (established 1.0,
  reported 0.8, disputed 0.5, claimed 0.3). The hypothesis that survives is the one carrying
  the least contradiction, which is a different thing from the one with the most rows in its
  favour. Read strain beside it. An account that is never contradicted but is strained on
  every row survives by assumption, and that is what an immunised account looks like in a
  matrix.
- **Retally on record-only rows**: established and reported rows, with every row that relays
  a party's own claim removed ("X has said that…"). On the first run, reported speech had been
  scored as if it were established fact, and this retally caught it. Say which orderings hold
  and which become a near tie.

`tools/ach_tally.py` does all three and reports ties instead of breaking them by list order.
The worked example is `tools/examples/marston-fair.matrix.json`.

## 7. Test every coincidence against chance

A striking alignment ("it began its descent at the very moment of the shot") is evidence
only if chance would rarely produce one as good. Count **every** comparable event in the
window, not only the ones that look meaningful, take the tolerance the claim itself implies,
and measure how much of the window lies that close to some event. That share is the chance
that a moment picked at random would look just as well timed.

```
python3 tools/coincidence.py --window 12:00 12:49 --tolerance 60 <every event time> --at <the observed moment>
```

Six comparable events in a 49-minute window, with a tolerance of a minute either side, cover
about a quarter of it. A reading can be right to the minute and still not be evidence. Then
check the axes the coincidence leaves out. A match in time says nothing about place, and an
aircraft on time can be hundreds of kilometres from the scene.

## 8. Test the grader before trusting it

- **Pre-register falsifiers** before the full run, written as checks over the answers. For
  example: if more than a fifth of claims land in the unsettled band on whether the speaker
  asserted them, the question cannot read hedged speech. Report the ones that fire. Never
  edit them out.
- **Perturb the frame.** Change one thing that should not matter, such as the description of
  the episode, rerun, and record which grades moved. Report it as a map of which change moved
  which claims and by how much, never as an average shift. On the first run, changing only the
  episode's one-line description moved 13 of 85 grades. The page said so.
- **Compare with independent labels**: research agents' verdicts, written apart from the facts
  and never shown to the grader. Report agreement on contradiction and agreement on support
  separately; the first run agreed on 11 of 14 contradictions and 1 of 11 supports, which
  showed a grader that is cautious about calling anything solid.
- **Repeat calls** to measure jitter, and mark every answer near a cut-off.
- **Run it once on an unseen case** before using the same grading on new material.
- **Ask for human labels.** Until a person has graded some claims, the tiers are a first
  reading and not a calibrated one. Say so on the page.

## 9. Deliver

A full pass is delivered as a page the reader can annotate, with the pictures carrying it:
the ledger as a timeline, the ground chart (claims by tier), each hypothesis matrix with its
non-diagnostic rows greyed, the coincidence against its base rate, any primary data rebuilt
and drawn, and the grader's own checks. Draw unknown as unknown: a claim not graded sits in
its own column and does not vanish.

- Lead with the load-bearing claims.
- Credit good practice where it happens: a claim that names what would refute it, or an
  ordinary explanation the speaker raised and examined.
- Watch for the pattern the first run kept finding. The right alternative was raised out
  loud, then set aside without being measured. Two people did the hard part well and stopped
  one measurement short. Say where that happened, because it is the most reusable lesson and
  it applies to our own reasoning as much as anyone's.
- Show the grader's weaknesses on the same page as its findings.
- The page reports ground. It never calls anyone a liar and never decides guilt, which is a
  court's job. Anything for the public is written separately, by whoever writes for the
  public, from the findings.

## On our own conjectures

The same stages, smaller, apply when the case is ours. In debugging, the ledger is the
observations with where each came from. The hypotheses include "the instrument is wrong"
and "it did not happen the way we think". The trap is the test that would pass without the
fix. The record is the logs and measurements, gathered before the favourite explanation is
written down. The coincidence check is the flake rate: how often does this test fail with
nothing changed? The falsifier is written before the fix: what result would prove it wrong?
When two independent checks agree against our own label, the label is the first suspect.

## Files

- `reference/missteps.md`: the weak moves, each with a matched example at the fictional fair.
- `reference/hypotheses.md`: writing the set, standing, diagnosticity, reading the tallies.
- `reference/grading-with-jev.md`: the two grading passes and the matrix as typed Jev calls,
  the cut-offs, and the tools this skill grew out of.
- `tools/ach_tally.py`: the matrix tally. `tools/coincidence.py`: the base rate.
  `tools/test_tools.py`: their tests (`python3 -m unittest discover -s tools`).
