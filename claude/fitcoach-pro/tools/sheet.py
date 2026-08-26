"""Validate a filled-in client sheet before it reaches anyone.

The sheet is a template with {{PLACEHOLDERS}}. A model filling it in can miss
one, leave the bundled example program in place, or put a load field on a
bodyweight exercise. All three reach the client looking finished.

This checks the rendered file against the program it is supposed to render.

Standard library only.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from metrics import InsufficientData
import volume as vol

# Placeholders that live inside template comments and are meant to stay:
# they mark a block the trainer edits by hand, not a value to substitute.
COMMENT_MARKERS = {"PROGRAM", "PROGRAMA", "DAYS", "DIAS", "RULES", "REGRAS",
                   "TARGETS", "METAS", "EXPORT_HEADER", "CABECALHO_EXPORT"}

EXAMPLE_MARKERS = ("The example below exists only so the page opens",
                   "O exemplo abaixo existe só para a página abrir")


@dataclass
class Finding:
    level: str      # "error" | "warning"
    message: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class SheetReport:
    path: str
    findings: List[Finding]
    exercises_found: int

    @property
    def errors(self) -> List[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {"path": self.path, "ok": self.ok, "exercises": self.exercises_found,
                "findings": [f.as_dict() for f in self.findings]}

    def summary(self) -> str:
        if not self.findings:
            return "sheet looks ready: %d exercises, no placeholders left, no field mismatches" % self.exercises_found
        lines = []
        for f in self.findings:
            lines.append("%-8s %s" % (f.level.upper(), f.message))
        lines.append("")
        lines.append("%d error(s), %d warning(s)%s"
                     % (len(self.errors), len(self.findings) - len(self.errors),
                        "" if self.errors else " — safe to hand over"))
        return "\n".join(lines)


def check(path: Path, program: Optional[Sequence[dict]] = None,
          catalog: Optional[vol.Catalog] = None) -> SheetReport:
    if not path.exists():
        raise InsufficientData("no such sheet: %s" % path)
    html = path.read_text(encoding="utf-8", errors="replace")
    findings: List[Finding] = []

    # 1. placeholders that should have been substituted
    left = set(re.findall(r"\{\{([A-Z_]+)\}\}", html)) - COMMENT_MARKERS
    for name in sorted(left):
        findings.append(Finding("error",
            "{{%s}} was never filled in — it will show literally on the client's screen" % name))

    # 2. the bundled example program still in place
    if any(marker in html for marker in EXAMPLE_MARKERS):
        findings.append(Finding("error",
            "the template's example program is still there; the sessions were never replaced"))

    # 3. read the program embedded in the page
    exercises = _extract_exercises(html)
    if not exercises:
        findings.append(Finding("error",
            "could not read any exercise from the page — the PROGRAM array is missing or malformed"))
    else:
        findings.extend(_check_fields(exercises, catalog))

    # 4. the start date should be a Monday
    start = re.search(r'var START = "(\d{4}-\d{2}-\d{2})"', html) or \
            re.search(r'var INICIO = "(\d{4}-\d{2}-\d{2})"', html)
    if start:
        from datetime import date
        y, m, d = (int(x) for x in start.group(1).split("-"))
        try:
            if date(y, m, d).weekday() != 0:
                findings.append(Finding("warning",
                    "block starts on %s, which is not a Monday — week numbering will look off"
                    % start.group(1)))
        except ValueError:
            findings.append(Finding("error", "start date %s is not a real date" % start.group(1)))

    # 5. the trainer must be identifiable on the client's document
    if "{{TRAINER}}" in html or "{{PROFISSIONAL}}" in html:
        pass  # already reported above
    elif not re.search(r"(prescribed and reviewed by|prescrito e revisado por)", html):
        findings.append(Finding("warning",
            "the footer no longer names the responsible trainer — put it back"))

    # 6. does the page match the program it should render?
    if program:
        findings.extend(_compare_to_program(exercises, program))

    return SheetReport(str(path), findings, len(exercises))


def _extract_exercises(html: str) -> List[dict]:
    """Pull name/sets/flags out of the PROGRAM array without executing JS."""
    block = re.search(r"var (?:PROGRAM|PROGRAMA) = \[(.*?)\n  \];", html, re.S)
    if not block:
        return []
    out: List[dict] = []
    for raw in re.finditer(r"\{\s*n:\s*\"((?:[^\"\\]|\\.)*)\"(.*?)\}", block.group(1), re.S):
        name, rest = raw.group(1), raw.group(2)
        item: Dict[str, object] = {"name": name}
        sets = re.search(r"\bs:\s*(\d+)", rest)
        if sets:
            item["sets"] = int(sets.group(1))
        flag = re.search(r'\bf:\s*"(\w+)"', rest)
        if flag:
            item["f"] = flag.group(1)
        reps = re.search(r'\br:\s*"((?:[^"\\]|\\.)*)"', rest)
        if reps:
            item["reps"] = reps.group(1)
        rir = re.search(r'\brir:\s*"((?:[^"\\]|\\.)*)"', rest)
        item["rir"] = rir.group(1) if rir else ""
        out.append(item)
    return out


def _check_fields(exercises: Sequence[dict], catalog: Optional[vol.Catalog]) -> List[Finding]:
    findings: List[Finding] = []
    for ex in exercises:
        name = ex["name"]
        if "sets" not in ex:
            findings.append(Finding("error", "%s has no set count" % name))
        elif not 1 <= int(ex["sets"]) <= 10:
            findings.append(Finding("warning",
                "%s is prescribed %s sets — check that this is deliberate" % (name, ex["sets"])))

        flag = ex.get("f")
        reps = str(ex.get("reps", ""))
        # a bodyweight exercise showing a load field is the error clients report first
        looks_bodyweight = re.search(r"(pull-?up|chin-?up|push-?up|plank|dip|hanging|"
                                     r"barra fixa|prancha|flex[aã]o|abdominal)", name, re.I)
        if looks_bodyweight and flag not in ("pc", "tempo"):
            findings.append(Finding("warning",
                "%s looks like a bodyweight exercise but has no f:\"pc\" flag — the sheet will "
                "ask the client for a load" % name))
        if re.search(r"\d+\s*s\b", reps) and flag != "tempo":
            findings.append(Finding("warning",
                "%s is prescribed in seconds but is not flagged f:\"tempo\" — the sheet will "
                "ask for repetitions" % name))
        if flag == "tempo" and ex.get("rir"):
            findings.append(Finding("warning",
                "%s is an isometric hold with an RIR target, which does not apply" % name))

    if catalog:
        for ex in exercises:
            try:
                catalog.find(ex["name"])
            except InsufficientData:
                findings.append(Finding("warning",
                    "%s is not in the exercise catalog, so it will not be counted in the volume "
                    "audit. Add it to a local catalog if the gym has it." % ex["name"]))
    return findings


def _compare_to_program(sheet: Sequence[dict], program: Sequence[dict]) -> List[Finding]:
    """The sheet is a rendering of program.md. Divergence means one is stale."""
    findings: List[Finding] = []
    planned: Dict[str, int] = {}
    for session in program:
        for item in session.get("exercises", []):
            key = str(item.get("name", "")).strip().lower()
            if key:
                planned[key] = planned.get(key, 0) + int(item.get("sets", 0) or 0)

    rendered: Dict[str, int] = {}
    for ex in sheet:
        key = str(ex["name"]).strip().lower()
        rendered[key] = rendered.get(key, 0) + int(ex.get("sets", 0) or 0)

    for name in sorted(set(planned) - set(rendered)):
        findings.append(Finding("error",
            "the program prescribes %r but the sheet does not include it" % name))
    for name in sorted(set(rendered) - set(planned)):
        findings.append(Finding("error",
            "the sheet includes %r, which is not in the program" % name))
    for name in sorted(set(planned) & set(rendered)):
        if planned[name] != rendered[name]:
            findings.append(Finding("warning",
                "%r: program says %d sets, sheet says %d" % (name, planned[name], rendered[name])))
    return findings
