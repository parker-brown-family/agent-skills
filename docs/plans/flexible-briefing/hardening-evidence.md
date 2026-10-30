# Hardening Evidence

This note supports the [hardening review](hardening.html). It records what was run on 2026-10-30, against which code, and what came back. The before column is `main` at the round-trip merge (`abd152d`, "Preserve feedback through reader controls and literal markup"); the after column is the `harden/briefing-portable` branch.

## Probes

Each probe was a scratch file and one command, run against both versions of `briefing/scripts/brief.py`.

| Probe | Before | After |
|---|---|---|
| A Markdown brief linking `[t](missing-one.md "a title")`, `[f](file:///nonexistent/x.md)`, `![img](missing.png)` and `[ref][r]` / `[r]: missing-ref.md` | `check` exit 0, `"links": 1`: the titled, image and reference links were never extracted, and the `file://` link was skipped as external | each refuses in turn: `brief: broken local link: missing-one.md`, then `file:///nonexistent/x.md`, `missing.png`, `missing-ref.md` |
| `<!--BRIEF:notes-->` moved inside `<!--brief-content-->` | `html` exit 0; a map exported straight from the new page resolved with `revision_changed` (map `sha256:a2c4…`, page `sha256:5462…`) | `brief: keep <!--BRIEF:head--> and <!--BRIEF:notes--> outside the <!--brief-content--> region`, exit 1, no file written |
| Edit the built page by hand (`The Target` → `The Target (hand fix)`), rebuild from the source | rebuild exit 0; `grep -c 'hand fix'` on the page went from 1 to 0 | `check` reports `"edited_since_build": true`; `html` refuses with `out4.html was edited after its last build and src.html does not have those edits…`; the edit stays. `--discard-output-edits` rebuilds and names the `.bak` that holds it |
| Output path is an unrelated page | `brief: brief-meta: expected exactly one island` | `brief: other.html exists and was not built by this helper (…); choose another output path or move that file aside` |
| No Omarchy themes (the wallpaper script pointed at empty directories) | `brief: Command '['/usr/bin/python3', '…/brief-wall']' returned non-zero exit status 1.` | `brief: no wallpaper: brief-wall: no Omarchy themes with backgrounds found under …. Pass --no-wall to build on the stylesheet's own dark ground, outside the Omarchy house look.` |
| `briefing` copied alone, without its sibling skills | `brief: [Errno 2] No such file or directory: '…/decision-brief/assets/base.css'` | names all six missing files, says Markdown needs nothing else, and points at `doctor`. `doctor` reports `html_build` not ready and the wallpaper as `null`, unknown, because nothing could be looked at |

## The Gate Finding

A page built with `--no-wall` has no `<style id="brief-wall">` element, yet `fancy-pants check` printed `PASS … mean luminance 23/255`. The gate's regex started its match at byte 965, inside `base.css`'s own comment `…into a <style id="brief-wall"> block…`, and found `data:image` in another comment (`--wall: none; /* brief-wall: url("data:image/webp;base64,…") */`). Filed as [agent-skills#52](https://github.com/parker-brown-family/agent-skills/issues/52), "the glass gate passes a page with no wallpaper", with a reproduction and an invalidation check. Not fixed in this branch: the gate belongs to `fancy-pants-brief`.

## The Wallpaper

Building the [review page](hardening.html) twice showed a different palette the second time. The first build's `<style id="brief-wall">` element held 8,435 bytes, including 7,856 bytes of embedded image (theme kanagawa). After a rebuild with nothing changed, the element held 28,920 bytes, no image, and began ` block that goes straight after this * file.` — the tail of `base.css`.

The cause: `pick_wall` kept the old wallpaper with `re.search(r'<style id="brief-wall">.*?</style>', old)`. `base.css`'s opening comment contains that exact string, so the match started inside the stylesheet and ran to its closing tag. Every rebuild of every page did this. The glass gate searches the same way ([agent-skills#52](https://github.com/parker-brown-family/agent-skills/issues/52)), so it passed the stripped pages. `fancy-pants dress` has the same shape: on a page built with `--no-wall`, it changed 0 bytes and its check printed `PASS`. That is recorded in a [comment on the issue](https://github.com/parker-brown-family/agent-skills/issues/52#issuecomment-6532236198).

Two shipped pages had been stripped: `briefing/examples/engineering.html` and `review.html` in this folder. Both were rebuilt on this branch. Their content revisions are unchanged (`sha256:8dade01d6271…` and `sha256:a0482ab20a3c…`), so existing maps still resolve, and each now wears a wallpaper (`tokyo-night · 1-quattro.jpg`, `matte-black · 2-dot-hands.jpg`).

`wall_of` now finds the element with the same `HTMLParser` locator the notes islands use. It treats a wall without an embedded image as damage, so a damaged page gets a fresh wallpaper on its next rebuild. `check` and `html` report the wallpaper they found as `theme · file`, or `null`.

## The Cold Reader

A clean-context agent was given only the skill's directory and four tasks, with writes confined to a scratch directory. It completed all four:

- a Markdown brief: `check` exit 0
- an HTML brief with a figure: `check` exit 0, glass gate passed
- a hand-written Copy map, resolved by stdin: exit 0, then exit 2 with `revision_changed` after a reworded rebuild
- `doctor`, plus six deliberate refusals: each exit 1, with the file unchanged by `cmp`

What it reported, and what changed:

| Finding | Change |
|---|---|
| A rebuild drops the wallpaper; `check` and the gate miss it | Fixed, above; `check` now reports `wallpaper` |
| Copy map text with CRLF, a BOM or a chat quote is refused | Accepted; test `test_copy_map_survives_crlf_a_bom_and_a_chat_quote` |
| Built pages are mode 0600 (`mkstemp`) | `atomic` keeps the old mode or applies the umask; test `test_a_built_page_is_readable_like_any_file` |
| The Copy map has one example and no grammar | A line-by-line grammar in [feedback](../../../briefing/reference/feedback.md) |
| `output belongs to a different brief` names no id; the unreadable-map refusal gives no next step | Both messages now carry the id or the next step |
| HTML and Markdown ids must differ, said only in one reference; `--id` retyped on every build | Said in SKILL.md; `new` writes the id into the source, so `html` needs no flags |
| html.md's `reference/glass.md` reads as this skill's file | The path is spelled `decision-brief/reference/glass.md` |
| No command checks controls and overflow on your own page | `node tests/browser.mjs your.html` is documented, and now checks clipped figure text too |
| `check` reports only the first broken link | Every broken link, in one message |
| `"anchors": 7` with three explicit anchors, unexplained | `comment_targets` reports the explicit ones |
| `html` output does not mention the `.bak` | `backup` in the result |
| A twelve-digit prefix stored in `document.revision` | Moved to `document.revision_prefix`; `revision` stays `null` |
| An id ending in `-` and twelve hex digits is split wrongly in hand-typed text | Not changed. Real Copy map text always ends with the page's own twelve digits, which the parser takes from the end; a misread hand-typed id lands as `document_mismatch`, which is review |

## Tests

From `briefing/`:

```bash
python3 -m unittest discover -s tests -v
node tests/browser.mjs
```

The Python suite went from 23 tests to 42, all passing. The nineteen new tests are in [test_brief.py](../../../briefing/tests/test_brief.py), under the comments `links the checker used to skip`, `build guards`, `scaffold`, `the HTML reader's Copy map, pasted back` and `found by a clean-context agent following only the docs`. The test wallpaper now carries an embedded image, as `brief-wall`'s does; the old fake had none, so no test could see the wallpaper go.

The browser test passed with two new results, `copyMapResolves` and `copyMapOrphanNeedsReview`. It copies the real page's Copy map text out of headless Chromium and pipes it through `resolve -`, expecting exit 0 and the comment `resolved`. After the commented section is removed and the page rebuilt, it pipes the new Copy map text and expects exit 2 with `["revision_unknown", "target_missing"]` and the reader's words intact. With `CHROMIUM=/nonexistent` it prints `SKIPPED: no Chromium or Chrome found…` and exits 77.

The paired examples still pass `check`, and the Markdown example's map still resolves with exit 0. The HTML example was rebuilt only to restore its wallpaper; its content revision is unchanged.

## Source Trace

Every change is in [brief.py](../../../briefing/scripts/brief.py): `markdown_links`, `local_target` and `check` for links; `build`, `pick_wall` and `kit_missing` for the build guards; `copy_map`, `load_map` and `resolve` for pasted maps; `scaffold`, `source_identity` and `doctor` for the new commands; `wall_of`, `wall_label` and `atomic` for the wallpaper and file mode. [browser.mjs](../../../briefing/tests/browser.mjs) gained `findChromium` and the two Copy map checks.

## Limits

The Copy map parser reads the text `decision-brief/assets/notes.js` writes in `buildMap`, plus the lines the handoff bridge appends. A change to either format needs a matching change in `copy_map` and its tests. Copy map text joins each note's lines with spaces, so `resolve` marks it `"text_exact": false`.

The hand-edit guard compares the page's content fingerprint with the one recorded at build. A future change to the fingerprint rules would make an untouched older page look edited; the refusal then fails loud rather than losing anything, and [refusals](../../../briefing/reference/refusals.md) says how to tell the cases apart.

Saving notes into the file inside Terminal Delight, and inline commenting in any Markdown reader, were not exercised.
