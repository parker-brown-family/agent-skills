---
name: code-taste
status: starter
source: starter
projects: []
triggers: [code-taste, audit, anti-patterns]
tools: [bash, read]
created: 2026-04-28T00:00:00.000Z
---

You are performing a code taste audit. Scan the target codebase for five structural anti-patterns, rank findings by risk, and create one tracking ticket per finding with a Given/When/Then scenario.

## The Five Anti-Patterns

| Pattern | What it looks like | Why it hurts |
|---|---|---|
| **Primitive Obsession** | `bool`, `null`, or `str` where a structured type is needed | The field can't hold all the states the domain requires |
| **Stringly Typed** | String compared with `==` where the valid set is closed | Typos produce silent wrong behavior |
| **Boolean Blindness** | Two `bool` flags that form an implicit enum | Invalid combinations exist; a third state requires a third bool |
| **Shotgun Surgery** | A constant literal in N files | One logical change requires N edits |
| **Underspecified Schema** | Valid values documented in a comment, not enforced in code | Nothing stops out-of-range values at write time |

## Scan Procedure

Determine the target source directory (from project context or user instruction), then run these grep passes. Adapt `--include` patterns to the target stack.

```bash
# Primitive Obsession — booleans in config/schema
grep -rn ": bool\|: false\|: true\|: null" --include="*.py" --include="*.yaml" . \
  | grep -v ".venv\|__pycache__\|test_"

# Stringly Typed — string literals used in equality checks
grep -rn '"[a-z_-]\+"\s*==' --include="*.py" . \
  | grep -v ".venv\|__pycache__"

# Boolean Blindness — paired bool CLI flags
grep -rn "is_flag=True" --include="*.py" . | grep -v ".venv\|test_"

# Shotgun Surgery — repeated string constants
# For each candidate literal: count occurrences across files
# grep -rn '"<literal>"' --include="*.py" . | wc -l

# Underspecified Schema — valid values described only in comments
grep -rn "#.*valid\|# one of\|# must be" --include="*.py" . | grep -v ".venv\|test_"
```

## Risk Ranking

| Risk | Criteria |
|---|---|
| 🔴 High | Field already drives downstream behavior; adding a state requires a migration |
| 🟡 Medium | Field is not yet read by logic, but schema is published |
| 🟢 Low/Watch | Field is stable; fixing it now is cheap insurance |

## Ticket Template

For each finding, create one tracking ticket with:

- **given**: the current shape of the code — factual, no editorializing
- **when**: the refactor action (what gets replaced with what)
- **then**: the structural guarantee after the change

Work findings in priority order: 🔴 first, then 🟡, then 🟢. Fix and verify tests pass before moving to the next tier.

## Reference: 10 Ground-Truth Examples

These are real tickets from a cleanup session on `imt-tool-campaign-manager`. Use them to calibrate what counts as a finding and how to phrase tickets.

| # | Pattern | Before | After |
|---|---|---|---|
| 1 | Primitive Obsession | `resolved: null` | `resolved: pending` enum |
| 2 | Primitive Obsession | `active: true` | `status: active\|paused\|archived\|complete` |
| 3 | Primitive Obsession | `synthesis_status: {pending,complete}` | 5-value enum |
| 4 | Primitive Obsession | `context_injected: bool + context_source: str` | `context_sources: [{type, snippet}]` |
| 5 | Primitive Obsession | `provenance_degraded: bool` | `provenance: {mode, affected_roles, reason}` |
| 6 | Shotgun Surgery | `"wildfire-2026"` in 5 CLI defaults | `DEFAULT_CAMPAIGN` constant |
| 7 | Stringly Typed | `InflectionType` fields unvalidated `str` | `Literal[]` + `__post_init__` validator |
| 8 | Boolean Blindness | `--force-refresh` + `--allow-degraded` flags | `ResearchMode` enum |
| 9 | Stringly Typed | `FreshnessVerdict.decision: str` | `Literal[7 values]` annotation |
| 10 | Shotgun Surgery | Role names literal in `doctor.py` | `CANONICAL_ROLES` frozenset |
