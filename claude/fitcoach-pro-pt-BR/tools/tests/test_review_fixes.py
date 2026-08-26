"""Fixes from a review of physiological and operational blind spots.

Each class here corresponds to a gap that was real: expenditure overestimated
in high-adiposity clients, 1RM inflated from high-rep sets, hydration and meal
distribution documented but never computed, ACWR treating a deadlift set like a
lateral raise, and no way to see a whole roster at once.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cohort
import load as load_mod
import logstore
import metrics as m
import volume as vol


class TestHighAdiposity(unittest.TestCase):
    def test_warns_when_bmi_is_high_and_composition_unknown(self):
        r = m.bmr(105, 175, 38, "male")
        self.assertGreater(r.bmi, 30)
        self.assertIsNotNone(r.warning)
        self.assertIn("overestimates", r.warning)

    def test_no_warning_at_normal_bmi(self):
        r = m.bmr(71, 178, 41, "male")
        self.assertLess(r.bmi, 25)
        self.assertIsNone(r.warning)

    def test_katch_takes_over_when_composition_is_known(self):
        r = m.bmr(105, 175, 38, "male", fat_free_mass_kg=65)
        self.assertEqual(r.method, "katch")
        self.assertEqual(r.used, r.katch)
        self.assertLess(r.used, r.mifflin)   # the whole point: a lower, truer number

    def test_mean_is_kept_at_normal_bmi(self):
        r = m.bmr(71, 178, 41, "male", fat_free_mass_kg=57.7)
        self.assertEqual(r.method, "mean(mifflin,katch)")

    def test_adjusted_weight_lowers_the_estimate(self):
        plain = m.bmr(105, 175, 38, "male")
        adj = m.bmr(105, 175, 38, "male", use_adjusted_weight=True)
        self.assertLess(adj.used, plain.used)
        self.assertIn("adjusted body weight", adj.warning)

    def test_adjusted_weight_is_a_noop_below_ideal(self):
        # a lean client is already at or under ideal weight; nothing to adjust
        self.assertEqual(m.adjusted_weight(60, 178, "male"), 60.0)

    def test_devine_ideal_weight_shape(self):
        # 175 cm male: 50 + 2.3 * (175-152.4)/2.54 ≈ 70.5 kg ideal
        # adjusted = 70.5 + 0.4 * (105 - 70.5) ≈ 84.3
        self.assertAlmostEqual(m.adjusted_weight(105, 175, "male"), 84.3, delta=0.6)

    def test_bmi_is_computed(self):
        self.assertAlmostEqual(m.bmi(105, 175), 34.3, places=1)


class TestOneRepMaxRigour(unittest.TestCase):
    def test_refuses_above_ten_reps(self):
        with self.assertRaises(m.InsufficientData) as ctx:
            m.one_rep_max(60, 15)
        self.assertIn("acidosis", str(ctx.exception))

    def test_ten_reps_still_carries_a_caution_despite_formula_agreement(self):
        # Epley and Brzycki cross near 10 reps; agreement there is arithmetic
        # coincidence, not evidence the estimate is sound
        r = m.one_rep_max(60, 10)
        self.assertAlmostEqual(r.epley, r.brzycki, places=1)
        self.assertIsNotNone(r.caution)
        self.assertIn("least reliable", r.caution)

    def test_low_rep_set_reports_the_spread(self):
        r = m.one_rep_max(100, 5)
        self.assertIsNotNone(r.caution)
        self.assertIn("range", r.caution)

    def test_the_formulas_cross_at_ten_reps(self):
        """Epley and Brzycki intersect exactly at 10 reps.

        W(1 + 10/30) = 4W/3 = W·36/(37-10). They diverge on both sides of it.
        So formula agreement is a terrible confidence signal — at the least
        reliable rep count it is perfect — which is why the caution is driven
        by rep count and not by the spread.
        """
        ten = m.one_rep_max(100, 10)
        self.assertAlmostEqual(ten.epley, ten.brzycki, places=1)
        self.assertIn("least reliable", ten.caution)

        three = m.one_rep_max(100, 3)
        self.assertGreater(abs(three.epley - three.brzycki), 1)


class TestHydrationAndMeals(unittest.TestCase):
    def test_macros_include_water_fibre_and_per_meal_protein(self):
        r = m.macros(2700, 71, "male", protein_g_kg=2.11, fat_g_kg=0.99, meals=5)
        self.assertAlmostEqual(r.water_ml, 71 * 35, delta=10)
        self.assertGreaterEqual(r.fibre_g, 25)
        self.assertLessEqual(r.fibre_g, 40)
        self.assertEqual(r.meals, 5)
        self.assertAlmostEqual(r.protein_per_meal_g, 150 / 5, delta=1)

    def test_warns_when_protein_per_meal_is_too_low(self):
        # 100 g of protein for a 90 kg client across 6 meals: ~17 g each,
        # well under the ~0.3 g/kg that maximises the response
        r = m.macros(2600, 90, "male", protein_g_kg=1.2, fat_g_kg=0.9, meals=6)
        self.assertIsNotNone(r.floor_warning)
        self.assertIn("per meal", r.floor_warning)

    def test_absurd_meal_count_refuses(self):
        with self.assertRaises(m.InsufficientData):
            m.macros(2500, 70, "male", meals=12)

    def test_fibre_scales_with_calories_within_bounds(self):
        low = m.macros(1400, 55, "female", protein_g_kg=1.8, fat_g_kg=0.8)
        high = m.macros(3800, 95, "male", protein_g_kg=1.8, fat_g_kg=0.9)
        self.assertEqual(low.fibre_g, 25)     # floor
        self.assertEqual(high.fibre_g, 40)    # ceiling


class TestFatigueWeighting(unittest.TestCase):
    def setUp(self):
        self.cat = vol.Catalog()

    def test_axial_compound_outweighs_isolation(self):
        deadlift = self.cat.find("Conventional deadlift")
        raise_ = self.cat.find("Dumbbell lateral raise")
        self.assertGreater(load_mod.fatigue_weight(deadlift), load_mod.fatigue_weight(raise_) * 2)

    def test_unknown_exercise_weighs_neutral_not_zero(self):
        self.assertEqual(load_mod.fatigue_weight(None), 1.0)

    def test_session_load_separates_heavy_from_light(self):
        heavy = [{"name": "Barbell back squat", "sets": [{"load_kg": 100, "reps": 5}] * 4}]
        light = [{"name": "Dumbbell lateral raise", "sets": [{"load_kg": 10, "reps": 15}] * 4}]
        h = load_mod.session_load(heavy, "weighted", self.cat)
        l = load_mod.session_load(light, "weighted", self.cat)
        self.assertGreater(h, l)
        # flat counting cannot tell them apart, which was the bug
        self.assertEqual(load_mod.session_load(heavy, "sets"),
                         load_mod.session_load(light, "sets"))

    def test_tonnage_mode_still_works(self):
        ex = [{"name": "x", "sets": [{"load_kg": 60, "reps": 8}]}]
        self.assertEqual(load_mod.session_load(ex, "tonnage"), 480)

    def test_unknown_mode_refuses(self):
        with self.assertRaises(m.InsufficientData):
            load_mod.session_load([], "vibes")


class TestWeightedAcwr(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.log = Path(self.dir.name) / "log.jsonl"
        self.cat = vol.Catalog()

    def tearDown(self):
        self.dir.cleanup()

    def _log_session(self, day, name, sets):
        logstore.append(self.log, "session", {
            "session_id": "s",
            "exercises": [{"name": name, "sets": [{"load_kg": 60, "reps": 6}] * sets}]},
            ts="%sT18:00:00" % day)

    def test_swapping_isolation_for_axial_work_raises_the_ratio(self):
        """The bug: four weeks of curls then a week of deadlifts read as flat."""
        start = date(2026, 6, 1)
        for i in range(21):
            self._log_session(start + timedelta(days=i), "Dumbbell curl", 6)
        for i in range(21, 28):
            self._log_session(start + timedelta(days=i), "Conventional deadlift", 6)

        flat = load_mod.acwr({d: float(v) for d, v in logstore.hard_sets_by_day(self.log).items()})
        weighted = load_mod.acwr(logstore.weighted_load_by_day(self.log, self.cat))

        self.assertAlmostEqual(flat.ratio, 1.0, delta=0.05)      # blind
        self.assertGreater(weighted.ratio, 1.5)                  # sees it
        self.assertEqual(weighted.verdict, "spike")

    def test_cardio_session_without_sets_still_carries_load(self):
        logstore.append(self.log, "session", {"session_id": "run", "duration_min": 60.0},
                        ts="2026-06-01T07:00:00")
        loads = logstore.weighted_load_by_day(self.log, self.cat)
        self.assertGreater(loads[date(2026, 6, 1)], 0)


class TestCohort(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name) / "clients"
        self.root.mkdir(parents=True)

    def tearDown(self):
        self.dir.cleanup()

    def _client(self, name, days=30, per_day=-0.08, last_day=date(2026, 7, 30), sessions=True):
        folder = self.root / name
        folder.mkdir()
        log = folder / "log.jsonl"
        for i in range(days):
            day = last_day - timedelta(days=days - 1 - i)
            logstore.append(log, "weight", {"kg": round(90 + per_day * i, 1)},
                            ts="%sT07:00:00" % day)
            if sessions and day.weekday() in (0, 2, 4):
                logstore.append(log, "session", {
                    "session_id": "s",
                    "exercises": [{"name": "Barbell back squat",
                                   "sets": [{"load_kg": 100, "reps": 5}] * 4}]},
                    ts="%sT18:00:00" % day)
        return folder

    def test_empty_root_refuses_with_guidance(self):
        with self.assertRaises(m.InsufficientData) as ctx:
            cohort.scan(self.root)
        self.assertIn("no client folders", str(ctx.exception))

    def test_missing_root_refuses(self):
        with self.assertRaises(m.InsufficientData):
            cohort.scan(self.root / "nope")

    def test_client_without_a_log_is_reported_not_skipped(self):
        (self.root / "never_started").mkdir()
        self._client("maria")
        rows = cohort.scan(self.root)
        names = {r.name: r for r in rows}
        self.assertEqual(names["never_started"].status, "no_data")
        self.assertIn("never set up", names["never_started"].alerts[0])

    def test_stale_client_is_measured_against_the_roster_not_itself(self):
        """The bug: each client's own last entry made everyone look current."""
        self._client("active", last_day=date(2026, 7, 30))
        self._client("gone", last_day=date(2026, 7, 16))
        rows = {r.name: r for r in cohort.scan(self.root)}
        self.assertEqual(rows["active"].days_since_activity, 0)
        self.assertEqual(rows["gone"].days_since_activity, 14)
        self.assertEqual(rows["gone"].status, "stale")

    def test_too_fast_loss_is_flagged_as_risk(self):
        self._client("fast", per_day=-0.25)
        rows = {r.name: r for r in cohort.scan(self.root)}
        self.assertEqual(rows["fast"].status, "risk")
        self.assertIn("too fast", " ".join(rows["fast"].alerts))

    def test_rows_are_sorted_by_severity(self):
        self._client("ok_client", per_day=-0.08)
        self._client("fast", per_day=-0.25)
        self._client("gone", last_day=date(2026, 7, 10))
        rows = cohort.scan(self.root)
        self.assertEqual(rows[0].name, "fast")
        self.assertLessEqual(cohort.SEVERITY[rows[0].status], cohort.SEVERITY[rows[-1].status])

    def test_render_names_who_to_start_with(self):
        self._client("ok_client", per_day=-0.08)
        self._client("fast", per_day=-0.25)
        text = cohort.render(cohort.scan(self.root))
        self.assertIn("start with:", text)
        self.assertIn("fast", text)
        self.assertIn("2 clients", text)


class TestExpandedCatalog(unittest.TestCase):
    def setUp(self):
        self.cat = vol.Catalog()

    def test_common_commercial_gym_machines_are_present(self):
        for query in ["adductor", "abductor", "smith machine squat", "remada cavalinho",
                      "preacher curl machine", "45° leg press", "standing single-leg curl",
                      "hip thrust machine", "rope pushdown", "french press"]:
            with self.subTest(exercise=query):
                self.cat.find(query)   # raises if missing or ambiguous

    def test_ambiguous_family_names_still_refuse(self):
        # "t-bar row" matches both the free and the chest-supported version;
        # refusing and listing them beats silently picking one
        with self.assertRaises(m.InsufficientData) as ctx:
            self.cat.find("t-bar row")
        self.assertIn("matches 2", str(ctx.exception))

    def test_catalog_has_grown_past_a_hundred(self):
        self.assertGreaterEqual(len(self.cat.exercises), 100)

    def test_every_substitution_target_still_resolves(self):
        for reason, table in self.cat.substitutions.items():
            for source, targets in table.items():
                for key in [source] + list(targets):
                    with self.subTest(reason=reason, exercise=key):
                        self.assertIn(key, self.cat.exercises)

    def test_smith_squat_is_flagged_axial(self):
        self.assertTrue(self.cat.find("Smith machine squat").get("axial"))


if __name__ == "__main__":
    unittest.main()
