#!/usr/bin/env python3
"""Tally an Analysis of Competing Hypotheses matrix: which rows can tell the hypotheses apart, and how much
strain and contradiction each hypothesis carries across those rows.

Input is one JSON file:

    {"hypotheses": {"h1": "the ordinary account", "h2": "...", ...},
     "rows": [{"id": "E01", "statement": "...", "standing": "established",
               "relays_claim": false,
               "levels": {"h1": 0, "h2": 1, "h3": 2, "h4": 3}}]}

A cell is a level from 0 to 3, read as
    0 predicted     had the evidence been missing, that would count against the hypothesis
    1 comfortable   sits with it without any added assumption
    2 strained      needs an assumption it does not otherwise need (a coincidence, an error, a cover-up)
    3 contradicted
or a probability distribution over those levels, {"0": p0, "1": p1, "2": p2, "3": p3}, as a graded Score
returns it. A cell that is null or missing is unknown: its row cannot be measured and is skipped, never
filled with a level.

`standing` is how the evidence itself stands: established 1.0, reported 0.8, disputed 0.5, claimed 0.3.
`relays_claim` marks a row whose content is a party's own claim reported back ("X has said that ..."); the
record-only tally drops it. `--relays REGEX` marks rows by their statement instead.

The tally counts only diagnostic rows, whose spread (highest expected level minus lowest) is at least
--diagnostic (default 0.75). A row every hypothesis sits comfortably with is consistent with all of them,
however striking it sounds, and says nothing about which is true. The hypothesis that survives is the one
carrying the least contradiction, not the one with the most rows in its favour.

Usage: ach_tally.py matrix.json [--diagnostic 0.75] [--relays REGEX] [--json]
"""
import argparse
import json
import re
import sys

WEIGHT = {"established": 1.0, "reported": 0.8, "disputed": 0.5, "claimed": 0.3}
RECORD = ("established", "reported")


def distribution(cell):
    """A cell as {level: probability}; None when the cell is unknown."""
    if cell is None:
        return None
    if isinstance(cell, (int, float)):
        level = int(round(cell))
        if not 0 <= level <= 3:
            raise ValueError(f"level {cell} is outside 0..3")
        return {lv: (1.0 if lv == level else 0.0) for lv in range(4)}
    if isinstance(cell, dict):
        d = {int(k): float(v) for k, v in cell.items()}
        total = sum(d.values())
        if total <= 0:
            return None
        return {lv: d.get(lv, 0.0) / total for lv in range(4)}
    raise ValueError(f"cannot read cell {cell!r}")


def expected(d):
    return sum(lv * p for lv, p in d.items())


def tally(matrix, diagnostic=0.75, relays=None):
    hyps = list(matrix["hypotheses"])
    rows_out, unknown_standing = [], []
    for r in matrix["rows"]:
        cells = r.get("levels") or r.get("probs") or {}
        dists = {h: distribution(cells.get(h)) for h in hyps}
        known = all(d is not None for d in dists.values())
        exp = {h: (round(expected(d), 3) if d else None) for h, d in dists.items()}
        spread = round(max(exp.values()) - min(exp.values()), 3) if known else None
        standing = r.get("standing")
        if standing not in WEIGHT:
            unknown_standing.append(r.get("id"))
        relayed = bool(r.get("relays_claim")) or bool(relays and re.search(relays, r.get("statement", "")))
        flags = []
        if known and min(exp.values()) >= 2.0:
            flags.append("no hypothesis sits with this row: the set is missing one, or the row is wrong")
        split = [h for h, d in dists.items() if d and d[0] >= 0.3 and d[2] + d[3] >= 0.3]
        if split:
            flags.append(f"the answer for {', '.join(split)} splits between predicted and strained: the row may bundle two facts")
        rows_out.append({"id": r.get("id"), "statement": r.get("statement", ""), "standing": standing,
                         "relays_claim": relayed, "expected": exp, "spread": spread,
                         "diagnostic": spread is not None and spread >= diagnostic, "flags": flags, "_d": dists})

    def columns(record_only):
        t = {h: {"strain": 0.0, "contradiction": 0.0, "rows": 0} for h in hyps}
        for r in rows_out:
            if not r["diagnostic"] or r["standing"] not in WEIGHT:
                continue
            if record_only and (r["standing"] not in RECORD or r["relays_claim"]):
                continue
            w = WEIGHT[r["standing"]]
            for h in hyps:
                t[h]["strain"] += w * r["_d"][h][2]
                t[h]["contradiction"] += w * r["_d"][h][3]
                t[h]["rows"] += 1
        for h in hyps:
            t[h] = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in t[h].items()}
        # contradiction decides; strain breaks a tie; an exact tie on both is reported, never broken by list order
        key = lambda h: (t[h]["contradiction"], t[h]["strain"])
        order = sorted(hyps, key=key)
        return {"columns": t, "least_to_most_contradicted": order,
                "tied_for_least": [h for h in order if key(h) == key(order[0])]}

    all_rows, record_only = columns(False), columns(True)
    for r in rows_out:
        del r["_d"]
    return {"hypotheses": matrix["hypotheses"], "diagnostic_threshold": diagnostic,
            "rows": rows_out,
            "counts": {"rows": len(rows_out),
                       "unknown": sum(1 for r in rows_out if r["spread"] is None),
                       "diagnostic": sum(1 for r in rows_out if r["diagnostic"]),
                       "standing_not_recognised": unknown_standing},
            "all_rows": all_rows, "record_only": record_only}


def report(out):
    c = out["counts"]
    lines = [f"{c['rows']} rows: {c['diagnostic']} diagnostic (spread >= {out['diagnostic_threshold']}), "
             f"{c['rows'] - c['diagnostic'] - c['unknown']} consistent with every hypothesis, {c['unknown']} unknown"]
    if c["standing_not_recognised"]:
        lines.append(f"standing not recognised, left out of the tallies: {', '.join(map(str, c['standing_not_recognised']))}")
    for mode in ("all_rows", "record_only"):
        m = out[mode]
        cols = m["columns"]
        n = next(iter(cols.values()))["rows"] if cols else 0
        lines.append(f"\n{mode.replace('_', ' ')} ({n} rows)   strain / contradiction, weighted by standing")
        for h in m["least_to_most_contradicted"]:
            lines.append(f"  {h}  {cols[h]['strain']:5.2f} / {cols[h]['contradiction']:5.2f}   {out['hypotheses'][h]}")
        if len(m["tied_for_least"]) > 1:
            lines.append(f"  tied for least contradicted: {' = '.join(m['tied_for_least'])}")
    a, b = out["all_rows"]["least_to_most_contradicted"], out["record_only"]["least_to_most_contradicted"]
    lines.append("\nordering holds on record-only rows" if a == b else
                 f"\nordering changes on record-only rows: {' < '.join(a)} becomes {' < '.join(b)}")
    flagged = [r for r in out["rows"] if r["flags"]]
    for r in flagged:
        lines.append(f"flag {r['id']}: {'; '.join(r['flags'])}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("matrix")
    ap.add_argument("--diagnostic", type=float, default=0.75)
    ap.add_argument("--relays", help="regex: rows whose statement matches relay a party's own claim")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    with open(a.matrix, encoding="utf-8") as f:
        out = tally(json.load(f), a.diagnostic, a.relays)
    print(json.dumps(out, indent=1) if a.json else report(out))


if __name__ == "__main__":
    sys.exit(main())
