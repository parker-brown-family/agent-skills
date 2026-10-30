# Briefing

A skill that has an AI agent write up its work as a brief you can read in a few minutes and comment on passage by passage. Each claim links to its evidence. Your comments go back to the agent pinned to the section and the version you read, so it can tell "answer this" apart from "you were reading an older draft" and "that passage is gone".

It writes HTML, drawn and commentable in any browser, or Markdown with a plain JSON file for comments. The agent picks the medium and the purpose (summary, engineering explanation, decision, or one you name) from what you asked and any preferences you've recorded. It doesn't interview you about formats.

## Try It

From this directory. The Markdown route needs only Python 3.9+:

```bash
python3 scripts/brief.py doctor
python3 scripts/brief.py check examples/engineering.md
python3 scripts/brief.py resolve examples/engineering.md examples/engineering.feedback.json
```

The last command places a reader's comment against the brief and reports it `resolved`: its section exists in the version the comment was written on. Change one word in a copy of the example and resolve again: the comment is still there, now `needs_review` with `revision_changed`, and the command exits 2.

The HTML route, with the `decision-brief` and `fancy-pants-brief` skills installed beside this one:

```bash
python3 scripts/brief.py new /tmp/demo.src.html --id demo-brief --purpose summary --title "Demo"
python3 scripts/brief.py html /tmp/demo.src.html /tmp/demo.html
python3 scripts/brief.py check /tmp/demo.html
```

`check` refuses the page until every `TODO(brief)` that `new` left has been written. Open the [HTML example](examples/engineering.html) to see a finished brief: every heading and figure takes a note, and **Copy map** produces the text a reader pastes back to the agent.

## Install

Put the skill where your agent discovers skills. For Claude Code that is `~/.claude/skills/briefing` (personal) or `.claude/skills/briefing` (one project). Other agents that read `SKILL.md` folders have their own directory, and an agent with no skill system can be pointed at `SKILL.md` directly.

For HTML, install `decision-brief` and `fancy-pants-brief` from this repository as well. `brief.py` finds them beside its own real location, so symlinks to a full clone work, and so does copying all three directories together. Copying `briefing` alone gives you everything except `html`, and `brief.py doctor` will say so.

| Part | Needs |
|---|---|
| `new`, `check`, `feedback`, `resolve` | Python 3.9+ |
| `html` | the two sibling skills above |
| The wallpaper behind an HTML brief | [Omarchy](https://omarchy.org) themes and `vips`. Elsewhere, `html --no-wall` builds on the stylesheet's own dark ground |
| `tests/browser.mjs` | Node 22+ and Chromium or Chrome (`CHROMIUM=/path` to choose one) |

## Commands

| Command | Does |
|---|---|
| `new SOURCE --id ID --purpose P [--title T]` | Writes a starting `.md` or `.src.html` with every marker in place. Never overwrites |
| `html SOURCE OUTPUT [--id ID --purpose P]` | Assembles a self-contained, commentable page; a source from `new` names itself, so the flags are optional. On a rebuild it keeps the reader's notes, agreements and wallpaper byte for byte and backs up the old page |
| `check DOCUMENT` | Checks anchors, leftover `TODO(brief)` passages and every local link, image, `file://` URL and fragment, listing every problem at once. Reports `wallpaper` and `edited_since_build` for a built page |
| `feedback DOCUMENT` | Prints a page's saved notes, or a blank Markdown comment file, as JSON |
| `resolve DOCUMENT MAP` | Places returned comments against the current document. `MAP` is the JSON file, Copy map text, or `-` for stdin. Exit 2 means some need review |
| `doctor` | Says which commands work on this machine and why the rest don't |

Every refusal names its fix; [refusals](reference/refusals.md) lists them. Run the tests with `python3 -m unittest discover -s tests -v` and `node tests/browser.mjs`; add a path to the second to check your own HTML brief in the same headless browser. The browser test exits 77 when it cannot run, and that means not checked.

## How Comments Come Back

Markdown and HTML share one handoff format, not one renderer. A map names the brief, the revision the reader saw, the passage, and the reader's words; see the [feedback contract](reference/feedback.md).

In an HTML brief opened in an ordinary browser, notes are kept in that browser's storage, and **Copy map** is how they leave. Paste the text to the agent; `resolve` reads it as it is. An HTML brief opened in Terminal Delight can have its notes saved into the file itself, and `feedback` exports them. A Markdown brief takes comments in an adjacent `name.feedback.json`, which `feedback` creates blank.

A comment whose passage was removed stays in the results, marked unresolved. A comment written on an older version is marked for review, never quietly applied to the new wording. An empty comment is never read as agreement.

## Limits

- The notes format does not record which version each individual comment was written on. Once a brief's wording changes under saved comments, their revision is reported as unknown and the old page is kept as a `.bak` for comparison.
- Copy map text joins each comment's lines with spaces; `resolve` says so with `"text_exact": false`.
- Notes held only in one browser's storage must be copied out before the agent rebuilds the page.
- Two people editing the same page at once can still make the shared notes engine restore a comment the other deleted.
- Markdown has no comment controls of its own; inline commenting depends on the reader app.
- Saving notes into the file inside Terminal Delight has not been exercised by these tests.

## MP4

**Future medium. No video generation, playback controller, timestamp editor or video-annotation export is implemented here.**

The intended loop follows the same principle as the working media: pause on screen, remark on a moment or interval, resume playback, then return the map with the particular cut and an agent summary. A future target needs the cut identity, revision and an explicit time unit. Time zero is a valid position; an absent timestamp is unknown. A range cannot quietly become a point. A re-edit must keep old comments unresolved until their targets are reviewed. Spatial feedback on a frame may be added when a concrete use requires it.

The current helper refuses MP4. The README earmark is the entire video scope of this version.

## Alongside the Other Brief Skills

`briefing` sits beside `decision-brief` and `narrative-brief`, and an explicit request for either still gets that skill. It reuses `decision-brief`'s notes engine and stylesheet as they are, with one checked adaptation at build time and no copy of either, and changes no reader.

On Parker's machine, link the directory once into a discovery root, run `agent-parity --sync-skills`, then `agent-parity`. The repository directory stays the canonical source.
