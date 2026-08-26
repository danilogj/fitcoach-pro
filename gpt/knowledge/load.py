"""Training load monitoring: acute:chronic workload and deload triggers.

Borrowed from endurance sport, where load management is quantified rather than
guessed. Adapted to resistance training by counting hard sets per day.

Standard library only.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Dict, List, Optional, Sequence

from metrics import InsufficientData

# How much systemic cost a set carries, relative to a supported compound.
# Four sets of heavy deadlift and four sets of lateral raise are not the same
# week of training, and counting them equally lets axial fatigue accumulate
# without the ratio ever flagging it.
FATIGUE_WEIGHTS = {
    "axial_compound": 1.4,      # bar on the back or in the hands: squat, deadlift, RDL
    "compound": 1.0,            # supported or machine-based multi-joint work
    "unilateral": 0.8,          # meaningful load, half the systemic cost per set
    "isolation": 0.5,           # curls, raises, extensions
    "core": 0.4,
}

_PATTERN_CLASS = {
    "horizontal_push": "compound", "vertical_push": "compound",
    "horizontal_pull": "compound", "vertical_pull": "compound",
    "knee_dominant": "compound", "hip_dominant": "compound",
    "unilateral_lower": "unilateral", "calf": "isolation",
    "isolation_shoulder": "isolation", "isolation_arm": "isolation",
    "core": "core",
}


def fatigue_weight(exercise: Optional[dict]) -> float:
    """Systemic cost multiplier for one set of a given exercise.

    Unknown exercises weigh 1.0 — the neutral assumption, not zero, so an
    uncatalogued lift is never invisible to load monitoring.
    """
    if not exercise:
        return FATIGUE_WEIGHTS["compound"]
    if exercise.get("axial"):
        return FATIGUE_WEIGHTS["axial_compound"]
    klass = _PATTERN_CLASS.get(exercise.get("pattern"), "compound")
    return FATIGUE_WEIGHTS[klass]


@dataclass(frozen=True)
class Acwr:
    ratio: Optional[float]
    acute_per_day: float
    chronic_per_day: float
    acute_days: int
    chronic_days: int
    verdict: str
    note: str

    def as_dict(self) -> dict:
        return asdict(self)


def acwr(load_by_day: Dict[date, float], reference: Optional[date] = None,
         acute_days: int = 7, chronic_days: int = 28,
         min_chronic_days: int = 21) -> Acwr:
    """Acute (7-day) load against chronic (28-day) load.

    Refuses before there is enough history: with two weeks of data the ratio is
    arithmetic without information. Below 0.8 is undertraining, 0.8-1.3 is the
    productive band, above 1.5 is where load-related injury clusters.
    """
    if not load_by_day:
        raise InsufficientData("no training sessions logged")
    end = reference or max(load_by_day)
    first = min(load_by_day)
    history = (end - first).days + 1
    if history < min_chronic_days:
        raise InsufficientData(
            "only %d days of training history; ACWR needs at least %d. Until then judge "
            "load by the check-in table, not by a ratio." % (history, min_chronic_days)
        )

    acute = _mean_daily(load_by_day, end, acute_days)
    chronic = _mean_daily(load_by_day, end, chronic_days)
    if chronic <= 0:
        raise InsufficientData("chronic load is zero; nothing to compare against")

    ratio = acute / chronic
    verdict, note = _classify(ratio)
    return Acwr(round(ratio, 2), round(acute, 2), round(chronic, 2),
                acute_days, chronic_days, verdict, note)


def _mean_daily(load_by_day: Dict[date, float], end: date, window: int) -> float:
    start = end - timedelta(days=window - 1)
    total = sum(v for d, v in load_by_day.items() if start <= d <= end)
    return total / float(window)


def _classify(ratio: float) -> tuple:
    if ratio < 0.8:
        return "undertrained", ("acute load is well below the recent norm — a missed week, not "
                                "a recovery problem. Resume at the previous week's volume.")
    if ratio <= 1.3:
        return "productive", "load is where progressive overload happens"
    if ratio <= 1.5:
        return "watch", ("load climbed faster than the body adapted; hold volume flat for a week "
                         "before adding more")
    return "spike", ("acute load is far above the chronic norm — this is the pattern that "
                     "precedes injury. Cut back this week.")


@dataclass(frozen=True)
class DeloadCheck:
    should_deload: bool
    signals: List[str]
    note: str

    def as_dict(self) -> dict:
        return asdict(self)


def deload_check(*, weeks_since_deload: Optional[int] = None,
                 performance_dropping_weeks: int = 0,
                 sleep_hours_avg: Optional[float] = None,
                 soreness_avg: Optional[float] = None,
                 readiness_avg: Optional[float] = None,
                 acwr_verdict: Optional[str] = None,
                 appetite_down: bool = False,
                 motivation_down: bool = False,
                 joint_pain: bool = False) -> DeloadCheck:
    """Two or more independent signals trigger a deload.

    One signal is a bad week. Two are a pattern. Only pass values that were
    actually measured — absent inputs never count as signals.
    """
    signals: List[str] = []

    if performance_dropping_weeks >= 2:
        signals.append("performance down %d weeks running on the same exercises" % performance_dropping_weeks)
    if sleep_hours_avg is not None and sleep_hours_avg < 6.5:
        signals.append("sleep averaging %.1f h" % sleep_hours_avg)
    if soreness_avg is not None and soreness_avg >= 4:
        signals.append("soreness averaging %.1f/5" % soreness_avg)
    if readiness_avg is not None and readiness_avg < 40:
        signals.append("wearable readiness averaging %.0f/100" % readiness_avg)
    if acwr_verdict in ("watch", "spike"):
        signals.append("acute:chronic load flagged %s" % acwr_verdict)
    if joint_pain:
        signals.append("persistent joint pain that does not clear with the warm-up")
    if appetite_down:
        signals.append("appetite falling during a surplus")
    if motivation_down:
        signals.append("consistent loss of desire to train")

    scheduled = weeks_since_deload is not None and weeks_since_deload >= 8

    if len(signals) >= 2:
        return DeloadCheck(True, signals,
                           "two or more independent signals — pull the deload forward: sets to "
                           "~60%, load held, RIR 3-4")
    if scheduled:
        return DeloadCheck(True, signals + ["%d weeks since the last deload" % weeks_since_deload],
                           "scheduled deload is due even without warning signs")
    if len(signals) == 1:
        return DeloadCheck(False, signals,
                           "one signal is a bad week, not a pattern. Recheck next week before cutting volume")
    return DeloadCheck(False, [], "no deload indicated; keep progressing")


def session_load(exercises: Sequence[dict], mode: str = "weighted",
                 catalog=None) -> float:
    """Load for one session.

    "weighted" (the default) counts sets scaled by systemic cost, so a session
    of heavy squats and deadlifts outweighs the same set count of arm work.
    "sets" counts them flat, and "tonnage" multiplies load by reps.
    """
    if mode == "sets":
        return float(sum(len(e.get("sets", [])) for e in exercises))

    if mode == "tonnage":
        total = 0.0
        for exercise in exercises:
            for item in exercise.get("sets", []):
                load = item.get("load_kg")
                reps = item.get("reps")
                if load and reps:
                    total += float(load) * float(reps)
        return total

    if mode == "weighted":
        total = 0.0
        for exercise in exercises:
            entry = None
            if catalog is not None and exercise.get("name"):
                try:
                    entry = catalog.find(exercise["name"])
                except Exception:
                    entry = None      # uncatalogued lifts fall back to neutral weight
            total += len(exercise.get("sets", [])) * fatigue_weight(entry)
        return round(total, 2)

    raise InsufficientData("mode must be 'weighted', 'sets' or 'tonnage'")
