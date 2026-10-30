# Briefing

An opt-in skill for short briefs with linked evidence and feedback on specific passages. It sits beside `decision-brief`; existing skill names and assets keep their current behavior.

Choose a medium and a purpose independently:

| Medium | Summary | Engineering | Decision |
|---|---|---|---|
| HTML | Visual account | Mechanism and validation | Options and recommendation |
| Markdown | Short account | Explanation and evidence links | Choice and consequences |
| MP4 | Future | Future | Future |

Start with [SKILL.md](SKILL.md). Open the [HTML engineering example](examples/engineering.html) or its [Markdown counterpart](examples/engineering.md). They explain the same feedback mechanism; neither is a finding about an unrelated project.

## Evidence

The main artifact stays brief. Choose the depth of its linked evidence: sources, reasoning, or code trace. The default reaches primary evidence, with tests and source for code claims. Supporting notes use portable Markdown links and can be navigated as an Obsidian-style collection. No Obsidian installation is required.

Only the requested brief is declared as the primary review artifact. A linked test log, evidence note or source file does not get its own declaration or steal focus. See [evidence policy](reference/evidence.md).

## Feedback

Markdown and HTML share the [handoff contract](reference/feedback.md), not a renderer or a storage migration. The map identifies the exact document revision, target and reader comment. A missing target or changed revision remains visible and unresolved.

HTML uses the existing format-1 islands and browser interaction. In Terminal Delight, submitted annotations can be saved into the original file by its native reader. In a standalone browser, edits stay in browser storage; copy the map or use a tested host snapshot/write capability. Do not claim those edits reached disk.

Markdown's portable fallback is an adjacent editable JSON map. It preserves comments on named sections or blocks and can be copied into a prompt or supplied as a file. Inline commenting and direct send depend on the chosen reader and must be checked separately.

## Tools

Run from this directory:

```bash
python3 scripts/brief.py html examples/engineering.src.html examples/engineering.html --id reader-feedback-html --purpose engineering
python3 scripts/brief.py check examples/engineering.html
python3 scripts/brief.py feedback examples/engineering.html
python3 scripts/brief.py feedback examples/engineering.md
python3 scripts/brief.py resolve examples/engineering.md examples/engineering.feedback.json
python3 -m unittest discover -s tests -v
node tests/browser.mjs
```

`feedback` prints JSON to copy or save beside the document. For a new Markdown brief, save it as `name.feedback.json` and add reader comments there. It never writes or declares another artifact automatically. `resolve` prints every comment with its resolution status; exit 2 means review is required, and exit 1 means malformed or unsupported input. Neither means that comments were discarded.

The HTML assembler reads canonical assets from sibling directories. It adapts one checked anchor-selection line at assembly time to honor `data-brief-anchor`. It keeps no forked notes asset and changes no canonical file or island format. An upstream hook change causes a visible refusal. The assembler preserves both notes islands and the last reader-notes mirror byte for byte, keeps the wallpaper, backs up the existing output, and refuses malformed notes or a detected concurrent change. It expects UTF-8 files. New HTML sources must have the markers shown in the example.

Its small handoff bridge shows a review notice for carried feedback with an unknown revision or missing target. Copy Map retains comments on removed targets and labels them unresolved. This bridge is local to the new skill's output; the older skill is unchanged.

When a changed brief carries old annotations, format 1 cannot establish the content revision of every individual comment. The exported revision becomes `null`, and resolution reports `revision_unknown`. Preserve the backup and review it with the current brief; never relabel the comments as current by default. Browser-held deletion conflicts in the existing notes engine remain a known limitation.

## MP4

**Future medium. No video generation, playback controller, timestamp editor or video-annotation export is implemented here.**

The intended loop follows the same principle as the working media: pause on screen, remark on a moment or interval, resume playback, then return the map with the particular cut and an agent summary. A future target needs the cut identity, revision and an explicit time unit. Time zero is a valid position; an absent timestamp is unknown. A range cannot quietly become a point. A re-edit must keep old comments unresolved until their targets are reviewed. Spatial feedback on a frame may be added when a concrete use requires it.

The current helper refuses MP4. The README earmark is the entire video scope of this version.

## Adoption

Invoke `briefing` by name to use this pattern. `decision-brief`, `narrative-brief` and `fancy-pants-brief` remain available. This version adds no changes to Terminal Delight or Markdown Delight and does not change their defaults.

Install by linking this directory into the host's skill-discovery location. On Parker's machine, link it once into a discovery root, run `agent-parity --sync-skills`, then `agent-parity`. Keep the repository directory as the canonical source. Existing assets remain canonical in the sibling skills.
