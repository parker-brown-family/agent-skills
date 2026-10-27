# Grading with Jev

The grading passes in stages 5 and 6 are many small judgements of the same shape, which is
what a System One model is for. Jev (TypeSafe's model, also served by OpenRouter at
`/v1/systemone`) takes application state plus a typed question and returns a probability,
in place of prose to parse. A **Noul** answers whether one statement holds, as a single
probability. A **Score** places something on described, ordered levels and returns a
distribution over them. Code keeps everything else: who said what, which record was
researched, the weights, the tiers and the tallies. The model never sees a rule, and the
rule never sees a sentence.

Any model can run these passes by hand. What Jev adds is the probability on every answer,
which is what lets code put a cut-off on it, mark the answers near one, and measure the
whole run against its traps.

## Two frames that never meet

| Frame | Fields | Never contains |
|---|---|---|
| reasoning | the episode's own metadata; the speaker; the verbatim quote; the restatement | any record fact |
| record | the speaker; the restatement; facts found by research, each with its source kind and date; ordinary explanations found; what is not public; the case timeline | the speaker's words |

When a list is empty, the frame says research looked and found none, as a separate note
field, so that an empty list never reads as a finding by default. The record frame always
carries the case timeline, or a line saying no case timeline applies: this is the field the
missing-deciding-fact trap added. Batch every question over one frame into one request.
Asking them separately costs one request and one copy of the state per question for the
same answers.

## The questions

Reasoning frame, one request:

| Question | Type | Asks whether, in the speaker's own words… |
|---|---|---|
| asserted | Noul | the proposition is presented as true, even with "I think" or "it appears", rather than floated, disbelieved, asked, or reported as someone else's |
| rests_on_absence | Noul | the support is something expected that is missing, unexplained or unreported |
| rests_on_private_source | Noul | the support is a private conversation the listener cannot check |
| rests_on_speaker_standing | Noul | the speaker's experience or authority stands in for evidence the listener could examine |
| immunised | Noul | contrary evidence is treated as produced by the concealment, so that it counts in the claim's favour |
| names_what_would_refute | Noul | the speaker names what would settle the claim |
| checkable_in_public | Noul | public material could check the proposition |
| leap | Score 0–3 | how far the proposition goes beyond the observation the speaker points to: 0 restates it, 1 adds the plain reading, 2 concludes identity, intent or coordination the observation does not show, 3 asserts a hidden actor or cover-up nothing observed shows |

Record frame, one request:

| Question | Type | Asks whether… |
|---|---|---|
| record_confirms | Noul | the researched record confirms the proposition, read with the times in the case timeline |
| record_contradicts | Noul | the researched record contradicts it, read the same way; an empty record must not contradict |
| ordinary_explanation_fits | Noul | a listed ordinary explanation covers the observation as well as the claim does |

Each Noul carries criteria for true and false with two or three short examples of each,
written from the trap pairs in `missteps.md` and never from the case being graded.

The matrix is one request per case and row, with one Score per hypothesis over the four
levels in `hypotheses.md`. The judge-by line tells the model to take the evidence as stated
at the standing given, to judge this one hypothesis against this one piece of evidence and
nothing else, and that who holds a hypothesis is no reason to believe it.

## What an answer means

Cut the Noul probabilities at **0.245 and 0.755**, so that 0.245 to 0.755 is the unsettled
band, and treat **under 0.055 or over 0.945** as confident. Put the cut-offs at half
hundredths, so that no answer can sit exactly on one. A weak move counts when its answer
is 0.755 or more, or when the leap is 2.5 or more. A deciding answer within 0.05 of a
cut-off is marked as one that could flip between identical runs.

## What it cost

The first run made 170 calls for 85 claims and 56 for the matrix rows, for about two cents
in all, with a median latency near 155 ms. Cost is no reason to grade fewer claims or to
skip the perturbation rerun.

## Where this was built

On the machine this skill was written on, the method also exists in executable form, in
private repositories:

- **`jev-decision-spec`**: `specs/claim-ground/` and `specs/competing-hypotheses/`, the two
  passes and the matrix as Jev Decision Specs, with their trap anchors at the fictional fair,
  their meaning maps, invariants, falsifiers and changelogs. `bin/jds probe` runs the traps
  and `bin/jds run` runs a spec over an items file. The `jev-decision-spec` skill is how to
  write a new one, and its first step, writing the traps, is stage 3 above.
- **`research-delight`**: the `source-figure` kind (the dossier on a source) and the
  `claim-audit` kind (one subject per spoken claim, with its grade derived from a claim-ground
  run), and the first run's directory under `runs/`, which holds the claims ledger, the
  research rounds, both Jev runs, the analysis scripts and a `SOURCES.txt` for everything
  downloaded.
- **`jev-integrations`**: the Jev client (`JevClient.ask_many` for a batched request), and the
  key, which stays server-side.

Anywhere else, run each stage by hand or on whatever typed model is available, and keep the
two frames apart.
