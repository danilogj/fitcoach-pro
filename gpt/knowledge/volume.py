"""Weekly volume accounting and exercise selection.

Counting sets by hand is where the assistant silently gets it wrong. This does
the arithmetic and checks it against per-muscle landmarks.

Standard library only.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from metrics import InsufficientData

DATA = Path(__file__).resolve().parent.parent / "data" / "exercises.json"

# Weekly hard sets per muscle: minimum effective, adaptive range, maximum
# recoverable. Ranges from the training-volume literature — they are population
# averages with wide individual variation, not personal prescriptions.
LANDMARKS: Dict[str, Dict[str, int]] = {
    "chest":      {"mev": 8,  "mav_low": 12, "mav_high": 18, "mrv": 22},
    "back":       {"mev": 10, "mav_low": 14, "mav_high": 20, "mrv": 25},
    "front_delt": {"mev": 0,  "mav_low": 6,  "mav_high": 12, "mrv": 16},
    "side_delt":  {"mev": 8,  "mav_low": 12, "mav_high": 20, "mrv": 26},
    "rear_delt":  {"mev": 6,  "mav_low": 10, "mav_high": 18, "mrv": 24},
    "traps":      {"mev": 0,  "mav_low": 6,  "mav_high": 14, "mrv": 20},
    "biceps":     {"mev": 6,  "mav_low": 10, "mav_high": 16, "mrv": 20},
    "triceps":    {"mev": 6,  "mav_low": 10, "mav_high": 16, "mrv": 20},
    "forearms":   {"mev": 0,  "mav_low": 4,  "mav_high": 10, "mrv": 15},
    "quads":      {"mev": 8,  "mav_low": 12, "mav_high": 18, "mrv": 22},
    "hamstrings": {"mev": 6,  "mav_low": 10, "mav_high": 16, "mrv": 20},
    "glutes":     {"mev": 4,  "mav_low": 8,  "mav_high": 14, "mrv": 18},
    "calves":     {"mev": 6,  "mav_low": 8,  "mav_high": 16, "mrv": 20},
    "core":       {"mev": 0,  "mav_low": 6,  "mav_high": 12, "mrv": 18},
}

# Beginners need less to grow and recover from less.
PROFILE_SCALE = {
    "beginner": 0.7,
    "detrained_intermediate": 0.75,
    "intermediate": 1.0,
    "advanced": 1.15,
}


@dataclass(frozen=True)
class MuscleVolume:
    muscle: str
    direct: float
    indirect: float
    verdict: str
    note: str

    def as_dict(self) -> dict:
        return asdict(self)


class Catalog:
    """The bundled exercise catalog, optionally extended by a local one.

    No packaged list survives contact with a real gym: machines vary by brand,
    trainers have their own variations, and a client's shoulder may need a grip
    nobody catalogued. A local file adds or overrides entries without touching
    the package, so an update never wipes the trainer's additions.
    """

    def __init__(self, path: Optional[Path] = None, extra: Optional[Path] = None):
        self.path = Path(path) if path else DATA
        if not self.path.exists():
            raise InsufficientData("exercise catalog not found at %s" % self.path)
        doc = json.loads(self.path.read_text(encoding="utf-8"))
        self.exercises = {e["id"]: e for e in doc["exercises"]}
        self.substitutions = dict(doc.get("substitutions", {}))
        self.muscles = doc["muscles"]
        self.patterns = doc["patterns"]
        self.local_ids: List[str] = []
        self.overridden_ids: List[str] = []

        if extra:
            self._merge(Path(extra))

        self.by_name = {e["name"].lower(): e for e in self.exercises.values()}

    def _merge(self, path: Path) -> None:
        """Add or override entries from a trainer- or gym-specific catalog."""
        if not path.exists():
            raise InsufficientData(
                "local catalog not found at %s. Create it as {\"exercises\": [...]} using "
                "the same fields as data/exercises.json." % path)
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InsufficientData("local catalog %s is not valid JSON: %s" % (path.name, exc))

        for raw in doc.get("exercises", []):
            entry = self._validate(raw, path.name)
            if entry["id"] in self.exercises:
                self.overridden_ids.append(entry["id"])
            else:
                self.local_ids.append(entry["id"])
            self.exercises[entry["id"]] = entry

        for reason, table in doc.get("substitutions", {}).items():
            merged = dict(self.substitutions.get(reason, {}))
            merged.update(table)
            self.substitutions[reason] = merged

    def _validate(self, raw: dict, source: str) -> dict:
        """A local entry gets the same scrutiny as a bundled one."""
        for field in ("id", "name", "pattern", "equipment", "primary"):
            if field not in raw:
                raise InsufficientData(
                    "%s: exercise %r is missing %r. Required fields: id, name, pattern, "
                    "equipment, primary." % (source, raw.get("name", raw.get("id", "?")), field))
        if raw["pattern"] not in self.patterns:
            raise InsufficientData(
                "%s: exercise %r has pattern %r, which is not one of: %s"
                % (source, raw["name"], raw["pattern"], ", ".join(self.patterns)))
        for group in list(raw["primary"]) + list(raw.get("secondary", [])):
            if group not in self.muscles:
                raise InsufficientData(
                    "%s: exercise %r lists muscle %r, which is not one of: %s"
                    % (source, raw["name"], group, ", ".join(self.muscles)))
        if not raw["primary"]:
            raise InsufficientData(
                "%s: exercise %r has no primary muscle — it would count toward no volume "
                "at all." % (source, raw["name"]))
        return raw

    def find(self, key: str) -> dict:
        """Resolve an exercise by id, exact name, substring, or word overlap.

        Trainers write "one-arm dumbbell row" for what the catalog calls
        "One-arm supported dumbbell row". Requiring a contiguous substring
        would reject it and silently drop those sets from the volume audit, so
        an all-words-present match is tried before giving up.
        """
        k = (key or "").strip().lower()
        if not k:
            raise InsufficientData("no exercise name given")
        if k in self.exercises:
            return self.exercises[k]
        if k in self.by_name:
            return self.by_name[k]

        matches = [e for n, e in self.by_name.items() if k in n]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            words = [w for w in re.split(r"[^a-z0-9]+", k) if len(w) > 2]
            if words:
                matches = [e for n, e in self.by_name.items()
                           if all(w in n for w in words)]
                if len(matches) == 1:
                    return matches[0]

        if not matches:
            raise InsufficientData(
                "exercise %r is not in the catalog. Add it to a local catalog "
                "(clients/<name>/exercises.json) with its primary and secondary muscles, "
                "or use a catalog name." % key
            )
        raise InsufficientData(
            "%r matches %d exercises: %s" % (key, len(matches), ", ".join(m["name"] for m in matches[:6]))
        )

    def filter(self, pattern: Optional[str] = None,
               equipment: Optional[Sequence[str]] = None) -> List[dict]:
        """Exercises in a pattern that the available equipment can perform."""
        have = {e.strip().lower() for e in (equipment or [])}
        out = []
        for ex in self.exercises.values():
            if pattern and ex["pattern"] != pattern:
                continue
            if have and not set(ex["equipment"]).issubset(have):
                continue
            out.append(ex)
        return sorted(out, key=lambda e: e["name"])

    def substitute(self, exercise_key: str, reason: str) -> List[dict]:
        """Swaps inside the same movement pattern for a given limitation."""
        ex = self.find(exercise_key)
        reason = reason.strip().lower()
        table = self.substitutions.get(reason)
        if table is None:
            raise InsufficientData(
                "no substitution table for %r; known reasons: %s"
                % (reason, ", ".join(sorted(self.substitutions)))
            )
        ids = table.get(ex["id"])
        if not ids:
            same = [c for c in self.filter(pattern=ex["pattern"]) if c["id"] != ex["id"]]
            if not same:
                raise InsufficientData("no substitute found for %s" % ex["name"])
            return same
        return [self.exercises[i] for i in ids]


def weekly_volume(program: Sequence[dict], catalog: Optional[Catalog] = None,
                  profile: str = "intermediate") -> List[MuscleVolume]:
    """Sum hard sets per muscle across a week and judge each against landmarks.

    `program` is a list of sessions: [{"exercises": [{"name": ..., "sets": N}]}]
    Direct sets come from primary muscles. Secondary muscles are reported in a
    separate column at half weight — a reporting convention, not physiology.
    """
    cat = catalog or Catalog()
    key = profile.strip().lower().replace(" ", "_").replace("-", "_")
    if key not in PROFILE_SCALE:
        raise InsufficientData(
            "unknown profile %r; use one of %s" % (profile, ", ".join(sorted(PROFILE_SCALE)))
        )
    scale = PROFILE_SCALE[key]

    direct: Dict[str, float] = {m: 0.0 for m in LANDMARKS}
    indirect: Dict[str, float] = {m: 0.0 for m in LANDMARKS}

    for session in program:
        for item in session.get("exercises", []):
            ex = cat.find(item.get("name") or item.get("id", ""))
            sets = item.get("sets")
            if sets is None:
                raise InsufficientData("exercise %r has no set count" % ex["name"])
            if not isinstance(sets, (int, float)) or sets <= 0:
                raise InsufficientData("exercise %r: sets must be a positive number" % ex["name"])
            for muscle in ex["primary"]:
                direct[muscle] = direct.get(muscle, 0.0) + float(sets)
            for muscle in ex.get("secondary", []):
                indirect[muscle] = indirect.get(muscle, 0.0) + float(sets) * 0.5

    out: List[MuscleVolume] = []
    for muscle in sorted(LANDMARKS):
        d = direct.get(muscle, 0.0)
        i = indirect.get(muscle, 0.0)
        verdict, note = _judge(muscle, d, scale)
        out.append(MuscleVolume(muscle, round(d, 1), round(i, 1), verdict, note))
    return out


def _judge(muscle: str, direct: float, scale: float) -> tuple:
    lm = LANDMARKS[muscle]
    mev = lm["mev"] * scale
    mav_low = lm["mav_low"] * scale
    mav_high = lm["mav_high"] * scale
    mrv = lm["mrv"] * scale

    if direct == 0 and lm["mev"] == 0:
        return "ok", "no direct work needed; covered indirectly"
    if direct < mev:
        return "below_mev", ("%.0f direct sets is under the ~%.0f minimum effective volume — "
                             "maintenance at best" % (direct, mev))
    if direct < mav_low:
        return "low", ("%.0f sets works and leaves room to grow — the intended starting point "
                       "for a new block" % direct)
    if direct <= mav_high:
        return "productive", "%.0f sets is inside the adaptive range" % direct
    if direct <= mrv:
        return "high", ("%.0f sets is near the maximum recoverable volume; only justified with "
                        "sleep, food and adherence in place" % direct)
    return "above_mrv", ("%.0f sets exceeds the ~%.0f maximum recoverable volume — this is where "
                         "the block breaks" % (direct, mrv))


def check_coverage(program: Sequence[dict], catalog: Optional[Catalog] = None) -> Dict[str, List[str]]:
    """Which movement patterns the week covers, and which are missing."""
    cat = catalog or Catalog()
    seen = set()
    for session in program:
        for item in session.get("exercises", []):
            seen.add(cat.find(item.get("name") or item.get("id", ""))["pattern"])
    essential = ["horizontal_push", "vertical_push", "horizontal_pull", "vertical_pull",
                 "knee_dominant", "hip_dominant"]
    return {"covered": sorted(seen), "missing": [p for p in essential if p not in seen]}
