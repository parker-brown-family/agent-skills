"""Which global skills are COPIES of a file that lives somewhere else?

A copy is the drift this whole symlink pattern exists to prevent, and the only
way to know is to go looking: hash every global SKILL.md, then hash every
SKILL.md in the places skills are actually authored, and report the ones that
match by name so a human can see identical-vs-diverged at a glance.
"""
import hashlib, os, subprocess, time

GLOBAL = os.path.expanduser("~/.claude/skills")
SEARCH = [
    os.path.expanduser("~/BROWN-FAMILY-SPORTS/Software/agent-skills"),
    os.path.expanduser("~/BROWN-FAMILY-SPORTS/Software/Agent-Skills-for-Context-Engineering"),
    os.path.expanduser("~/BROWN-FAMILY-SPORTS/Software/agent-skills"),
    os.path.expanduser("~/Projects"),
    os.path.expanduser("~/Work"),
]

def h(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
    except Exception:
        return None

def when(p):
    try:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(p)))
    except Exception:
        return "?"

# every candidate SKILL.md outside the global dir, by skill name
elsewhere = {}
for root in SEARCH:
    if not os.path.isdir(root):
        continue
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "upstream", "target")]
        if base.count(os.sep) - root.count(os.sep) > 3:
            dirs[:] = []
            continue
        if "SKILL.md" in names:
            elsewhere.setdefault(os.path.basename(base), []).append(os.path.join(base, "SKILL.md"))

print(f"{'skill':26} {'global':14} {'state':11} other copy")
print("-" * 100)
linked = same = drift = alone = 0
for name in sorted(os.listdir(GLOBAL)):
    d = os.path.join(GLOBAL, name)
    g = os.path.join(d, "SKILL.md")
    if not os.path.exists(g):
        continue
    if os.path.islink(d):
        print(f"{name:26} {'symlink':14} {'LINKED':11} -> {os.path.realpath(d).replace(os.path.expanduser('~'), '~')}")
        linked += 1
        continue
    others = [p for p in elsewhere.get(name, []) if os.path.realpath(p) != os.path.realpath(g)]
    if not others:
        alone += 1
        continue
    for o in others:
        state = "identical" if h(g) == h(o) else "DIVERGED"
        if state == "DIVERGED":
            drift += 1
        else:
            same += 1
        print(f"{name:26} {when(g):14} {state:11} {o.replace(os.path.expanduser('~'), '~')}  ({when(o)})")

print("-" * 100)
print(f"{linked} already symlinked · {same} identical copies · {drift} DIVERGED · {alone} global-only")
