"""Fixtures with hand-checked numbers. If these drift, the advice drifts."""
from __future__ import annotations

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import metrics as m


class TestBmr(unittest.TestCase):
    def test_mifflin_male(self):
        # 10*71 + 6.25*178 - 5*41 + 5 = 710 + 1112.5 - 205 + 5 = 1622.5
        r = m.bmr(71, 178, 41, "male")
        self.assertAlmostEqual(r.mifflin, 1622.5, places=1)
        self.assertEqual(r.method, "mifflin")

    def test_mifflin_female(self):
        # 10*62 + 6.25*165 - 5*34 - 161 = 620 + 1031.25 - 170 - 161 = 1320.25
        # (Python rounds half to even, so the stored value is 1320.2)
        r = m.bmr(62, 165, 34, "female")
        self.assertAlmostEqual(r.mifflin, 1320.25, delta=0.06)

    def test_katch_and_spread(self):
        # 370 + 21.6*57.7 = 1616.32
        r = m.bmr(71, 178, 41, "male", fat_free_mass_kg=57.7)
        self.assertAlmostEqual(r.katch, 1616.3, places=1)
        self.assertLess(r.spread, 10)
        self.assertAlmostEqual(r.used, (1622.5 + 1616.3) / 2, places=0)

    def test_accepts_portuguese_sex(self):
        self.assertEqual(m.bmr(71, 178, 41, "masculino").mifflin, m.bmr(71, 178, 41, "male").mifflin)

    def test_rejects_bad_input(self):
        for args in [(0, 178, 41, "male"), (71, 0, 41, "male"), (71, 178, 0, "male")]:
            with self.assertRaises(m.InsufficientData):
                m.bmr(*args)
        with self.assertRaises(m.InsufficientData):
            m.bmr(71, 178, 41, "unspecified")
        with self.assertRaises(m.InsufficientData):
            m.bmr(71, 178, 41, "male", fat_free_mass_kg=90)  # above body weight


class TestTdee(unittest.TestCase):
    def test_multiplier(self):
        self.assertEqual(m.tdee(1600, "sedentary"), 1920)
        self.assertEqual(m.tdee(1600, "very_active"), 3040)

    def test_unknown_activity_refuses(self):
        with self.assertRaises(m.InsufficientData):
            m.tdee(1600, "athlete")

    def test_components_grosses_up_tef(self):
        # subtotal = 1600 + 192 + 4*320/7 = 1974.86 ; /0.9 = 2194.3
        b = m.tdee_components(1600, neat_pct=0.12, sessions_per_week=4)
        self.assertAlmostEqual(b.total, 2194, delta=1)
        self.assertAlmostEqual(b.bmr + b.neat + b.training + b.tef, b.total, delta=1)

    def test_components_reject_absurd_neat(self):
        with self.assertRaises(m.InsufficientData):
            m.tdee_components(1600, neat_pct=0.9)

    def test_range_is_symmetric(self):
        lo, hi = m.tdee_range(2000, 0.06)
        self.assertEqual((lo, hi), (1880, 2120))


class TestMacros(unittest.TestCase):
    def test_carbs_take_the_remainder(self):
        r = m.macros(2700, 71, "male", protein_g_kg=2.11, fat_g_kg=0.99)
        self.assertEqual(r.protein_g, 150)
        self.assertEqual(r.fat_g, 70)
        # 2700 - (150*4 + 70*9) = 2700 - 1230 = 1470 -> 367.5 g
        self.assertAlmostEqual(r.carb_g, 368, delta=1)

    def test_floor_warning_for_low_target(self):
        r = m.macros(1100, 55, "female", protein_g_kg=1.8, fat_g_kg=0.8)
        self.assertIsNotNone(r.floor_warning)

    def test_refuses_impossible_split(self):
        with self.assertRaises(m.InsufficientData):
            m.macros(800, 90, "male", protein_g_kg=2.2, fat_g_kg=1.0)

    def test_refuses_absurd_protein(self):
        with self.assertRaises(m.InsufficientData):
            m.macros(2500, 70, "male", protein_g_kg=5.0)


def _series(start: date, values):
    return [(start + timedelta(days=i), v) for i, v in enumerate(values)]


class TestTrend(unittest.TestCase):
    def test_ema_smooths_a_spike(self):
        pts = _series(date(2026, 1, 1), [80, 80, 80, 84, 80, 80, 80])
        trend = m.ema_trend(pts, alpha=0.25)
        self.assertLess(trend[3].ema, 81.5)  # the 84 kg spike barely moves it
        self.assertEqual(trend[3].raw, 84)

    def test_fills_gaps(self):
        pts = [(date(2026, 1, 1), 80.0), (date(2026, 1, 5), 79.0)]
        trend = m.ema_trend(pts)
        self.assertEqual(len(trend), 5)
        self.assertIsNone(trend[2].raw)

    def test_refuses_single_point(self):
        with self.assertRaises(m.InsufficientData):
            m.ema_trend([(date(2026, 1, 1), 80.0)])


class TestRate(unittest.TestCase):
    def test_refuses_short_window(self):
        trend = m.ema_trend(_series(date(2026, 1, 1), [80] * 10))
        with self.assertRaises(m.InsufficientData):
            m.rate_of_change(trend, "loss")

    def test_detects_safe_loss(self):
        values = [90 - 0.1 * i for i in range(28)]  # 0.7 kg/week on ~89 kg = 0.79%/wk
        trend = m.ema_trend(_series(date(2026, 1, 1), values))
        r = m.rate_of_change(trend, "loss")
        self.assertEqual(r.verdict, "on_track")
        self.assertLess(r.kg_per_week, 0)

    def test_flags_too_fast_loss(self):
        values = [90 - 0.25 * i for i in range(28)]  # ~1.75 kg/week
        trend = m.ema_trend(_series(date(2026, 1, 1), values))
        self.assertEqual(m.rate_of_change(trend, "loss").verdict, "too_fast")

    def test_flags_stall(self):
        trend = m.ema_trend(_series(date(2026, 1, 1), [80.0] * 28))
        self.assertEqual(m.rate_of_change(trend, "loss").verdict, "stalled")

    def test_flags_wrong_direction(self):
        values = [80 + 0.05 * i for i in range(28)]
        self.assertEqual(
            m.rate_of_change(m.ema_trend(_series(date(2026, 1, 1), values)), "loss").verdict,
            "wrong_direction")

    def test_gain_band(self):
        values = [71 + 0.04 * i for i in range(28)]  # 0.28 kg/wk on 71 kg = 0.39%/wk
        self.assertEqual(
            m.rate_of_change(m.ema_trend(_series(date(2026, 1, 1), values)), "gain").verdict,
            "on_track")


class TestObservedTdee(unittest.TestCase):
    def setUp(self):
        self.start = date(2026, 1, 1)
        # steady 0.5 kg/week loss over 28 days on 2000 kcal
        self.values = [90 - (0.5 / 7) * i for i in range(28)]
        self.trend = m.ema_trend(_series(self.start, self.values))

    def test_refuses_without_enough_meal_days(self):
        intake = {self.start + timedelta(days=i): 2000.0 for i in range(5)}
        with self.assertRaises(m.InsufficientData) as ctx:
            m.observed_tdee(intake, self.trend)
        self.assertIn("logged intake", str(ctx.exception))

    def test_computes_expenditure_above_intake_when_losing(self):
        intake = {self.start + timedelta(days=i): 2000.0 for i in range(28)}
        r = m.observed_tdee(intake, self.trend)
        self.assertGreater(r.kcal, 2000)
        self.assertLess(r.kg_change, 0)
        # losing ~0.5 kg/wk on 2000 kcal implies roughly 2000 + 550 kcal/day
        self.assertAlmostEqual(r.kcal, 2550, delta=120)

    def test_suggested_target_applies_delta(self):
        intake = {self.start + timedelta(days=i): 2000.0 for i in range(28)}
        r = m.observed_tdee(intake, self.trend, goal_delta_kcal=-400)
        self.assertAlmostEqual(r.suggested_target_kcal, r.kcal - 400, delta=1)


class TestOneRepMax(unittest.TestCase):
    def test_epley_and_brzycki(self):
        r = m.one_rep_max(100, 5)
        self.assertAlmostEqual(r.epley, 116.7, places=1)      # 100*(1+5/30)
        self.assertAlmostEqual(r.brzycki, 112.5, places=1)    # 100*36/32
        # the two formulas disagree by 4.2 kg at 5 reps, and the caution says so
        self.assertIn("range", r.caution)

    def test_high_reps_get_a_caution(self):
        self.assertIn("least reliable", m.one_rep_max(60, 10).caution)

    def test_refuses_beyond_ten_reps(self):
        with self.assertRaises(m.InsufficientData):
            m.one_rep_max(60, 15)
        with self.assertRaises(m.InsufficientData):
            m.one_rep_max(60, 12)


class TestProjection(unittest.TestCase):
    def test_weeks_to_goal(self):
        values = [90 - (0.5 / 7) * i for i in range(28)]
        trend = m.ema_trend(_series(date(2026, 1, 1), values))
        rate = m.rate_of_change(trend, "loss")
        p = m.projection(trend, 85.0, rate)
        self.assertGreater(p["weeks"], 0)

    def test_refuses_when_rate_is_flat(self):
        trend = m.ema_trend(_series(date(2026, 1, 1), [80.0] * 28))
        rate = m.rate_of_change(trend, "loss")
        with self.assertRaises(m.InsufficientData):
            m.projection(trend, 75.0, rate)

    def test_reports_wrong_direction(self):
        values = [80 + 0.05 * i for i in range(28)]
        trend = m.ema_trend(_series(date(2026, 1, 1), values))
        rate = m.rate_of_change(trend, "gain")
        p = m.projection(trend, 75.0, rate)
        self.assertIsNone(p["weeks"])


if __name__ == "__main__":
    unittest.main()
