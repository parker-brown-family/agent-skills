#!/usr/bin/env python3
"""Read-only validation of a translation batch against a frozen JSON manifest.

Python 3.9+, standard library only. Named-brace placeholders and explicitly
protected literal tokens; use the application's parser for other grammars.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys


PLACEHOLDER = re.compile(r"(?<!\{)\{([A-Za-z_][A-Za-z_0-9]*)\}(?!\})")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=object_pairs, parse_constant=reject_constant)


def leaves(value, where):
    """Flatten only nonempty string/object trees; retain exact form paths."""
    if isinstance(value, str):
        require(nonempty(value), f"{where}: empty text")
        return {(): value}
    require(isinstance(value, dict) and value, f"{where}: expected text or a nonempty form object")
    result = {}
    for key, child in value.items():
        require(nonempty(key), f"{where}: empty form key")
        for path, text in leaves(child, f"{where}/{key}").items():
            result[(key,) + path] = text
    return result


def placeholders(text, where):
    # Refuse unsupported brace grammar rather than silently ignoring ICU, a
    # misspelled placeholder or an unmatched brace. Escaped literal braces stay.
    rest = PLACEHOLDER.sub("", text).replace("{{", "").replace("}}", "")
    require("{" not in rest and "}" not in rest,
            f"{where}: unsupported brace syntax; use the project's parser")
    return Counter(PLACEHOLDER.findall(text))


def token_pattern(token):
    # A chord or range endpoint must not pass as a prefix of a different one:
    # Ctrl+T is not Ctrl+Tab or Ctrl+T+X, and 1 … 4 is not 1 … 44.
    # ASCII key/identifier continuations matter here. Korean particles may
    # directly follow a shortcut (Ctrl+T로), so Unicode \w would reject valid UI.
    left = r"(?<![A-Za-z0-9_+])" if token[0].isascii() and (token[0].isalnum() or token[0] == "_") else ""
    right = r"(?![A-Za-z0-9_+])" if token[-1].isascii() and (token[-1].isalnum() or token[-1] == "_") else ""
    return re.compile(left + re.escape(token) + right)


def keyed(document, where):
    require(isinstance(document, dict), f"{where}: expected object")
    entries = document.get("entries")
    require(isinstance(entries, list) and entries, f"{where}: nonempty entries list required")
    result = {}
    for entry in entries:
        require(isinstance(entry, dict), f"{where}: entry must be an object")
        key = entry.get("key")
        require(nonempty(key), f"{where}: nonempty key required")
        require(key not in result, f"{where}: duplicate entry key: {key}")
        result[key] = entry
    return result


def validate(manifest, batch):
    expected = keyed(manifest, "manifest")
    actual = keyed(batch, "batch")
    locales = manifest.get("locales")
    require(isinstance(locales, list) and locales and all(nonempty(x) for x in locales),
            "manifest: explicit nonempty locales list required")
    require(len(locales) == len(set(locales)), "manifest: duplicate locale")
    source_locale = manifest.get("source_locale")
    require(nonempty(source_locale) and source_locale in locales,
            "manifest: source_locale must be in locales")
    require(set(actual) == set(expected),
            f"batch keys differ: missing={sorted(set(expected) - set(actual))}, "
            f"extra={sorted(set(actual) - set(expected))}")
    values = 0
    for key, entry in expected.items():
        require(nonempty(entry.get("context")), f"{key}: context required")
        source = entry.get("source")
        source_leaves = leaves(source, f"{key}/source")
        protected = entry.get("protected_tokens")
        require(isinstance(protected, list) and all(nonempty(x) for x in protected),
                f"{key}: explicit protected_tokens list required (may be empty)")
        require(len(protected) == len(set(protected)), f"{key}: duplicate protected token")
        contracts = entry.get("source_by_locale", {})
        require(isinstance(contracts, dict) and set(contracts) <= set(locales),
                f"{key}: source_by_locale has an unknown locale")
        require(source_locale not in contracts or contracts[source_locale] == source,
                f"{key}: source-locale contract differs from source")
        reasons = entry.get("same_as_source", {})
        require(isinstance(reasons, dict) and set(reasons) <= set(locales) - {source_locale}
                and all(nonempty(x) for x in reasons.values()),
                f"{key}: unchanged-text exceptions need target locales and reasons")
        translations = actual[key].get("translations")
        require(isinstance(translations, dict) and set(translations) == set(locales),
                f"{key}: translations must include exactly the required locales")
        require(translations[source_locale] == source, f"{key}: source-locale value changed")
        contract_texts = list(source_leaves.values())
        for locale, contract in contracts.items():
            texts = list(leaves(contract, f"{key}/{locale} contract").values())
            require(all(text in source_leaves.values() for text in texts),
                    f"{key}/{locale}: contract must arrange the frozen source text")
            contract_texts.extend(texts)
        for token in protected:
            require(any(token_pattern(token).search(text) for text in contract_texts),
                    f"{key}: protected token absent from source contracts: {token}")
        for locale in locales:
            contract = leaves(contracts.get(locale, source), f"{key}/{locale} contract")
            target = leaves(translations[locale], f"{key}/{locale}")
            require(set(target) == set(contract), f"{key}/{locale}: form shape changed")
            for path, original in contract.items():
                where = "/".join((key, locale) + path)
                text = target[path]
                require(placeholders(text, where) == placeholders(original, where + " source"),
                        f"{where}: placeholders changed")
                for token in protected:
                    pattern = token_pattern(token)
                    require(len(pattern.findall(text)) == len(pattern.findall(original)),
                            f"{where}: protected token changed: {token}")
                prose = PLACEHOLDER.sub("", original)
                for token in protected:
                    prose = token_pattern(token).sub("", prose)
                if locale != source_locale and text == original and any(c.isalpha() for c in prose):
                    require(locale in reasons, f"{where}: unchanged prose needs a reason")
                values += 1
    return {"entries": len(expected), "locales": len(locales), "values": values}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("batch", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate(load(args.manifest), load(args.batch))
    except (ValueError, OSError, RecursionError) as error:
        print(f"check_batch: {error}", file=sys.stderr)
        return 1
    print(f"Validated {result['entries']} entries, {result['locales']} locales, "
          f"{result['values']} leaf values; no catalogs written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
