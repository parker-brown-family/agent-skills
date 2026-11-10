# Reading time: checks and limits

The browser and native reader keep independent sessions in the original HTML’s `report-reading` island. Comments and concurrence keep their existing formats. A retry merges cumulative maxima for the same session; another visit adds a session. Never sum a section and its contained figures to infer total reading time.

## Evidence

| Check | Result |
|---|---|
| Python brief/server suite | 133 passed, including selected-file writes, revision conflicts, typed notes, unsafe targets, concurrent rebuilds and stable browser origin on restart. |
| JavaScript clock | A still active hour counts; an inactive day adds nothing; fractional time, previous viewport, unknown geometry and sleep gaps pass. |
| Real Chromium | Focus/tab/modal pauses, following rail, notes/time save/reopen, Copy map, portable export without a stale server token and disabled probe recording pass. |
| Rust record/notes suite | 67 passed, including pending-write recovery and subtraction of measured chrome. |
| Two separate writer processes | 32 sessions and 16 notes preserved; retries did not add time twice; authored revision unchanged. |
| Real native reader | Private Xvfb/software Vulkan run passes foreground pause, scroll, FOCUS, note-modal pause, zoom, resize, note/time coexistence, Copy map and original-file reopen. Includes opening/section/figure/entry targets, time-only Copy map, pane/tab pauses and the 1,708px-wide native left rail. Latest complete run is linked below. |
| Native unit suite | 3,438 passed, zero failed, 12 ignored with four test threads; formatting and clippy pass. |
| Alternate terminal core | Builds with the reference Alacritty core. Native runtime checks use the shipped Rio core. |

[Native proof](07-native-proof.json) · [Two-process race](07-race-proof.json) · [Browser proof](06-browser-proof.json)

The native test uses a temporary synthetic brief. Its Chromium renderer and note read-back add no browser session. No input goes to Parker’s display. The screenshot on the review page comes from that private display and contains test data.

## Repository gate limit

The unrestricted parallel unit run repeatedly timed out one real-terminal prompt-completion test at `Delivered`; the same test passed alone, and the full suite passed with four test threads. This is recorded as a [separate falsifiable follow-up](https://github.com/parker-brown-family/terminal-delight/issues/1411). The introducing commit is not established. No native release or installation is claimed while integration gates remain to be settled.

## Failure and recovery

The race exposed a real bug: the browser note writer found a literal `</body>` inside the notes template’s instructional comment and inserted the note mirror there. The native content hash correctly refused subsequent writes. The writer now uses an HTML parser to find the actual closing body; a regression test and the repeated two-process race pass.

Browser checkpoints persist in per-session localStorage. The review CLI remembers a port per file so reopening after a server restart keeps the same origin; the access token rotates. Browser storage clearing, an explicitly changed origin or a moved file is outside that recovery guarantee. Plain file opening keeps browser-local edits until export; it is not a disk write.

Native checkpoints enter a durable local retry journal before writing the original. Failed writes stay pending. A runtime/style rebuild of the same authored revision rebases the displayed-byte guard and preserves cumulative pending time; a focused regression covers both same-session retry and another reader recovering it. Closing/reopening retries retained sessions, and a verified save clears the acknowledged journal. Cooperating browser, native notes/time and POSIX rebuild writers share a stable lock beside the HTML. Non-cooperating writers remain guarded by fresh-byte comparisons, not a promised transaction.

The clock records foreground exposure, not attention or comprehension. It has no mouse/keyboard idle cutoff. It counts positive exposed area and excludes native rail, note bar and cue using their painted bounds. Over three seconds without an observation is a gap, not invented reading time. Unknown geometry stays `null`; measured unseen time can be zero. Original content changes after layout leave incompatible native checkpoints pending. The browser verifies the authored fingerprint. Native TD checks the file bytes against the snapshot it displayed and uses the file’s declared brief revision; rebuild manually edited output before review.

## Build choice

The native feature uses the current T3 preview as its base, preserving the newer HTML-open path. It lives in an isolated `feat/brief-reading-time` checkout with the matching private renderer. Moving those feature commits to the chosen integration branch is the undo. The release assignment is **unassigned**. This work does not claim an installed or released native feature.

## Source and reproduction

- Browser clock and rail: [reading.js](../../../briefing/assets/reading.js).
- Portable format, shared lock and typed notes: [reading.py](../../../briefing/scripts/reading.py).
- Exact-file browser server: [review_server.py](../../../briefing/scripts/review_server.py).
- Browser checks: [browser_clock.py](../../../briefing/tests/browser_clock.py), [clock cases](../../../briefing/tests/reading.mjs), [save cases](../../../briefing/tests/test_reading.py).
- Real two-process check: [native_race.py](../../../briefing/tests/native_race.py).
- Native implementation: [reading.rs](/home/parker/Work/terminal-delight/.worktrees/brief-reading-build/terminal-delight/app/src/docview/reading.rs), [page.rs](/home/parker/Work/terminal-delight/.worktrees/brief-reading-build/terminal-delight/app/src/docview/page.rs).
- Private-display check: [reading-smoke.py](/home/parker/Work/terminal-delight/.worktrees/brief-reading-build/terminal-delight/scripts/reading-smoke.py).

The Python, JavaScript and Rust checks use byte-identical portable record fixtures. The final native display run is `/tmp/brief-native-smoke-12`; the complete proof is linked above. Native source is committed as `465fc306` on `feat/brief-reading-time`. The tested debug binary reports base `e3990e0c8d8f270b3f8a19009b1d425b978c52f4`, dirty=true, version 0.5.2, Rio 0.5.29, opt-level 0, wire `b92c55624bb8636e`, protocol `7acbf1ac2d1d9d11`. Its tested changes are the native source commit. The final HTML passes the glass gate (mean luminance 39/255), brief validation (10 comment targets, no recording sessions from probes) and isolated browser layout/comment checks at 968px and 390px. The narrative diagnostic reads as an argument; cold-reader grasp 0.50.

Tested binary SHA-256: `3331395c24255bfec178ed1e03df707c5c2e9af3577254d5c3a425de64110e66`. [Saved native source](https://github.com/parker-brown-family/terminal-delight/commit/465fc306) is awaiting integration; it is not an installation.

## Browser delivery repair

Parker's Chrome screenshot showed “Browser storage only · original HTML not saved”: the local file was open without the save adapter, and the separate live-review service had stopped. A link to that stopped service was not a usable saving route.

`brief.py review PAGE.html` now starts or reuses a per-file systemd user service, validates the current connection and opens the default browser there. Repeating it recovers a stopped service or restarts for rebuilt content. The browser origin stays the same; the private route rotates on restart. The launcher checks a saved loopback URL without redirects or proxy use. Browser handoffs include the full recovery command and a line-initial URL. The foreground `serve` command remains available.

The Python suite now passes 138 tests, including verified reuse, remote/mismatched-session refusal, stale content, service restart and startup failures. `briefing/tests/launcher_smoke.py` checks the real service lifecycle and Chromium saves on a temporary synthetic file. Its captured result is `/tmp/brief-launcher-smoke.log`; user documents are never the recording fixture.
