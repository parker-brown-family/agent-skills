# agent-skills

A collection of agent skills — each one a markdown file you paste into any LLM agent.

## What is a skill?

A skill is a SKILL.md file: YAML frontmatter (name, triggers, tools) followed by a plain-text prompt body. No code. No build step. You give the file to an agent and it knows what to do.

## How to use a skill

**Option A** — paste the raw URL into your system prompt or agent rules:

    https://raw.githubusercontent.com/parker-brown-family/agent-skills/main/code-taste/SKILL.md

**Option B** — copy the body into your agent framework skill/rule system (Augment, Claude Code, Cursor, Codex, etc.).

## Skills

| Skill | Triggers | Description |
|---|---|---|
| [code-taste](./code-taste/SKILL.md) | code-taste, audit, anti-patterns | Scan a codebase for five structural anti-patterns, rank by risk, open one ticket per finding |
| [decision-brief](./decision-brief/SKILL.md) | decision-brief, audit, review, intake assessment, findings report | Produce a single self-contained HTML brief the reader annotates in the browser; notes anchor to elements and export as a token-cheap map the agent reads back |
| [storytelling](./storytelling/SKILL.md) | storytelling, tell this as a story, make this land, write the narration, caption this clip | Run HOOK/SHAPE/FLESH/JUDGE/LAND as a coaching loop over anything that has to land on an audience; includes narration mode for word-by-word video captions |
| [udev-rule-deploy](./udev-rule-deploy/SKILL.md) | udev, udev-rule, deploy rules, udevadm, cloud udev | Deploy a udev rules file to a Linux host and reload the device subsystem without rebooting |

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

One skill per directory. Each directory must contain a SKILL.md with valid YAML frontmatter (name, status, source, projects, triggers, tools) followed by the prompt body.

Open a PR. Skills must be **agent-agnostic** — no hard-coded paths, no tool-specific API calls in the core body.
