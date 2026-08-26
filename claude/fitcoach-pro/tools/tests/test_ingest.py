"""Import adapters.

The fixtures below imitate the documented shape of each vendor's export. They
are synthetic — no real export was available while writing this — so the first
real file from any given service may still need a column alias added. That is
what `--inspect` is for, and why every adapter reports what it could not map
instead of failing silently.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ingest
import logstore
import metrics as m

D0 = date(2026, 6, 1)


def _samsung_weight() -> str:
    rows = ["com.samsung.health.weight,1,structured_data",
            "com.samsung.health.weight.start_time,com.samsung.health.weight.weight,"
            "com.samsung.health.weight.body_fat"]
    for i in range(10):
        d = D0 + timedelta(days=i)
        rows.append("%s 07:12:00.000,%.1f,%.1f" % (d.isoformat(), 88.0 - 0.1 * i, 22.0))
    return "\n".join(rows)


def _samsung_sleep() -> str:
    rows = ["com.samsung.health.sleep,1",
            "com.samsung.health.sleep.start_time,com.samsung.health.sleep.sleep_duration,"
            "com.samsung.health.sleep.sleep_score"]
    for i in range(10):
        d = D0 + timedelta(days=i)
        rows.append("%s 23:40:00.000,%d,%d" % (d.isoformat(), 420, 78))  # minutes
    return "\n".join(rows)


class IngestTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        self.log = self.root / "log.jsonl"

    def tearDown(self):
        self.dir.cleanup()

    def _write(self, name: str, text: str) -> Path:
        p = self.root / name
        p.write_text(text, encoding="utf-8")
        return p


class TestSamsung(IngestTestCase):
    def test_skips_the_vendor_metadata_line(self):
        p = self._write("com.samsung.health.weight.csv", _samsung_weight())
        report = ingest.parse(p, "samsung")
        self.assertEqual(len(report.candidates), 10)
        self.assertTrue(all(c.type == "weight" for c in report.candidates))
        self.assertAlmostEqual(report.candidates[0].data["kg"], 88.0, places=1)

    def test_sleep_minutes_become_hours(self):
        p = self._write("com.samsung.health.sleep.csv", _samsung_sleep())
        report = ingest.parse(p, "samsung")
        self.assertTrue(report.candidates)
        self.assertAlmostEqual(report.candidates[0].data["hours"], 7.0, places=1)
        self.assertEqual(report.candidates[0].data["score"], 78)

    def test_detects_source_from_a_zip(self):
        z = self.root / "samsung.zip"
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr("com.samsung.health.weight.csv", _samsung_weight())
        self.assertEqual(ingest.detect_source(z), "samsung")
        self.assertEqual(len(ingest.parse(z).candidates), 10)

    def test_unrecognisable_zip_refuses_with_instructions(self):
        z = self.root / "com.samsung.empty.zip"
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr("readme.txt", "nothing here")
        with self.assertRaises(m.InsufficientData) as ctx:
            ingest.parse(z, "samsung")
        self.assertIn("Download personal data", str(ctx.exception))


class TestGarminAndStrava(IngestTestCase):
    def test_garmin_activities_become_sessions(self):
        rows = ['"Activity Type","Date","Title","Distance","Calories","Time","Avg HR"']
        for i in range(4):
            d = D0 + timedelta(days=i)
            rows.append('"Cycling","%s 07:05:11","Ride","18.4","520","00:52:14","132"' % d.isoformat())
        p = self._write("Activities.csv", "\n".join(rows))
        self.assertEqual(ingest.detect_source(p), "garmin")
        report = ingest.parse(p)
        self.assertEqual(len(report.candidates), 4)
        self.assertAlmostEqual(report.candidates[0].data["duration_min"], 52.23, places=1)

    def test_strava_elapsed_seconds_become_minutes(self):
        rows = ["Activity ID,Activity Date,Activity Name,Activity Type,Elapsed Time,Distance"]
        rows.append("1001,%s 06:30:00,Easy run,Run,2760,6.20" % D0.isoformat())
        p = self._write("activities.csv", "\n".join(rows))
        self.assertEqual(ingest.detect_source(p), "strava")
        report = ingest.parse(p)
        self.assertEqual(len(report.candidates), 1)
        self.assertAlmostEqual(report.candidates[0].data["duration_min"], 46.0, places=0)


class TestApple(IngestTestCase):
    def test_steps_sum_per_day_and_weight_takes_the_last(self):
        recs = []
        for i in range(3):
            d = (D0 + timedelta(days=i)).isoformat()
            recs.append('<Record type="HKQuantityTypeIdentifierBodyMass" unit="kg" '
                        'startDate="%s 07:00:00 -0300" value="%.1f"/>' % (d, 88.0 - i))
            for k in range(3):
                recs.append('<Record type="HKQuantityTypeIdentifierStepCount" unit="count" '
                            'startDate="%s 1%d:00:00 -0300" value="2000"/>' % (d, k))
        p = self._write("export.xml", "<HealthData>%s</HealthData>" % "".join(recs))
        report = ingest.parse(p, "apple")
        steps = [c for c in report.candidates if c.type == "steps"]
        weights = [c for c in report.candidates if c.type == "weight"]
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0].data["count"], 6000)
        self.assertEqual(len(weights), 3)

    def test_empty_export_refuses(self):
        p = self._write("export.xml", "<HealthData></HealthData>")
        with self.assertRaises(m.InsufficientData):
            ingest.parse(p, "apple")


class TestGeneric(IngestTestCase):
    def test_semicolons_and_day_first_dates(self):
        rows = ["Data da Medicao;Massa (kg);Gordura corporal (%)"]
        rows.append("01/06/2026;88,4;22,5")
        rows.append("02/06/2026;88,1;22,4")
        p = self._write("balanca.csv", "\n".join(rows))
        report = ingest.parse(p, "generic")
        weights = [c for c in report.candidates if c.type == "weight"]
        self.assertEqual(len(weights), 2)
        self.assertAlmostEqual(weights[0].data["kg"], 88.4, places=1)
        self.assertEqual(weights[0].ts[:10], "2026-06-01")

    def test_body_composition_derived_from_percentage(self):
        rows = ["date,weight,body fat", "2026-06-01,80.0,20.0"]
        p = self._write("scale.csv", "\n".join(rows))
        comp = [c for c in ingest.parse(p, "generic").candidates if c.type == "body_comp"]
        self.assertEqual(len(comp), 1)
        self.assertAlmostEqual(comp[0].data["fat_mass_kg"], 16.0, places=1)
        self.assertAlmostEqual(comp[0].data["ffm_kg"], 64.0, places=1)

    def test_unrecognised_columns_refuse_with_a_hint(self):
        p = self._write("weird.csv", "alpha,beta\n1,2\n3,4")
        with self.assertRaises(m.InsufficientData) as ctx:
            ingest.parse(p, "generic")
        self.assertIn("--inspect", str(ctx.exception))

    def test_explicit_mapping_rescues_an_odd_export(self):
        p = self._write("weird.csv", "quando,quanto\n2026-06-01,81.5")
        report = ingest.parse(p, "generic", {"date": "quando", "weight_kg": "quanto"})
        self.assertEqual(len(report.candidates), 1)
        self.assertAlmostEqual(report.candidates[0].data["kg"], 81.5, places=1)

    def test_inspect_names_the_columns(self):
        p = self._write("balanca.csv", "Data;Massa (kg)\n01/06/2026;88,4")
        text = ingest.inspect(p)
        self.assertIn("Massa (kg)", text)
        self.assertIn("weight_kg", text)


class TestWriting(IngestTestCase):
    def _report(self):
        p = self._write("com.samsung.health.weight.csv", _samsung_weight())
        return ingest.parse(p, "samsung")

    def test_writes_then_becomes_a_noop(self):
        report = self._report()
        written, skipped = ingest.write(report, self.log, logstore)
        self.assertEqual((written, skipped), (10, 0))
        again = ingest.write(report, self.log, logstore)
        self.assertEqual(again, (0, 10))
        self.assertEqual(len(logstore.read(self.log)), 10)

    def test_two_sessions_same_day_both_import(self):
        rows = ['"Activity Type","Date","Time"',
                '"Cycling","2026-06-01 07:00:00","00:40:00"',
                '"Running","2026-06-01 18:00:00","00:30:00"']
        p = self._write("Activities.csv", "\n".join(rows))
        report = ingest.parse(p, "garmin")
        written, _ = ingest.write(report, self.log, logstore)
        self.assertEqual(written, 2)
        self.assertEqual(len(logstore.read(self.log, "session")), 2)
        self.assertEqual(ingest.write(report, self.log, logstore), (0, 2))

    def test_out_of_range_values_are_dropped_not_written(self):
        p = self._write("scale.csv", "date,weight\n2026-06-01,880.0\n2026-06-02,81.0")
        report = ingest.parse(p, "generic")
        # 880 kg never becomes a candidate; the plausible row still imports
        self.assertEqual(len(report.candidates), 1)
        written, _ = ingest.write(report, self.log, logstore)
        self.assertEqual(written, 1)

    def test_missing_file_refuses(self):
        with self.assertRaises(m.InsufficientData):
            ingest.parse(self.root / "nope.csv")


class TestParsers(unittest.TestCase):
    def test_duration_formats(self):
        self.assertAlmostEqual(ingest._duration_minutes("00:52:14"), 52.23, places=1)
        self.assertAlmostEqual(ingest._duration_minutes("45:00"), 45 * 60, places=0)
        self.assertAlmostEqual(ingest._duration_minutes("2760"), 46.0, places=0)
        self.assertAlmostEqual(ingest._duration_minutes("40"), 40.0, places=0)
        self.assertIsNone(ingest._duration_minutes("soon"))

    def test_sleep_formats(self):
        self.assertAlmostEqual(ingest._sleep_hours("420"), 7.0, places=1)
        self.assertAlmostEqual(ingest._sleep_hours("7:30"), 7.5, places=1)
        self.assertAlmostEqual(ingest._sleep_hours("6.8"), 6.8, places=1)

    def test_date_formats(self):
        self.assertEqual(ingest._to_ts("2026-06-01")[:10], "2026-06-01")
        self.assertEqual(ingest._to_ts("01/06/2026")[:10], "2026-06-01")
        self.assertEqual(ingest._to_ts("2026-06-01 18:30:00")[11:16], "18:30")
        self.assertIsNone(ingest._to_ts("not a date"))

    def test_alias_matching_is_separator_agnostic(self):
        self.assertEqual(ingest._match_alias("com.samsung.health.weight.weight"), "weight_kg")
        self.assertEqual(ingest._match_alias("Avg HR"), "avg_hr")
        self.assertEqual(ingest._match_alias("Massa (kg)"), "weight_kg")
        self.assertIsNone(ingest._match_alias("notes"))


if __name__ == "__main__":
    unittest.main()
