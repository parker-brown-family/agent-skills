"""Read every SKILL.md frontmatter the way a strict YAML parser does.

Claude Code's skill loader forgives frontmatter that strict YAML rejects, so a
skill can work on the author's machine and still be invisible to the `skills`
CLI, which is how skills.sh finds a skill at all. On 2026-10-31 five of the
eleven skills here were skipped that way: three unquoted descriptions holding
": ", and two with no description. This fails on either.

Needs PyYAML (`pip install pyyaml`). Exit 0 clean, 1 on a bad skill, 2 when
it cannot run.
"""
import os, sys

try:
    import yaml
except ImportError:
    print("check-frontmatter: needs PyYAML (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."

bad = []
skills = 0
for base, dirs, names in os.walk(ROOT):
    dirs[:] = sorted(d for d in dirs if d != ".git")
    if "SKILL.md" not in names:
        continue
    skills += 1
    path = os.path.join(base, "SKILL.md")
    lines = open(path, encoding="utf-8").read().split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        bad.append((path, "no frontmatter block"))
        continue
    end = lines.index("---", 1)
    try:
        fm = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f" at line {mark.line + 2}" if mark else ""
        bad.append((path, f"YAML error{where}: {getattr(e, 'problem', e)}"))
        continue
    if not isinstance(fm, dict):
        bad.append((path, "frontmatter is not a mapping"))
        continue
    for field in ("name", "description"):
        if not isinstance(fm.get(field), str) or not fm[field].strip():
            bad.append((path, f"missing {field}"))

for path, why in bad:
    print(f"{path}: {why}")
print(f"{skills} skills, {len(bad)} problems")
sys.exit(1 if bad else 0)
