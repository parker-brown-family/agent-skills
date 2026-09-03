# Page anatomy

Top to bottom, with the scope of each part. The ordering is a real sequence —
the reader meets these in this order — so it's worth holding to.

| # | Part | Scope | Notes |
|---|---|---|---|
| 1 | back-link | shared | To the property's article index. |
| 2 | category chip | shared | One only, from the profile's vocabulary. Omitted entirely where the property has fewer than two categories in use — a chip that always reads the same is ceremony. |
| 3 | h1 title | shared | The article's name. Not any register's headline. |
| 4 | dek | shared | The question and the stake. **Never the finding.** |
| 5 | series nav | shared | Only when the piece is one part of several. |
| 6 | byline · date · share · utility CTA | shared | Byline form comes from the profile. A **utility** CTA may sit here — a calculator, a dataset, a tool the article is about. A **conversion** CTA may not; see below. |
| 7 | liability banner | shared | Only where the profile declares a gate. Full text, every register. |
| 8 | update banner | shared | Timestamped. Only when the piece has been overtaken by events. |
| 9 | register tabs | shared | Absent entirely when only the default register exists. |
| 9a | register kicker | **per register** | Names the register. |
| 9b | register headline | **per register** | Its own, written for its voice. |
| 9c | copy button | **per register** | Scoped to this register only. |
| 9d | lead callout | **per register** | Exactly one. |
| 9e | prose body | **per register** | |
| 9f | closing CTA | **per register** | The conversion ask, at the end of the register the reader actually finished. Pitched to that register's depth. |
| 10 | sources | shared | One list. Article-level. |
| 11 | back-to-top | shared | |
| 12 | footer note | shared | |

## Why the split falls where it does

**Shared means it belongs to the reporting.** The finding, the sources, the date,
the category, the liability posture — these are facts about the work, and a
per-register copy of a fact is a copy that will drift. Sources are the clearest
case: three lists means three lists that disagree within a month.

**Per register means it belongs to the telling.** The kicker, the headline, the
lead callout, the prose, and the copy button. Everything that changes when you
change who you're talking to.

The tab bar itself is shared, and it is the seam. Above it, one article. Below
it, several tellings.

## The dek, specifically

The dek and the default register sit inches apart on the rendered page. If both
carry the finding, the page repeats itself in the reader's first four seconds,
and that is the most common structural fault in a converted article.

- **Dek:** what was in question, and why it mattered. Ends without resolving.
- **Default register:** the resolution.

A dek that can be deleted without the reader losing the stakes was doing nothing.
A dek that makes the tl;dr redundant was doing too much.

## The CTA, and the funnel

Two different things get called a call to action, and they belong in different
places.

- **A utility CTA** is part of the article's value — the calculator the piece
  explains, the dataset it analyses, the tool it reviews. It may sit up in the
  meta row, because offering it costs the reader nothing and using it deepens
  the read.
- **A conversion CTA** asks the reader for something: their attention on your
  portfolio, their email, their business. It goes at the **end of the register
  they finished**, and never at the top. A conversion ask above the article is
  asking before delivering.

**Pitch it to the register's depth.** A reader leaving the tl;dr has spent
fifteen seconds; a reader who finished the technical register has spent twenty
minutes and is far warmer. The same ask under both wastes the warm reader and
crowds the cold one. Scale it: a quiet line after the short register, a real
invitation after the long one.

**Respect the property's funnel guard.** The profile names what an article may
*not* ask for. The usual case is a booking or meeting link: an article is
top-of-funnel, a calendar is bottom, and putting the calendar in the article
asks a stranger to commit before they have any reason to. Where a booking link
exists elsewhere in the codebase, it is one copy-paste from an article — so the
guard belongs in the profile as an explicit "never", not as a shared
understanding.

## Component vocabulary

Framework-agnostic names, kept close to the ones already in use on the BFS
properties so two implementations stay legible side by side:

```
article-frame          the whole piece
  article-head
    back-link
    article-tag        the category chip
    article-title      h1
    article-dek
    series-nav         .now marks the current part
    article-meta       byline, date, share row, utility CTA only
  article-inner
    liability-banner
    update-banner
    register-dossier   the tab group
      folder-tabs      role=tablist
      folder-body
        register-panel role=tabpanel  (one per register)
          register-kicker
          register-headline
          copy-button    receives THIS register's content; never queries upward
          callout        the lead callout
          article-prose
          register-cta   the conversion ask, pitched to this register's depth
    source-box         ol.source-list
    back-to-top
    article-footer-note
```

Inside `article-prose`, the components worth having ready because they recur:

- **stat strip** — a row of key numbers, each with label, value, and note; good
  / warning / bad variants for verdicts. Earns its place when the article turns
  on three or four figures.
- **comparison cards** — two or more side-by-side accounts, each with a source
  label, for when parties genuinely disagree. State every side as close to its
  own words as you can get; an investigation that quotes one side isn't one.
- **figure** — image or inline SVG plus a caption that says something the image
  doesn't. Inline SVG where the property has multiple themes, so the graphic
  inherits `currentColor` and re-skins with the page.
- **citation** — a superscript keyed to the shared sources list. Technical
  register only.

## Multipart articles

When a finding needs more than one publication — the question, the data, the
verdict — each part is a full article with its own registers, and the series nav
is shared across them. Two rules:

- **Each part stands alone.** A reader landing on part 2 from a search result
  gets the stakes without part 1.
- **The finding may change between parts, and the earlier part is not
  rewritten.** Add a timestamped update banner to it pointing forward. Silently
  editing a published part to match a later conclusion destroys the thing a
  multipart investigation is for.
