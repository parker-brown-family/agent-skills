---
name: graded-gates
description: "Plan and build a feature by grading it first: the grade sets how many gates a person approves before code exists, a tracer round proves the architecture, and the build then runs without stopping for the person until a completion brief. Use for \"graded-gates\", \"grade this\", \"run the gates\", or when a person asks for a planned build with approvals. Not for a typo, a rename or a one-line config edit."
license: MIT
disable-model-invocation: true
---

# Graded Gates

Meet the problem, grade it, and let the grade decide how much of a person's attention the planning gets. A hard problem passes more gates. Once the plan is approved the build runs without the person, and it ends in a brief that says what was done and what is doubted.

The four gates (product, architecture, program design, vertical slices) come from Dex Horthy's software-factory playbook at HumanLayer. The rest of this workflow, and this text, are our own.

## Words

One word for each idea, so a plan, a brief and a message all say it the same way.

| Word | It means |
|---|---|
| **grade** | how hard the problem is, out of ten, judged when you meet it |
| **gate** | a planning stage a person approves |
| **tracer round** | a hello world sent through every system the feature touches |
| **seam** | a place where two systems meet |
| **surface** | something exposed: a screen, an endpoint, a file format, an attack point |
| **brief** | the page a person reads and comments on |
| **notes map** | the reader's comments, each tied to the item it is on |

## The stages

| # | Stage | What it makes | Who |
|---|---|---|---|
| 1 | Grade | a number and one line | you, at once |
| 2 | Tracer round | a hello world through every seam | you |
| 3 | Gate: product | the problem, the measure of success, screens | person approves |
| 4 | Gate: architecture | what it touches, data, flow, surfaces | person approves |
| 5 | Gate: program design | files, types, the specification, and the tests by name | person approves |
| 6 | Gate: slices | the build order, each slice working end to end | person approves |
| 7 | Second opinion | findings on the plan, answered | another model or person |
| 8 | Build | the slices, each proven | you, without the person |
| 9 | Two reviews | security findings; everything else | you or a reviewer |
| 10 | Completion brief | what was done, doubts, follow-ups | person reads |

### Grade

Say it before writing any document: **Grade 5/10: one surface, a shape I have built before, cheap to undo. That buys one gate.** It is a judgement, so make it quickly. Two things move it: how long the work could be wrong before anyone notices, and what undoing it costs. File count, line count and duration do not. A person's number wins.

| Grade | Gates |
|---|---|
| 1–3 | none. Say the grade and do the work |
| 4–6 | one. Stages 3 to 6 are one short plan with one approval |
| 7–10 | four, in order, each approved before the next |

The grade is a prediction, so check it. Two gates in a row approved with nothing changed and nothing questioned mean it was too high: say so and fold what is left into one plan. A fork you cannot choose between means it was too low: say so and open the next gate properly. At the end, write down what the number should have been.

### Tracer round

Grade 4 and up. Before the gates, send a hello world through each system: the thinnest real path from what the person touches to where the data lands, with stand-ins behind it. It proves the architecture, the surfaces and the seams, and it finds the seam that does not hold while changing it is cheap. Show it running. It is thrown away or kept on a branch; it is never quietly shipped as the feature.

### The gates

Each gate is one document in `docs/plans/<feature>/`. Summarise it as a brief (see *Briefs on the page*) or in ten lines or fewer, and ask for approval. Anything but a clear yes means change it and ask again. A person can circle back to an earlier gate, and so can you: if a later gate shows an approved decision is wrong, say so, reopen that gate and get it approved again.

- **Product.** The problem in the user's words, one measured result, and a mockup for anything a person will look at. No databases, endpoints or file names.
- **Architecture.** Read the code first. What it touches, the data, the order things call each other, every seam and every security surface. Name the points that need common sense rather than code, and say for each who supplies it: a person, a model, or a rule. That is the judgement surface.
- **Program design.** Files, types and signatures with no bodies. The specification, and the tests by name with what each proves, written before any of them exist. A numbered list of the decisions you are least sure of.
- **Slices.** Build order, one line each. Every slice runs end to end. Never all of one layer first.

### Second opinion

Before building, one reader who did not write the plan looks for what it missed: another model, or a person. One round. Answer every finding, by a change or a reason.

### Build

Build one slice at a time, prove it by running it, commit it, record it in the status file, and go on to the next. **Do not ask whether to continue.** Stop and ask only when a slice breaks something the person approved, or when a step cannot be undone without them. Any other decision the plan left open is yours: make it and record it for the completion brief.

**Keep one agent on the build.** In two measured jobs, of three slices and seven, a fresh agent for each slice passed the same tests as one agent doing all of them and cost 1.7 and 2.4 times as much, because each one paid to start and to read the code again. Both jobs took one agent under 30 turns. Hand over to a fresh agent, from the status file, only when a session has grown genuinely long; whether that pays has not been measured.

A test must fail against the code before the change. Never skip or weaken one to get to green.

### Two reviews

Security is reviewed as an attacker would. Everything else is reviewed as a colleague would, looking for what would make the work better. Prove a finding with a run before fixing it.

### Completion brief

What was done and how it was proven, the decisions you made that nobody made, what you doubt, and what should follow. Link the evidence. Say what the grade should have been.

## The status file

`docs/plans/<feature>/00-status.md` is the memory. Create it with the grade, and update it at every approval and every slice.

```markdown
# Status: <feature>

Grade: 7/10 — <one line>
Stage: 4 gate: architecture
Turned out to be: <filled in at the end>

- [x] 1 grade
- [x] 2 tracer round — <where it ran>
- [x] 3 gate: product — approved <date> — [brief](03-product.html)
- [ ] 4 gate: architecture
- [ ] 5 gate: program design
- [ ] 6 gate: slices
- [ ] 7 second opinion
- [ ] 8 build
  - [ ] slice 1 — <one line>
- [ ] 9 two reviews
- [ ] 10 completion brief

## For a fresh session
<anything decided in conversation>
```

A session that finds this file reads every document beside it and carries on from the first unchecked line. It never redoes an approved gate. Nothing important may live only in the conversation.

## Briefs on the page

A gate is a decision a person makes, so where the `briefing` skill is installed each gate's summary is a brief: an HTML page with drawings, a note on every section and figure, and a copy of the notes map that comes back to you. Without it, ten lines in chat or a Markdown page do the same job.

| Stage | The brief | Made with |
|---|---|---|
| a gate (or the one plan at 4–6) | the gate's document told for a reader, with the decision asked for at the end | `brief.py new <page>.src.html --purpose decision --id <feature>-<gate>`, then `html` and `check` |
| the next gate | a new page, never the last one edited | `brief.py new … --follows <last gate's page>`: it opens with what came of each note on the last one |
| a reader's notes | each note answered by a change or a reason, in the next page | `brief.py resolve <page> <notes map>` |
| decisions made while building | one row each, for the person to stamp or overturn | `brief.py call`, then `brief.py calls <ledger> --html` in the completion brief |
| completion brief | what was done, proved, doubted and owed, and the grade it should have been | `brief.py new … --purpose summary --follows <last gate's page>` |

The page lives beside the plans, as `docs/plans/<feature>/<nn>-<gate>.html` with its `.src.html`, and the status file links it on the gate's line. A notes map that ends in a clear yes is the approval: record the date. `brief.py attention <page>` names the passages the reader scrolled past; lead the next page with any that carried a decision.

## Handing over

A gate is an approval, not a handover. The agent that graded the work runs every gate and every slice, and the status file carries it across a pause, a compaction or a new day. A fresh agent takes over only when a session has grown genuinely long, and it starts from the status file and the documents beside it, never from a summary written for it. If the work does go to another agent, write `## For a fresh session` in the status file first: anything that was decided only in conversation.

## What a brief may say at each stage

A brief is about the stage the status file names. It can look ahead, because a person approving one stage needs to know where it leads. It does not do a later stage's work.

| Distance ahead | In the brief |
|---|---|
| this stage | the work itself, in full, and the decision asked for |
| the next stage | a glance: one short section headed *Coming next*, naming what that stage will have to settle |
| two or more stages ahead | a thought: one line where it changes today's decision, such as "the build will need a migration window" |
| anything behind | a link. Approved work is not argued again |

Asking for approval of a later stage, or handing over its document, is out of bounds. So a product brief may say that storage is the next question; it does not propose a schema, and it does not estimate the build.

**The grade moves the line.** At 4 to 6 stages 3 to 6 are one stage, so one brief covers all four fully. At 1 to 3 there is usually no brief. When an approval folds stages together, they count as one from then on. If the status file does not name a stage, say the stage is unknown; do not guess one.
