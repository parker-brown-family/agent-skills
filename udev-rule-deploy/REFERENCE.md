# udev Rule Deploy — Reference

## How udev Works

udev is the Linux device manager. It runs as `systemd-udevd` and listens for kernel uevent messages. When a device event fires, udev matches it against rules in `/etc/udev/rules.d/` (and `/lib/udev/rules.d/`) in lexicographic order by filename. Higher numbers run later and can override earlier rules.

### The three commands explained

| Command | What it does |
|---|---|
| `sudo cp <file> /etc/udev/rules.d/` | Installs the rules file. udev re-reads rules on demand, not on copy. |
| `sudo udevadm control --reload-rules` | Signals `systemd-udevd` to re-parse all rules files. **Does not apply rules to existing devices.** |
| `sudo udevadm trigger` | Replays synthetic uevents for all current devices, causing re-evaluation of rules. Equivalent to re-plugging every device. |

All three are required. Skipping `trigger` means existing devices remain under old rules.

## Rules File Naming Convention

Files in `/etc/udev/rules.d/` must end in `.rules`. Numeric prefix controls load order:

- `00-09` — very early, rarely used
- `60-89` — hardware-specific rules (common range)
- `90-99` — late overrides and local customizations
- `99-` — highest priority, runs last

`90-legion-rgb.rules` is a local hardware override — correct placement.

## File Permissions

```
-rw-r--r-- 1 root root <size> /etc/udev/rules.d/90-legion-rgb.rules
```

Owner: `root:root`, mode `644`. udev reads rules as root; world-readable is fine.

## Sudoers Configuration (NOPASSWD)

For headless/cloud deployments, grant targeted NOPASSWD:

```
# /etc/sudoers.d/udev-deploy
deploy ALL=(root) NOPASSWD: /bin/cp * /etc/udev/rules.d/*, /bin/chmod * /etc/udev/rules.d/*, /sbin/udevadm control --reload-rules, /sbin/udevadm trigger
```

Validate with `visudo -c -f /etc/sudoers.d/udev-deploy` before deploying.

**Never grant blanket `NOPASSWD: ALL`** — scope to the exact commands needed.

## Debugging

### Test rule matching without applying

```bash
udevadm test $(udevadm info --query=path --name=/dev/<device>)
```

### Check rule syntax (udev >= 252)

```bash
udevadm verify /etc/udev/rules.d/90-legion-rgb.rules
```

### Watch live udev events

```bash
udevadm monitor --environment --udev
```

### Dump device attributes (for writing rules)

```bash
udevadm info --attribute-walk --name=/dev/<device>
```

### Check udevd journal for errors

```bash
journalctl -u systemd-udevd -f
```

## Cloud / Container Notes

| Environment | udev available | Notes |
|---|---|---|
| Bare metal | Yes | Full support |
| Cloud VM (KVM/Xen) | Yes | Full support; no physical devices |
| Docker (default) | No | udev runs on host, not in container |
| Docker (privileged) | Partial | Can trigger but shares host udev |
| LXC unprivileged | No | Host udev manages devices |
| LXC privileged | Yes | Full support |
| cloud-init user data | Yes | Runs as root, no sudo needed in runcmd |
| Ansible | Yes | `become: true` for privilege escalation |

## Legion RGB Context

`90-legion-rgb.rules` grants write access to the Lenovo Legion keyboard backlight sysfs interface to non-root users. Typical content:

```
SUBSYSTEM=="leds", KERNEL=="platform::kbd_backlight", TAG+="uaccess"
```

or for HID-based RGB:

```
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="17ef", ATTRS{idProduct}=="6099", TAG+="uaccess"
```

Adjust `idVendor`/`idProduct` for your Legion model. Find values with:

```bash
lsusb | grep -i lenovo
udevadm info --attribute-walk /dev/hidraw<N> | grep -E "idVendor|idProduct"
```
