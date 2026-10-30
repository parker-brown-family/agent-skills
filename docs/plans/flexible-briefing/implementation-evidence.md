# Implementation Evidence

The new `briefing` skill is implemented alongside the current briefing skills. This record distinguishes automated checks from host features that were not exercised.

## Validation

From the skill directory, `python3 -m unittest discover -s tests -v` passes 18 tests. The tests cover preserved notes islands, concurs, mirror and backup; malformed/unknown formats; duplicate anchors; detected concurrent writes; stale, unknown and missing feedback targets; explicit agreement; manual HTML edits; browser serialization; a changed upstream adapter hook; and broken evidence paths/fragments.

`node tests/browser.mjs` passes using a separate headless Chromium and temporary profile. It checks each of four section headings and three figures for the correct stable target and a working note control. A real comment survives reload, appears in the exported map, survives the snapshot path and a rebuild after a heading rename. The changed brief exports an unknown feedback revision rather than claiming that the old comment was made on the new wording.

Removing that target then produces a visible review notice. Copy Map retains the orphaned comment and labels it unresolved. A local handoff bridge supplies this behavior in new outputs without changing the canonical notes engine.

At both 968 and 390 pixels, the browser reports the requested width, no horizontal page overflow and no clipped SVG text. A wide mechanism drawing scrolls inside its figure. The evidence selector hides the deeper levels at its sources setting. Screenshots were inspected at both widths; these are rendering checks in an isolated browser, not checks in the native Terminal Delight document square.

The paired Markdown and HTML examples pass the helper's local-link and anchor checks. The saved Markdown feedback example resolves to its intended section. The HTML example passes the glass gate with photographed mean luminance 23/255. This value only establishes the gate's dark-page condition, not aesthetic quality.

The skill-audit scanner reports no instruction override, shell-execution request, exfiltration request, permission request or hidden text. Its credential/write-word matches come from the canonical inlined CSS/notes comments using words such as “tokens” and “overwrite”; they are not credential operations.

## Source Trace

The [skill](../../../briefing/SKILL.md) routes medium and purpose. The [helper](../../../briefing/scripts/brief.py) implements `build`, `inspect`, `content_revision`, `feedback` and `resolve`. [Python tests](../../../briefing/tests/test_brief.py) establish the refusal and preservation cases. The [browser check](../../../briefing/tests/browser.mjs) establishes the UI cases above. Each path opens the source; symbols are named here without appending line locators to the links.

The HTML adapter changes one anchor-selection expression in the assembled output. It reads and checks the shared canonical script at build time; it does not edit or store a fork of that script. The common handoff envelope is distinct from the unchanged format-1 HTML storage.

The old [decision-brief](../../../decision-brief/SKILL.md) and [fancy-pants-brief](../../../fancy-pants-brief/SKILL.md) tracked files are unchanged by this task. The only root catalogue edit adds the opt-in skill. No Terminal Delight or Markdown Delight code was changed.

## Limits

Native inline Markdown commenting and native Terminal Delight in-place saving were not exercised in this implementation run. The Markdown fallback is an ordinary adjacent JSON file. Browser comment persistence was tested through localStorage and snapshot export; it is not a claim that a standalone browser wrote the original file.

Rebuilds preserve existing on-disk annotations and keep the old bytes in a backup. Unsaved browser-only comments must be exported or saved before regeneration. Mixed-origin format-1 comments do not carry exact individual content revisions. The exporter marks their revision unknown and retains their text.

The existing browser-held deletion conflict remains in the reused HTML engine. A detected concurrent output edit causes refusal, but the assembler does not implement a host-wide multi-writer transaction. MP4 remains a visible future earmark with no implemented annotation feature.

## Reproduction

Run from the skill directory:

```bash
python3 -m unittest discover -s tests -v
node tests/browser.mjs
python3 scripts/brief.py check examples/engineering.md
python3 scripts/brief.py check examples/engineering.html
python3 scripts/brief.py resolve examples/engineering.md examples/engineering.feedback.json
python3 ../fancy-pants-brief/scripts/fancy-pants check examples/engineering.html
```

To invalidate the central feedback claim, remove an anchor or alter the document after generating a map. The resolver must retain the comment, label the mismatch and return exit 2. A resolved result or discarded reader text falsifies the claim.
