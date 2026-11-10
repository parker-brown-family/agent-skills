# Saved Reading

## Decision

Keep self-contained HTML with embedded JavaScript. Add one versioned reading-record island inside the file. Use the reader that owns the visible viewport to measure it, and the host that owns the file to save it. No new document extension, framework, remote service or database.

The left rail and brevity requirements were approved in the [product review](01-product.html). This gate settles measurement and persistence. Parker's follow-up allows HTML-adjacent designs and suggests JavaScript or a local server; a format change is unnecessary for this design.

## Fit

| Existing part | Change |
|---|---|
| `fancy-pants-brief/assets/sections.js` and `decision-brief/assets/base.css` | Following left rail, active section, nested entries and time values; compact navigation at narrow widths. |
| `briefing/scripts/brief.py` | Assemble the reading script/data island, preserve records on rebuild, extract an agent-readable summary. Add a local `serve` mode for browser review. |
| Browser reading script | Observe target geometry in the actual viewport; update the rail; send records to an available save adapter. |
| TD `app/src/docview/page.rs`, `engine.rs`, extraction and native reader chrome | Use actual native scroll/viewport/focus and explicit target geometry; render a native following rail because fixed CSS inside a snapshot cannot follow native scrolling. |
| TD document writer | Serialize notes and reading-record writes through one file transaction boundary. Change only recognized data regions and keep existing content/conflict checks. |

TD currently photographs the page after running its scripts. Its hidden browser's visibility does not follow native scrolling. Do not count hidden rendering, screenshots, agent QA or read-back validation as human reading. The engine already reports anchors, but section headings alone are insufficient: add explicit bounds for sections, figures and entries.

The T3 scuttle branch inspected here adds inbox/composer behavior. A live HTML reader is not established by the inspected engine interface. A future live engine can use the browser adapter without changing the record format.

## Endpoints

An optional `brief.py serve PAGE.html` process binds to loopback on an ephemeral port and serves only the explicitly selected file and its review API. It opens no directory browser and accepts no client-supplied filesystem path.

- `GET /review/<random-token>` — serve the selected HTML with the local save adapter injected into the response, never into the saved document.
- `POST /review/<random-token>/save` — submit typed note edits, concurrence and cumulative reading counters, associated with the rendered content revision. Return the acknowledged record and current save status.

Reject wrong Host/Origin, missing token, unsupported content type, malformed/oversized data, unknown document identity and incompatible content revisions. No permissive CORS. The token grants access to this review session and this one file. Reads and writes are serialized; on-disk changes are checked before an atomic replacement. Reuse existing Python standard-library HTTP and brief parsing/writing helpers where applicable.

TD uses its native writer and needs no HTTP endpoint. Plain `file://` opening keeps the document readable and commentable with browser-local pending data; it must state that the original is not saved. Opening through the local review command enables original-file saving.

## Data

No database. Store a `report-reading` JSON island next to the existing reader-note islands. Give it its own format version, separate from note and brief versions.

Each observation belongs to a document identity, content revision, recording session, measurement method version and reader host. Each target has its stable anchor, kind, title, eligibility and cumulative visible milliseconds. An explicitly observed zero stays zero; a missing record or unavailable geometry stays unknown. Do not store a zero for a target that could not be observed.

Use a random recording-session id and monotonic elapsed time. Merge repeated checkpoints by the maximum cumulative counter for that session and anchor, rather than adding a retry twice. Different simultaneous sessions remain separate; their sum is not claimed as unique human attention. No person identity or inferred interest score.

Counters belong to the content revision actually displayed. Rebuilds preserve older revision records without applying their time to changed material. Same-content rebuilds retain current records. Removed targets remain in historical records. Both writers preserve notes, concurrence and other sessions while updating reading data. Exclude all recognized reader-data regions from content/layout hashes, so a checkpoint does not force a page redraw or invalidate feedback.

## Measurement

The target set is the opening, each section, each figure and explicitly anchored entries. Measure each target's content bounds, never its rail link or note button. Nested targets may be visible simultaneously; their times must not be summed into a document reading time.

Count elapsed time while a target intersects the unobscured viewport and that document is foreground and focused. Pause when the tab/window/document is hidden or loses focus, or a modal covers the reading surface. Do not guess attention from pointer movement or invent an idle timeout: a person can read without moving. Label the value as visible time. The exact geometry and event contract is Gate 3 work.

Checkpoint periodically while counters change, and on focus loss or close. A save is acknowledged only after the file write succeeds. Keep pending data locally through failures; report pending or failed explicitly. Closing or a crash may lose the unacknowledged tail; do not claim a final checkpoint that was never confirmed. The checkpoint interval and recovery limits are Gate 3 decisions.

## Flow

1. Build the self-contained brief with stable targets, content revision, rail script and empty/retained reading island.
2. Open it in TD or through the local browser review command. The host declares which adapter owns measurement and saving, preventing double recording.
3. The visible reader starts a session and reports cumulative per-target time. The rail shows acknowledged plus pending time with save status.
4. The host validates and merges a checkpoint against fresh file bytes, preserving other reader data, then atomically updates the selected HTML.
5. Copy map and the agent extraction command include a compact visibility summary with notes. TD's existing send-back action uses that summary. The saved file remains the durable source.
6. The next writer sees which parts received little time, then judges why. Neither the script nor an AI classifies a short view as irrelevant or poorly written.

## External

None: no third-party API, credentials, model call or new dependency. The local review server is task-scoped, not a shared machine service.

## Proof required before completion

Use real browser and native-reader runs: scroll between targets; lose focus; open a modal; save and reopen the same original file; retry a checkpoint; edit a note while a checkpoint saves; rebuild the same and changed content. Confirm unknowns, historical revision isolation and unchanged authored bytes. Verify stale writes and unauthorized HTTP requests cannot alter the file. Agent QA must not create human reading records.

## Evidence from the current source

- [Current page engine](/home/parker/Work/terminal-delight/app/src/docview/engine.rs): `PageEngine` describes snapshots and a future live engine; `Anchor` carries geometry.
- [Native reader and writer](/home/parker/Work/terminal-delight/app/src/docview/page.rs): `PageDoc::wheel` owns native scrolling; `write_notes` reads fresh bytes, checks the layout hash, plans, verifies and commits the write.
- [Writable note regions](/home/parker/Work/terminal-delight/app/src/docview/notes.rs): `notes_regions` and `outside_notes` currently recognize notes, concurrence and the note mirror.
- [Brief builder](../../../briefing/scripts/brief.py): `build` assembles scripts and preserves reader notes/concurrence.
- [Browser snapshot export](../../../decision-brief/assets/notes.js): `snapshotNotes` exports HTML; the current browser status explicitly says browser storage only.
- [Current section links](../../../fancy-pants-brief/assets/sections.js): `nav.sections` is generated from headings.

Source paths are supporting references. These are observations from the current checkout, not a claim that the proposed behavior is implemented or released.
