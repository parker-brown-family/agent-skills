---
name: boot-apes
status: starter
source: starter
projects: []
triggers: [boot apes, start apes, boot-apes]
tools: []
created: 2026-04-28T00:00:00.000Z
---

You are executing the standard APES session preamble. Complete these four steps in order before any substantive work begins. This prevents working blind.

## Step 1 — Ensure the APES MCP server is running

Check whether the APES MCP server process is alive. If not, start it with nohup in the background, redirecting output to `/tmp/apes-mcp.log`. Report one of:

- `APES: already running ✓`
- `APES: started ✓`

## Step 2 — Resolve the project name

Detect the project from the workspace root directory name (the last path segment visible in the system prompt or active workspace). Do NOT guess. If ambiguous, stop and ask the user.

## Step 3 — Load context

Call both tools in order:

1. `apes_orient(project="<project>")`
2. `apes_context(project="<project>", section="all")`

Do not proceed until both calls return successfully.

## Step 4 — Output a crisp summary (≤ 20 lines)

Cover these four items only — no padding, no elaboration:

- **Project**: name, stack, one-line description of key patterns
- **Active issues**: any bugs flagged in Known Issues
- **Top tasks**: the highest-priority items in backlog or todo
- **MCP status**: tools confirmed active, or note if a session restart is needed
