---
name: ai-slop
description: Flag a piece of AI-sounding text as slop, work out why it is slop, and add it to the machine-global specimen ledger so it stops coming back. Use when Parker quotes a sentence and calls it slop or an AI-ism, when he says "/ai-slop", "this is slop", "AI-ism", "adds nothing", or when you catch one in your own draft. Also the mandatory pre-draft read for any user-facing prose — the ledger is the flags his own eye has caught, which the generic anti-AI-writing skills do not carry.
license: MIT
---

# ai-slop — the flags Parker's own eye caught

Two jobs, and the second is the one that actually saves anything.

**Capture.** Turn a flagged sentence into a ledger entry that names the trap,
explains what it cost, and where possible carries a regex a build can grep for.

**Prevent.** Get read before the first sentence of a draft, every time.

The ledger is `~/.claude/writing/ai-slop.md`. The doctrine it serves is
`~/.claude/writing/house-style.md`, which stays the authority on rules — this is
the evidence file underneath it.

## Why this exists, stated plainly

On 2026-09-04 an article shipped with four flagged AI-isms in its opening
register. Two of them were **already banned in `house-style.md`**, in entries
dated the day before:

> *"A punchy summarising opener is the same AI-ism with the label removed."*
> *"Never use 'it isn't X; it's Y'... a flourish carrying zero information."*

The `avoid-ai-writing` skill had been run on the text and passed it, because
those are upstream's patterns and these are Parker's. The pile existed; nothing
made anyone read it. That is the failure this skill is built against, and it is
a *retrieval* failure, not a taste failure.

## Capture — `/ai-slop "<the offending text>"`

1. **Quote the specimen exactly.** Never paraphrase, never invent a
   representative example. The value is that it is real and that it shipped.
2. **Name the trap** in three or four words. It becomes the heading and the
   thing you will recall mid-draft.
3. **Say what it costs the reader.** Not "this is bad writing" — what does a
   reader lose by passing through this sentence? Almost always the answer is
   *nothing was added*, and the useful part is saying what the sentence was
   pretending to add.
4. **Say what to do instead**, concretely enough to act on at 2am.
5. **Write a regex only if it can be honest.** A pattern that fires on
   legitimate prose is worse than no pattern: it gets disabled, and then nothing
   is enforced. Test it against the specimen *and* against a paragraph of
   Parker's good writing before committing it.
6. **Record where it shipped**, so the same surface can be re-checked.
7. **If the entry generalises to a rule**, add a dated one-liner to
   `house-style.md`'s Log as well, and cross-reference. Rules there; evidence
   here.

Ask Parker for the *why* if it is not obvious. His reason is usually sharper
than the one you would infer, and the reason is the part that transfers.

## Prevent — the read

**Before drafting** any article, brief, post, letter or client copy: read the
ledger's entry headings and the standing checks at the bottom. It is short by
design. Anything longer than a screen has failed at its own job.

**As the final pass**, after `avoid-ai-writing`: re-read the specimens against
the draft. `avoid-ai-writing` catches the industry's tells; this catches
Parker's, and they overlap less than you would expect.

**Where a property has a build gate** — parkerbrown-dev's
`scripts/check-articles.mjs` is the worked example — wire the regex-carrying
entries into it, so the flags run on every build instead of on every good
intention.

## What is not slop

Do not let this become a machine for flattening the voice. Parker's style
overrides live in `house-style.md` and they win here too:

- **Em dashes are welcome.** Do not strip them.
- **Contractions are welcome.**
- A **specific** number, name, error or date is never slop, however dense.
- A metaphor **held** through a passage is craft. A metaphor abandoned after one
  sentence is decoration.
- Short declaratives are fine. The tell is not brevity; it is a sentence that
  adds nothing, and length has no bearing on that.

The test is always the same, and it is not about style: **delete the sentence
and see whether the reader lost anything.**
