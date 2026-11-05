# Case Notes

This method was extracted from Terminal Delight's native-app localization work,
including the [179-field completion](https://github.com/parker-brown-family/terminal-delight/pull/1350).
It is a worked case, not a benchmark or a claim of universal translation quality.

| Observation | Reusable lesson |
|---|---|
| The old insertion generator was not committed. | Keep a small checked adapter in the repository before bulk translation. |
| Four grouped source requests used one glossary conversation; the largest had 116 entries across nine locales. | Batch related surfaces with every locale together, bounded by the output budget. Do not turn that batch size into a universal limit. |
| Literal call sites were translated while a skin's icon-to-word converter still returned English. | Trace shared helpers and inspect word controls separately from glyph controls. |
| A Japanese painter tile contained the translated caption but drew only its shortcut. | Correct data does not prove correct rendering; check second lines and compact modes. |
| CONFIG was exempted as a product name until live review asked for it to be localized. | Establish naming exceptions from actual product intent, not uppercase spelling. |
| Artifact cards and a small counter called raw state labels, while the memory popup used localized ones. | Keep stable ids separate and reuse the localized caption at every human render site. |
| A stricter test rejected Spanish “error” because it equaled English. | Permit reasoned cognates; source inequality is not a language-quality test. |
| Soft width budgets exceeded character estimates, but many slots had not been opened. | Record native fit for each observed slot; keep the rest unverified. |
| A browser created a tab but could not attach for navigation. | Check the actual translation workflow before preparing a large browser request. Respect supported access boundaries. |

The originating product supported nine languages including English. This skill
uses the host project's locale list and grammar. Its program-facing values
retain whatever contract that project already defines. Neither its test count
nor its screenshots are evidence that another application has been localized.
