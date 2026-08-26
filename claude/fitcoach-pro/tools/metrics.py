"""Deterministic metrics for FitCoach Pro.

Every number the assistant reports must come from here. No mental math.

Standard library only, Python 3.9+.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

KCAL_PER_KG = 7700.0  # energy density of body mass change, a working convention

SEX_MALE = "male"
SEX_FEMALE = "female"

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# Floors below which we refuse to prescribe without clinical supervision.
KCAL_FLOOR = {SEX_MALE: 1500.0, SEX_FEMALE: 1200.0}


class InsufficientData(Exception):
    """Raised when the inputs cannot support an honest answer.

    Refusing is the point: a guessed number is worse than no number.
    """


@dataclass(frozen=True)
class BmrResult:
    mifflin: float
    katch: Optional[float]
    used: float
    method: str
    spread: Optional[float]
    bmi: Optional[float] = None
    warning: Optional[str] = None

    def as_dict(self) -> dict:
        return asdict(self)


def bmi(weight_kg: float, height_cm: float) -> float:
    if weight_kg <= 0 or height_cm <= 0:
        raise InsufficientData("weight and height must be positive")
    return round(weight_kg / (height_cm / 100.0) ** 2, 1)


def adjusted_weight(weight_kg: float, height_cm: float, sex: str,
                    factor: float = 0.4) -> float:
    """Adjusted body weight for high-adiposity cases.

    Mifflin-St Jeor takes total body weight, and adipose tissue is far less
    metabolically active than lean tissue. Above roughly BMI 30 that inflates
    the estimate by a few hundred kcal, which turns a prescribed deficit into
    maintenance and makes the first weeks look like a failure of adherence.

    Ideal weight by the Devine equation, plus 40% of the excess. This is a
    clinical convention, not a measurement — when body composition is known,
    Katch-McArdle beats it and should be used instead.
    """
    sex = _normalize_sex(sex)
    inches_over_5ft = max(0.0, (height_cm - 152.4) / 2.54)
    ideal = (50.0 if sex == SEX_MALE else 45.5) + 2.3 * inches_over_5ft
    if weight_kg <= ideal:
        return round(weight_kg, 1)
    return round(ideal + factor * (weight_kg - ideal), 1)


def bmr(weight_kg: float, height_cm: float, age: int, sex: str,
        fat_free_mass_kg: Optional[float] = None,
        use_adjusted_weight: bool = False) -> BmrResult:
    """Mifflin-St Jeor, plus Katch-McArdle when fat-free mass is known.

    When both are available the mean is used and the spread reported. A wide
    spread means the body-composition estimate is wrong, not the BMR.
    """
    sex = _normalize_sex(sex)
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        raise InsufficientData("weight, height and age must be positive")

    index = bmi(weight_kg, height_cm)
    mif_weight = weight_kg
    warning = None

    if use_adjusted_weight:
        mif_weight = adjusted_weight(weight_kg, height_cm, sex)
        warning = ("Mifflin computed on adjusted body weight %.1f kg instead of %.1f kg "
                   "(clinical convention for high adiposity, not a measurement)"
                   % (mif_weight, weight_kg))
    elif index >= 30 and fat_free_mass_kg is None:
        warning = ("BMI %.1f with no body-composition data: Mifflin uses total body weight and "
                   "overestimates expenditure by roughly 200-400 kcal at this adiposity. Measure "
                   "fat-free mass and let Katch-McArdle take over, or pass --adjusted-weight. "
                   "Either way, the weekly weight average settles it in three weeks." % index)

    mif = 10.0 * mif_weight + 6.25 * height_cm - 5.0 * age + (5.0 if sex == SEX_MALE else -161.0)

    if fat_free_mass_kg is None:
        return BmrResult(round(mif, 1), None, round(mif, 1), "mifflin", None, index, warning)

    if not 0 < fat_free_mass_kg < weight_kg:
        raise InsufficientData("fat-free mass must be positive and below body weight")

    katch = 370.0 + 21.6 * fat_free_mass_kg
    used = (mif + katch) / 2.0
    if index >= 30:
        # with real body composition, the equation built on lean mass is the better one
        used = katch
        warning = ("BMI %.1f: using Katch-McArdle alone. Mifflin takes total body weight and "
                   "overestimates at this adiposity." % index)
    return BmrResult(round(mif, 1), round(katch, 1), round(used, 1),
                     "katch" if index >= 30 else "mean(mifflin,katch)",
                     round(abs(mif - katch), 1), index, warning)


def tdee(bmr_kcal: float, activity: str) -> float:
    """Formula TDEE. Always a starting point, never the truth.

    The real error lives in NEAT and runs into the hundreds of kcal. Correct it
    with observed_tdee() once there is enough logged data.
    """
    key = activity.strip().lower().replace(" ", "_").replace("-", "_")
    if key not in ACTIVITY_FACTORS:
        raise InsufficientData(
            "unknown activity level %r; use one of %s" % (activity, ", ".join(sorted(ACTIVITY_FACTORS)))
        )
    return round(bmr_kcal * ACTIVITY_FACTORS[key], 0)


@dataclass(frozen=True)
class TdeeBreakdown:
    bmr: float
    neat: float
    training: float
    tef: float
    total: float
    method: str

    def as_dict(self) -> dict:
        return asdict(self)


def tdee_components(bmr_kcal: float, neat_pct: float = 0.12,
                    sessions_per_week: int = 0, kcal_per_session: float = 320.0,
                    tef_pct: float = 0.10) -> TdeeBreakdown:
    """Maintenance built from its parts instead of one activity multiplier.

    A single multiplier hides where the error is. Summing NEAT, training and the
    thermic effect of food shows which term is the guess — and it is always NEAT.

    TEF is a share of intake, and at maintenance intake equals expenditure, so
    the subtotal is grossed up rather than multiplied.
    """
    if bmr_kcal <= 0:
        raise InsufficientData("BMR must be positive")
    if not 0.0 <= neat_pct <= 0.5:
        raise InsufficientData("NEAT is 0-25% of BMR for most people; 50% is the hard ceiling")
    if not 0.0 <= tef_pct < 0.3:
        raise InsufficientData("thermic effect of food sits near 10% of intake")
    if sessions_per_week < 0 or sessions_per_week > 14:
        raise InsufficientData("sessions per week must be between 0 and 14")

    neat = bmr_kcal * neat_pct
    training = sessions_per_week * kcal_per_session / 7.0
    subtotal = bmr_kcal + neat + training
    total = subtotal / (1.0 - tef_pct)
    return TdeeBreakdown(round(bmr_kcal, 0), round(neat, 0), round(training, 0),
                         round(total - subtotal, 0), round(total, 0), "components")


def tdee_range(tdee_kcal: float, pct: float = 0.06) -> Tuple[float, float]:
    """Honest uncertainty band around a formula TDEE. Report this, not a point."""
    return (round(tdee_kcal * (1 - pct), 0), round(tdee_kcal * (1 + pct), 0))


@dataclass(frozen=True)
class MacroTarget:
    kcal: float
    protein_g: float
    fat_g: float
    carb_g: float
    protein_g_per_kg: float
    fat_g_per_kg: float
    carb_g_per_kg: float
    floor_warning: Optional[str]
    fibre_g: float = 0.0
    water_ml: float = 0.0
    meals: int = 4
    protein_per_meal_g: float = 0.0

    def as_dict(self) -> dict:
        return asdict(self)


def macros(target_kcal: float, weight_kg: float, sex: str,
           protein_g_kg: float = 1.8, fat_g_kg: float = 0.9,
           meals: int = 4, water_ml_per_kg: float = 35.0) -> MacroTarget:
    """Protein and fat by body weight; carbohydrate takes the remainder.

    Also returns fibre, water and per-meal protein — targets the reference file
    documents but that nobody computes by hand, so they quietly get dropped.
    """
    sex = _normalize_sex(sex)
    if target_kcal <= 0 or weight_kg <= 0:
        raise InsufficientData("target calories and weight must be positive")
    if not 1.2 <= protein_g_kg <= 3.0:
        raise InsufficientData("protein target outside the defensible 1.2-3.0 g/kg range")
    if fat_g_kg < 0.5:
        raise InsufficientData("fat below 0.5 g/kg compromises hormonal function")

    protein_g = protein_g_kg * weight_kg
    fat_g = fat_g_kg * weight_kg
    remaining = target_kcal - (protein_g * 4.0 + fat_g * 9.0)
    if remaining < 0:
        raise InsufficientData(
            "protein and fat alone exceed the calorie target; raise calories or lower g/kg"
        )
    carb_g = remaining / 4.0

    warning = None
    floor = KCAL_FLOOR[sex]
    if target_kcal < floor:
        warning = ("target of %d kcal is below the %d kcal floor for %s without clinical "
                   "supervision" % (round(target_kcal), round(floor), sex))

    if not 2 <= meals <= 8:
        raise InsufficientData("meals per day must be between 2 and 8")

    # 14 g of fibre per 1000 kcal, the usual population guideline, held inside 25-40 g
    fibre = min(40.0, max(25.0, target_kcal / 1000.0 * 14.0))
    per_meal = protein_g / meals
    if per_meal < 0.25 * weight_kg and meals > 3:
        warning = (warning + " · " if warning else "") + (
            "%.0f g of protein per meal is below the ~0.3 g/kg that maximises the response; "
            "fewer, larger meals would work better" % per_meal)

    return MacroTarget(
        kcal=round(target_kcal, 0),
        protein_g=round(protein_g, 0),
        fat_g=round(fat_g, 0),
        carb_g=round(carb_g, 0),
        protein_g_per_kg=round(protein_g_kg, 2),
        fat_g_per_kg=round(fat_g_kg, 2),
        carb_g_per_kg=round(carb_g / weight_kg, 2),
        floor_warning=warning,
        fibre_g=round(fibre, 0),
        water_ml=round(weight_kg * water_ml_per_kg, -1),
        meals=meals,
        protein_per_meal_g=round(per_meal, 0),
    )


@dataclass(frozen=True)
class TrendPoint:
    day: date
    raw: Optional[float]
    ema: float


def ema_trend(points: Sequence[Tuple[date, float]], alpha: float = 0.25) -> List[TrendPoint]:
    """Exponentially smoothed weight trend on a daily grid.

    alpha=0.25 behaves like a 7-day window. Gaps carry the previous value
    forward so a missed weigh-in does not distort the slope.
    """
    if len(points) < 2:
        raise InsufficientData("need at least 2 weigh-ins to compute a trend")
    if not 0 < alpha <= 1:
        raise InsufficientData("alpha must be in (0, 1]")

    by_day: Dict[date, List[float]] = {}
    for day, value in points:
        by_day.setdefault(day, []).append(float(value))
    daily = {d: statistics.fmean(v) for d, v in by_day.items()}

    start, end = min(daily), max(daily)
    out: List[TrendPoint] = []
    current: Optional[float] = None
    day = start
    while day <= end:
        raw = daily.get(day)
        if current is None:
            current = raw if raw is not None else 0.0
        elif raw is not None:
            current = alpha * raw + (1 - alpha) * current
        out.append(TrendPoint(day=day, raw=raw, ema=round(current, 3)))
        day += timedelta(days=1)
    return out


@dataclass(frozen=True)
class RateResult:
    kg_per_week: float
    pct_per_week: float
    days: int
    verdict: str
    note: str

    def as_dict(self) -> dict:
        return asdict(self)


def rate_of_change(trend: Sequence[TrendPoint], goal: str = "loss",
                   min_days: int = 14) -> RateResult:
    """Least-squares slope over the smoothed trend, with a safety verdict.

    Refuses under min_days: water, salt and glycogen dominate anything shorter.
    """
    if len(trend) < min_days:
        raise InsufficientData(
            "need at least %d days of weight data; have %d. Water and glycogen noise "
            "dominates shorter windows." % (min_days, len(trend))
        )
    goal = goal.strip().lower()
    if goal not in ("loss", "gain", "maintain"):
        raise InsufficientData("goal must be loss, gain or maintain")

    xs = list(range(len(trend)))
    ys = [p.ema for p in trend]
    slope = _least_squares_slope(xs, ys)
    kg_week = slope * 7.0
    mean_weight = statistics.fmean(ys)
    pct_week = (kg_week / mean_weight) * 100.0 if mean_weight else 0.0

    verdict, note = _classify_rate(pct_week, goal)
    return RateResult(round(kg_week, 3), round(pct_week, 2), len(trend), verdict, note)


def _classify_rate(pct_week: float, goal: str) -> Tuple[str, str]:
    if goal == "maintain":
        if abs(pct_week) <= 0.15:
            return "on_track", "weight stable, which is the target"
        return "drifting", "weight is moving %.2f%%/week while the goal is maintenance" % pct_week

    if goal == "loss":
        if pct_week > 0.1:
            return "wrong_direction", "gaining while the goal is fat loss — check adherence before cutting calories"
        if pct_week > -0.15:
            return "stalled", "no meaningful loss; confirm adherence for 3 weeks before adjusting"
        if pct_week >= -1.0:
            return "on_track", "within the 0.5-1.0%/week band"
        return "too_fast", "faster than 1%/week costs lean mass; raise calories"

    if pct_week < -0.1:
        return "wrong_direction", "losing while the goal is gaining — raise calories"
    if pct_week < 0.1:
        return "stalled", "no meaningful gain; add roughly 200 kcal and wait 3 weeks"
    if pct_week <= 0.5:
        return "on_track", "within the 0.1-0.5%/week band"
    return "too_fast", "above 0.5%/week the fraction arriving as fat climbs; cut roughly 200 kcal"


@dataclass(frozen=True)
class ObservedTdee:
    kcal: float
    mean_intake_kcal: float
    kg_change: float
    days: int
    meal_days: int
    suggested_target_kcal: Optional[float]

    def as_dict(self) -> dict:
        return asdict(self)


def observed_tdee(intake_by_day: Dict[date, float], trend: Sequence[TrendPoint],
                  window_days: int = 28, min_meal_days: int = 10,
                  goal_delta_kcal: Optional[float] = None) -> ObservedTdee:
    """Energy expenditure measured from real intake against real weight change.

    This is the number that corrects a formula TDEE that drifted from reality.
    It refuses rather than guesses: without enough logged days the arithmetic
    produces a confident number with no information in it.
    """
    if not trend:
        raise InsufficientData("no weight trend available")

    end = trend[-1].day
    start = end - timedelta(days=window_days - 1)
    window = [p for p in trend if start <= p.day <= end]
    if len(window) < min_meal_days:
        raise InsufficientData(
            "weight trend covers %d days in the window; need at least %d" % (len(window), min_meal_days)
        )

    meals = {d: v for d, v in intake_by_day.items() if start <= d <= end and v > 0}
    if len(meals) < min_meal_days:
        raise InsufficientData(
            "only %d days with logged intake in the last %d days; need at least %d. "
            "Log meals consistently for another %d days, or use the formula estimate and say so."
            % (len(meals), window_days, min_meal_days, min_meal_days - len(meals))
        )

    mean_intake = statistics.fmean(meals.values())
    kg_change = window[-1].ema - window[0].ema
    days_span = (window[-1].day - window[0].day).days or 1
    expenditure = mean_intake - (kg_change * KCAL_PER_KG / days_span)

    suggested = round(expenditure + goal_delta_kcal, 0) if goal_delta_kcal is not None else None
    return ObservedTdee(
        kcal=round(expenditure, 0),
        mean_intake_kcal=round(mean_intake, 0),
        kg_change=round(kg_change, 2),
        days=days_span + 1,
        meal_days=len(meals),
        suggested_target_kcal=suggested,
    )


@dataclass(frozen=True)
class OneRepMax:
    epley: float
    brzycki: float
    mean: float
    reps_used: int
    caution: Optional[str]

    def as_dict(self) -> dict:
        return asdict(self)


def one_rep_max(load_kg: float, reps: int) -> OneRepMax:
    """Estimated 1RM by Epley and Brzycki. Estimate, never a prescription."""
    if load_kg <= 0 or reps <= 0:
        raise InsufficientData("load and reps must be positive")
    if reps > 10:
        raise InsufficientData(
            "1RM formulas are validated on low-rep sets and inflate badly above 10 reps — "
            "a 15-rep set measures resistance to acidosis, not maximal force. Test with a "
            "set of 3-8 reps instead."
        )
    epley = load_kg * (1 + reps / 30.0)
    brzycki = load_kg * 36.0 / (37.0 - reps)
    spread = abs(epley - brzycki)
    mean = (epley + brzycki) / 2

    caution = None
    if reps > 6:
        # the two equations happen to cross near 10 reps, so agreement here is
        # arithmetic coincidence, not evidence that the estimate is good
        caution = ("estimated from a %d-rep set, where these formulas are least reliable — "
                   "high-rep performance reflects fatigue resistance as much as maximal force. "
                   "Treat it as a wide range and re-test with 3-6 reps when the number matters."
                   % reps)
    elif spread > 0.02 * mean:
        caution = ("Epley and Brzycki differ by %.1f kg here — use the range %.1f-%.1f, not the "
                   "midpoint" % (spread, min(epley, brzycki), max(epley, brzycki)))
    return OneRepMax(round(epley, 1), round(brzycki, 1), round(mean, 1), reps, caution)


def projection(trend: Sequence[TrendPoint], target_kg: float,
               rate: RateResult) -> dict:
    """Weeks to goal at the observed rate. Refuses when the rate goes nowhere."""
    if not trend:
        raise InsufficientData("no trend available")
    current = trend[-1].ema
    delta = target_kg - current
    if abs(rate.kg_per_week) < 0.02:
        raise InsufficientData(
            "observed rate is effectively zero; a projection would be meaningless"
        )
    if (delta > 0) != (rate.kg_per_week > 0):
        return {"current_kg": round(current, 2), "target_kg": target_kg,
                "weeks": None, "note": "current trend moves away from the target"}
    weeks = delta / rate.kg_per_week
    return {"current_kg": round(current, 2), "target_kg": target_kg,
            "weeks": round(weeks, 1),
            "note": "at the observed %.2f kg/week; recompute at every check-in" % rate.kg_per_week}


def _least_squares_slope(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


def _normalize_sex(sex: str) -> str:
    s = (sex or "").strip().lower()
    if s in ("m", "male", "masculino", "homem"):
        return SEX_MALE
    if s in ("f", "female", "feminino", "mulher"):
        return SEX_FEMALE
    raise InsufficientData("sex must be male or female (affects the BMR equation)")
