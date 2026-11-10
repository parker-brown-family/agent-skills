# Reading rail: implementation status

**Difficulty:** 6/10, revised to 7/10. **Post-hoc:** 7/10 for shared-file recovery and native activity ownership. The last two design gates were bare approvals; no further gates were added.

## Approved

All four gates are approved. The original review pages retain Parker's notes and concurrence:

- Product — `01-product.html`, reading surface.
- Architecture — `02-architecture.html`, notes and time inside the HTML.
- Program design — `03-program-design.html`, onscreen and active, with no input-idle cutoff.
- Build order — `04-slices.html`, browser first, then Terminal Delight.

## Implementation

- [x] Browser save tracer, original-file reopen and duplicate-safe merge.
- [x] Browser clock, following rail, focus/tab/modal pauses, notes and time saving.
- [x] Native viewport clock, original-file save/reopen and browser-readable record.
- [x] Native opening/section/figure/entry rail, pane/tab/window/modal lifecycle, FOCUS ownership and time-only Copy map/send controls.
- [x] Combined recovery/build verification, two-process race, portable export and updated skill instructions.

## Current evidence and boundaries

See [the short review](07-native-reading.html) and [checks, limits and source](08-proof.md). Current Python suite: 133 passed. Rust focused record/notes suite: 67 passed. Real browser export/save/reopen and JavaScript long-duration tests pass. Two independent writer processes preserved 32 sessions and 16 notes. Final native smoke passes both rail layouts, original-file reopen, all target kinds and the pane/tab/window/modal/FOCUS/zoom matrix. The full native suite passes 3,438 tests with four threads, with 12 ignored; clippy and formatting pass.

The unrestricted native suite has a load-sensitive prompt-completion timeout, recorded in [the falsifiable follow-up](https://github.com/parker-brown-family/terminal-delight/issues/1411). The prior full run passed with four test threads. Do not call unrestricted CI green.

Native source: `/home/parker/Work/terminal-delight/.worktrees/brief-reading-build/terminal-delight`, branch `feat/brief-reading-time`, based on current T3 preview `e3990e0c8d8f270b3f8a19009b1d425b978c52f4`, with a matching private renderer next door. This is a debug test build, **not installed**; release **unassigned**. The approved slice contract requires that distinction, not an unverified installation.

Browser autosaving requires `brief.py serve PAGE.html`. Direct file opening stores browser-local pending edits until export. Native checkpoints enter a retry journal before original-file writes; runtime rebuilds of the same authored revision preserve pending time. Different authored revisions stay separate. Browser, native and cooperating rebuild writers use one stable lock.

Native source is committed and pushed as `465fc306`; its APES task is in review awaiting integration. The APES task is `record-active-visible-time-in-native-html-documents-mwadjec8`. No subagents were used. Pre-existing handoff/CDX changes in agent-skills and unrelated root TD work remain untouched. This page replaces transient run logs; concrete proof lives in the linked JSON files.
