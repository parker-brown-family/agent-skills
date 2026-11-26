# agent-skills

A collection of agent skills — each one a markdown file you paste into any LLM agent.

## What is a skill?

A skill is a SKILL.md file: YAML frontmatter (at least a `name` and a `description`) followed by a plain-text prompt body. You give the file to an agent and it knows what to do.

Most skills here are that file and nothing else. A few also ship small Python scripts the agent runs: `briefing` has `brief.py`, `decision-brief` has `brief-wall`, `glass-one-pager` has `onepager.py`, and `fancy-pants-brief` has `fancy-pants`. The three for briefs are installed together; [briefing/README.md](./briefing/README.md#install) says how.

## How to use a skill

**Option A** — paste the raw URL into your system prompt or agent rules:

    https://raw.githubusercontent.com/parker-brown-family/agent-skills/main/code-taste/SKILL.md

**Option B** — copy the body into your agent framework skill/rule system (Augment, Claude Code, Cursor, Codex, etc.).

## Skills

| Skill | Triggers | Description |
|---|---|---|
| [briefing](./briefing/SKILL.md) | write this up, brief me, explain what you changed, summarize for review, /briefing, a reader's returned notes | A short brief in HTML or Markdown with evidence behind every claim and comments pinned to the passage and version the reader saw. `brief.py` scaffolds, builds, checks every local link, and resolves returned notes, including Copy map text pasted into chat. Markdown needs only Python; `doctor` says what works on a machine. MP4 is reserved |
| [article](./article/SKILL.md) | article, write an article, guide, build log, investigation, explainer, convert to registers | Write one finding in several registers — tl;dr / ELI5 / technical, or beginner / intermediate / advanced — in the house page structure, sequencing `storytelling` for narrative and `avoid-ai-writing` for delivery |
| [code-taste](./code-taste/SKILL.md) | code-taste, audit, anti-patterns | Scan a codebase for five structural anti-patterns, rank by risk, open one ticket per finding |
| [graded-gates](./graded-gates/SKILL.md) | graded-gates, grade this, run the gates | Plan and build a feature by grading it first. The grade sets how many gates a person approves before code exists; a tracer round proves the architecture; the build then runs without stopping for the person and ends in a completion brief. Says what a brief may and may not look ahead to at each stage |
| [localization](./localization/SKILL.md) | localization, i18n, untranslated UI, all languages, mixed-language screens | Classify readers, translate related surfaces in complete locale batches, validate before insertion, inspect shared caption renderers and verify the running interface. Includes a read-only JSON batch checker and scoped proof templates |
| [design-language](./design-language/SKILL.md) | design or restyle a screen, a design system, tokens, a style guide, light and dark, a product family, product colours, a UI audit | Give a family of products one design language with each product recognisably its own: measure a standard in its source, roles before colours, rules a reviewer can test, colour from Omarchy themes by one rule, and a script that proves contrast at both ends of every gradient, outlines, status collisions and colour-blind distance, with a self-test that old wrong values fail. Ships the folio tab, a 2 px title line and a light, dark and system switch remembered per account; the Head Waters suite is the worked example |
| [web-ux](./web-ux/SKILL.md) | web UX, it jumps around, too snappy, can't find X, the arrow keys do nothing, the background keeps changing, the PDF looks too white, /web-ux | How an interactive page behaves, as rules a reviewer can test, each with the failure that earned it: nothing moves under the reader, search finds what a person types, dense results arrive organised, the keyboard works from the moment anything opens, page turns land where they say, a page switch never changes the ground behind it, and a PDF shown inside a themed site wears the theme with the original one click away. Ships scripts that measure whether an overlay holds still, check its keys work the moment it opens, find duplicate functions in a shared scope, and record a page switch frame by frame |
| [web-3d](./web-3d/SKILL.md) | 3D, something I can move around, lay it flat, explode the layers, WebGL, three.js, use the graphics card, would WebAssembly help, /web-3d | Turn structured data into a 3D model on a web page that the reader turns, lays flat, lifts apart into layers and clicks into, on the graphics card through WebGL2 and a bundled three.js. Every part is placed by a rule, never by hand; not run and unknown each look different; a click lands on the part drawn there; a flat view stands in without a graphics card. Ships a starter scene, a bundling script, a screenshot script for hill-climbing the look, and a contract test that runs headless on the real GPU and was mutation-checked against the bugs it guards |
| [decision-brief](./decision-brief/SKILL.md) | decision-brief, audit, review, intake assessment, findings report | Produce a single self-contained HTML brief the reader annotates in the browser; notes anchor to elements and export as a token-cheap map the agent reads back. In [Terminal Delight](https://docs.terminal-delight.brownfamilysports.com/briefs), use its own [Workbench edition](https://github.com/parker-brown-family/terminal-delight/blob/main/app/skills/decision-brief/SKILL.md) instead: the brief opens inside the terminal and ↪ sends the notes back |
| [fancy-pants-brief](./fancy-pants-brief/SKILL.md) | fancy pants, any HTML page a person reads, it came out white, the glass look | The house look for every HTML page an agent makes: glass over a random Omarchy wallpaper in its theme, always dark, gel buttons and a rail of sections, with a tool that builds or dresses the page and a gate that fails one that is light, flat or needs the network |
| [glass-one-pager](./glass-one-pager/README.md) | one-page portfolio PDF, open-source one-pager, work sample, "upload anything", make it look like a terminal | A one-page PDF of what someone builds, drawn as a terminal window with curved glass: live links, sharp text, and a check that its pull request marks are still true. [See one](./glass-one-pager/examples/open-source/parker-brown-open-source.pdf) |
| [scientific-method](./scientific-method/SKILL.md) | scientific method, put this to the test, fact-check this episode, stress-test this theory, competing hypotheses, is this a coincidence, what else could explain this | Test a claim, a theory or a whole argument: a verbatim claims ledger, competing hypotheses written before the evidence, traps that would embarrass the grading, the record gathered apart from the argument, two blind grading passes, a hypothesis matrix that counts only evidence able to tell the accounts apart, coincidences checked against chance, and checks on the grader itself |
| [storytelling](./storytelling/SKILL.md) | storytelling, tell this as a story, make this land, write the narration, caption this clip | Run HOOK/SHAPE/FLESH/JUDGE/LAND as a coaching loop over anything that has to land on an audience; includes narration mode for word-by-word video captions |
| [td-skin](./td-skin/SKILL.md) | td-skin, custom TD skin | Author a personal Terminal Delight skin against the installed binary's exported surface inventory, preview native controls, and preserve a way back |
| [udev-rule-deploy](./udev-rule-deploy/SKILL.md) | udev, udev-rule, deploy rules, udevadm, cloud udev | Deploy a udev rules file to a Linux host and reload the device subsystem without rebooting |
| [ai-slop](./ai-slop/SKILL.md) | ai-slop, this is slop, adds nothing, nobody talks like that, a quoted line plus a complaint | Record a sentence the operator flagged as AI-sounding into a personal slop ledger, in their words, with a regex where an honest one exists |
| [viral-circular-lymric](./viral-circular-lymric/SKILL.md) | make it lymric, circular lyric, make it loop like a poem | Write a looping short's narration as rhymed verse whose last card feeds its first, closing on grammar, rhyme and meaning at once |

## The writing craft is published from a private repository

`ai-slop`, `article`, `storytelling` and `viral-circular-lymric` are edited in
the private `writers-block` repository and mirrored here by its
`tools/publish-skills.sh`, one pull request per publish. Edit them there: a
change made in this repository is overwritten by the next publish.

## Property profiles stay out of this repo

The `article` skill splits deliberately. The craft is here — the register
contracts, the page anatomy, the tab and copy mechanism, the pre-publish gate,
and an **unfilled** profile template. The filled-in profile for a given site
lives as `ARTICLE-PROFILE.md` in that site's own repo, next to the code that
renders its articles.

That split is not tidiness. A filled profile carries a voice, a brand and a
commercial intent, and for client work it carries whose they are — none of which
belongs in a public repository. Keeping the profile beside the renderer also
stops the two drifting, which a copy in here would guarantee.

## Vendored craft

`storytelling/upstream/` carries [Storyteller](https://github.com/ringofai/storyteller)
by Ringo Fai under CC BY 4.0. Provenance, the changes made, and the security
review are in [storytelling/NOTICE.md](./storytelling/NOTICE.md). The BFS layer
on top adds narration for video, coaching content, and
[the loop short](./storytelling/reference/loop-short.md) — the short-form
structure whose ending feeds its beginning, which is the default form for
anything we publish.

**Audit any third-party skill before vendoring it.** A markdown skill ships no
code, so the supply-chain questions — postinstall hooks, binaries, dependency
trees — come back clean and mean very little. The real surface is that an agent
*reads* the prose and does what it says. `tools/skill-audit.py` checks for
instruction override, exfiltration, credential requests, filesystem writes and
hidden characters:

```bash
python3 tools/skill-audit.py path/to/candidate-skill
```

## Contributing

One skill per directory. Each directory must contain a SKILL.md with valid YAML frontmatter and a prompt body. New skills use portable `name` and `description` fields, with optional catalogue information under `metadata`; existing skills also carry legacy status, source, projects, triggers and tools fields.

Before opening a PR, run `python3 tools/check-frontmatter.py`. It reads every frontmatter as strict YAML, as the `skills` CLI does, and fails on a missing `name` or `description`.

Open a PR. Skills must be **agent-agnostic** — no hard-coded paths, no tool-specific API calls in the core body.
