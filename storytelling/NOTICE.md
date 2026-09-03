# Provenance and licence — storytelling

## What is vendored

`upstream/` is a copy of **Storyteller** by **Ringo Fai**, licensed
**CC BY 4.0**.

| | |
|---|---|
| Source | https://github.com/ringofai/storyteller |
| Commit | `135ca3441fdefad6607a0744413a88d06b73e625` |
| Commit date | 2026-07-04 |
| Vendored | 2026-09-02 |
| Licence | CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/legalcode |

CC BY 4.0 permits redistribution and adaptation, including commercially, and
requires attribution, a link to the licence, and an indication of changes. All
three are on this page, and `upstream/LICENSE` is kept verbatim.

## Changes made

1. **The two PNGs were not vendored** — `assets/storyteller-banner-bg.png` and
   `assets/storyteller-framework.png`, about 2 MB of banner and diagram that no
   agent reads. They remain at the source above.
2. **Nothing under `upstream/` was edited.** Every file there is byte-identical
   to the commit named.
3. **`SKILL.md` at this level is original BFS work**, not a derivative of the
   upstream SKILL.md: it is a map into `upstream/`, the house-style layer, and
   two modes that do not exist upstream (narration over video, coaching
   content). The upstream skill is a coaching loop for a person writing a story;
   ours adds the on-screen-caption and athlete-facing applications.
4. **Renamed to `storytelling`** rather than `storyteller`, so nothing implies
   this package is the upstream one or that its author endorses it.

## Why it was not installed the documented way

The README installs with `npx skills add ringofai/storyteller`. That runs an
arbitrary npm package with network access in order to place markdown files on
disk. There is nothing here but prose, so the package was cloned and the files
copied — same result, no third-party code executed.

## Security review, 2026-09-02

The usual supply-chain questions answer themselves and mean little: **no
`package.json`, no scripts, no postinstall hooks, no CI workflows, no binaries,
nothing executable, 27 markdown files and 2 images.** The real surface for a
skill package is different — an agent *reads* these files and does what they
say — so the prose was scanned for the things that would make a prompt
dangerous:

| Check | Result |
|---|---|
| Instruction override (*"ignore previous"*, *"do not tell the user"*) | **0** |
| Filesystem writes outside its lane (`~/.ssh`, `/etc`, `.env`) | **0** |
| Hidden or zero-width characters | **0** |
| Credential or API-key requests | **0** — hits were the words "token efficiency" and "paste your script" |
| Network / exfiltration | **0** — hits were shields.io badges and the CC licence link |
| Shell execution | **2** — both the `npx skills add` install line, deliberately not run |
| Tool/permission escalation | **0** — hits were the word "bypass" in "bypassed the paralysis" |

The audit script is `tools/skill-audit.py` in this repository. **Re-run it on any
third-party skill before vendoring one**, and re-run it on this package if the
upstream commit is ever advanced.

## Re-checking upstream later

```bash
git clone --depth 1 https://github.com/ringofai/storyteller /tmp/storyteller-check
```
```bash
diff -r --exclude=assets --exclude=.git /tmp/storyteller-check ~/BROWN-FAMILY-SPORTS/Software/agent-skills/storytelling/upstream
```

A clean diff means the vendored copy is current. If it is not, audit before
advancing it, and update the commit hash above.
