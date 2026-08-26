"""Append-only event log for FitCoach Pro.

One JSON object per line. The log is never rewritten: corrections are appended
and the newest event for a given key wins. That way a client's history cannot
be silently destroyed by an edit.

Standard library only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from metrics import InsufficientData


class ValidationError(Exception):
    """The event does not satisfy the schema. Nothing is written."""


# field -> (python type, minimum, maximum). None bound means unbounded.
_NUM = (float, int)

SCHEMA: Dict[str, Dict[str, Any]] = {
    "weight": {
        "required": {"kg": (_NUM, 25.0, 400.0)},
        "optional": {"source": (str, None, None)},
        "granularity": "day",
    },
    "measurement": {
        "required": {},
        "optional": {
            "waist_cm": (_NUM, 40.0, 200.0),
            "hip_cm": (_NUM, 50.0, 200.0),
            "arm_cm": (_NUM, 15.0, 70.0),
            "thigh_cm": (_NUM, 25.0, 100.0),
            "chest_cm": (_NUM, 50.0, 200.0),
            "calf_cm": (_NUM, 20.0, 70.0),
        },
        "granularity": "day",
        "at_least_one": True,
    },
    "body_comp": {
        "required": {"weight_kg": (_NUM, 25.0, 400.0)},
        "optional": {
            "fat_mass_kg": (_NUM, 1.0, 200.0),
            "ffm_kg": (_NUM, 10.0, 200.0),
            "method": (str, None, None),
            "protocol_ok": (bool, None, None),
        },
        "granularity": "day",
    },
    "session": {
        "required": {"session_id": (str, None, None)},
        "optional": {
            "exercises": (list, None, None),
            "duration_min": (_NUM, 5.0, 300.0),
            "week": (int, 1, 52),
            "notes": (str, None, None),
        },
        "granularity": "timestamp",
    },
    "meal": {
        "required": {"kcal": (_NUM, 0.0, 10000.0)},
        "optional": {
            "protein_g": (_NUM, 0.0, 500.0),
            "carb_g": (_NUM, 0.0, 1500.0),
            "fat_g": (_NUM, 0.0, 500.0),
            "estimated": (bool, None, None),
            "notes": (str, None, None),
        },
        "granularity": "timestamp",
    },
    "sleep": {
        "required": {"hours": (_NUM, 0.0, 24.0)},
        "optional": {"quality": (int, 1, 5), "score": (int, 0, 100), "source": (str, None, None)},
        "granularity": "day",
    },
    "steps": {
        "required": {"count": (int, 0, 200000)},
        "optional": {"source": (str, None, None)},
        "granularity": "day",
    },
    "recovery": {
        "required": {},
        "optional": {
            "soreness": (int, 1, 5),
            "stress": (int, 1, 5),
            "readiness": (int, 0, 100),
            "hrv_ms": (_NUM, 5.0, 300.0),
            "rhr_bpm": (_NUM, 25.0, 140.0),
            "source": (str, None, None),
            "notes": (str, None, None),
        },
        "granularity": "day",
        "at_least_one": True,
    },
    "note": {
        "required": {"text": (str, None, None)},
        "optional": {},
        "granularity": "timestamp",
    },
}


@dataclass(frozen=True)
class Event:
    type: str
    ts: str
    data: Dict[str, Any]

    @property
    def day(self) -> date:
        return datetime.fromisoformat(self.ts).date()

    def to_json(self) -> str:
        payload = {"type": self.type, "ts": self.ts}
        payload.update(self.data)
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def validate(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Type, range and enum check. Raises rather than coercing."""
    if event_type not in SCHEMA:
        raise ValidationError(
            "unknown event type %r; known types: %s" % (event_type, ", ".join(sorted(SCHEMA)))
        )
    spec = SCHEMA[event_type]
    clean: Dict[str, Any] = {}

    for field, rule in spec["required"].items():
        if field not in data:
            raise ValidationError("%s events require %r" % (event_type, field))
        clean[field] = _check(event_type, field, data[field], rule)

    known = set(spec["required"]) | set(spec["optional"])
    for field, value in data.items():
        if field in spec["required"]:
            continue
        if field not in known:
            raise ValidationError(
                "%s has no field %r; allowed: %s" % (event_type, field, ", ".join(sorted(known)))
            )
        clean[field] = _check(event_type, field, value, spec["optional"][field])

    if spec.get("at_least_one") and not clean:
        raise ValidationError("%s events need at least one field" % event_type)

    if event_type == "session" and "exercises" in clean:
        clean["exercises"] = [_check_exercise(x) for x in clean["exercises"]]

    return clean


def _check(event_type: str, field: str, value: Any, rule: Tuple[Any, Any, Any]) -> Any:
    expected, lo, hi = rule
    if expected is bool:
        if not isinstance(value, bool):
            raise ValidationError("%s.%s must be true or false" % (event_type, field))
        return value
    if expected is int and isinstance(value, bool):
        raise ValidationError("%s.%s must be a number, not a boolean" % (event_type, field))
    if not isinstance(value, expected):
        name = getattr(expected, "__name__", "number")
        raise ValidationError("%s.%s must be %s, got %r" % (event_type, field, name, value))
    if lo is not None and value < lo:
        raise ValidationError("%s.%s = %r is below the plausible minimum %s" % (event_type, field, value, lo))
    if hi is not None and value > hi:
        raise ValidationError("%s.%s = %r is above the plausible maximum %s" % (event_type, field, value, hi))
    return value


def _check_exercise(item: Any) -> Dict[str, Any]:
    if not isinstance(item, dict) or "name" not in item:
        raise ValidationError("each exercise needs at least a name")
    sets = item.get("sets", [])
    if not isinstance(sets, list):
        raise ValidationError("exercise %r: sets must be a list" % item.get("name"))
    for s in sets:
        if not isinstance(s, dict):
            raise ValidationError("exercise %r: each set must be an object" % item["name"])
        for key, lo, hi in (("load_kg", 0.0, 1000.0), ("reps", 0, 200), ("rir", 0, 10)):
            if key in s and s[key] is not None:
                v = s[key]
                if isinstance(v, bool) or not isinstance(v, _NUM):
                    raise ValidationError("exercise %r: %s must be a number" % (item["name"], key))
                if not lo <= v <= hi:
                    raise ValidationError("exercise %r: %s = %r out of range" % (item["name"], key, v))
    return item


def append(path: Path, event_type: str, data: Dict[str, Any],
           ts: Optional[str] = None) -> Event:
    """Validate then append one event. Creates the file if needed."""
    clean = validate(event_type, data)
    stamp = ts or datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        datetime.fromisoformat(stamp)
    except ValueError as exc:
        raise ValidationError("ts must be ISO-8601: %s" % exc) from exc

    event = Event(event_type, stamp, clean)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(event.to_json() + "\n")
    return event


def read(path: Path, event_type: Optional[str] = None,
         since: Optional[date] = None, until: Optional[date] = None) -> List[Event]:
    """Read events, newest-wins deduplication applied."""
    if not path.exists():
        return []
    events: List[Event] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            etype = payload.pop("type")
            stamp = payload.pop("ts")
        except (json.JSONDecodeError, KeyError) as exc:
            raise ValidationError("log line %d is corrupt: %s" % (line_no, exc)) from exc
        events.append(Event(etype, stamp, payload))

    events = _dedup(events)
    if event_type:
        events = [e for e in events if e.type == event_type]
    if since:
        events = [e for e in events if e.day >= since]
    if until:
        events = [e for e in events if e.day <= until]
    return sorted(events, key=lambda e: e.ts)


def _dedup(events: Sequence[Event]) -> List[Event]:
    """Later events replace earlier ones with the same key.

    Day-granular types key on (type, day) so a re-import or a correction
    overwrites; timestamp-granular types key on (type, ts) so two sessions on
    the same day both survive.
    """
    keyed: Dict[Tuple[str, str], Event] = {}
    for event in events:
        gran = SCHEMA.get(event.type, {}).get("granularity", "timestamp")
        if gran == "day":
            key = (event.type, event.day.isoformat())
        else:
            key = (event.type, event.ts + json.dumps(event.data, sort_keys=True)[:64])
        keyed[key] = event
    return list(keyed.values())


def weights(path: Path, since: Optional[date] = None) -> List[Tuple[date, float]]:
    return [(e.day, float(e.data["kg"])) for e in read(path, "weight", since=since)]


def intake_by_day(path: Path, since: Optional[date] = None) -> Dict[date, float]:
    totals: Dict[date, float] = {}
    for event in read(path, "meal", since=since):
        totals[event.day] = totals.get(event.day, 0.0) + float(event.data["kcal"])
    return totals


def hard_sets_by_day(path: Path, since: Optional[date] = None) -> Dict[date, int]:
    """Sets actually performed per day — flat count, no fatigue weighting."""
    totals: Dict[date, int] = {}
    for event in read(path, "session", since=since):
        count = 0
        for exercise in event.data.get("exercises", []):
            count += len(exercise.get("sets", []))
        totals[event.day] = totals.get(event.day, 0) + count
    return totals


def weighted_load_by_day(path: Path, catalog=None,
                         since: Optional[date] = None) -> Dict[date, float]:
    """Daily training load with each set scaled by its systemic cost.

    This is the ACWR input: four sets of heavy deadlift cost more than four
    sets of lateral raise, and a flat count hides exactly the axial spike the
    ratio is supposed to catch.
    """
    import load as load_mod  # local import keeps the modules independent

    totals: Dict[date, float] = {}
    for event in read(path, "session", since=since):
        exercises = event.data.get("exercises", [])
        if exercises:
            value = load_mod.session_load(exercises, "weighted", catalog)
        else:
            # a logged cardio session with no sets still costs something
            minutes = float(event.data.get("duration_min") or 0)
            value = round(minutes / 12.0, 2) if minutes else 0.0
        totals[event.day] = round(totals.get(event.day, 0.0) + value, 2)
    return totals
