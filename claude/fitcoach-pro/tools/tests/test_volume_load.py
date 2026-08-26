"""Volume accounting and load management."""
from __future__ import annotations

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import load as load_mod
import metrics as m
import volume as vol


class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.cat = vol.Catalog()

    def test_finds_by_id_and_name_and_substring(self):
        self.assertEqual(self.cat.find("bench_barbell")["id"], "bench_barbell")
        self.assertEqual(self.cat.find("Barbell bench press")["id"], "bench_barbell")
        self.assertEqual(self.cat.find("goblet")["id"], "squat_goblet")

    def test_unknown_exercise_refuses_with_guidance(self):
        with self.assertRaises(m.InsufficientData) as ctx:
            self.cat.find("kettlebell juggling")
        self.assertIn("not in the catalog", str(ctx.exception))

    def test_ambiguous_query_refuses(self):
        with self.assertRaises(m.InsufficientData) as ctx:
            self.cat.find("curl")
        self.assertIn("matches", str(ctx.exception))

    def test_filter_respects_available_equipment(self):
        found = self.cat.filter("horizontal_push", ["bodyweight"])
        self.assertTrue(found)
        for ex in found:
            self.assertTrue(set(ex["equipment"]).issubset({"bodyweight"}))
        # a barbell-only gym cannot do the machine press
        ids = {e["id"] for e in self.cat.filter("horizontal_push", ["barbell", "bench"])}
        self.assertIn("bench_barbell", ids)
        self.assertNotIn("chest_press_machine", ids)

    def test_every_pattern_has_a_bodyweight_option(self):
        for pattern in ["horizontal_push", "vertical_push", "vertical_pull",
                        "horizontal_pull", "knee_dominant", "hip_dominant"]:
            with self.subTest(pattern=pattern):
                self.assertTrue(self.cat.filter(pattern, ["bodyweight", "pullup_bar"]),
                                "no equipment-free option for %s" % pattern)

    def test_substitution_stays_in_pattern(self):
        subs = self.cat.substitute("squat_back", "low_back_pain")
        self.assertTrue(subs)
        for s in subs:
            self.assertFalse(s.get("axial"), "%s still loads the spine" % s["name"])

    def test_shoulder_substitution_avoids_flagged_exercise(self):
        subs = self.cat.substitute("bench_barbell", "shoulder_impingement")
        ids = {s["id"] for s in subs}
        self.assertNotIn("bench_barbell", ids)
        self.assertIn("bench_dumbbell", ids)

    def test_unknown_reason_refuses(self):
        with self.assertRaises(m.InsufficientData):
            self.cat.substitute("squat_back", "bad_vibes")


PROGRAM = [
    {"exercises": [{"name": "Barbell bench press", "sets": 4},
                   {"name": "Pull-up", "sets": 4},
                   {"name": "Dumbbell shoulder press", "sets": 3},
                   {"name": "One-arm supported dumbbell row", "sets": 3},
                   {"name": "Dumbbell lateral raise", "sets": 3},
                   {"name": "Face pull", "sets": 3}]},
    {"exercises": [{"name": "Barbell back squat", "sets": 4},
                   {"name": "Romanian deadlift", "sets": 3},
                   {"name": "Leg extension", "sets": 3},
                   {"name": "Lying leg curl", "sets": 3},
                   {"name": "Standing calf raise", "sets": 3},
                   {"name": "Plank", "sets": 3}]},
]


class TestWeeklyVolume(unittest.TestCase):
    def setUp(self):
        self.rows = {r.muscle: r for r in vol.weekly_volume(PROGRAM)}

    def test_direct_sets_are_summed_from_primary_muscles(self):
        self.assertEqual(self.rows["chest"].direct, 4)
        self.assertEqual(self.rows["back"].direct, 7)     # pull-up 4 + row 3
        self.assertEqual(self.rows["quads"].direct, 7)    # squat 4 + extension 3
        self.assertEqual(self.rows["side_delt"].direct, 3)

    def test_indirect_is_counted_at_half_and_kept_separate(self):
        # triceps: bench 4 + shoulder press 3 = 7 secondary sets -> 3.5
        self.assertEqual(self.rows["triceps"].indirect, 3.5)
        self.assertEqual(self.rows["triceps"].direct, 0)

    def test_below_mev_is_flagged(self):
        self.assertEqual(self.rows["chest"].verdict, "below_mev")
        self.assertIn("minimum effective", self.rows["chest"].note)

    def test_profile_scales_the_landmarks(self):
        # 6 chest sets: under the intermediate MEV of 8, at the beginner MEV of 5.6
        six = [{"exercises": [{"name": "Barbell bench press", "sets": 6}]}]
        inter = {r.muscle: r for r in vol.weekly_volume(six, profile="intermediate")}
        begin = {r.muscle: r for r in vol.weekly_volume(six, profile="beginner")}
        self.assertEqual(inter["chest"].verdict, "below_mev")
        self.assertNotEqual(begin["chest"].verdict, "below_mev")

    def test_above_mrv_is_flagged(self):
        heavy = [{"exercises": [{"name": "Barbell bench press", "sets": 30}]}]
        rows = {r.muscle: r for r in vol.weekly_volume(heavy)}
        self.assertEqual(rows["chest"].verdict, "above_mrv")

    def test_missing_set_count_refuses(self):
        with self.assertRaises(m.InsufficientData):
            vol.weekly_volume([{"exercises": [{"name": "Plank"}]}])

    def test_unknown_profile_refuses(self):
        with self.assertRaises(m.InsufficientData):
            vol.weekly_volume(PROGRAM, profile="olympian")

    def test_coverage_reports_missing_patterns(self):
        cov = vol.check_coverage(PROGRAM)
        self.assertEqual(cov["missing"], [])
        partial = vol.check_coverage([PROGRAM[0]])
        self.assertIn("knee_dominant", partial["missing"])


def _load_series(start: date, per_day, days):
    return {start + timedelta(days=i): float(per_day) for i in range(days)}


class TestAcwr(unittest.TestCase):
    def test_refuses_without_enough_history(self):
        with self.assertRaises(m.InsufficientData) as ctx:
            load_mod.acwr(_load_series(date(2026, 1, 1), 10, 10))
        self.assertIn("at least", str(ctx.exception))

    def test_steady_load_is_productive(self):
        r = load_mod.acwr(_load_series(date(2026, 1, 1), 12, 28))
        self.assertAlmostEqual(r.ratio, 1.0, delta=0.05)
        self.assertEqual(r.verdict, "productive")

    def test_spike_is_flagged(self):
        data = _load_series(date(2026, 1, 1), 5, 28)
        end = date(2026, 1, 28)
        for i in range(7):
            data[end - timedelta(days=i)] = 30.0
        r = load_mod.acwr(data, reference=end)
        self.assertEqual(r.verdict, "spike")

    def test_missed_week_reads_as_undertrained(self):
        data = _load_series(date(2026, 1, 1), 12, 28)
        end = date(2026, 1, 28)
        for i in range(7):
            data[end - timedelta(days=i)] = 0.0
        self.assertEqual(load_mod.acwr(data, reference=end).verdict, "undertrained")


class TestDeload(unittest.TestCase):
    def test_one_signal_is_not_enough(self):
        r = load_mod.deload_check(performance_dropping_weeks=2)
        self.assertFalse(r.should_deload)
        self.assertEqual(len(r.signals), 1)

    def test_two_signals_trigger(self):
        r = load_mod.deload_check(performance_dropping_weeks=2, sleep_hours_avg=5.8)
        self.assertTrue(r.should_deload)

    def test_absent_inputs_never_count_as_signals(self):
        r = load_mod.deload_check()
        self.assertFalse(r.should_deload)
        self.assertEqual(r.signals, [])

    def test_scheduled_deload_fires_without_symptoms(self):
        r = load_mod.deload_check(weeks_since_deload=8)
        self.assertTrue(r.should_deload)

    def test_acwr_spike_counts_as_a_signal(self):
        r = load_mod.deload_check(acwr_verdict="spike", joint_pain=True)
        self.assertTrue(r.should_deload)


class TestSessionLoad(unittest.TestCase):
    def test_counts_sets(self):
        ex = [{"name": "x", "sets": [{"load_kg": 60, "reps": 8}] * 4}]
        self.assertEqual(load_mod.session_load(ex), 4.0)

    def test_tonnage(self):
        ex = [{"name": "x", "sets": [{"load_kg": 60, "reps": 8}, {"load_kg": 60, "reps": 6}]}]
        self.assertEqual(load_mod.session_load(ex, "tonnage"), 60 * 8 + 60 * 6)

    def test_unknown_mode_refuses(self):
        with self.assertRaises(m.InsufficientData):
            load_mod.session_load([], "vibes")


if __name__ == "__main__":
    unittest.main()
