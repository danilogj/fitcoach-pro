"""The dashboard degrades instead of failing, and never invents a section."""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dashboard
import logstore
import metrics as m


class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        self.log = self.root / "log.jsonl"
        self.out = self.root / "dashboard.html"

    def tearDown(self):
        self.dir.cleanup()

    def _weights(self, days: int = 30, start: float = 88.0, per_day: float = -0.08):
        d0 = date(2026, 6, 1)
        for i in range(days):
            logstore.append(self.log, "weight", {"kg": round(start + per_day * i, 1)},
                            ts="%sT07:00:00" % (d0 + timedelta(days=i)))

    def _sessions(self, weeks: int = 4):
        d0 = date(2026, 6, 1)
        for i in range(weeks * 7):
            day = d0 + timedelta(days=i)
            if day.weekday() not in (0, 1, 3, 4):
                continue
            logstore.append(self.log, "session", {
                "session_id": "upper",
                "exercises": [
                    {"name": "Barbell bench press", "sets": [{"load_kg": 70, "reps": 8}] * 4},
                    {"name": "Pull-up", "sets": [{"reps": 8}] * 4},
                    {"name": "Barbell back squat", "sets": [{"load_kg": 90, "reps": 6}] * 4},
                ]}, ts="%sT18:00:00" % day)


class TestDegradation(DashboardTestCase):
    def test_empty_log_refuses_with_guidance(self):
        self.log.touch()
        with self.assertRaises(m.InsufficientData) as ctx:
            dashboard.render(self.log, self.out)
        self.assertIn("ingest", str(ctx.exception))

    def test_weight_only_still_renders(self):
        self._weights(30)
        result = dashboard.render(self.log, self.out, target_kg=82.0)
        self.assertIn("weight", result["sections"])
        self.assertNotIn("volume", result["sections"])
        self.assertTrue(self.out.exists())

    def test_gaps_name_the_missing_data_instead_of_failing(self):
        self._weights(5)
        result = dashboard.render(self.log, self.out)
        joined = " ".join(result["gaps"])
        self.assertIn("14 days", joined)          # rate refuses and says why
        self.assertIn("no sessions logged", joined)
        self.assertIn("Not shown yet", self.out.read_text(encoding="utf-8"))

    def test_single_weigh_in_is_a_gap_not_a_crash(self):
        logstore.append(self.log, "weight", {"kg": 80.0}, ts="2026-06-01T07:00:00")
        result = dashboard.render(self.log, self.out)
        self.assertTrue(any("at least 2" in g for g in result["gaps"]))


class TestContent(DashboardTestCase):
    def test_full_log_renders_every_section(self):
        self._weights(30)
        self._sessions(4)
        d0 = date(2026, 6, 1)
        for i in range(30):
            day = d0 + timedelta(days=i)
            logstore.append(self.log, "meal", {"kcal": 2100.0}, ts="%sT20:00:00" % day)
            logstore.append(self.log, "sleep", {"hours": 7.1}, ts="%sT23:00:00" % day)
            logstore.append(self.log, "steps", {"count": 8200}, ts="%sT23:30:00" % day)
        result = dashboard.render(self.log, self.out, client="Maria", goal="loss", target_kg=82.0)
        for section in ("weight", "rate", "observed_tdee", "volume",
                        "volume_by_muscle", "acwr", "sleep", "steps", "lifts"):
            self.assertIn(section, result["sections"], "missing %s" % section)

    def test_page_is_self_contained(self):
        self._weights(20)
        dashboard.render(self.log, self.out)
        html = self.out.read_text(encoding="utf-8")
        for forbidden in ("http://", "https://", "<script", "cdn."):
            self.assertNotIn(forbidden, html, "page reaches outside itself: %s" % forbidden)

    def test_client_name_is_escaped(self):
        self._weights(20)
        dashboard.render(self.log, self.out, client='<img src=x onerror="alert(1)">')
        html = self.out.read_text(encoding="utf-8")
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;img", html)

    def test_muscle_chart_labels_an_unfinished_week(self):
        # 3 full weeks: the current week has as many sessions as the previous
        # one, so it is representative — but it has not finished, and says so.
        self._sessions(3)
        self._weights(21)
        dashboard.render(self.log, self.out)
        html = self.out.read_text(encoding="utf-8")
        self.assertIn("Direct sets per muscle", html)
        self.assertIn("(in progress)", html)

    def test_muscle_chart_falls_back_to_the_last_full_week(self):
        # two full weeks, then a single Monday session: one day describes nothing
        self._sessions(2)
        self._weights(20)
        logstore.append(self.log, "session", {
            "session_id": "upper",
            "exercises": [{"name": "Barbell bench press", "sets": [{"load_kg": 70, "reps": 8}] * 3}]},
            ts="2026-06-15T18:00:00")
        dashboard.render(self.log, self.out)
        html = self.out.read_text(encoding="utf-8")
        self.assertIn("week of 08/06", html)
        self.assertNotIn("(in progress)", html)

    def test_cardio_only_sessions_do_not_draw_an_empty_volume_chart(self):
        """Regression: imported cardio has a duration and no sets.

        Counting those as zero sets produced a division by zero, and would have
        implied the client lifted nothing all week.
        """
        self._weights(25)
        d0 = date(2026, 6, 1)
        for i in range(0, 21, 3):
            logstore.append(self.log, "session",
                            {"session_id": "running", "duration_min": 42.0},
                            ts="%sT07:00:00" % (d0 + timedelta(days=i)))
        result = dashboard.render(self.log, self.out)
        self.assertNotIn("volume", result["sections"])
        self.assertTrue(any("none record sets" in g for g in result["gaps"]))
        self.assertIn("Weight", self.out.read_text(encoding="utf-8"))

    def test_uncatalogued_exercises_become_a_gap(self):
        self._weights(20)
        for i in range(8):
            day = date(2026, 6, 1) + timedelta(days=i)
            logstore.append(self.log, "session", {
                "session_id": "x",
                "exercises": [{"name": "Kettlebell juggling", "sets": [{"reps": 10}] * 3}]},
                ts="%sT18:00:00" % day)
        result = dashboard.render(self.log, self.out)
        self.assertNotIn("volume_by_muscle", result["sections"])
        self.assertTrue(any("catalog" in g for g in result["gaps"]))


if __name__ == "__main__":
    unittest.main()
