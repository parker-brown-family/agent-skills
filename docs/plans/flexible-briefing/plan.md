# Flexible Briefing

**Difficulty: 5/10.** One combined plan; approved 2026-10-30: “Send it - great!” The original illustrated plan is [plan.html](plan.html); the implemented result is [review.html](review.html).

## What It Is For

Give an agent one way to plan a brief while keeping its medium and purpose explicit. Markdown and HTML carry short, plain explanations, linked evidence and feedback tied to a specific passage. HTML remains the visual default. MP4 has a visible future earmark and no current production or annotation support. The existing decision-brief skill remains available and unchanged.

## The Shape

Add a sibling `briefing/` directory with SKILL.md, README.md, focused references, and paired examples. The agent records medium, purpose, reader, reading budget, desired response, and evidence depth before composing. Infer these from the request where possible; clarify only when the answer changes the work. Summary, engineering and decision are purpose guides across media, not rigid section templates. Other purposes can be named with an explicit intended reader outcome.

The common rule is a feedback target that can be resolved against the exact brief the reader saw. Share the handoff vocabulary: brief identity, revision, media-specific target, readable title or excerpt, comment and optional explicit agreement. Markdown targets stable section/block identifiers; HTML targets stable element identifiers. Future video targets a point or interval in a particular cut. Time zero is a valid target; an unrecorded time is unknown. A deleted target remains unresolved rather than attaching its comment to a nearby passage.

Share this as a documented handoff contract and worked examples first. Do not build a universal annotation engine, rewrite either renderer or migrate the existing HTML notes islands. Existing HTML copy-map output remains accepted; normalize it only at handoff, accompanied by the document/revision it came from. Preserve source maps and reader text. If identity or revision is unavailable, label that limitation instead of inventing one.

Evidence depth has three settings: sources, reasoning, and code trace. Default to code trace where code exists, otherwise the deepest available primary evidence; missing evidence is stated. This sets how far the linked chain goes, not how much prose appears on the brief. The example chain is brief → evidence note → test or measurement → source location. Evidence notes use portable relative Markdown links with Obsidian-compatible heading/block anchors; wiki-link syntax is optional and must resolve in the chosen reader. For local source links, preserve the path and write the symbol, commit and line separately so Terminal Delight can open it.

The brief alone is declared as the review deliverable. Linked evidence, exports and source files remain supporting references, with no automatic artifact declaration or focus change. A source note can become a deliverable only when the user expressly asks to review that note.

HTML reuses decision-brief's canonical notes, styles and fixtures and fancy-pants-brief's look and gate. A new skill can refer to a sibling's assets without inheriting decision-only prose requirements. Preserve embedded notes, concurs and revision metadata when rebuilding, back up before replacement, and refuse malformed annotation data. Never silently change an anchor. Existing cross-writer deletion limitations remain documented, not claimed solved.

Markdown uses stable explicit anchors and an inspectable adjacent feedback map as a portable fallback. A supporting reader may offer inline commenting and direct send; verify that capability before promising it. The fallback provides section targeting, persistent reader text and a map that can be copied or supplied with the original document. It requires no Obsidian installation. The skill must label any difference between native and fallback interaction.

## Files Planned

- `briefing/SKILL.md`: concise routing and production loop.
- `briefing/README.md`: usage, supported behavior, MP4 earmark and adoption boundary.
- `briefing/reference/`: purpose guides, HTML and Markdown workflows, evidence policy, feedback contract and verification cases.
- `briefing/examples/`: the same engineering finding as HTML and Markdown, evidence note(s), and a return-comment example. Clearly distinguish demonstrations from measured project findings.
- A small standard-library helper only if the tracer bullet exposes a recurring gap in validating links/anchors or exporting the existing maps. No new runtime dependency. Its exact interface is determined from the existing format before implementation.
- Root `README.md`: one opt-in catalogue entry after validation. Discovery uses symlinks to the canonical source plus `agent-parity --sync-skills`; do not copy bodies or redirect existing names.

## Least Confident Decisions

1. Start with a shared handoff contract and separate media storage. A universal storage schema would couple this skill to readers that are not part of the task.
2. Markdown's portable feedback fallback is an adjacent editable map. Native inline comments depend on the reader; a skill cannot give a plain text file a UI by itself.
3. Evidence depth changes the linked chain. A brief stays short even when its proof reaches the source.
4. Call the new skill `briefing`. Existing briefing skill names keep their current behavior until an explicit later migration.

## Slices and Proof

1. **Tracer bullet:** same purpose, same finding, two media. Follow a claim through its evidence, leave a comment, reopen it and return the map with the correct document. Show a stale revision and a missing target visibly unresolved.
2. **Skill:** document the common authoring loop, three purpose guides, separate media workflows and evidence choices. README marks MP4 as future-only, including pause, timestamp/interval, comment, resume and agent handoff principles. No video implementation.
3. **Verify and expose:** exercise comment persistence and export; preserve notes through rebuild and reject malformed islands; reject duplicate/missing anchors and broken relative evidence links; retain unknowns; check no supporting file is declared as the primary artifact. HTML passes the glass gate and narrow-width/annotation/SVG text checks. Validate discovery and that existing decision-brief tracked files are unchanged. No changes to Terminal Delight or Markdown Delight.

## Source Record

These are local design inputs, not claims that the planned skill is implemented:

- User's request in this session, 2026-10-30: separate media; shared section feedback; high evidence depth behind links; protect artifact visibility; new sibling skill; MP4 placeholder; summary/engineering/decision purposes.
- [Existing HTML notes contract](../../../decision-brief/SKILL.md).
- [Rebuild can erase notes](https://github.com/parker-brown-family/agent-skills/issues/36).
- [Browser-held notes can restore a deletion](https://github.com/parker-brown-family/agent-skills/issues/26).
- [SVG structural checks miss clipped text](https://github.com/parker-brown-family/agent-skills/issues/19).
- [An assembler is already requested](https://github.com/parker-brown-family/agent-skills/issues/38). Reuse if available at implementation; avoid pretending the new skill fixes the older skill.
