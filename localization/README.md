# Localization

An agent-agnostic workflow for finishing translations and checking the screens
that use them. It covers reader classification, grouped translation requests,
safe catalog insertion, shared caption renderers and scoped visual evidence.

Read [SKILL.md](SKILL.md), or install the skill with your agent's skill manager:

```bash
npx skills add parker-brown-family/agent-skills --skill localization
```

That optional route needs Node.js 22.20+; see the
[skills CLI installation reference](https://github.com/vercel-labs/skills#install-a-skill).

For a manual installation, keep this whole directory and point the agent at
`SKILL.md`. Link it from the agent's discovery directory if supported; a managed
source avoids divergent copies. References, examples and scripts are relative
to this directory. The core workflow needs no other skill or service.

## Batch Checker

Python 3.9+, standard library only. From this directory:

```bash
python3 scripts/check_batch.py examples/manifest.json examples/translations.json
python3 -m unittest discover -s tests -v
```

The checker compares the returned batch against a frozen source manifest. It
refuses missing/extra keys or locales, duplicate JSON keys, changed source
values, missing form keys, lost/duplicated named substitutions or declared
shortcuts, and unjustified unchanged prose. It is read-only and does not insert
into arbitrary application source. See [the contract and limits](reference/batches.md).

Use the project's parser for ICU, gettext, printf and rich-text syntax. The
checker does not establish linguistic quality, pixel fit, actual catalog
installation or that the inventory found every UI string. Those need the rest
of the workflow.

## Contents

- [Core workflow](SKILL.md).
- [Batch contract](reference/batches.md) and executable examples.
- [Prompt, sample and evidence templates](reference/runbook.md).
- [Observed failures behind the method](reference/case-notes.md).
- [MIT license](LICENSE).
