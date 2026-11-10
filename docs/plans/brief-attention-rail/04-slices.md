# Build Order

The [program design](03-program-design.html) is approved. These slices build the same approved design in working increments. Each ends with a result that can be opened and checked. No implementation exists yet.

## Slice 1 — Save and reopen

**Tracer bullet:** open a temporary, clearly labelled synthetic HTML fixture through the local review server; submit a hardcoded counter for one section; write the reading island into that exact file; reopen and show the saved value.

Use the approved format and a stubbed display. The purpose is to prove the complete file round trip before building the real clock. Synthetic data stays in this fixture and is never presented as a person's reading record. Implement selected-file authority checks, validation, the shared lock, checked atomic replacement and pending/saved distinction from the first write.

**Proof:** original path unchanged; authored bytes and notes preserved; reopen reads the written value; a duplicate checkpoint does not add it twice; a wrong token/revision and a failed write cannot alter the file or say Saved. Deliver a local HTML demonstration with its synthetic status visible.

## Slice 2 — Read in a browser

Replace the fixture counter with the real browser clock. Supply the following rail, active section and nested entries, target bounds, one-second observations, five-second checkpoints and typed note edits. Count still active periods, pause away/covered states, preserve unknowns and gaps, show failed saves, and include the anchored summary in Copy map and extraction. Plain file opening retains its explicit browser-storage-only behavior.

**Proof:** real isolated browser scroll/focus/modal/save/reopen run plus fake-clock long-period cases. Verify an active hour without input counts, an inactive day does not, and missing geometry is not zero. Check desktop and narrow layouts, note controls, original-file preservation and no external requests.

## Slice 3 — Read one section in Terminal Delight

Wire one real section end to end through TD's active native document viewport, clock, checkpoint queue and existing file writer. Use the same portable record and lock as the browser. Disable recording in hidden Chromium probes and read-back validation. Add one native navigation entry showing its actual visible time and save state.

**Proof:** an isolated TD window scrolls into/out of the section, loses focus, saves and reopens the original HTML. Browser extraction reads the native record. The hidden renderer and save confirmation add no human session. Native notes and reading updates preserve each other.

## Slice 4 — Complete the native reader

Extend the working native path to the opening, sections, figures and explicit entries; add the following rail and compact narrow behavior. Wire pane/tab/window/modal/FOCUS lifecycle changes, resizing and zoom against actual content bounds. Carry the summary through native Copy map/send-back and translate native strings.

**Proof:** the native activity matrix, target geometry, nested targets, one owner during FOCUS lending and zoom, layout at pane/phone/desktop widths, and all note/send-back anchors. Run against both supported terminal cores where required by the selected TD branch. Use an isolated display; do not take Parker's live input seat.

## Slice 5 — Preserve the record through ordinary work

Finish cross-reader use: concurrent note and timer saves, retry/recovery, file changes and same/changed-revision rebuilds. Run the shared fixtures in all three languages and a real two-process race. Update briefing and fancy-pants instructions to produce short, contextual sections, with concise decisions and deeper evidence behind links. Deliver one final short review page showing actual completed behavior and remaining measured limits.

**Proof:** no lost notes or sessions under cooperating concurrent writers; revision isolation; pending data survives failure and is cleared only on acknowledgement; authored bytes are preserved. Run the required repository gates, HTML/comment/layout checks and exact-file reopen in both readers. Record the tested native build and release assignment without claiming unverified installation or release.

## Slice boundaries

At each completion, update `00-status.md`, show the working result and its evidence, then ask "Continue to slice N+1, or re-steer?" as the software-factory skill requires. Preserve an inspectable working state at every boundary. A fresh session can resume from the first unchecked slice and the approved product/architecture/program design.

If a later slice invalidates an approved decision, stop and return to that specific gate with the concrete finding. Routine implementation choices stay with the agent and are recorded. No additional dependencies, new document format, remote service or parallel agents are planned.
