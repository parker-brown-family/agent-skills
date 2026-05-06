# udev-rule-deploy — Summary

**What**: Deploy a udev rules file to a Linux host and reload the device subsystem without rebooting.

**Why**: Hardware rules (keyboard backlights, RGB controllers, USB device permissions) take effect immediately when properly deployed — no reboot, no unplug.

**The drop**:
```bash
sudo cp 90-legion-rgb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**For agents**: Load SKILL.md. Verify NOPASSWD sudo before deploying. Sequence is strict: cp → reload → trigger.

**For cloud/CI**: Use cloud-init `runcmd` or Ansible `copy` + handler. The agent must not have an interactive TTY requirement — no password prompts.

**What can go wrong**:
- No NOPASSWD sudo → deploy hangs silently
- Running inside a container → udev not available
- Wrong SUBSYSTEM/ATTR in rules file → device unchanged after trigger

**Reference**: REFERENCE.md for sudoers setup, debugging commands, and container compatibility table.
