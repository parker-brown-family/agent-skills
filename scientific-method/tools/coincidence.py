#!/usr/bin/env python3
"""How often would chance line up this well? Given the comparable events in a window and a tolerance,
the share of the window that lies within the tolerance of at least one event is the chance that a moment
picked at random would look just as "timed".

    coincidence.py --window 12:00 12:49 --tolerance 60 12:04:10 12:12:51 12:23:04 --at 12:23:00

Times are HH:MM, HH:MM:SS, or plain seconds. --at reports how far an observed moment sits from the nearest
event, so the striking alignment and the base rate can be read side by side. List every comparable event
in the window, not only the ones that look meaningful: picking events after seeing the target is how a
coincidence gets manufactured.

The share is exact: the union of [event - tolerance, event + tolerance], clipped to the window, divided by
the window's length. A tolerance chosen after seeing the match flatters it; say what the claim itself
implied ("at the moment of", "within a minute").
"""
import argparse
import json
import sys


def seconds(text):
    if isinstance(text, (int, float)):
        return float(text)
    parts = str(text).split(":")
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) not in (2, 3):
        raise ValueError(f"cannot read time {text!r}")
    h, m, s = (parts + ["0"])[:3]
    return int(h) * 3600 + int(m) * 60 + float(s)


def share_within(start, end, events, tolerance):
    """Fraction of [start, end] lying within `tolerance` of any event, and the events inside the window."""
    if end <= start:
        raise ValueError("the window must end after it starts")
    spans = sorted((max(start, e - tolerance), min(end, e + tolerance)) for e in events)
    covered, cur_a, cur_b = 0.0, None, None
    for a, b in spans:
        if b <= a:
            continue
        if cur_b is None or a > cur_b:
            if cur_b is not None:
                covered += cur_b - cur_a
            cur_a, cur_b = a, b
        else:
            cur_b = max(cur_b, b)
    if cur_b is not None:
        covered += cur_b - cur_a
    inside = [e for e in events if start <= e <= end]
    return covered / (end - start), inside


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("events", nargs="+", help="every comparable event, as times")
    ap.add_argument("--window", nargs=2, required=True, metavar=("START", "END"))
    ap.add_argument("--tolerance", required=True, help="seconds either side, or a time like 0:01:00")
    ap.add_argument("--at", help="the observed moment the claim says was timed")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    start, end = seconds(a.window[0]), seconds(a.window[1])
    tol = seconds(a.tolerance)
    events = [seconds(e) for e in a.events]
    share, inside = share_within(start, end, events, tol)
    out = {"window_s": end - start, "tolerance_s": tol, "events_in_window": len(inside),
           "events_outside_window": len(events) - len(inside), "chance_share": round(share, 4)}
    if a.at:
        t = seconds(a.at)
        nearest = min(events, key=lambda e: abs(e - t))
        out["observed_offset_s"] = round(abs(nearest - t), 1)
        out["observed_within_tolerance"] = abs(nearest - t) <= tol
    if a.json:
        print(json.dumps(out))
        return
    print(f"{len(inside)} events in a {out['window_s'] / 60:g}-minute window, tolerance ±{tol:g} s: "
          f"a moment picked at random falls within tolerance of one {share:.0%} of the time")
    if out["events_outside_window"]:
        print(f"{out['events_outside_window']} listed events fall outside the window and only clip its edges")
    if a.at:
        print(f"the observed moment sits {out['observed_offset_s']:g} s from the nearest event"
              + (" (inside the tolerance)" if out["observed_within_tolerance"] else " (outside the tolerance)"))


if __name__ == "__main__":
    sys.exit(main())
