# Batch Contract

The helper needs Python 3.9+ and no third-party packages. It performs no network
requests and writes no catalogs. Keep the manifest under version control and
review changes to it separately from the returned translations.

From the skill directory:

```bash
python3 scripts/check_batch.py examples/manifest.json examples/translations.json
python3 -m unittest discover -s tests -v
```

## Manifest

`source_locale` names the source; `locales` is the exact required set, including
the source. Each `entries` row declares:

- `key`: stable id; duplicate or empty ids are refused.
- `source`: a nonempty string or a nonempty nested object of strings, such as
  the plural forms the project actually stores.
- `context`: where the text appears and what it means.
- `protected_tokens`: an explicit list, even when empty. Record literal
  shortcuts, range endpoints and other invariants here. The checker does not
  guess whether “Tab” means a physical key or a translated UI noun.
- `source_by_locale`: optional locale-to-contract map. Each contract uses source
  text arranged in the exact shape required for that locale; its leaves must
  come from the frozen source, not introduce new source phrases. This permits
  Russian `one/few/many/other` and Japanese `other` without pretending they
  share English's form set. Declare the project's shape; do not invent CLDR
  rules. The source-locale contract cannot differ from `source`.
- `same_as_source`: optional locale-to-reason map for legitimate unchanged
  prose. Capitalization or a model's assertion alone is not a reason.

Other context metadata may describe the surface, reader and a soft width budget;
the checker does not certify them. If a contract or a protected token is wrong,
fix the independently reviewed manifest rather than weakening checks in the reply.

## Returned Batch

`entries` is a list of `{ "key": "…", "translations": { "locale": value } }`.
Every expected key and every required locale must appear exactly once. The
source-locale value must equal the frozen source. A translated tree must have
the same object keys as its locale's contract, and all leaves must be strings.

Named placeholders such as `{name}` are checked as multisets, so a lost or
duplicated placeholder fails. `{{` and `}}` are literal brace escapes. Each
declared protected token is counted at the corresponding leaf with word/chord
boundaries, so `Ctrl+Tab` cannot pass for `Ctrl+T`. This is not a parser for
arbitrary identifiers or rich text; use the project's grammar-specific checks.
Unchanged prose needs a reason; placeholder-only and protected-token-only
strings do not. Duplicate JSON object keys and non-finite numbers are refused.

Exit 0 means structural checks passed. Exit 1 names a refusal or unreadable
input. The helper also prints the numbers of entries, locales and leaf values.
It cannot prove that a declared key was absent from the original inventory.

## Limits and Installation

The helper deliberately rejects unsupported brace grammar. It does not parse
ICU select/plural expressions, printf substitutions, gettext catalogs, HTML,
Markdown link targets or application-specific rich-text tags. Use the host
framework's checker for those; a clean run here is not a substitute.

Write the accepted values through the project's existing catalog adapter. That
adapter must handle target-language escaping and imports, verify installed
values after formatting, and support a dry run or a reviewable patch. The helper
does not make arbitrary text replacement into a safe inserter.

Export CSV from the accepted data when useful. Keep actual newlines, quote
cells correctly, and compare the export back to its source. When opening
untrusted text in a spreadsheet, account for that application's formula handling.
Do not edit JSON and CSV as independent sources of truth.
