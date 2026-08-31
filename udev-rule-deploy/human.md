# udev-rule-deploy — Human Guide

## What This Is

This skill teaches an LLM agent how to deploy a Linux udev rules file to any Linux host — bare metal or cloud VM — and reload udev so the rules take effect immediately.

The canonical use case: you have `90-legion-rgb.rules` (or any `.rules` file) and you want it live on a machine right now, without rebooting.

## How to Use the Skill

### Option A — Paste the raw URL into your agent's system prompt

```
https://raw.githubusercontent.com/parker-brown-family/agent-skills/main/udev-rule-deploy/SKILL.md
```

The agent will load the full skill on the next request.

### Option B — Copy the SKILL.md body into your agent framework

Works with Augment, Claude Code, Cursor, Codex, or any tool that accepts rule/skill injections.

## What the Agent Will Do

When triggered (keywords: `udev`, `deploy rules`, `udevadm`, `90-legion-rgb`, etc.):

1. Run pre-flight checks on the target host (udev running? sudo passwordless?)
2. Transfer the rules file if on a remote host
3. Run the three-command sequence: cp → reload-rules → trigger
4. Verify deployment (file present, no udevd errors in journal)
5. Report success or diagnose failure

## Setting Up the Target Host

For headless/cloud agents to work without password prompts, add this to the target:

```bash
sudo visudo -f /etc/sudoers.d/udev-deploy
```

Paste:
```
deploy ALL=(root) NOPASSWD: /bin/cp * /etc/udev/rules.d/*, /sbin/udevadm control --reload-rules, /sbin/udevadm trigger
```

Replace `deploy` with the username the agent uses to SSH in.

## Testing Locally

```bash
# 1. Dry-run: verify rule syntax (udev >= 252)
udevadm verify 90-legion-rgb.rules

# 2. Deploy
sudo cp 90-legion-rgb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

# 3. Confirm
ls -la /etc/udev/rules.d/90-legion-rgb.rules
journalctl -u systemd-udevd --since "2 minutes ago" | grep -i error
```

## Extending to Other Rules Files

The skill is rules-file-agnostic. The agent reads the rules filename from context or instruction. To deploy a different file, just pass the filename — the procedure is identical.

## Not Supported

- **Containers without privileged mode**: udev is not available inside standard Docker/LXC containers. The skill's pre-flight will detect this and abort.
- **Windows/macOS**: udev is Linux-only.
- **Old kernels (< 3.x)**: `udevadm trigger` behavior differs. Modern distros (Ubuntu 20.04+, RHEL 8+, Arch) are fully supported.

## Files in This Skill

| File | Audience | Purpose |
|---|---|---|
| SKILL.md | Agent | Injected into agent as skill/rule |
| README.md | Agent + Human | Navigation and quick reference |
| REFERENCE.md | Agent + Human | Deep udev internals and debugging |
| SUMMARY.md | Human | One-paragraph orientation |
| human.md | Human | This file — setup, testing, extension |
