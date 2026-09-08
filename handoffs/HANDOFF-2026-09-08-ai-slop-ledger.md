# Handoff — the ai-slop ledger and the article rewrite (2026-09-08)

## Status

**One thing needs Parker:** `agent-skills` PR #17 is OPEN and MERGEABLE, unmerged
since 2026-09-04. `main` is a protected branch, so the skill cannot land without
it.

Everything else is done. `parkerbrown-dev` at `f27af2e`, pushed and deployed —
the rewritten article is live and returns 200. The global writing files
(`~/.claude/writing/`) are not under version control anywhere, so they exist only
on this machine.

## What's done

**`/ai-slop`** — a skill in `agent-skills/ai-slop/`, symlinked to
`~/.claude/skills/ai-slop`. Two jobs: capture a flagged sentence as a ledger
entry (trap named, cost to the reader, regex where one can be honest), and get
read *before* drafting. The second job is the one that was missing.

**The ledger** — `~/.claude/writing/ai-slop.md`, seeded with the four specimens
Parker flagged. Rules stay in `house-style.md` (four new dated entries); the
specimen, the reasoning and the pattern live in the new file.

**A gate, not a good intention** — `parkerbrown-dev/scripts/check-articles.mjs`
gained `style/split-negation`, which fails `npm run build`. Verified against 3
specimens and 6 innocent sentences, and both previously published articles pass.

**The article rewrite** — the `Unearned Zero` landing register was rebuilt from a
`storytelling` SHAPE that should have been run the first time: setting → want →
turn → resolution, 149 words. Three flagged constructions removed from it, one
more from ELI5, one from technical.

## How to run/verify

```bash
cd ~/BROWN-FAMILY-SPORTS/Software/parkerbrown-dev && npm run build
```
```bash
node /home/parker/BROWN-FAMILY-SPORTS/Software/parkerbrown-dev/scripts/check-articles.mjs
```
```bash
cd ~/BROWN-FAMILY-SPORTS/Software/parkerbrown-dev && ./deploy.sh
```

A git push does **not** publish that site — prod is static files rsynced to
`piper-prod`, and `deploy.sh` protects the `aircraft-telemetry` co-tenant sharing
the web root.

## Not done / next

- **Merge PR #17.** Nothing else is blocked on it, but the skill is not in the
  repo until it lands.
- **The article's LinkedIn credit is still unnamed.** Parker chose *name and
  link*; the author and URL were never supplied and would not be invented. One
  line in `lib/writing/unearned-zero.ts`, then `./deploy.sh`.
- **`~/.claude/writing/` is not backed up.** `house-style.md` is now 17 dated
  rules of accumulated judgement and `ai-slop.md` is the specimen ledger; neither
  is in any repo. Worth a decision.
- **Only one flag became a regex.** The other three — thesis-as-punchy-count,
  parallel fragment stacking, compressed-abstract opening — are prose entries. The
  fragment-stacking one is probably mechanisable (count consecutive verbless
  sentences of similar length); the other two are not.

## Watch out

- **A foreign commit sits on the `ai-slop-skill` branch.** `37a2376` ("The note
  bar copies the map on one click") is a `decision-brief` change from another
  session, committed onto this branch on 2026-09-05 and never pushed. **PR #17 is
  clean today** because only `0567ed3` was pushed — but pushing this branch again
  would silently add unrelated work to the PR. The commit is preserved on
  `decision-brief-copy-map`; nothing was reset or discarded.
- **Do not kill the server on port 8731.** It belongs to another session
  (pid 3992267, started 2026-09-06, serving `~/reports`). Mine on that port was
  stopped on the 4th. Same for 8742.
- The `viral-circular-lymric/` directory untracked in `agent-skills` is not mine.
- `avoid-ai-writing` passing a draft means nothing about Parker's own flags. Run
  the ledger separately, as a second pass.

## Where it's recorded

- APES: **no episode** — neither `agent-skills` nor `parkerbrown-dev` is a
  registered project. Flagged at the previous tie-off too.
- lean-ctx: `ctx_session` decision updated. `ctx_knowledge` is not bound.
- file-memory: `a-rule-nobody-retrieves-is-not-a-rule` added.
- Session package: `~/reports/2026-09-04-tailings-session.cdx`.
- Prior handoff, same session:
  `~/Work/tailings/handoffs/HANDOFF-2026-09-04-tailings-multi-agent.md`.
