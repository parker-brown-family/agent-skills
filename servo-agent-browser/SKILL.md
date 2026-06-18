---
name: servo-agent-browser
status: starter
source: starter
projects: [servo-agent, servo]
triggers: [servo-agent, servo browser, agentic browsing, browser harness, web research, T1]
tools: [mcp, webdriver, bash, read]
created: 2026-06-17T00:00:00.000Z
updated: 2026-06-18T00:00:00.000Z
---

You are using **servo-agent** — an agent-controllable browser built on the Brown
Family Sports Servo fork. The harness now lives in its **own installable repo**,
`Software/servo-agent` (MCP server, CLI, tests, docs, examples); the `servo` fork
is the engine it drives. The goal is not merely to fetch pages: drive real
rendered pages, learn where the harness helps or hurts, and produce findings that
steer T3 in-tree extraction and the remaining external-tooling gaps. (T2 and T4
have shipped — see below.)

## Start Here

Confirm whether the `servo-agent` MCP tools are available in the current session:

- `open_url(url)` — navigate; returns title/url once the document commits
- `read_page(max_chars=12000)` — post-render DOM → clean markdown (the value-add)
- `find(selector)` / `wait_for_selector(selector)` — query / wait for elements
- `click(selector)` / `type_text(selector, text)` / `fill_form(...)` — interaction
- `scroll(...)` — to bottom/top, a selector, or a pixel offset
- `extract_links(...)` / `extract_table(selector)` — structured extraction → JSON
- `eval_js(script)` — run JavaScript, get JSON back
- `screenshot(path)` / `status()` — capture / introspect

If the tools are missing, explain that MCP tools are injected at session startup
and the client must be restarted after registering `servo-agent`. Validate the
whole stack end-to-end (spawns its own headless engine) with:

```bash
servo-agent selftest "https://news.ycombinator.com"
```

(From a source checkout: `uv run --project /path/to/servo-agent servo-agent selftest "…"`.)

## Operating Pattern

For live browsing or research, use Servo where rendered DOM matters: dynamic
content, link discovery, interaction, screenshots, or evaluating the harness.

1. Open the first URL with `open_url`.
2. Use `read_page` for the clean rendered-page digest.
3. Use `wait_for_selector` when content is JS-injected before reading/interacting.
4. Use `extract_table` / `extract_links` for structured data instead of hand-rolled `eval_js`.
5. Use `find` for targeted CSS checks before `click` / `type_text` / `fill_form`.
6. Use `eval_js` for structured facts no other tool captures; `screenshot` for visual proof.
7. Repeat across pages when the task is a T1 browsing evaluation.

Prefer built-in web/search tools for broad discovery; reach for Servo on pages
that need rendering, interaction, structured extraction, or dogfooding. For cheap
static reads, plain WebFetch is still cheaper than spinning the engine.

Worked patterns already ship as runnable code in the repo — consult them before
reinventing: `examples/` (research_read, universal_read, extract_table_demo,
scrape_fallback, site_qa, watch_page) and `integrations/` (verify_site,
schedule_watch, deep_research_provider).

## T1 Findings Log

When running a T1 agentic-browsing task, record findings in this shape:

```text
Site:
Task:
Tools used:
What worked:
Rough edge:
Severity: low | medium | high
Implication: T3 in-tree extraction | external tooling | docs/test only
Evidence:
```

Look specifically for:

- `read_page` mangling: missing headings, tables, nav context, article body, forms, images, comments, or code blocks.
- Remaining tool gaps: downloads, multi-tab, history navigation, cookies/session controls, persistent login profile (no auth-state persistence today — Playwright still wins for login-gated flows).
- Roundtrip pain: too many `find`/`eval_js` calls, repeated DOM extraction, slow navigation readiness, brittle selectors.
- Render gaps: screenshot mismatch, incomplete page load, dynamic content not committed, media/canvas limitations.
- Engine constraints: debug build, headless, single session — note when these block a task rather than working around them silently.

## Repo Rules

When working in `/home/pbrown/BROWN-FAMILY-SPORTS/Software/servo-agent` (the
harness) or `/home/pbrown/BROWN-FAMILY-SPORTS/Software/servo` (the engine):

- Boot APES before substantive work: `apes_orient(project="servo-agent")` for harness work (package, MCP, examples, T1/T2); use `apes_orient(project="servo")` only when changing the engine fork in-tree (T3).
- Harness changes go in the `servo-agent` repo (package, MCP server, examples); only touch the `servo` fork for deliberate T3 in-tree extraction work.
- Verify with `servo-agent selftest` (and `uv run pytest`) before claiming done.
- Record durable findings by layer: harness / tool-gap / T1 / T2 → APES project `servo-agent`; engine in-tree (T3) → APES project `servo`.
- Do not add AI attribution to commits or PRs.

## Output Expectations

For a browsing task, produce the synthesis the user asked for and append a short
harness findings section using the T1 shape above.

For a harness-improvement task, produce the smallest scoped change, show
self-test evidence, and classify each discovered limitation as T3 in-tree,
external tooling, or docs/test only.
