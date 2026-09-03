---
name: article
description: Write a publishable article for a Brown Family Sports property or a client — one finding told in several registers (tl;dr / ELI5 / technical, or beginner / intermediate / advanced), in the house page structure, with the narrative pass and the anti-slop pass already run. Use when asked to write, restructure, or review an article, guide, build log, investigation or explainer for a site; when converting an existing post to the multi-register format; or when onboarding a new property or client to the article system. NOT for a decision that ends in a ticket — that is decision-brief.
license: MIT
---

# article — one finding, several registers

An article earns its place by settling something. The register system exists
because the same settled thing has to reach a stranger who will give it fifteen
seconds and a peer who will try to break it, and those are not the same piece of
writing — but they must be the same *finding*, or the article has quietly become
three articles that disagree.

This skill is the pipeline that gets there. It does not replace `storytelling`
or `avoid-ai-writing`; it sequences them and supplies the container they were
missing.

```
finding  →  profile  →  SHAPE once  →  cast per register  →  slop pass  →  gate
            (property)   (storytelling)  (hook + flesh each)  (avoid-ai-writing)
```

## Before anything: the finding

Write the finding as **one sentence**, and do not write prose until it exists.

> The board wasn't a control plane, because progress and drift were the same axis.

If that sentence won't come, there is no article yet — there is research. Say so
and stop. This is the single most common way an article goes wrong: it gets
written to find out what it thinks, and it ships still looking.

The finding is not the headline and not the dek. It is the thing all registers
are telling, and it is what you check them against at the end.

**A guide has a finding too — it's the thesis it teaches**, not a dispute it
settles. "Heat is a training stimulus you can bank, not only a race-day tax" is
a finding, and everything in that guide serves it. What fails this bar is the
piece with no thesis at all: a tour of a topic, organised by subheading,
arriving nowhere. That's a useful document and it isn't an article — publish it
as reference material instead of dressing it as one.

## Step 1 — load the property profile

Every property publishes differently. Read `ARTICLE-PROFILE.md` at the root of
the property's own repo. It carries the variable half of the system: the register
axis, the voice, the byline, the category vocabulary, the design tokens, the
sources posture, and the liability gate.

**If there is no profile, run the intake in `reference/profile-template.md`
first.** Nine questions, and one of them decides the register axis. Do not guess
a client's voice — a wrong guess is expensive and reads as carelessness.

The profile is authoritative for everything it covers. This skill is
authoritative for the structure underneath it, which does not vary.

## Step 2 — SHAPE once, with `storytelling`

Run `storytelling`, but not five stages three times over. The stages split:

| Stage | Run it | Why |
|---|---|---|
| **1 HOOK** | **per register** | Each register faces a different appetite, so the gap between "where the reader is" and "the ending" is a different gap. Three registers, three hooks, three headlines. |
| **2 SHAPE** | **once, shared** | The spine and the three acts belong to the *finding*, not to a telling of it. This is the step that stops the registers drifting into separate articles. |
| **3 FLESH** | **per register** | The register decides the dose. tl;dr strips it to nothing, ELI5 is where all of it lives, technical swaps sensory detail for numbers — which is storytelling's own rule that data stories skip stage 3's sensory work. |
| **4 JUDGE** | **per register** | Every register ships alone. Score each one on its own and force the rewrite before moving on. |
| **5 LAND** | **per register** | Simulate a different skeptic each time: the stranger deciding whether to keep reading, and the peer looking for the hole. |

One spine, several hooks. That is why three headlines on one article isn't
repetition — and it's the answer to give anyone who asks why the tabs don't all
say the same thing.

## Step 3 — cast the registers

Read `reference/registers.md` for the contracts: target length, voice, what each
register opens and ends with, and what is banned in it. The profile names which
axis this property uses; the contracts hold either way.

Then read `reference/anatomy.md` for what goes on the page and in what order,
and which parts are shared across registers versus written per register.

## Step 4 — the slop pass

Run `avoid-ai-writing` on each register separately, as the last pass before the
gate. **Do not show the audit, the intermediate draft, or the rewrite notes** —
return the finished prose. Where the operator keeps a house-style file, it wins
over both that skill and this one.

Run it per register, not once over the whole article: the passes that clean up a
200-word tl;dr are not the passes a 3,000-word technical piece needs, and a
single sweep over all three flattens the voice differences the registers exist
to create.

## Step 5 — the gate

`reference/checklist.md` is pass/fail and every item is verifiable by reading
the rendered page. Run it before you call the article done. An article that
fails one item is not "mostly ready" — the failing items are exactly the ones a
reader notices.

## Invariants

Everything else in this skill is a default you may override for a property.
These are not.

1. **The finding is one sentence, written first.** No finding, no article.
2. **The dek states the question and the stake. The default register states the
   finding.** Never both — they sit inches apart on the page and the repetition
   is the first thing a reader sees.
3. **Every register is a finished telling.** None is the simplified version of
   another, and none may end by telling the reader to go read a better one.
4. **Copy is scoped to the visible register**, and carries a metadata header
   naming the source URL and the register. See `reference/mechanism.md` — there
   is a live implementation of this that gets it wrong, and it is worth not
   copying.
5. **Never invent the concrete detail.** A real split, a real error message, a
   real date, a real number. In this work the specifics are load-bearing, and a
   fabricated one turns an article into a liability.
6. **Sources are article-level, and every number in the technical register
   resolves to one.** One list, shared across registers, because three copies
   will drift.
7. **The story does not soften the finding.** If the answer is that the thing
   doesn't work, the arc lands there.

## House voice

Three rules that outrank every contract below them. They are house style, not
article structure, so they apply to anything published — a talk, a post, a case
study, a README.

### The title is a coined term, and it is short

Name the thing, then spend the article earning the name. *Agentic Attention
Surface.* *Taskeroids.* Two or three words, no verb, no colon, no clause after a
dash. The body's job is to walk the reader to the point where that term means
something, so the title does not need to explain itself and should not try.

What this replaces: the summarising sentence-title, and worse, the two-beat
construction — *"I built a control plane. It was a map."* It reads as a caption
for the article rather than a name for the idea, and it spends the punchline on
the first line.

### Tell the story. Do not lead with the conclusion, labelled

The worst opening is a bolded label, a colon, and a compressed finding. The
second worst is the same sentence without the label — a punchy declarative that
summarises the piece before the reader has any reason to care about it.

Open where the reader already is. What was happening, what you saw, the question
it raised. The finding lands harder three paragraphs later inside a situation the
reader recognises than it does in the first line with nothing underneath it.

A working opening is usually the honest answer to *what made you look into
this?* — and that answer is nearly always a scene, not a thesis.

### Plainer, more human, fewer words

Every example gets one pass asking whether a person would say it that way out
loud. Concrete nouns beat abstractions, a short sentence beats a qualified one,
and an example a reader can picture beats a precise one they cannot. If an
explanation needs three sentences and a definition, the example is wrong — find
a better one rather than propping up the one you have.

## Building the page

`reference/mechanism.md` carries the implementation: the tab component built
from radio inputs and CSS sibling selectors so it works with no JavaScript and
every register stays crawlable, the ARIA contract, hash deep-linking, and the
scoped-copy behaviour. It is framework-agnostic — the same markup and CSS work
in a static export, a React app, or hand-written HTML.

## Converting an existing article

Articles written before the register system get converted, not rewritten:

1. Extract the finding from the existing piece. If you can't, that's the real
   problem and the conversion is blocked on it.
2. The existing article is almost always the **technical** register already.
   Keep it, and check it against that contract.
3. Write the tl;dr from the finding, not by summarising the prose. A summary of
   prose reads like a summary; the tl;dr is its own telling.
4. ELI5 last, and only if the subject has a metaphor worth holding. A forced
   ELI5 is worse than an absent one — and the axis makes it optional.
5. Move the dek off the finding if it was carrying it.

## Related skills

- **`storytelling`** — the narrative craft this sequences. Stage depth lives in
  its `upstream/framework/`.
- **`avoid-ai-writing`** — the delivery pass, run per register at step 4.
- **`decision-brief`** — for analysis that ends in a decision rather than a
  publication. If the output's job is to get a call made, use that instead.
