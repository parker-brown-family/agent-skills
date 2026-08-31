---
name: udev-rule-deploy
status: stable
source: parker-brown-family
projects: []
triggers: [udev, udev-rule, udev deploy, deploy rules, udevadm, 90-legion-rgb, linux hardware rules, cloud udev]
tools: [bash, ssh, read, write]
created: 2026-05-06T00:00:00.000Z
---

You are executing a full udev rule deployment. This workflow installs a udev rules file on a Linux host and hot-reloads the kernel device subsystem — no reboot required. Works on bare metal, cloud VMs, and headless CI runners.

## The Three-Command Drop

```bash
sudo cp <rules-file> /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Installs the file → reloads the kernel ruleset → replays device events so running processes see the change immediately.

## Pre-flight Checklist

Run these on the target host before deploying:

| Check | Command | Pass condition |
|---|---|---|
| udev is running | `systemctl is-active systemd-udevd` | `active` |
| passwordless sudo | `sudo -n true 2>&1` | exit 0 |
| rules dir exists | `ls /etc/udev/rules.d/` | directory present |
| not a container | `systemd-detect-virt -c` | non-zero or `none` |

**Containers** (Docker, LXC unprivileged): udev does not manage devices inside. Skip `udevadm trigger`; use privileged mode or external udev hooks instead.

## Step-by-Step Deployment

### 1 — Transfer (if remote)
```bash
scp 90-legion-rgb.rules deploy@<host>:/tmp/
```

### 2 — Install, reload, trigger
```bash
sudo cp /tmp/90-legion-rgb.rules /etc/udev/rules.d/
sudo chmod 644 /etc/udev/rules.d/90-legion-rgb.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 3 — Verify
```bash
ls -la /etc/udev/rules.d/90-legion-rgb.rules
journalctl -u systemd-udevd --since "1 minute ago" | grep -i error
```

## Headless / Cloud Agent Rules

When running without an interactive TTY:

1. **Probe NOPASSWD first** — if `sudo -n cp --version` fails, report the gap and stop. It will hang, not fail.
2. **Order is strict** — `cp` → `--reload-rules` → `trigger`. Do not parallelize.
3. **It is idempotent** — running the sequence twice is safe.
4. **Use `set -euo pipefail`** so any failure aborts the script.

```bash
set -euo pipefail
sudo cp "$RULES_FILE" /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "deployed."
```

## Cloud-Init

```yaml
runcmd:
  - cp /var/lib/cloud/instance/scripts/90-legion-rgb.rules /etc/udev/rules.d/
  - udevadm control --reload-rules
  - udevadm trigger
```

## Ansible

```yaml
- name: Deploy udev rules
  copy:
    src: 90-legion-rgb.rules
    dest: /etc/udev/rules.d/90-legion-rgb.rules
    mode: '0644'
  notify: reload udev

handlers:
  - name: reload udev
    command: "{{ item }}"
    loop:
      - udevadm control --reload-rules
      - udevadm trigger
```

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `sudo: a password is required` | No NOPASSWD grant | Add sudoers entry (see REFERENCE.md) |
| `systemd-udevd` not found | Container without udev | Use privileged container |
| Rule not applied | Syntax error | Run `udevadm verify <file>` |
| Device unchanged | Wrong SUBSYSTEM/ATTR match | See REFERENCE.md debugging section |
