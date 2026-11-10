# Active Reading

## Approved rule

Parker: "it is possible a brief opens and is not read, so might sit stagnant for 5 10 minutes an hour a day. so consider, but count all the same" and "timer only ticks while the doc is ONSCREEN AND ACTIVE". This clarifies the approved [saving architecture](02-architecture.html). No mouse/keyboard idle timeout, attention inference or automatic relevance judgement.

The display says **Visible time**. Long still periods count while the host reports an active visible document. This is a foreground exposure record, not proof that a person was reading. Generic browser APIs cannot prove every pixel is unoccluded by another application; preserve the host/method in the record rather than claiming eye attention or universal occlusion detection.

## Files

All paths below are proposed changes. No feature implementation is written at this gate.

### agent-skills

- `briefing/assets/reading.js` — target registration, activity state, clock, pending queue, summary/export hooks.
- `briefing/scripts/reading.py` — reading schema, validation, merge and exact-island updates; no HTTP or UI.
- `briefing/scripts/review_server.py` — selected-file loopback server; serves the document, validates typed edits and acknowledges saves.
- `briefing/scripts/brief.py` — assemble/preserve reading data; `serve`, `reading` and feedback summary; coordinate builds with the shared review-file lock.
- `briefing/assets/feedback-bridge.js` and `decision-brief/assets/notes.js` — expose typed note changes and include reading in Copy map and snapshot export. Preserve existing note/concur wire formats.
- `fancy-pants-brief/assets/sections.js`, `decision-brief/assets/base.css` — responsive left navigation, nested entries and cumulative time.
- `briefing/tests/reading.mjs`, `briefing/tests/test_reading.py`, `briefing/tests/browser.mjs` — clock/host/server/rebuild fixtures and real browser behavior.
- `briefing/tests/fixtures/reading/` — shared JSON and HTML fixtures, consumed by Python, JavaScript and TD Rust tests.
- `briefing/SKILL.md`, `briefing/reference/html.md`, `fancy-pants-brief/SKILL.md` — document saved/pending behavior and brief writing rules: short sections, self-contained context, evidence behind links.

### Terminal Delight

- `app/src/docview/reading.rs` — pure types, clock transitions, region parsing, schema/merge, save planning and summary.
- `app/src/docview/reading_ui.rs` — native section navigation and visible-time/status labels, using existing document hit routing.
- `app/src/docview/engine.rs`, `extract.js`, `snapshot.rs`, `cache.rs` — explicit reading-target bounds and hierarchy; capability metadata; extraction/cache-version update. Snapshot probes declare recording disabled before author scripts run.
- `app/src/docview/page.rs` — native viewport updates, target clock, checkpoint queue, combined note/reading write transaction and watcher acknowledgement.
- `app/src/docview.rs`, `backend.rs`, `app/src/pane/doc.rs` — lifecycle/activity contract for floating square, document face and FOCUS lending; correct pause/resume on switching surfaces.
- `app/src/docview/notes.rs` — extend known reader-data masks and the existing checked commit boundary; share the lock protocol, never replace note parsing with DOM serialization.
- `app/src/pane.rs`, `main.rs` — route window/pane/overlay activity transitions to the selected document, including loss of focus and shutdown.
- `app/src/lang.rs` or its current document-string module — translate new native visible-time/save-state strings for all supported languages.
- `app/tests/reading_record.rs`, `app/tests/snapshot_engine.rs` and document integration tests — shared fixtures and native save/reopen/activity proof.

Implementation uses an isolated TD worktree based on the then-current selected integration branch. Read its own release instructions and current document code before patching; source paths above identify responsibilities, not permission to overwrite another agent's work. Release assignment remains unselected at this gate.

## Types and signatures

The portable JSON names use snake_case. Milliseconds are finite, nonnegative safe integers. A session id is random and unique per actual recording session, reused for its checkpoints and recovery.

```ts
type Activity = 'active' | 'inactive' | 'unknown';
type TargetKind = 'opening' | 'section' | 'figure' | 'entry';
type ReadingTarget = {
  anchor: string; title: string; kind: TargetKind;
  parent: string | null;
  visible_ms: number | null; // null: observation unavailable; 0: monitored, unseen
};
type ReadingSession = {
  session: string; document: string; revision: string;
  host: 'browser' | 'terminal-delight'; method: 1;
  targets: ReadingTarget[];
  gaps: { sequence: number; reason: 'clock_gap' | 'activity_unknown'; elapsed_ms: number }[];
};
type ReadingRecord = { format: 1; sessions: ReadingSession[] };
type Checkpoint = { format: 1; reading: ReadingSession; note_edits: NoteEdit[] };
type SaveResult =
  | { state: 'saved'; acknowledged: ReadingSession; file_revision: string }
  | { state: 'pending' | 'failed'; reason: string };
declare function activity(): Activity;
declare function sample(nowMs: number, activity: Activity, visibleAnchors: string[]): void;
declare function checkpoint(): Promise<SaveResult>;
```

`NoteEdit` follows TD's existing add/delete/concur operations, with exact baseline entry matching for deletion and per-target concurrence changes. Browser save requests send changes, never a replacement map that could erase another reader's note. The pre-change island is the baseline; unchanged notes generate no edit. Shared fixtures pin the exact operation wire names during implementation.

```python
def validate_session(value: object, document: str, revision: str) -> ReadingSession: ...
def merge_record(saved: ReadingRecord, incoming: ReadingSession) -> ReadingRecord: ...
def plan_reading_write(html: bytes, session: ReadingSession) -> WritePlan: ...
def review_lock(path: Path) -> ContextManager[None]: ...
def serve_review(path: Path, *, port: int = 0) -> None: ...
```

```rust
pub enum Activity { Active, Inactive, Unknown }
pub struct ReadingClock { /* private state, no implementation in this gate */ }
impl ReadingClock {
    pub fn sample(&mut self, now: Duration, activity: Activity, visible: &[String]);
    pub fn checkpoint(&self) -> Option<ReadingSession>;
}
pub fn merge(saved: &ReadingRecord, incoming: &ReadingSession) -> Result<ReadingRecord, Refusal>;
pub fn plan_write(bytes: &[u8], update: &ReadingSession) -> Result<ReadingWrite, Refusal>;
pub fn review_lock(path: &Path) -> Result<ReviewLock, Refusal>;
// Backend lifecycle hook, separate from drawing and scroll-position reporting.
fn reading_activity(&mut self, activity: Activity, cx: &mut Context<DocumentView>);
```

## Clock contract

1. A browser records only when `visibilityState` is visible, `hasFocus()` is true, no modal covers the reading surface, and human-review recording is enabled. Native TD additionally requires the pane/tab and document surface to be selected and the window to be active. Unknown activity pauses recording and retains an explicit gap.
2. No input-idle cutoff. An hour without mouse movement is an hour if observations continue to establish active visibility.
3. Sample once a second while a document is active, and settle the prior interval at scroll/resize, focus, visibility, modal, surface, target-layout and close transitions. Use a monotonic clock. Never attribute an interval to the new viewport before the transition.
4. A sample gap over three seconds is recorded as an observation gap and excluded from visible counters. This catches sleep, suspension and stalled event loops without treating their entire delay as active exposure. It is not an idle timeout: regularly observed still pages keep counting.
5. A target counts when its measured content rectangle intersects the unoccluded content viewport with positive area. Browser: opening block, section container, figure, explicit entry. TD: the same extracted bounds, transformed by native scroll/zoom and clipped to the actual document body. Rail, note controls and covered background contribute no area.
6. Known target geometry starts at zero on an active session; unavailable geometry stays null. Nested targets count independently. Do not sum them as document reading time. Native snapshot/QA/read-back probes set recording disabled; a hidden renderer never starts a human session.
7. Preserve continuous page residency through resizing/FOCUS lending as the same session, with one measurement owner. Duplicate views start separate sessions. All displayed times are explicitly session-based or aggregated across sessions, never claimed as unique attention.

## Save contract

- Checkpoint changed counters every five seconds and on deactivation/close. Coalesce queued checkpoints to the newest cumulative values. Save visible data before reporting success; final close is best effort and unacknowledged time stays pending.
- Merge a retry using per-session, per-target maxima. Do not add the same checkpoint twice. Reject document/revision/method disagreement for an existing session. A content change starts a new session; old measurements stay historical.
- One stable adjacent hidden lock file, `.<basename>.brief-review.lock`, coordinates Python `fcntl.flock(LOCK_EX)` and Rust's existing `libc::flock(LOCK_EX)`. Create it with mode 0600, refuse symlinks/foreign owners/hardlinks, and never unlink it on close. Hold it across fresh read, merge, validation, atomic rename and read-back. Notes, reading and rebuild writes all participate. Never lock the replaceable HTML inode itself. Lock artifacts contain no remarks or reader data.
- Reuse checked atomic commits and backup policy. Verify that authored bytes and unrelated reader islands have not changed; exclude the reading island from authored revision and layout hashes. Preserve current notes and other recording sessions under the lock. External editors that do not honor the lock are guarded by fresh-byte checks; conflicts remain pending rather than silently rebasing authored content.
- Store pending checkpoints in browser storage or TD's existing per-document state area, keyed by document/revision/session. Clear only acknowledged values. On storage failure keep memory state and show failure. Retry while the review session is alive; recovery never invents intervals while closed.
- Local server: exact loopback Host/Origin and random-token route, same-file-only, JSON payload limit 1 MiB, finite counters, bounded identifiers/arrays, no arbitrary paths or HTML bodies. Reject symlinks, hardlinks, readonly files and replaced targets according to existing commit rules. Wrong identity/revision returns a conflict without touching the file. No external requests or browser-opening side effects unless requested.
- Snapshot export includes reading; Copy map and native send-back append a compact anchored visible-time summary. Keep summary labels distinct from user-written notes. `brief.py reading PAGE.html` extracts all sessions/revisions; normal feedback can show the current revision summary without dropping historical data.

## Call stack

**Browser:** review page response declares adapter → reading script registers targets → activity/viewport transitions settle clock → checkpoint typed changes → server validates request → acquire review lock → read fresh HTML → merge data and existing note edits → verify preserved regions → atomic write/read-back → acknowledge → clear pending checkpoint.

**TD:** pane/workspace selects the visible reading surface → DocumentView forwards activity → PageDoc supplies native viewport and extracted bounds → ReadingClock samples → checkpoint queue → combined existing note/read transaction under review lock → file watcher recognizes own write → acknowledge without resetting layout → update rail and compact summary.

**Rebuild:** acquire same review lock → existing `build` checks document ownership and authored edits → retain all reader islands/revision records → assemble new content/scripts → atomic write → current revision reads only its own counters.

## Test plan

| Test | What must be proved |
|---|---|
| `still_active_hour_counts` | 3,600 seconds of regular observations with no input produce 3,600 seconds on the visible target. |
| `inactive_open_day_does_not_count` | Hidden, unfocused and nonselected surfaces remain unchanged despite staying open. |
| `activity_transition_settles_old_view` | Scroll/focus change attributes elapsed time to the old viewport and pauses promptly. |
| `covered_document_pauses` | Native overlays and browser modal dialogs stop background-section clocks. |
| `sleep_or_stall_is_a_gap` | A long scheduling gap is explicit and never charged as reading. |
| `unknown_geometry_is_not_zero` | Missing geometry stays null; known unseen targets remain zero. |
| `one_owner_during_lending` | FOCUS lending or backend probing cannot double-record. |
| `retry_checkpoint_is_idempotent` | Repeated and out-of-order cumulative checkpoints preserve the maximum once. |
| `concurrent_note_and_reading_survive` | Two real processes saving browser/native-compatible updates preserve both under the lock. |
| `same_revision_rebuild_retains_data` | Measurements and notes survive without revision drift. |
| `changed_revision_does_not_inherit_time` | New content starts unmeasured; prior records remain extractable. |
| `server_refuses_wrong_authority` | Wrong Host/Origin/token, path, identity, revision, malformed and oversized payloads cannot write. |
| `save_reopen_exact_original` | Real browser and isolated native reader reopen the same file and display acknowledged counters/notes. |
| `save_failure_stays_pending` | Readonly, write failure and conflict never say Saved or erase pending data. |
| `qa_does_not_become_human_reading` | Browser/native render validation creates no observation session. |
| `rail_and_maps_keep_context` | Desktop/narrow layout, section jumps, nested entries, Copy map and native send-back retain anchors and visible-time meaning. |

## Least confident decisions

1. **Active visibility uses the host's focus and surface signals.** This implements Parker's request without pretending that browser APIs can see all external occlusion. Actual host lifecycle checks are required before shipping.
2. **One-second observation, three-second gap, five-second save.** These are proposed engineering values, not measured requirements. Tests distinguish a still reader from a suspended monitor. The saved method version makes a future change explicit.
3. **A shared per-path lock and checked data-only writes.** Both runtimes must follow the same lock protocol. Shared wire fixtures and a real two-process race test guard against code drift; a noncooperating external editor can still create a conflict, which must be visible.

Gate 4 will order the tracer bullet and working slices after this design is approved. No implementation code exists yet.
