#!/usr/bin/env python3
"""A second opinion on a translated catalog, from a machine translator.

    crosscheck.py google SOURCE.json TARGET.json --lang de [--plain PLAIN.json] [-o OUT.json]

For every string in TARGET (a flat JSON catalog: key -> string, or key -> an
object of plural forms) this asks Google Translate two things:

  back     what our translation says, put back into the source language.
           A person who cannot read the target language reads this column.
           Meaning that changed on the way (a lost "not", "could" turned into
           "will", an instruction reversed) shows here.
  forward  how Google would translate the source itself. Where ours and
           Google's differ a lot, one of them chose an unusual word.

--plain names a catalog of the sensitive keys with the plain idea each must
carry (see reference/cross-checks.md). For those keys the forward translation
starts from the plain idea instead of the source string, and the row is marked
sensitive.

Neither column is a verdict. A back-translation that reads correctly does not
prove the target reads naturally, and Google is itself often clumsy. The
output is rows for a reader, or for a model, to judge.

It uses the addresses Google's own web clients call, with no key. Neither is
a documented API: either can change or refuse without notice, and one that
answers 429 is not asked again in that run.
A row it could not fill carries null, never an empty string, and the summary
counts them. Send only text that is public already; catalog strings go to
Google's servers. Standard library only.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# The two addresses Google's own web clients call. Neither is a documented
# API. The first takes several q= values and answers a list, one per string;
# the second takes one text and answers segments. Each has refused requests
# from one machine while the other answered, so both are tried.
ENDPOINTS = [
    ("https://clients5.google.com/translate_a/t", "dict-chrome-ex"),
    ("https://translate.googleapis.com/translate_a/single", "gtx"),
]
AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36"
BATCH = 16           # strings per request
BATCH_CHARS = 1500   # and no more than this many characters
REFUSED = set()      # addresses that answered 429 or 403; not asked again
# Google's language codes where they differ from a catalog's file name.
GOOGLE_CODE = {"zh-CN": "zh-CN", "zh-TW": "zh-TW", "pt-BR": "pt", "pt": "pt-PT", "es-MX": "es", "no": "no", "fil": "tl", "he": "iw"}


def flatten(catalog):
    """key -> string, with a plural object spread as key#one, key#other."""
    out = {}
    for key, value in catalog.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            for form, text in value.items():
                if isinstance(text, str):
                    out[f"{key}#{form}"] = text
        elif isinstance(value, str):
            out[key] = value
    return out


def fetch(url, params):
    request = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}", headers={"User-Agent": AGENT})
    with urllib.request.urlopen(request, timeout=20) as reply:
        return json.load(reply)


def ask(texts, source, target, pause):
    """Translate a list of single-line strings. A string nobody answered is None."""
    for url, client in ENDPOINTS:
        if url in REFUSED:
            continue
        base = [("client", client), ("sl", source), ("tl", target)]
        try:
            if client == "gtx":
                data = fetch(url, base + [("dt", "t"), ("q", "\n".join(texts))])
                lines = "".join(part[0] for part in data[0] if part and part[0]).split("\n")
            else:
                data = fetch(url, base + [("q", text) for text in texts])
                lines = [item[0] if isinstance(item, list) else item for item in data]
            time.sleep(pause)
            if len(lines) == len(texts) and all(isinstance(line, str) for line in lines):
                return [line.strip() for line in lines]
        except urllib.error.HTTPError as error:
            if error.code in (403, 429):
                REFUSED.add(url)       # refused: asking again only makes it worse
        except Exception:
            time.sleep(1.5)
    return [None] * len(texts)


def translate_all(texts, source, target, pause):
    out, batch, size = [], [], 0
    for text in texts:
        one_line = " ".join(text.split())
        if batch and (len(batch) >= BATCH or size + len(one_line) > BATCH_CHARS):
            out += ask(batch, source, target, pause)
            batch, size = [], 0
        batch.append(one_line)
        size += len(one_line)
    if batch:
        out += ask(batch, source, target, pause)
    return out


def tidy(text):
    """A translator can part a percent sign from its digit; put %1 back together."""
    if text is None:
        return None
    for n in "123456789":
        text = text.replace(f"% {n}", f"%{n}")
    return text


def google(args):
    source = flatten(json.load(open(args.source, encoding="utf-8")))
    target = flatten(json.load(open(args.target, encoding="utf-8")))
    plain = flatten(json.load(open(args.plain, encoding="utf-8"))) if args.plain else {}
    code = GOOGLE_CODE.get(args.lang, args.lang.split("-")[0])
    src = args.source_lang

    keys = [k for k in target if k.split("#")[0] in {s.split("#")[0] for s in source}]
    def source_of(key):
        base = key.split("#")[0]
        return source.get(key) or source.get(f"{base}#other") or source.get(base)
    def plain_of(key):
        return plain.get(key.split("#")[0])

    back = translate_all([target[k] for k in keys], code, src, args.pause)
    forward = translate_all([plain_of(k) or source_of(k) for k in keys], src, code, args.pause)
    rows = []
    for key, b, f in zip(keys, back, forward):
        rows.append({
            "key": key, "lang": args.lang, "sensitive": plain_of(key) is not None,
            "source": source_of(key), "plain": plain_of(key), "ours": target[key],
            "google_back_of_ours": tidy(b), "google_forward": tidy(f),
            "forward_from": "plain" if plain_of(key) else "source",
        })
    summary = {
        "lang": args.lang, "strings": len(rows),
        "back_unavailable": sum(r["google_back_of_ours"] is None for r in rows),
        "forward_unavailable": sum(r["google_forward"] is None for r in rows),
        "forward_identical_to_ours": sum(r["google_forward"] == r["ours"] for r in rows),
        # A language with one plural form has no key#one; that is not a gap.
        "missing_from_target": sorted({k.split("#")[0] for k in source} - {k.split("#")[0] for k in target}),
        "refused_by": sorted(REFUSED),
    }
    result = {"summary": summary, "rows": rows}
    text = json.dumps(result, ensure_ascii=False, indent=1) + "\n"
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text)
        print(json.dumps(summary, ensure_ascii=False))
    else:
        sys.stdout.write(text)
    return 1 if summary["back_unavailable"] or summary["forward_unavailable"] else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    g = sub.add_parser("google", help="back- and forward-translate a catalog with Google Translate")
    g.add_argument("source")
    g.add_argument("target")
    g.add_argument("--lang", required=True, help="the target catalog's language code, e.g. de, ja, zh-CN, pt-BR")
    g.add_argument("--source-lang", default="en")
    g.add_argument("--plain", help="catalog of sensitive keys -> the plain idea each must carry")
    g.add_argument("-o", "--out")
    g.add_argument("--pause", type=float, default=0.4, help="seconds between requests")
    g.set_defaults(run=google)
    args = parser.parse_args()
    sys.exit(args.run(args))


if __name__ == "__main__":
    main()
