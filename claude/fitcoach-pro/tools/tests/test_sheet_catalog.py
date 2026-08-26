"""Sheet validation, local catalogs, and translation parity.

These three exist because of a review that pointed at real gaps: nothing
verified a filled-in sheet before it reached a client, the exercise catalog
could not be extended for a real gym, and nothing guarded the two language
versions against drifting apart.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import metrics as m
import sheet as sheet_mod
import volume as vol

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT.parent          # the folder holding both language versions

# The same suite ships inside both skills. Which one is running decides the
# template filename and the placeholder names, so both are discovered rather
# than hard-coded — otherwise running the tests from the translated copy fails
# on filenames that only exist in the other one.
_TEMPLATES = {
    "client-sheet.template.html": {
        "{{CLIENT}}": "Maria Silva", "{{SUBTITLE}}": "Upper/Lower", "{{START}}": "2026-08-31",
        "{{TOTAL_WEEKS}}": "8", "{{INTRO_UNTIL}}": "3", "{{DELOAD_WEEK}}": "7",
        "{{SLUG}}": "maria", "{{CLIENT_SUMMARY}}": "F, 34", "{{TRAINER}}": "John Coach",
        "{{CERT}}": "NSCA-CPT",
    },
    "ficha-aluno.template.html": {
        "{{ALUNO}}": "Maria Silva", "{{SUBTITULO}}": "Upper/Lower", "{{INICIO}}": "2026-08-31",
        "{{TOTAL_SEMANAS}}": "8", "{{ENTRADA_ATE}}": "3", "{{DELOAD_EM}}": "7",
        "{{SLUG}}": "maria", "{{RESUMO_ALUNO}}": "F, 34", "{{PROFISSIONAL}}": "John Coach",
        "{{CREF}}": "CREF 000000-G/SP",
    },
}


def _discover_template():
    for name, values in _TEMPLATES.items():
        candidate = ROOT / "assets" / name
        if candidate.exists():
            return candidate, values
    raise unittest.SkipTest("no client sheet template found in %s" % (ROOT / "assets"))


TEMPLATE, FILLED = _discover_template()
PROGRAM_VAR = "PROGRAM" if TEMPLATE.name.startswith("client-sheet") else "PROGRAMA"
TRAINER_KEY = "{{TRAINER}}" if "{{TRAINER}}" in FILLED else "{{PROFISSIONAL}}"
START_KEY = "{{START}}" if "{{START}}" in FILLED else "{{INICIO}}"

REAL_PROGRAM = '''  var %s = [
    {
      id: "supA", dia: "Mon", nome: "Upper A", foco: "Push and pull",
      ex: [
        { n: "Barbell bench press", s: 4, r: "6-8", rir: "1-2", t: "hold", d: 150, dl: "2-3 min" },
        { n: "Pull-up", s: 4, r: "max", rir: "1-2", t: "hold", f: "pc", d: 150, dl: "2-3 min" },
        { n: "Plank", s: 3, r: "45-60 s", rir: "", t: "", f: "tempo", d: 45, dl: "45 s" }
      ]
    }
  ];
''' % PROGRAM_VAR


def _sheet(tmp: Path, *, fill=True, program=REAL_PROGRAM, **overrides) -> Path:
    text = TEMPLATE.read_text(encoding="utf-8")
    text = re.sub(r"  var (?:PROGRAM|PROGRAMA) = \[.*?\n  \];\n", program, text, count=1, flags=re.S)
    for marker in sheet_mod.EXAMPLE_MARKERS:
        text = text.replace(marker, "")
    if fill:
        values = dict(FILLED)
        values.update(overrides)
        for k, v in values.items():
            text = text.replace(k, v)
    out = tmp / "sheet.html"
    out.write_text(text, encoding="utf-8")
    return out


class SheetTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def _messages(self, report):
        return " | ".join(f.message for f in report.findings)


class TestSheetCheck(SheetTestCase):
    def test_a_correctly_filled_sheet_passes(self):
        report = sheet_mod.check(_sheet(self.tmp), catalog=vol.Catalog())
        self.assertTrue(report.ok, self._messages(report))
        self.assertEqual(report.exercises_found, 3)

    def test_unfilled_placeholder_is_an_error(self):
        path = _sheet(self.tmp)
        path.write_text(path.read_text(encoding="utf-8").replace("John Coach", TRAINER_KEY),
                        encoding="utf-8")
        report = sheet_mod.check(path)
        self.assertFalse(report.ok)
        self.assertIn(TRAINER_KEY, self._messages(report))

    def test_template_comment_markers_are_not_flagged(self):
        report = sheet_mod.check(_sheet(self.tmp))
        # {{RULES}} and friends live in comments and are meant to stay
        for marker in ("{{RULES}}", "{{TARGETS}}", "{{DAYS}}", "{{REGRAS}}", "{{METAS}}", "{{DIAS}}"):
            self.assertNotIn(marker, self._messages(report))

    def test_leftover_example_program_is_an_error(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for k, v in FILLED.items():
            text = text.replace(k, v)
        path = self.tmp / "sheet.html"
        path.write_text(text, encoding="utf-8")
        report = sheet_mod.check(path)
        self.assertFalse(report.ok)
        self.assertIn("example program is still there", self._messages(report))

    def test_bodyweight_exercise_without_the_flag_warns(self):
        bad = REAL_PROGRAM.replace('{ n: "Pull-up", s: 4, r: "max", rir: "1-2", t: "hold", f: "pc"',
                                   '{ n: "Pull-up", s: 4, r: "max", rir: "1-2", t: "hold"')
        report = sheet_mod.check(_sheet(self.tmp, program=bad))
        self.assertIn("ask the client for a load", self._messages(report))

    def test_isometric_without_the_tempo_flag_warns(self):
        bad = REAL_PROGRAM.replace('{ n: "Plank", s: 3, r: "45-60 s", rir: "", t: "", f: "tempo"',
                                   '{ n: "Plank", s: 3, r: "45-60 s", rir: "", t: ""')
        report = sheet_mod.check(_sheet(self.tmp, program=bad))
        self.assertIn("ask for repetitions", self._messages(report))

    def test_start_date_that_is_not_a_monday_warns(self):
        report = sheet_mod.check(_sheet(self.tmp, **{START_KEY: "2026-09-02"}))
        self.assertIn("not a Monday", self._messages(report))

    def test_sheet_missing_an_exercise_from_the_program(self):
        program = [{"exercises": [{"name": "Barbell bench press", "sets": 4},
                                  {"name": "Pull-up", "sets": 4},
                                  {"name": "Plank", "sets": 3},
                                  {"name": "Romanian deadlift", "sets": 3}]}]
        report = sheet_mod.check(_sheet(self.tmp), program=program)
        self.assertFalse(report.ok)
        self.assertIn("romanian deadlift", self._messages(report).lower())

    def test_set_count_mismatch_against_the_program(self):
        program = [{"exercises": [{"name": "Barbell bench press", "sets": 5},
                                  {"name": "Pull-up", "sets": 4},
                                  {"name": "Plank", "sets": 3}]}]
        report = sheet_mod.check(_sheet(self.tmp), program=program)
        self.assertIn("program says 5 sets, sheet says 4", self._messages(report))

    def test_missing_file_refuses(self):
        with self.assertRaises(m.InsufficientData):
            sheet_mod.check(self.tmp / "nope.html")


class TestLocalCatalog(SheetTestCase):
    def _write(self, doc) -> Path:
        p = self.tmp / "exercises.json"
        p.write_text(json.dumps(doc), encoding="utf-8")
        return p

    def test_adds_an_exercise_the_package_does_not_have(self):
        path = self._write({"exercises": [{
            "id": "belt_squat", "name": "Belt squat", "pattern": "knee_dominant",
            "equipment": ["machine"], "primary": ["quads"], "secondary": ["glutes"]}]})
        cat = vol.Catalog(extra=path)
        self.assertEqual(cat.find("belt squat")["id"], "belt_squat")
        self.assertEqual(cat.local_ids, ["belt_squat"])

    def test_overrides_a_bundled_entry(self):
        path = self._write({"exercises": [{
            "id": "bench_barbell", "name": "Barbell bench press (Smith machine)",
            "pattern": "horizontal_push", "equipment": ["machine"],
            "primary": ["chest"], "secondary": ["triceps"]}]})
        cat = vol.Catalog(extra=path)
        self.assertIn("Smith", cat.find("bench_barbell")["name"])
        self.assertEqual(cat.overridden_ids, ["bench_barbell"])

    def test_local_exercises_count_toward_volume(self):
        path = self._write({"exercises": [{
            "id": "belt_squat", "name": "Belt squat", "pattern": "knee_dominant",
            "equipment": ["machine"], "primary": ["quads"]}]})
        cat = vol.Catalog(extra=path)
        rows = {r.muscle: r for r in vol.weekly_volume(
            [{"exercises": [{"name": "Belt squat", "sets": 4}]}], cat)}
        self.assertEqual(rows["quads"].direct, 4)

    def test_invalid_pattern_is_refused_with_the_valid_list(self):
        path = self._write({"exercises": [{
            "id": "x", "name": "X", "pattern": "flying", "equipment": ["air"], "primary": ["chest"]}]})
        with self.assertRaises(m.InsufficientData) as ctx:
            vol.Catalog(extra=path)
        self.assertIn("knee_dominant", str(ctx.exception))

    def test_invalid_muscle_is_refused(self):
        path = self._write({"exercises": [{
            "id": "x", "name": "X", "pattern": "core", "equipment": ["bodyweight"],
            "primary": ["wings"]}]})
        with self.assertRaises(m.InsufficientData):
            vol.Catalog(extra=path)

    def test_entry_without_a_primary_muscle_is_refused(self):
        path = self._write({"exercises": [{
            "id": "x", "name": "X", "pattern": "core", "equipment": ["bodyweight"], "primary": []}]})
        with self.assertRaises(m.InsufficientData) as ctx:
            vol.Catalog(extra=path)
        self.assertIn("no primary muscle", str(ctx.exception))

    def test_malformed_json_says_so(self):
        p = self.tmp / "exercises.json"
        p.write_text("{not json", encoding="utf-8")
        with self.assertRaises(m.InsufficientData) as ctx:
            vol.Catalog(extra=p)
        self.assertIn("not valid JSON", str(ctx.exception))

    def test_missing_local_catalog_explains_the_format(self):
        with self.assertRaises(m.InsufficientData) as ctx:
            vol.Catalog(extra=self.tmp / "nope.json")
        self.assertIn("exercises", str(ctx.exception))

    def test_the_shipped_example_is_valid(self):
        example = SKILLS.parent / "examples" / "local-catalog-example.json"
        if not example.exists():
            self.skipTest("example catalog not present in this install")
        cat = vol.Catalog(extra=example)
        self.assertTrue(cat.local_ids)
        self.assertEqual(cat.find("belt squat")["name"], "Belt squat")


class TestNameResolution(unittest.TestCase):
    def setUp(self):
        self.cat = vol.Catalog()

    def test_word_overlap_resolves_a_shortened_name(self):
        # a trainer writes this; the catalog says "One-arm supported dumbbell row"
        self.assertEqual(self.cat.find("one-arm dumbbell row")["id"], "row_dumbbell")

    def test_substring_still_works(self):
        self.assertEqual(self.cat.find("goblet")["id"], "squat_goblet")

    def test_ambiguity_still_refuses(self):
        with self.assertRaises(m.InsufficientData) as ctx:
            self.cat.find("curl")
        self.assertIn("matches", str(ctx.exception))

    def test_unknown_points_at_the_local_catalog(self):
        with self.assertRaises(m.InsufficientData) as ctx:
            self.cat.find("kettlebell juggling")
        self.assertIn("local catalog", str(ctx.exception))


class TestTranslationParity(unittest.TestCase):
    """The two language versions must not drift apart in structure."""

    PAIRS = [("01-principles", "01-principios"), ("02-intake-screening", "02-anamnese-triagem"),
             ("03-program-design", "03-prescricao-treino"),
             ("04-progression-adjustment", "04-progressao-e-ajuste"),
             ("05-nutrition", "05-nutricao"), ("06-body-assessment", "06-avaliacao-corporal"),
             ("07-cardio", "07-cardio"), ("08-deliverables", "08-entregaveis")]

    def setUp(self):
        """Locate both skills explicitly, never relative to whichever copy runs."""
        self.en_root = SKILLS / "fitcoach-pro"
        self.pt_root = SKILLS / "fitcoach-pro-pt-BR"
        if not (self.en_root.exists() and self.pt_root.exists()):
            self.skipTest("only one language version is installed; parity cannot be checked")
        self.en = self.en_root / "references"
        self.pt = self.pt_root / "references"

    def test_both_versions_have_the_same_files(self):
        self.assertEqual(len(list(self.en.glob("*.md"))), len(list(self.pt.glob("*.md"))))

    def test_section_counts_match(self):
        for en_name, pt_name in self.PAIRS:
            with self.subTest(file=en_name):
                a = (self.en / (en_name + ".md")).read_text(encoding="utf-8")
                b = (self.pt / (pt_name + ".md")).read_text(encoding="utf-8")
                self.assertEqual(len(re.findall(r"^## ", a, re.M)),
                                 len(re.findall(r"^## ", b, re.M)),
                                 "%s and %s have a different number of sections — one was "
                                 "edited without the other" % (en_name, pt_name))

    def test_tools_are_identical_copies(self):
        for f in sorted((self.en_root / "tools").glob("*.py")):
            with self.subTest(file=f.name):
                twin = self.pt_root / "tools" / f.name
                self.assertTrue(twin.exists(), "%s missing from the pt-BR skill" % f.name)
                self.assertEqual(f.read_bytes(), twin.read_bytes(),
                                 "%s differs — run ./build.sh" % f.name)

    def test_both_skills_declare_the_three_hard_rules(self):
        en = (self.en_root / "SKILL.md").read_text(encoding="utf-8")
        pt = (self.pt_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Never do mental math", en)
        self.assertIn("Nunca faça conta de cabeça", pt)


if __name__ == "__main__":
    unittest.main()
