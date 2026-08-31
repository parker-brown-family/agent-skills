# Layout

How a brief is arranged, and which components earn their place. Read this when deciding the
shape of a document, not when styling one.

## The disclosure ladder

Four rungs. A reader who stops at any rung has enough to act at that level of detail.

| Rung | What it is | Budget |
|---|---|---|
| 1 · **Headline** | The one sentence he needs if he reads nothing else. A verdict, not a summary. | ~40 words |
| 2 · **The scannable layer** | Verdicts, Read-first. What must be looked at, ranked. | ~4 minutes |
| 3 · **The page** | Sections that carry an argument each — comparisons, one chart, a table. | ~20 minutes |
| 4 · **Modals** | Everything a reader would ask "why?" about. Unbounded; nobody is forced through it. | as long as it takes |

The mistake is putting rung-4 material on rung 3. If a section runs past a screen or two on
the main page it is competing with the brief — move it to a modal and leave a one-line entry.

**Order matters.** Verdicts before Read-first: the reader wants to know the answer before he
is told what to scrutinise. Parker argued for this explicitly and he was right — a
"read this first" block that precedes the conclusion asks for attention it has not yet earned.

## The index that is not a table of contents

The cross-cutting findings list is the most useful component in a brief, and it works because
it maps to **conclusions**, not to layout. Each row is a claim with its evidence one click away.

A traditional table of contents tells you where things are. This tells you what was found. If
your findings list reads like section names, rewrite it as sentences that assert something.

## Components, and when each earns its place

None of these is required. Build what the material needs.

| Component | Earns its place when | Do not use it when |
|---|---|---|
| **Verdict cards** | Several things are being compared and each gets its own call | There is one subject — a card of one is a header |
| **Read-first list** | The reader is time-boxed and items differ in urgency | Everything matters equally; then it is just the page |
| **Stat tiles** | One number per thing carries an argument on its own | The numbers only mean something next to each other — use a table |
| **A chart** | A comparison is genuinely visual and spans one order of magnitude | The spread is 4 orders of magnitude (243,648 vs 41 — that is a tile row, not a bar chart) |
| **Findings list** | There are cross-cutting conclusions that do not belong to any one subject | |
| **A grill section** | Real decisions remain that are the reader's to make | You are presenting a conclusion, not asking for one |
| **Modal sub-report** | A reader would ask "why?" and the answer is longer than a paragraph | |

Before adding a chart, read the `dataviz` skill. One good chart beats four; a bad one is worse
than a table. If nothing is worth plotting, plot nothing.

## Scoring

If subjects are scored, say what each score answers, in one line, in the method section. A bare
7/10 is noise. From the intake audit:

- **Security** — how much of our machine does this get, and how carefully does it treat it?
- **Novelty** — does it do something we cannot already do?
- **Restraint** — is the engineering proportionate to the problem?
- **Maintenance** — will this still be here, and answered, in a year?

Scores are a summary of prose you have already written. Never the other way round.

## The grill

When decisions remain, ask them properly:

- Model the open decisions as a tree; the **frontier** is every decision whose prerequisites
  are already settled.
- Ask the whole frontier in one round, numbered, **each with your recommended answer**.
- A question whose answer depends on one still open in this round belongs to a **later round**.
  Say which those are and why they are waiting.
- Facts are your job, decisions are his — never ask for something you could look up.

Use `AskUserQuestion` for the round itself (cap: 4). Record the answers in the brief afterwards
so the document carries the decision, not just the question.

## Verification checklist

Run before delivering. Screenshots crop, and return blank frames at deep scroll — the DOM does
not lie.

- [ ] `scrollWidth === clientWidth` (no horizontal overflow)
- [ ] every `[data-dlg]` resolves to a `<dialog>` that exists
- [ ] every dialog has non-trivial `.dlg-body` content
- [ ] `<script>` and `<dialog>` tags balance
- [ ] `.notable` count is non-zero; a note can be added and the badge appears
- [ ] the exported map has readable anchors, and reports its own token cost
- [ ] a chart's longest label is inside the figure, not overflowing it
- [ ] grid columns do not orphan the last card (4 cards in a 3-wide grid looks broken)
