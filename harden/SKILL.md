---
name: harden
description: "Find what a colleague's finished work missed, prove each miss with a run and a root-cause chain, fix only the top square-root of them, and hand back one brief the owner can concur with in a glance. Use for \"harden\", \"harden this\", \"what did they miss\", \"check my buddy's work\", or in place of an adversarial review when review noise is the problem."
disable-model-invocation: true
---

# Harden

A colleague finished a piece of work. It is good work, and it has a few misses in it, and nobody knows where. Your job is to find them, prove them, fix the ones that matter most, and hand the owner a page they can stamp.

You are the colleague's partner, not their opponent. An adversary is rewarded for volume, so it brings back nitpicks, style and risks that need a future change to matter, and every one of them costs the reader attention. A partner is rewarded only for a defect: a miss that a run proves and a root cause explains. Coming back with nothing is a valid result, and it says the work was sound.

Run this from a seat that did not do the work: a fresh session, or a different agent. One hunter. The colleague's own context is the thing that hid the misses.

## Do the work

Every question handed to the owner costs them a turn of attention, and attention is the scarce thing here. Across 52 real end-of-turn asks, the owner answered 35 with a bare go. So a decision this work needs is yours: make it, act on it, and record why on the brief. The owner stamps it afterwards.

Stop before a step only when it:

- contradicts something the owner approved, or
- cannot be undone without someone else: published or sent outside, money spent, a person's live screen taken over, or anything deleted that you did not create.

Nothing else is a stop. When one applies, hold that single step, finish everything else, and put it on the brief with your recommendation. "I'll wait for your go" is never how a run ends.

## 1. Frame

- **Scope** is what the user names. Otherwise it is the branch diff from its merge base, through the working tree.
- **Intent** is what the work was supposed to do, restated in one or two plain sentences from the user's message, the commits and the PR description. Every defect is measured against it. If it cannot be read from any of those, write your best reading on the page and carry on.

## 2. Hunt

Look for places where the work does not do what the intent says. For each suspect, **run something against the real code** that shows it: a failing test, a repro script, a command and its output. For a design or a plan, run a prototype or probe the current tree.

Leave out anything you did not run. That covers style, naming, structure, "consider adding", and anything that only matters after a change nobody has made. Those are not defects.

## 3. Root-cause every find

A symptom is not a defect. Each find gets a chain, written so a reader can judge it in one pass without opening anything:

| Link | Answers |
|---|---|
| **Observed** | the command, and the output it printed |
| **Expected** | the output the intent requires |
| **Mechanism** | the `file:line` where the wrong behaviour comes from |
| **Root cause** | the assumption the work made that is not true, in one sentence |
| **Fix** | the change at the root, not at the symptom |

Then merge. Several symptoms with one root cause are one defect. Count defects by root cause, never by symptom. Call that count **N**.

If you cannot write the root-cause line, you have a symptom, not a find. Keep digging or drop it.

## 4. Cut to the square root

Rank the N defects by how badly each breaks the intent, worst first. Break ties by the cheaper fix. Keep the top

    k = ceil(√N)

| N found | 1 | 2–4 | 5–9 | 10–16 |
|---|---|---|---|---|
| k kept | 1 | 2 | 3 | 4 |

This is Price's square-root law: across a set of N contributions, about √N of them carry half the value. The more you find, the more selective the cut. Four finds keep two, but sixteen finds keep only four.

The rest are not deleted. They go on the page as **left on the map**, one line each with their chain, so nothing is lost. Something nobody fixed is still a finding, and the owner owes this list nothing.

**Escalate instead of fixing when N > 16.** That many separate root causes means the premise was wrong: this was not good work with a few misses, and patching four of them hides the real state. Stop, fix nothing, and hand back the full list with the intent restated, a one-line read of what went wrong upstream, and your recommendation to repair, revert or redo.

## 5. Fix and re-run

For each of the k kept defects: apply the fix at the root cause, re-run the command from its chain, and record the new output. A fix without a passing re-run is not finished. If the re-run still fails, say so on the page and leave the fix unapplied.

Run the project's own checks once at the end, so the fixes did not break anything else.

## 6. The concur brief

One page the owner reads in a minute and stamps. Each row is a decision they can agree with on sight, because the evidence is already laid out.

- **Intent**: the restatement.
- **Fixed**: for each of the k fixed, the five-link chain, the fix (commit or diff), the re-run output, and a stamp slot, `CONCUR` or `OVERTURN`.
- **Left on the map**: the other N − k, one line each, with chain.
- **Count**: N found, k fixed, and how many suspects you dropped for having no run or no root cause.

No question appears on this page. Everything on it is done or decided, apart from any step held under the stop rule, which shows your recommendation.

The stamp is meant to be a rubber stamp. If a row needs the owner to go and read code before they can agree, the chain is not finished. Go back and finish it.

## In this house

- The brief is built with the `briefing` skill (purpose `decision`), so every row takes a note and the stamps come back pinned to the row.
- File left-on-the-map items yourself through `escalate-issue`. Do not ask first.
- One hunter, no fan-out. A second hunter is Parker's to seat on the Threshing Floor.
- When you are about to stop and are not sure the stop rule applies, ask Jev instead of Parker:

```bash
python3 scripts/stop-check --request "<what the owner asked for>" --step "<the step you are about to take or ask about>"
```

Exit 0 means carry on. Exit 3 means hold the step. Exit 2 means Jev did not answer, so apply the stop rule yourself. It costs about $0.00003 a call.

On those 52 asks it held 7, where a keyword match held 28, and it let 32 of the 35 bare-go asks through. It stopped a public pull request in Parker's name and a swap of his live window. It missed deletions, which is why deleting is on the written rule and never left to the check. A third question about personal taste scored at chance and was dropped. The labels came from his replies, and the two-question rule was chosen after a first run, so treat these numbers as a first read.
