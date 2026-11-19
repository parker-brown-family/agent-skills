# Cross-checks for a translation no native speaker has read

These are options. None is required. Reach for them when a catalog carries
strings where a wrong reading costs something, and nobody who speaks the
language will read it before it ships. For menu labels and status words, the
checks in the main skill are enough.

## Sensitive strings are written plainly, and that comes first

Some strings tell a person what to do, warn them, or say what the program is
about to do: instructions, security warnings, anything that overwrites or
deletes, anything about money. Those are the sensitive ones.

The owner's rule, 2026-11-19: *"Anything that is sensitive to translate, like
instructions, like particulars on behavior, we want to use the simplest, driest,
most directive language possible for the translation."* And: *"the translation
verbatim is less important than making sure that the idea is very crystal
clear."* The source language may stay nuanced, because its owner can review it.

So a sensitive string is not translated from the source catalog. It is
translated from a plain statement of its idea, kept beside the catalogs:

```json
{
  "confirm.ignore.sub": "Git does not ignore this file. Git could commit the key.",
  "error.tracked": "Git tracks %1. If you save here, the key would be committed. First run git rm --cached on that file."
}
```

Write the plain idea this way:

- Short sentences. One instruction per sentence.
- Name the subject each time. A pronoun ("it", "there") is the first thing a
  translation gets wrong: German *sie* and French *elle* attach to the nearest
  noun.
- State the condition. "The key would be committed" came back from Japanese and
  Chinese as "the key is committed". "If you save here, the key would be
  committed" survived in every language.
- Say what a command applies to. "First run: git rm --cached" reads as a
  complete command; it is not.
- No idiom, no figure of speech, no product nickname that implies more than the
  product does. "Key store" became "vault" in three languages.
- Keep placeholders, file names, commands and key legends exactly as written.

A check that belongs in the project's tests: every sensitive key exists, and
its plain idea has the same placeholders as the source string.

## The options

Each looks at the catalog from a different side. They disagree with each other
in useful ways, and each has a blind spot.

| Option | What it is | What it catches | What it misses |
|---|---|---|---|
| The product's own catalogs | Read the host product's existing translations for the same words before writing any | The established word for clipboard, folder, delete; the register (German *du*, French *vous*); spelling habits | Anything the host never says |
| Machine back-translation | `scripts/crosscheck.py google`: Google puts each of your strings back into the source language | Meaning that changed and a non-reader can see: a lost "not", "could" turned into "will", a word with a second sense | Whether the line reads naturally. Single words come back as noise |
| A second model, translating blind | Give another model (ChatGPT) only the plain ideas and ask for its own translations | Terms and phrasings two models reach independently are good evidence. Differences show where yours is unusual | It can make the same mistake you made, so agreement is not proof |
| A reviewing agent from another provider | One agent (Codex), one pass, told to report only problems in a fixed shape | Gender and number agreement, ambiguity about which file is the source and which the destination, a count that will not fit one form, a word that misleads | It prefers longer, fuller sentences. Take the idea and keep the line short |
| Blind back-translation of the final strings | Give a third model the finished strings with no source and ask what a native reader would understand | Whether the idea survives when nobody is told what it should say. Use it on the few highest-stakes lines as an acceptance check | Tone; anything outside the handful you sent |
| A photograph of the running product | The project's isolated display, one long-caption language and one with different glyphs | Overflow, clipped hints, missing fonts, an English string left behind | Meaning |

### Machine back-translation

```bash
python3 scripts/crosscheck.py google i18n/en.json i18n/de.json --lang de --plain i18n/_sensitive.json -o review/google-de.json
```

Each row carries the source, the plain idea when the key is sensitive, your
translation, Google's reading of your translation (`google_back_of_ours`) and
Google's own translation (`google_forward`). Read the back-translation column
for the sensitive rows in full. For the rest, look only at rows whose
back-translation shares few words with the source.

It calls the addresses Google's web clients use, with no key. They are not a
documented API. One of the two refused every request from the machine this was
first run on, and the other answered; the script tries both and does not ask a
refusing one again. A row it could not fill is `null`. Send only text that is
already public.

### A second model, translating blind

Send the plain ideas, the audience, the register per language and the protected
tokens. Ask for one JSON object and nothing else. Do not show it your
translations. Then read the two side by side for the sensitive keys.

### A reviewing agent from another provider

One round, said out loud to the person paying for it. The work order that
produced usable findings asked for: problems only, a fixed JSON entry per
problem (language, key, current, problem in one sentence, proposed, severity),
a summary entry per language so that a language with no findings is still
reported as read, and no edits to the catalogs.

### X's Translate button

Tried on 2026-11-19 and it is not an option for product strings. The button
appears on a post, translates into the viewer's display language, and that
language is an account setting: `?lang=ja` on the address did not change it for
a signed-in account. There is no way to put unposted text through it. Never post
text in order to translate it. What X offers without posting is Grok's chat, and
that is the third model used for the blind back-translation above.

## An order that worked

1. Glossary from the host product, then the first draft.
2. Machine back-translation and the reviewing agent, on the first draft.
3. Fix. Where a finding is really about the source string, fix the source.
4. The second model's blind translations, read against the fixed sensitive strings.
5. Fix, then the blind back-translation on the highest-stakes few.
6. Photograph, and run the catalog checks.

## What the first run found

The Secrets plugin for Omarchy, 172 strings into German, Japanese, Simplified
Chinese, Spanish, Brazilian Portuguese and French, 37 of them sensitive:

- 195 of 1,032 translated strings changed after the checks.
- Google's back-translation and the reviewing agent both caught a Portuguese
  line where "keep the file out of that system" had become "delete the file",
  and both caught Japanese and Chinese warnings that had lost their "would".
- The second model, translating blind, made that same Japanese and Chinese
  mistake. That is why the plain idea now states the condition.
- The reviewing agent returned 118 findings. Six were one finding about the
  word "today" in six languages; the fault was the English string, and the fix
  went there.
- The blind back-translation read 29 of 30 final strings as intended and found
  one German line that had drifted from its five siblings.

## What none of this proves

That the text reads naturally to a native speaker. Every reader here was a
machine. Say so wherever the translations are published, and make corrections
easy to send.
