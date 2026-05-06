# udev-rule-deploy

Deploy a udev rules file to a Linux host and hot-reload the device subsystem without rebooting.

## Canonical command sequence

```bash
sudo cp 90-legion-rgb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Files in this skill

| File | Purpose |
|---|---|
| SKILL.md | Agent prompt — paste into any LLM agent |
| README.md | This file |
| REFERENCE.md | Deep reference: udev internals, sudoers config, debugging |
| SUMMARY.md | One-pager for quick orientation |
| human.md | Human digest — how to set up, test, and extend |

## When to use this skill

- You have a `.rules` file that needs to be installed on a Linux machine
- You need the change to take effect immediately (no reboot)
- You are deploying from CI/CD, cloud-init, Ansible, or a headless agent
- The target is a bare-metal machine, cloud VM, or managed Linux host (not a container)

## Triggers

`udev`, `udev-rule`, `udev deploy`, `deploy rules`, `udevadm`, `90-legion-rgb`, `linux hardware rules`, `cloud udev`

## Raw skill URL

```
https://raw.githubusercontent.com/parker-brown-family/agent-skills/main/udev-rule-deploy/SKILL.md
```
