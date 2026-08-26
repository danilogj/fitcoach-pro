"""The log is the client's history. These tests are what stop it being lost."""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import logstore as ls


class LogTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "log.jsonl"

    def tearDown(self):
        self.dir.cleanup()


class TestValidation(LogTestCase):
    def test_rejects_unknown_type(self):
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "mood", {"level": 3})

    def test_rejects_missing_required_field(self):
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "weight", {"source": "scale"})

    def test_rejects_unknown_field(self):
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "weight", {"kg": 80, "mood": "good"})

    def test_rejects_out_of_range(self):
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "weight", {"kg": 900})
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "sleep", {"hours": 30})
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "recovery", {"soreness": 9})

    def test_rejects_wrong_type(self):
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "weight", {"kg": "eighty"})
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "steps", {"count": True})

    def test_requires_at_least_one_field(self):
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "recovery", {})

    def test_nothing_is_written_when_validation_fails(self):
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "weight", {"kg": 900})
        self.assertFalse(self.path.exists())

    def test_validates_nested_sets(self):
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "session", {
                "session_id": "upper_a",
                "exercises": [{"name": "Bench", "sets": [{"load_kg": 60, "reps": 400}]}]})
        with self.assertRaises(ls.ValidationError):
            ls.append(self.path, "session", {"session_id": "x", "exercises": [{"sets": []}]})


class TestAppendOnly(LogTestCase):
    def test_appends_do_not_rewrite(self):
        ls.append(self.path, "weight", {"kg": 80.0}, ts="2026-01-01T08:00:00")
        ls.append(self.path, "weight", {"kg": 79.5}, ts="2026-01-02T08:00:00")
        self.assertEqual(len(self.path.read_text().strip().splitlines()), 2)

    def test_correction_wins_for_day_granular(self):
        ls.append(self.path, "weight", {"kg": 88.0}, ts="2026-01-01T08:00:00")
        ls.append(self.path, "weight", {"kg": 80.0}, ts="2026-01-01T20:00:00")  # fixed typo
        events = ls.read(self.path, "weight")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].data["kg"], 80.0)
        # both lines survive on disk — history is never destroyed
        self.assertEqual(len(self.path.read_text().strip().splitlines()), 2)

    def test_two_sessions_same_day_both_survive(self):
        ls.append(self.path, "session", {"session_id": "upper_a"}, ts="2026-01-01T07:00:00")
        ls.append(self.path, "session", {"session_id": "lower_a"}, ts="2026-01-01T19:00:00")
        self.assertEqual(len(ls.read(self.path, "session")), 2)

    def test_reimport_is_idempotent(self):
        for _ in range(3):
            ls.append(self.path, "steps", {"count": 8000}, ts="2026-01-01T23:00:00")
        self.assertEqual(len(ls.read(self.path, "steps")), 1)


class TestQueries(LogTestCase):
    def setUp(self):
        super().setUp()
        for day, kg in [("01", 80.0), ("02", 79.8), ("03", 79.6)]:
            ls.append(self.path, "weight", {"kg": kg}, ts="2026-01-%sT08:00:00" % day)
        ls.append(self.path, "meal", {"kcal": 700.0, "protein_g": 40.0}, ts="2026-01-01T12:00:00")
        ls.append(self.path, "meal", {"kcal": 900.0}, ts="2026-01-01T20:00:00")
        ls.append(self.path, "session", {"session_id": "upper_a", "exercises": [
            {"name": "Barbell bench press", "sets": [{"load_kg": 60, "reps": 8},
                                                     {"load_kg": 60, "reps": 8}]},
            {"name": "Pull-up", "sets": [{"reps": 6}]}]}, ts="2026-01-02T07:00:00")

    def test_missing_file_returns_empty(self):
        self.assertEqual(ls.read(Path(self.dir.name) / "nope.jsonl"), [])

    def test_filter_by_type_and_date(self):
        self.assertEqual(len(ls.read(self.path, "weight")), 3)
        self.assertEqual(len(ls.read(self.path, "weight", since=date(2026, 1, 2))), 2)
        self.assertEqual(len(ls.read(self.path, "weight", until=date(2026, 1, 1))), 1)

    def test_intake_sums_per_day(self):
        self.assertEqual(ls.intake_by_day(self.path)[date(2026, 1, 1)], 1600.0)

    def test_hard_sets_counts_all_sets(self):
        self.assertEqual(ls.hard_sets_by_day(self.path)[date(2026, 1, 2)], 3)

    def test_weights_returns_sorted_pairs(self):
        pairs = ls.weights(self.path)
        self.assertEqual([p[0].day for p in pairs], [1, 2, 3])

    def test_corrupt_line_is_reported_not_swallowed(self):
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write("{not json}\n")
        with self.assertRaises(ls.ValidationError):
            ls.read(self.path)


if __name__ == "__main__":
    unittest.main()
