# Property profile — intake and template

Every property publishes differently. The profile carries the variable half of
the article system so the structure underneath can stay fixed.

**The profile lives at `ARTICLE-PROFILE.md` in the property's own repo**, beside
the code that renders the articles, so the two can't drift. It does not live in
this skill: a filled profile carries a client's voice, brand and commercial
intent, and this repository is public.

## Intake — nine questions

Ask these before writing anything for a new property. Don't infer the answers
from the existing site; a wrong guess about voice is expensive and reads as
carelessness.

1. **What does this property publish, and who reads it?** One sentence each.
2. **What is the reader's relationship to the author?** Peer, patient, client,
   prospect, student, fan. This sets the voice and most of the liability
   posture.
3. **Do readers arrive differing in what they already know, or in how much they
   want right now?** This decides the register axis, and it is the question
   people answer too fast. Differing knowledge → expertise axis. Differing
   appetite → treatment axis. See `registers.md`.
4. **Is the byline a named person or an editorial entity?** A named
   practitioner's byline carries their professional standing, which changes what
   may be published without review.
5. **What should a convinced reader do next — and what must an article never
   ask for?** Both halves. The ask is usually one step, not the last step: see
   the work, get the tool, join the list. The forbidden one is usually a booking
   or meeting link, because an article is top-of-funnel and a calendar is
   bottom. Name it explicitly, with the URL if one exists in the codebase — a
   guard that lives only in someone's head gets pasted over. If there is no ask
   at all, say so; a decorative button is worse than none.
6. **Does this content need a review or disclaimer gate?** Clinical, legal and
   financial content usually does. If yes: who signs off, what the banner says,
   and whether unreviewed drafts may publish behind a notice.
7. **What are the categories?** A closed set, five or six at most. An
   open-ended tag vocabulary stops meaning anything by the twentieth article.
8. **Sources posture.** Academic citations with a numbered list, plain
   contextual links, or none.
9. **Where do the design tokens and typefaces live?** Name the file. Also: how
   many themes ship, and do any of them invert?

## Template

Copy this to `ARTICLE-PROFILE.md` at the property repo root and fill it in.
Leave a field blank rather than guessing — a blank field is a question to ask,
a guessed one is a mistake to find later.

```markdown
# Article profile — <property name>

**Site:** <url>
**Index:** <url of the article index>
**Renders from:** <path or system that builds article pages>

## Audience

- **Publishes:** <what this property publishes>
- **Read by:** <who>
- **Reader's relationship to the author:** <peer | patient | client | prospect | student | fan>

## Registers

- **Axis:** <treatment (tl;dr / ELI5 / technical) | expertise (beginner / intermediate / advanced)>
- **Default register:** <the one a reader lands on>
- **Why this axis:** <one sentence — readers differ in knowledge, or in appetite>
- **Optional registers in practice:** <which ones actually get written, and when>

## Voice

- **Person:** <first | second | third>
- **Register of address:** <how formal, and any words the property does or doesn't use>
- **Byline:** <named person | editorial entity>
- **Never:** <words, claims or postures this property does not use>

## Liability gate

- **Required:** <yes | no>
- **Signed off by:** <name and credential, or n/a>
- **Banner text:** <exact wording, or n/a>
- **May unreviewed drafts publish?** <yes, behind a notice | no>

## Categories

<closed set, five or six>

## Call to action

- **Utility CTA (may sit in the meta row):** <a tool or dataset the article is about, or none>
- **Closing CTA, short register:** <a quiet line — label and destination>
- **Closing CTA, long register:** <a real invitation — label and destination>
- **Never in an article:** <the forbidden asks, with URLs if they exist in the codebase>

## Sources

- **Posture:** <numbered academic list | contextual links | none>
- **Conventions:** <how an entry is written>

## Design

- **Tokens:** <file path, and the token names for foreground, muted, background, accent, rule>
- **Typefaces:** <display, body, utility>
- **Themes:** <how many, which invert>
- **Register hues:** <one token per register>

## Notes

<anything a writer needs that doesn't fit above>
```

## Filling it for an existing property

Read the three or four best articles already on the site before writing the
profile, then confirm what you inferred rather than asserting it. Existing
articles are evidence of the voice, not proof of it — some of what's there is
drift, and the profile is the chance to say which is which.
