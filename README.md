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
| [udev-rule-deploy](./udev-rule-deploy/SKILL.md) | udev, udev-rule, deploy rules, udevadm, cloud udev | Deploy a udev rules file to a Linux host and reload the device subsystem without rebooting |

## Contributing

One skill per directory. Each directory must contain a SKILL.md with valid YAML frontmatter (name, status, source, projects, triggers, tools) followed by the prompt body.

Open a PR. Skills must be **agent-agnostic** — no hard-coded paths, no tool-specific API calls in the core body.
