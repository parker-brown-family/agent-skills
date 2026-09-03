"""Security first pass on a third-party SKILL package.

A markdown skill ships no code, so the usual questions (postinstall hooks,
binaries, dependency chains) come back clean and mean very little. The actual
surface is that an agent READS these files and does what they say. So this
looks for the things that would make a prompt dangerous: instructions to run
commands, reach the network, read credentials, write outside its lane, or
override the instructions it already has.
"""
import os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."

CHECKS = [
    ("instruction override", r"(?i)\b(ignore (all |any )?(previous|prior|above)|disregard (the )?(previous|prior|above|system)|override (your|the) (system|instructions)|do not tell the user|without (telling|informing) the user|regardless of (your|any) (instructions|guidelines))"),
    ("shell execution",      r"(?i)(^|\s)(bash|sh|zsh|curl|wget|npx|npm i|npm install|pip install|chmod|sudo|rm -rf|eval\(|os\.system|subprocess)\b"),
    ("network / exfil",      r"(?i)\b(https?://(?!(github\.com/ringofai|creativecommons\.org|raw\.githubusercontent\.com/ringofai))[^\s)\"']+|POST\s+to|send (it |them |the )?(to|via)|upload (it|the|your)|webhook|api\.[a-z0-9.-]+)"),
    ("credentials",          r"(?i)\b(api[_ -]?key|secret|token|password|credential|\.env\b|AWS_|ANTHROPIC_|OPENAI_)"),
    ("filesystem writes",    r"(?i)\b(write (to )?(the )?file|create a file at|~/\.|/etc/|/usr/|\.ssh|\.aws|overwrite)"),
    ("tool/permission ask",  r"(?i)\b(allowed-tools|allow(ed)?[- ]tools|permissions?:|tools:\s*\[|bypass|--dangerously|auto[- ]approve)"),
    ("hidden text",          r"[​-‏‪-‮⁠-⁤]"),
]

hits = {name: [] for name, _ in CHECKS}
files = 0
for base, dirs, names in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d != ".git"]
    for n in sorted(names):
        if not n.lower().endswith((".md", ".html", ".txt", "LICENSE")) and n != "LICENSE":
            continue
        p = os.path.join(base, n)
        files += 1
        try:
            body = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for i, line in enumerate(body.splitlines(), 1):
            for name, pat in CHECKS:
                if re.search(pat, line):
                    hits[name].append((os.path.relpath(p, ROOT), i, line.strip()[:150]))

print(f"scanned {files} text files under {ROOT}\n")
for name, _ in CHECKS:
    rows = hits[name]
    print(f"{name}: {len(rows)}")
    for f, i, line in rows[:6]:
        print(f"    {f}:{i}  {line}")
    if len(rows) > 6:
        print(f"    … {len(rows) - 6} more")
    print()
