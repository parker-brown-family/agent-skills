#!/usr/bin/env python3
"""Tests for ach_tally.py and coincidence.py. Run: python3 -m unittest discover -s scientific-method/tools"""
import json
import unittest
from pathlib import Path

from ach_tally import distribution, tally
from coincidence import seconds, share_within

EXAMPLE = Path(__file__).parent / "examples" / "marston-fair.matrix.json"


def row(id, levels, standing="established", **kw):
    return {"id": id, "statement": kw.pop("statement", id), "standing": standing, "levels": levels, **kw}


class AchTally(unittest.TestCase):
    hyps = {"h1": "a", "h2": "b"}

    def test_a_row_every_hypothesis_sits_with_is_left_out(self):
        out = tally({"hypotheses": self.hyps, "rows": [row("same", {"h1": 1, "h2": 1}), row("apart", {"h1": 0, "h2": 3})]})
        self.assertEqual(out["counts"]["diagnostic"], 1)
        self.assertEqual(out["all_rows"]["columns"]["h2"]["contradiction"], 1.0)
        self.assertEqual(out["all_rows"]["columns"]["h1"]["rows"], 1)

    def test_an_unknown_cell_leaves_the_row_unmeasured_rather_than_filled_in(self):
        out = tally({"hypotheses": self.hyps, "rows": [row("gap", {"h1": 0, "h2": None})]})
        self.assertIsNone(out["rows"][0]["spread"])
        self.assertEqual(out["counts"]["unknown"], 1)
        self.assertEqual(out["all_rows"]["columns"]["h1"]["rows"], 0)

    def test_record_only_drops_claims_and_relayed_claims(self):
        rows = [row("rec", {"h1": 0, "h2": 3}),
                row("claim", {"h1": 3, "h2": 0}, standing="claimed"),
                row("relay", {"h1": 3, "h2": 0}, standing="reported", statement="The guest has said the case was planted")]
        out = tally({"hypotheses": self.hyps, "rows": rows}, relays=r"\bhas said\b")
        self.assertEqual(out["record_only"]["columns"]["h1"]["rows"], 1)
        self.assertEqual(out["record_only"]["least_to_most_contradicted"], ["h1", "h2"])
        # on every row, the claimed and relayed rows weigh against h1: 0.3 + 0.8 = 1.1 against h2's 1.0
        self.assertEqual(out["all_rows"]["least_to_most_contradicted"], ["h2", "h1"])

    def test_standing_weights_the_tally(self):
        out = tally({"hypotheses": self.hyps, "rows": [row("d", {"h1": 0, "h2": 3}, standing="disputed")]})
        self.assertEqual(out["all_rows"]["columns"]["h2"]["contradiction"], 0.5)

    def test_an_unrecognised_standing_is_reported_and_given_no_weight(self):
        out = tally({"hypotheses": self.hyps, "rows": [row("x", {"h1": 0, "h2": 3}, standing="rumoured")]})
        self.assertEqual(out["counts"]["standing_not_recognised"], ["x"])
        self.assertEqual(out["all_rows"]["columns"]["h2"]["rows"], 0)

    def test_a_row_no_hypothesis_sits_with_is_flagged(self):
        out = tally({"hypotheses": self.hyps, "rows": [row("odd", {"h1": 2, "h2": 3})]})
        self.assertTrue(out["rows"][0]["flags"])

    def test_an_answer_split_between_predicted_and_strained_is_flagged_as_a_bundle(self):
        split = {"0": 0.5, "1": 0.1, "2": 0.4, "3": 0.0}
        out = tally({"hypotheses": self.hyps, "rows": [row("b", {"h1": split, "h2": 1})]})
        self.assertIn("bundle", out["rows"][0]["flags"][0])

    def test_a_graded_distribution_is_read_as_its_expected_level(self):
        d = distribution({"0": 0.5, "1": 0.0, "2": 0.0, "3": 0.5})
        self.assertAlmostEqual(sum(lv * p for lv, p in d.items()), 1.5)
        self.assertIsNone(distribution(None))
        with self.assertRaises(ValueError):
            distribution(4)

    def test_the_fictional_example(self):
        out = tally(json.loads(EXAMPLE.read_text()))
        self.assertEqual(out["counts"]["unknown"], 1)                 # E09: one cell nobody scored
        self.assertFalse(next(r for r in out["rows"] if r["id"] == "E05")["diagnostic"])   # the drone photo
        # on every row, the relayed "planted" claim strains the charged account and the cover-up account leads;
        # on record-only rows the two single-shooter accounts tie, and the second shooter is the most contradicted
        self.assertEqual(out["all_rows"]["least_to_most_contradicted"][0], "h2")
        self.assertEqual(out["record_only"]["tied_for_least"], ["h1", "h2"])
        self.assertEqual(out["record_only"]["least_to_most_contradicted"][-1], "h3")

    def test_a_tie_is_reported_rather_than_broken_by_list_order(self):
        out = tally({"hypotheses": self.hyps, "rows": [row("r", {"h1": 0, "h2": 0}), row("s", {"h1": 0, "h2": 1})]})
        self.assertEqual(out["all_rows"]["tied_for_least"], ["h1", "h2"])


class Coincidence(unittest.TestCase):
    def test_one_event_in_the_middle(self):
        self.assertAlmostEqual(share_within(0, 100, [50], 5)[0], 0.10)

    def test_an_event_at_the_edge_is_clipped_to_the_window(self):
        self.assertAlmostEqual(share_within(0, 100, [0], 5)[0], 0.05)

    def test_overlapping_tolerances_are_counted_once(self):
        self.assertAlmostEqual(share_within(0, 100, [50, 52], 5)[0], 0.12)

    def test_an_event_outside_the_window_still_clips_its_edge(self):
        share, inside = share_within(0, 100, [103], 5)
        self.assertAlmostEqual(share, 0.02)
        self.assertEqual(inside, [])

    def test_six_steps_in_forty_nine_minutes_cover_a_quarter_of_it(self):
        steps = [seconds(t) for t in ("12:04", "12:12", "12:20", "12:28", "12:36", "12:44")]
        share, _ = share_within(seconds("12:00"), seconds("12:49"), steps, 60)
        self.assertAlmostEqual(share, 12 / 49)

    def test_times_read_in_three_forms(self):
        self.assertEqual(seconds("12:23:04"), 12 * 3600 + 23 * 60 + 4)
        self.assertEqual(seconds("0:01"), 60)
        self.assertEqual(seconds("90"), 90)


if __name__ == "__main__":
    unittest.main()
