# Flexible Briefing

**Difficulty: 5/10** — the boundary between media, purpose, evidence and feedback needs review; a sibling skill is cheap to revise. One combined plan.
**Turned out to be:** 5/10 — preserving comments and distinguishing content revisions from save timestamps required the executable tracer bullet; one combined approval was enough.

- Combined plan: APPROVED 2026-10-30 — Parker: "Send it - great!"
- Implementation: complete; canonical skill links installed and parity verified.

## Slices

- [x] Tracer bullet: one engineering example in HTML and Markdown, separate evidence, and a comment returned to the right passage.
- [x] Skill: media and purpose routing, evidence controls, feedback rules, future MP4 earmark.
- [x] Verification and opt-in discovery: validate examples, preserve the existing skill, add the new catalogue entry and canonical discovery links.

## Result

Open review.html. The skill lives in briefing/; its README and references describe the media, purposes, evidence controls and shared handoff. Twenty-three Python tests and the isolated headless browser check pass, including script markup in reader comments and changed evidence/disclosure state during a save. Native Markdown inline commenting and native Terminal Delight in-place saving were not exercised; those limits are explicit. MP4 remains documentation only. The old skill directories and the pre-existing dirty handoff are untouched.

## Resume

Read plan.md and plan.html. The user requested a new skill alongside decision-brief, not a replacement. Proposed name: briefing. MP4 is documentation only. Existing HTML assets remain canonical in decision-brief; no storage-format migration or Terminal Delight changes are planned. A common feedback handoff is proposed; media-specific storage remains intact. This repository is not registered in APES according to agent-orient-boot --why. Pre-existing dirty file: handoffs/HANDOFF-2026-09-08-ai-slop-ledger.md; leave it untouched.

## Hardening Pass, 2026-10-30

**Difficulty: 3/10** — additive hardening of an approved, shipped skill behind its own tests; a mistake surfaces as a failing test or a loud refusal, and one revert undoes it.
**Turned out to be:** 4/10 — a rebuild had been silently stripping every page's wallpaper, hidden by the same text search in the glass gate. The test suite could not see it; a screenshot and a clean-context agent did.

- Branch `harden/briefing-portable`, one pull request. Review: [hardening.html](hardening.html); evidence: [hardening-evidence.md](hardening-evidence.md).
- Filed, not fixed here: [agent-skills#52 — the glass gate passes a page with no wallpaper](https://github.com/parker-brown-family/agent-skills/issues/52), with `fancy-pants dress` added to it.
- Repaired: `briefing/examples/engineering.html` and `review.html` had lost their wallpaper; their content revisions are unchanged.
- Open: saving notes into the file inside Terminal Delight and Markdown inline commenting remain unexercised; the repository has no root LICENSE although the skill declares MIT, which is the owner's call.
