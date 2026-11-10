# HTML

Before drawing, read `decision-brief/reference/pictures.md` and `decision-brief/reference/glass.md` from the sibling skill, if it is installed: the first is how to draw a figure that argues, the second is what the glass look expects of a page. Reuse `fancy-pants-brief` for the house look: dark glass over one random Omarchy wallpaper, themed ink, gel controls and a section rail. The new brief keeps its chosen purpose; using the assets does not turn every brief into a decision request.

Start with `scripts/brief.py new name.src.html --id STABLE-ID --purpose PURPOSE`, which writes a source with every marker in place, one section, one drawn figure and `TODO(brief)` where the writing goes. It also writes `<!-- briefing: {"id": …, "purpose": …} -->` into the head, so `html name.src.html name.html` needs no flags; a flag that disagrees with that comment is refused. [The engineering source](../examples/engineering.src.html) is a finished example. A complete source has one `<!--BRIEF:head-->` slot in its head, one `<!--BRIEF:notes-->` slot at the end of its body, and one `<!--brief-content-->` / `<!--/brief-content-->` pair around the authored header and main. The assembler rejects unknown or repeated slots, and slots inside the content region: anything assembled there would change the page's fingerprint and make every comment look stale from the start.

Give each significant comment target an explicit stable id and matching `data-brief-anchor`. Every section heading and figure needs one, and so does every decision a reader can stamp: an `.ask`, a `.grill-q`, or a `.q` inside a `.grill`. The title and first line need one too, in `<div class="opening" id="top" data-brief-anchor="top">`, which `new` writes and `adopt` adds to the `h1`. Name decisions `q-…` and calls `call-…`, so `orient` can tell them apart at a glance. Use the same id after renaming the heading; never reuse a removed id for a different claim.

Put stable ids on individual findings and table/list entries. Each explicit entry gets its own note and visible-time target in the rail.

```html
<h2 id="sec-return" data-brief-anchor="sec-return">Returning a comment</h2>
<figure id="fig-target" data-brief-anchor="fig-target">
  <span class="lbl">01 · A comment's target</span>
  <!-- Draw the mechanism here. -->
  <figcaption>A removed target keeps its comment unresolved.</figcaption>
</figure>
```

Terminal Delight draws a page as a picture and presses only links and `[data-dlg]` buttons, so a closed `<details>` stays closed there. Anything collapsed is a button that opens a `<dialog>`, which is what the Last time strip is.

Build with `scripts/brief.py html SOURCE OUTPUT`, adding `--id` and `--purpose` when the source does not name itself. It reads the existing canonical notes assets, with a checked one-line adaptation for explicit anchors. There is no forked asset or storage-format migration. Rebuild through the same command; do not paste empty notes islands over a reader's comments.

The output is self-contained for its rendering and annotation UI. Evidence links are deliberate navigation to adjacent files; share their directory when those sources must travel with it. Drawing assets and scripts are inline, with no CDN or network dependency. A linked evidence note is not a rendering dependency.

The new output's handoff bridge shows an unresolved-feedback notice when carried comments have an unknown revision or missing target. Copy Map includes those removed targets and their reader text. The older skill's map generator and storage stay unchanged.

Edit the source, never the built page. A rebuild replaces the page's content with the source's, so `html` refuses when the page's content no longer matches the revision it was built with, and `check` reports that as `edited_since_build: true`. Port the edit into the source and rebuild. `--discard-output-edits` rebuilds anyway, keeps the edited page as a `.bak`, and marks any carried comments' revision unknown, since the reader commented on wording that is now gone. `html` also refuses to write over a file it did not build.

The wallpaper comes from `decision-brief/scripts/brief-wall`, which needs Omarchy themes and `vips`. Where those are missing, the refusal carries `brief-wall`'s own reason. `--no-wall` builds on the stylesheet's own dark ground instead. That page is complete and commentable but outside the Omarchy house look; use it where the house look is not available, not to skip it.

On rebuilding an existing output, the tool preserves its wallpaper, both notes islands including revisions, and the last reader-notes mirror byte for byte. It validates the old islands before replacement and keeps the old bytes in a content-addressed `.bak` file. On POSIX, rebuilding uses the same stable lock as the local review server and compatible native readers. Fresh-byte comparisons still detect writers that do not cooperate; atomic replacement alone does not supply a transaction.

If a canonical source hook changes, assembly stops for review. Do not silently remove the guard or mutate the older skill to make this one pass. Review and update the small adaptation alongside its tests.

Verify with the sibling glass gate, this skill's local-link checker and an isolated headless browser. Check at a narrow pane width and a phone width. A figure's text must fit its own viewBox, not merely avoid page overflow. Every important target needs an actual note control; a total count cannot establish coverage.

In Terminal Delight, the native reader can submit comments into the original HTML. A standalone browser stores live edits in localStorage and exports a map. Test the host's persistence path before reporting a disk save. The existing notes engine can restore a browser-held comment deleted by another writer; this skill does not claim to solve that conflict.

## Visible-time record saves

New HTML builds contain a separate `report-reading` JSON island. It preserves recording sessions and their content revisions across rebuilds; an unknown time is `null`, distinct from a monitored zero. Extract it with:

```bash
python3 scripts/brief.py reading name.html
```

On Linux with a systemd user manager, open the autosaving browser review with:

```bash
python3 scripts/brief.py review name.html
```

This starts or reuses a per-file user service, checks its live connection and opens the default browser at that URL. It restarts a stopped service or one serving an older version. The service outlives the launching terminal and restarts on failure; after logout/reboot, rerun `review`. `--no-open` checks the connection and prints the URL without opening a browser. In Terminal Delight, print that URL on its own line and give the complete `review` command as the recovery route. A plain file opened in Chrome cannot write its original HTML; its “Browser storage only” status means export is still required. Do not describe that handoff as autosaving.

The underlying POSIX foreground server remains available:

```bash
python3 scripts/brief.py serve name.html
```

It prints the private loopback URL for that session and serves only the selected file. The CLI remembers one port per file under the user’s state directory, preserving the browser origin across restarts, while the route token changes. A busy remembered port is an explicit error; silently choosing a new origin would strand pending browser checkpoints. A page's adapter can submit cumulative reading checkpoints, which update the original HTML after validation, locking and read-back. Repeated checkpoints take the maximum for a session rather than adding the same elapsed time twice. Eight rolling backups live under the user's state directory. The stable adjacent `.brief-review.lock` is coordination metadata; it contains no feedback and must not be deleted while writers use it.

New builds include the browser clock and following rail. The clock records while the page is visible and focused, pauses behind modal dialogs or when switched away, and counts still periods without an input-idle cutoff. It samples each second and saves changed counters every five seconds or on deactivation. Monitoring gaps over three seconds are retained as gaps. Notes are submitted as exact add/delete/concur changes alongside reading checkpoints, preserving other writers' entries. Copy map and snapshot export include visible-time data. Rail numbers are cumulative totals across visits; a lit dot marks a target counting now. A section uses its full content box, so it and a visible figure or entry inside it may count together. Fully offscreen targets retain their totals and stop advancing. The current-section highlight follows the largest exposed section.

The exact-file server does not serve sibling source files. Local evidence references remain usable in the original HTML; in the live review they explain that the local copy is needed. External links remain normal deliberate navigation. A source rebuild and this server use the same lock. Writers that do not share it are guarded by fresh-byte comparisons. A compatible native Terminal Delight reader measures the real document viewport, selected pane, active tab and foreground window; the hidden Chromium rasterizer never supplies human time. It shares this record and lock, subtracts measured native chrome, preserves its session through FOCUS lending/zoom/resize, and journals pending writes for retry. Native Copy map/send-back includes the anchored summary. This needs the native reading-record integration; older TD builds remain annotation-only. Verify the build before claiming native timing is installed.

Browser QA and native render probes must set `window.BRIEF_READING_HOST={recording:false}` before page scripts run. Automated browsers also default to recording disabled when WebDriver is reported. Do not populate a person's reading record while verifying an artifact; use temporary fixtures for recording tests.
