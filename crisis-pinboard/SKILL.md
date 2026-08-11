---
name: crisis-pinboard
description: Build and maintain a dated, evidence-linked HTML "pin board" of the social-media reality of a breaking local event (disaster, evacuation, major incident) by sweeping logged-in social platforms in a real browser — Facebook search, groups, member activity pages, Instagram hashtags — capturing every post's permalink, engagement, and caution flags, then organizing everything into collapsible, line-item sections (official orders, viral posts, roads/escape routes, human stories, assets, disputed claims). Includes a same-model UPDATE-ROUND protocol for refreshing the board on later days. Use when the user asks for a "pin board", "news board", "social sweep", "what's happening on Facebook/Instagram about X", or wants a durable curated artifact of a live event.
status: stable
source: parker-brown-family
projects: []
triggers: [crisis-pinboard, /crisis-pinboard, pin board, pinboard, news board, social sweep, event sweep, evac board, disaster board, "what's happening on facebook", "what's happening on instagram"]
tools: [browser, read, write]
created: 2026-08-11T00:00:00.000Z
updated: 2026-08-11T00:00:00.000Z
---

You are building a **pin board**: one self-contained, dated HTML file that captures the social-media
reality of a breaking local event — the official orders, the viral posts, the road closures, the
human stories, the assets, and the rumors (clearly flagged) — with every pin carrying its
**permalink, engagement counts, and timestamp** so a human can open the source in one click.

This is slow, careful curation work, not a quick scrape. **Go slow. Try hard.** A sweep is done
when new searches stop surfacing new material, not when you have "enough for a summary."

## Non-negotiables

1. **Date everything.** The artifact is named `<YYYY-MM-DD>-<topic-slug>-pinboard.html` (creation
   date + topic slug — never a bare date; concurrent agents collide on date-only names). The header
   states the capture date. Every update round appends a dated entry to an **Update log** block.
   Engagement numbers are always "as-seen at capture time."
2. **Evidence over vibes.** A pin without a permalink is a rumor with formatting. Capture the post
   URL, author, timestamp, and reactions/comments/shares for anything you cite. If you could not
   get a permalink, say so on the pin.
3. **Verification ladder.** Rank and label what you found: official agency statements → verified
   outlets quoting officials → firsthand accounts with checkable evidence (timestamps, photos,
   street names) → secondhand reports → allegations. The top of the board carries the confirmed
   facts; allegations live at the bottom with an explicit warning.
4. **Harm rules.**
   - An allegation naming a private individual is **never** republished as fact. Pin it (it is part
     of the event's reality), flag it "UNVERIFIED — do not republish", and quote the in-thread
     pushback if any exists.
   - Do not reproduce personal phone numbers, exact home addresses, or minors' names from posts —
     describe the offer/request and link the post instead.
   - Respect stated privacy: if a family has asked for privacy around a death, carry the official
     statement, not speculation about identity.
5. **Same-model update rounds.** Refreshes of an existing board are done by the same model that
   built it (continuity of judgment, tier thresholds, and tone). Never silently rewrite history:
   new pins are marked `NEW <date>`, changed engagement is shown as a delta (`5.9K → 7.1K`), and
   corrections say what changed.

## Method

### 1 — Frame the event (5 minutes, before any browsing)

Write down: place names (town, lake, roads, neighborhoods), official incident codes/names, the
responsible agencies (regional district, emergency-info accounts, police), and the event's
plausible hashtags. You will fan out queries from this frame, and it grows as you sweep (a hashtag
on one post often reveals a second incident name — add it to the frame and search it).

### 2 — Query fan-out (breadth first)

Sweep **multiple queries per platform**; each angle finds posts the others miss:

- Core event terms: `<place> evacuation`, `<fire/incident name>`, `<place> fire`
- The hard-news probe: `<place> fatality died` (finds official statements fastest)
- Roads and logistics: `<highway> closed`, `<backroad name>`, `<place A> <place B> road`,
  `detour`, `connector`
- Recovery/help: `lost our home <place>`, `evacuees`, `donation`, `gofundme`
- Hashtags on visual platforms: `#<incidentname>`, `#<place>fire` — and any second-incident tags
  you discover
- **Groups**: local mutual-aid groups are the richest single source ("<place> locals helping
  locals" pattern). Sweep them separately (see playbook below).
- **Hub users**: inside a group, one or two members act as information dispatchers (resource
  spreadsheets, donation-centre relays). When you spot one, open their group activity page and
  sweep it — it is a pre-curated feed.

### 3 — Capture protocol (per post)

For each post worth pinning, record: author (and page/group), timestamp, text gist (quote the
load-bearing lines verbatim), reactions / comments / shares, media type (photo set, reel, map,
screenshot), and the **permalink**. Then note anything that affects trust: is it firsthand? does it
carry evidence (a time-stamped photo, a named intersection)? is it disputed in its own comments?

**Permalink capture in a real browser:** clicking a post's timestamp navigates to or overlays the
canonical post URL — read it from the browser's address/tab state, then go back (Escape closes
most overlay viewers). If your automation harness batches actions, note that intermediate URLs may
not be reported inside a batch — click timestamps as **standalone** actions so the resulting URL
is visible, then batch the Escape/scroll cleanup.

### 4 — Tiers and sections

Organize pins into collapsible sections (order matters — confirmed hard news first):

1. **💔 Hard news / fatalities** — official statements verbatim, plus who else is reporting it.
2. **🔥 Viral posts** — threshold: **≥1,000 reactions or ≥100 comments**. These are the posts the
   user means when they say "the one with hundreds of comments."
3. **🛣 Roads, closures & escape routes** — closure endpoints with street-level precision, growth
   maps, alert-in-the-car accounts, "fires on both sides" escape stories.
4. **📢 Official orders & alerts** — every evacuation order/rescind with issuing body and time.
5. **📸 Platform assets** (per extra platform swept) — images/reels/stories worth reusing, with
   engagement and a note on what the asset shows.
6. **🏘 Group deep-dives** — one section per major group: the timeline disputes, supply runners,
   re-entry status threads, resource spreadsheets, animal-search coordination.
7. **💬 Human stories & ground truth** — losses, saves, gratitude, small-business limbo,
   fundraisers (include amount raised at capture).
8. **⚠️ Disputed / unverified** — allegations and contested timelines, flagged loudly.

A "lower-engagement context" roll-up pin at the end of a section keeps small finds without
bloating the board.

### 5 — The artifact (UX spec)

One self-contained HTML file, no external dependencies, dark-theme friendly:

- **Header**: title, one-paragraph provenance (which platforms, which queries, capture date,
  logged-in session note), and the instruction "click a section to collapse; click a row to
  expand."
- **Timeline block** (collapsible): the event reconstructed as dated bullets *as told by the
  pins*, including disputed entries labeled `DISPUTED`.
- **Sections**: `<details open>` with a `<summary>` carrying the section emoji+title and a pin
  count. Per-section accent color on the row borders.
- **Pins as line items**: each pin is itself a collapsed `<details>` whose one-line `<summary>`
  holds: source (bold) · hook (one clause, truncating) · engagement (compact: `5.9K · 340c ·
  1.1Ks`) · time. The expanded body holds the fuller quote/context and `Open post →` permalink
  links. This keeps ~40+ pins to a few screens.
- **Warning boxes** inline on any caution pin.
- **Update log** (after round 2 exists): dated entries at the top listing what each round added,
  refreshed, or corrected.
- **Footer**: provenance repeated, links to the official sources of truth (emergency portals,
  road authorities), and explicit notes on what remains unverified. If a circulating post was
  *excluded* as unrelated/outdated, say so in the footer — silent omission looks like a miss.

### 6 — Update rounds ("same model, put a date on it, go slow, try hard")

When asked to refresh a board (typically the next day):

1. Re-run the **core queries** plus a `<place> update` / `<incident> update` probe for the new
   day's developments (containment, re-entry, arrests, official confirmations of yesterday's
   rumors).
2. **Re-visit the headline pins** (top ~5 by engagement + anything flagged disputed) and record
   engagement deltas; show them as `old → new`.
3. Check whether yesterday's unverified items resolved (charges laid? timeline officially
   addressed? fundraiser target hit?). Move pins between sections when their status changes, and
   note the move in the Update log.
4. Append the dated **Update log** entry summarizing: N new pins, which stats refreshed, what got
   corrected/moved. Mark new pins `NEW <date>` in their hook line.
5. Keep the original filename (creation date = the board's identity); the Update log carries
   round dates. If the user wants a frozen snapshot, copy the file to a new dated name instead of
   overwriting semantics.

## Platform playbook (web-UI patterns and gotchas)

Learned the hard way; all of these assume a real logged-in browser session.

**Facebook search** (`/search/posts?q=…`): the workhorse. Results interleave pages, groups, and
people. Scroll in ~10-tick increments with 2s settles; posts render lazily.

**Facebook groups as a non-member**: the main Discussion feed often refuses to hydrate past the
first post (endless skeleton loaders) even for public groups. Do not fight it — use the group's
own search (`/groups/<id>/search/?q=<term>`), which renders fully, and member activity pages
(`/groups/<id>/user/<uid>/`) for hub users. Sort param `?sorting_setting=CHRONOLOGICAL` helps when
the feed does load. Do **not** join a group just to scrape it without asking the user first.

**Facebook DOM**: heavily virtualized — posts scrolled out of view unmount, so "scrape all posts
via JS" fails; `innerText` on containers returns junk ("Facebook Facebook Facebook…"). Work
visually (screenshot sweeps) and extract only targeted things via JS. Some harnesses block JS
results that contain query-string-like data — strip everything after `?` from URLs before
returning them.

**Facebook permalinks**: hover-hydrated timestamp links (`href="#"` until hover). Clicking the
timestamp opens the post (often as an overlay) and the canonical URL appears in tab state —
capture it there, then Escape back. Inside action batches the intermediate URL may be invisible;
click solo.

**Instagram hashtag pages** (`/explore/search/keyword/?q=%23tag`): the grid's `<a href="/p/…">`
anchors ARE extractable via JS once thumbnails load. Collect shortcodes, then bulk-fetch metadata
same-origin: `fetch('/p/<code>/')` and regex `og:description` from the HTML — it yields
`"<likes> likes, <comments> comments - <user> on <date>: \"<caption>\""` in one line. This turns
40 posts into structured data in two calls. Watch for output-size truncation: stash results on
`window`, read back in slices.

**Instagram stories**: ephemeral; hashtag story reels are no longer exposed. Pin the *profiles*
that have active fire-related story rings instead, and say that's what you did.

**Renderer stalls**: screenshot calls can time out while heavy feeds hydrate ("renderer frozen").
Wait 5s and retry once before assuming breakage. After navigation, a blank viewport usually means
you're past the rendered window — scroll up a few ticks.

**Multiple connected browsers**: if more than one browser is paired, ask the user which one holds
the right logged-in session before acting. Sessions differ per browser; a group that won't render
in one may render in the other.

## Quality bar (the sweep is done when…)

- Every section has its load-bearing pins and the top pins carry permalinks.
- You ran the fatality probe and either pinned the official statement or noted none exists.
- Roads/escape-routes section names actual road endpoints, not "roads are closed."
- At least one group was deep-dived if any local mutual-aid group exists.
- New queries are returning only posts you've already pinned (dry-well test).
- Anything you excluded as viral-but-unrelated is footnoted.
- The file opens clean, sections collapse, rows expand, links work.
