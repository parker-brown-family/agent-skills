---
name: localization
description: "Complete or repair a product's translations across its supported languages. Use for localization, i18n, untranslated UI, translation batches, new language packs, mixed-language screens, and localization audits. Classify readers, batch by surface, validate before insertion, inspect shared renderers, and verify the running interface."
license: MIT
---

# Localization

Make the product read naturally in its supported languages, with evidence that
the interface uses the translations. Reuse the project's catalogs, framework,
glossary and checks. Do not introduce a second localization runtime.

## Establish the Contract

Read the project's instructions and existing translation guide. Establish:

- Scope: application, website, documentation or another named surface.
- Source locale and the complete required locale list, including regional ids.
- Catalog format, plural rules, interpolation syntax and existing insertion tools.
- Glossary, physical key names, protected identifiers and width constraints.
- Current checkout ownership, integration target and publication authorization.

Use the request and repository to settle routine choices. Ask only for missing
facts that materially change the work. Do not silently broaden an app task to
an entire documentation site. Record unknowns rather than inventing defaults.

## Inventory by Reader and Render Path

Keep a reviewable manifest with stable keys, source text, context, reader,
surface, locale requirements, protected tokens and any width constraint.

| Reader | Treatment |
|---|---|
| Person reading product chrome | Translate labels, hints, statuses and product-owned errors. |
| Person's authored content or saved evidence | Preserve it unless translation was requested. |
| Program consuming an id, protocol, saved value or structured answer | Preserve the existing contract; localize a separate human caption. |

A CLI can have both human and machine readers. A log or an agent response can
also be quoted in a human panel. Classify the actual reader; do not decide by
file extension or assume every CLI string must remain English.

Trace the shared paths as well as literals: icon-to-word converters, status
formatters, catalog defaults, fallback branches, tooltips, generated documents,
configuration menus and help directions. Search APIs that carry text through
properties or builders, not just literal child nodes. Read mixed files line by
line. Capitalization does not establish a protected brand name.

## Prepare Insertion Before Bulk Translation

Reuse the existing importer. If the project lacks one, build a small adapter
for its current catalogs before generating a large batch. It must validate the
whole plan before writing, preserve escaping and plural structures, and compare
installed values with the accepted batch after formatting.

Prove refusal of a missing locale, lost or duplicated substitution, changed
keycap, missing plural form and unexplained source-language fallback. Exercise
escaping and duplicate insertion. For multiple files, stage a reviewable patch
or provide rollback; atomic replacement of each file alone is not an atomic
transaction over the whole set.

The supplied [batch checker](scripts/check_batch.py) is a read-only helper for
JSON contracts with named-brace placeholders. It compares a returned batch
against a separate frozen manifest. It supports explicit locale-specific form
shapes, but does not infer linguistic plural rules. For ICU, gettext, printf,
rich text or another grammar, use the project's own parser and validators.
See [the batch contract](reference/batches.md) before using the helper.

## Translate in Surface Batches

Keep the glossary and decisions in one conversation where practical. Supply a
group of related UI surfaces with context and request every required locale
together. Use a strong model for language judgment, and deterministic code for
keys, counts, placeholders and installation checks.

Size batches to the output budget. A prior run completed 116 source entries
across nine languages in one request; that is evidence of one working size,
not a universal limit. Start with a small representative batch, wire it and
inspect it before expanding. Split or resume by stable key if a reply truncates;
never accept a partial locale column or silently fill it with the source.

Use JSON or the project's structured catalog as the editable source; export
CSV or a table for review. Freeze the expected keys and source independently of
the model's reply so a plausible but incomplete response cannot validate itself.
If using a browser, verify navigation, attachment, model selection and artifact
retrieval before a long request. Creating a tab alone proves little. Use the
available supported tools and respect access boundaries.

Translate the idea in the product's register. Preserve uncertainty, negation,
counts and action direction. Do not translate physical key names as though
they were prose. A correct cognate may equal the source: Spanish “error” is an
example. Keep explicit, reasoned exceptions instead of a blanket rule that
every translated value must differ.

## Wire at the Reader

Separate stable values from captions. A state id such as `idle` may remain
unchanged while its human view selects a localized label. Reuse that caption
function in every renderer, including text-control skins and compact counters.

Interpolate the real translated menu names into help and notifications. Preserve
authored titles, filenames and external diagnostics at their existing boundary.
Then verify the installed catalogs against the accepted batch and run the
project's relevant formatting, static and runtime checks.

## Inspect the Running Product

Photograph a small wired surface early. Include a long-caption locale, a script
with different glyph/shaping behavior, text controls, configuration menus, an
actual state-bearing card and a narrow layout. German and Japanese were useful
in the originating run; choose Arabic, Hindi, regional formats or other cases
when the project's supported locales require them. Check every changed locale
when a surface is cheap to stage.

Use an isolated test display or preview window that does not interrupt the
operator. Check font fallback, wrapping, clipping, omitted caption lines,
fallback English, keyboard legends, counts and right-to-left ordering where
applicable. Character-cell estimates are advisory for proportional or shaped
text; they do not establish pixel fit.

Record each observation by revision/build, surface, locale, control mode,
geometry, text scale, state and verdict. Keep unvisited slots and states
explicitly unverified. A capture of idle does not prove resting or asleep; use
their own observations or state a shared-render-path argument backed by tests.
Run the same surface again after a relevant renderer change.

## Finish and Prevent Regrowth

Report the exact scope, required locales, expected/installed key counts, checks,
native observations, exceptions and remaining unknowns. Catalog coverage,
render coverage and linguistic review are different claims. A passing checker
does not establish natural language quality or use on screen.

Improve the project's detector where the run found missed text-bearing calls.
Filter fixtures, ids and substitution keys, and test true examples and innocent
ones. Keep heuristic suggestions advisory when noisy; make deterministic
catalog integrity checks fail on actual contract violations. Avoid performing
an unrelated cleanup or imposing new publication rules.

Retain source manifests, accepted batches, review exports and scoped proof.
Follow the project's release workflow within the user's authorization. Record
the least-certain wording and unresolved fit checks. Never invent a percentage
speedup from the fact that one batch replaced several manual edits.

The [runbook](reference/runbook.md) supplies prompt and evidence templates;
the [case notes](reference/case-notes.md) explain the failures behind this method.
