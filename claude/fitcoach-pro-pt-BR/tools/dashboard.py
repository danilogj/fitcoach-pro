"""Render the client's log as a single self-contained HTML page.

No CDN, no build step, no JavaScript framework — inline SVG and a stylesheet.
The trainer opens the file, or emails it, and it works offline in five years.

Standard library only.
"""
from __future__ import annotations

import html
import statistics
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import load as load_mod
import logstore
import metrics as m
import volume as vol

W, H = 720, 200          # plot area of every chart
PAD_L, PAD_R, PAD_T, PAD_B = 46, 14, 16, 26


def render(log_path: Path, out_path: Path, *, client: str = "Client",
           goal: str = "loss", target_kg: Optional[float] = None) -> dict:
    """Write the dashboard and return what it managed to show."""
    events = logstore.read(log_path)
    if not events:
        raise m.InsufficientData(
            "the log is empty — nothing to plot. Record something first with "
            "`cli.py log add`, or import an export with `cli.py ingest`.")

    weights = logstore.weights(log_path)
    sessions = logstore.read(log_path, "session")
    sleeps = logstore.read(log_path, "sleep")
    steps = logstore.read(log_path, "steps")
    intake = logstore.intake_by_day(log_path)

    cards: List[Tuple[str, str, str]] = []
    charts: List[str] = []
    gaps: List[str] = []
    shown: List[str] = []

    trend = None
    if len(weights) >= 2:
        trend = m.ema_trend(weights)
        latest = trend[-1]
        cards.append(("Weight trend", "%.1f kg" % latest.ema, latest.day.isoformat()))
        charts.append(_weight_chart(trend, target_kg))
        shown.append("weight")
    else:
        gaps.append("Weight: %d weigh-ins logged, the trend needs at least 2." % len(weights))

    if trend:
        try:
            rate = m.rate_of_change(trend, goal)
            cards.append(("Rate", "%+.2f kg/wk" % rate.kg_per_week, rate.verdict.replace("_", " ")))
            shown.append("rate")
        except m.InsufficientData as exc:
            gaps.append("Rate of change: %s" % exc)
        try:
            obs = m.observed_tdee(intake, trend)
            cards.append(("Measured expenditure", "%d kcal" % obs.kcal,
                          "%d days logged" % obs.meal_days))
            shown.append("observed_tdee")
        except m.InsufficientData as exc:
            gaps.append("Measured expenditure: %s" % exc)

    # imported cardio sessions carry a duration but no sets: counting them as
    # zero would draw an empty volume chart and imply the client lifted nothing
    sets_daily = {d: v for d, v in _sets_by_day(sessions).items() if v > 0}
    weekly_sets = _weekly(sets_daily)
    if weekly_sets:
        charts.append(_bar_chart("Total hard sets per week", weekly_sets, unit="sets"))
        shown.append("volume")
        cards.append(("Sessions logged", str(len(sessions)),
                      "%d weeks of data" % len(weekly_sets)))
        muscle_chart = _muscle_chart(sessions)
        if muscle_chart:
            charts.append(muscle_chart)
            shown.append("volume_by_muscle")
        else:
            gaps.append("Sets per muscle: the logged exercise names are not in the "
                        "catalog, so they cannot be attributed to muscle groups.")
    elif sessions:
        gaps.append("Training volume: %d sessions logged, but none record sets. "
                    "Imported cardio carries duration only — resistance sets have to be "
                    "logged from the client's sheet." % len(sessions))
    else:
        gaps.append("Training volume: no sessions logged yet.")

    try:
        by_day = {d: float(v) for d, v in logstore.hard_sets_by_day(log_path).items()}
        acwr = load_mod.acwr(by_day)
        cards.append(("Acute:chronic load", "%.2f" % acwr.ratio, acwr.verdict))
        shown.append("acwr")
    except m.InsufficientData as exc:
        gaps.append("Acute:chronic load: %s" % exc)

    if sleeps:
        daily = {e.day: float(e.data["hours"]) for e in sleeps}
        charts.append(_bar_chart("Sleep", _series(daily), unit="h",
                                 bands=[(7, 9, "7-9 h")], per_day=True))
        avg = statistics.fmean(daily.values())
        cards.append(("Sleep average", "%.1f h" % avg,
                      "under 6.5 h is a deload signal" if avg < 6.5 else "adequate"))
        shown.append("sleep")

    if steps:
        daily = {e.day: float(e.data["count"]) for e in steps}
        charts.append(_bar_chart("Steps", _series(daily), unit="", per_day=True,
                                 bands=[(8000, 10000, "8-10k target")]))
        shown.append("steps")

    lifts = _lift_series(sessions)
    if lifts:
        charts.append(_multi_line("Load on the main lifts", lifts))
        shown.append("lifts")

    page = _page(client, cards, charts, gaps, log_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    return {"path": str(out_path), "sections": shown, "gaps": gaps,
            "events": len(events)}


# --------------------------------------------------------------------------
# data shaping
# --------------------------------------------------------------------------

def _sets_by_day(sessions) -> Dict[date, float]:
    out: Dict[date, float] = {}
    for e in sessions:
        n = sum(len(x.get("sets", [])) for x in e.data.get("exercises", []))
        out[e.day] = out.get(e.day, 0.0) + n
    return out


def _weekly(daily: Dict[date, float]) -> List[Tuple[str, float]]:
    if not daily:
        return []
    buckets: Dict[date, float] = {}
    for day, value in daily.items():
        monday = day - timedelta(days=day.weekday())
        buckets[monday] = buckets.get(monday, 0.0) + value
    return [(d.strftime("%d/%m"), v) for d, v in sorted(buckets.items())]


def _series(daily: Dict[date, float]) -> List[Tuple[str, float]]:
    return [(d.strftime("%d/%m"), v) for d, v in sorted(daily.items())]


def _lift_series(sessions, top: int = 4) -> Dict[str, List[Tuple[date, float]]]:
    """Heaviest working set per exercise per day, for the most-trained lifts."""
    by_ex: Dict[str, Dict[date, float]] = {}
    for e in sessions:
        for item in e.data.get("exercises", []):
            name = item.get("name")
            loads = [s.get("load_kg") for s in item.get("sets", []) if s.get("load_kg")]
            if not name or not loads:
                continue
            best = max(float(x) for x in loads)
            by_ex.setdefault(name, {})
            by_ex[name][e.day] = max(by_ex[name].get(e.day, 0.0), best)
    ranked = sorted(by_ex.items(), key=lambda kv: -len(kv[1]))[:top]
    return {name: sorted(days.items()) for name, days in ranked if len(days) >= 2}


# --------------------------------------------------------------------------
# svg
# --------------------------------------------------------------------------

def _scale(values: Sequence[float], pad: float = 0.06) -> Tuple[float, float]:
    lo, hi = min(values), max(values)
    if lo == hi:
        return lo - 1, hi + 1
    span = hi - lo
    return lo - span * pad, hi + span * pad


def _weight_chart(trend, target_kg: Optional[float]) -> str:
    emas = [p.ema for p in trend]
    raws = [(i, p.raw) for i, p in enumerate(trend) if p.raw is not None]
    pool = emas + [r for _, r in raws] + ([target_kg] if target_kg else [])
    lo, hi = _scale(pool)

    def x(i): return PAD_L + (i / max(1, len(trend) - 1)) * (W - PAD_L - PAD_R)
    def y(v): return PAD_T + (1 - (v - lo) / (hi - lo)) * (H - PAD_T - PAD_B)

    dots = "".join('<circle cx="%.1f" cy="%.1f" r="2" class="raw"/>' % (x(i), y(v))
                   for i, v in raws)
    line = " ".join("%.1f,%.1f" % (x(i), y(v)) for i, v in enumerate(emas))
    goal_line = ""
    if target_kg is not None and lo <= target_kg <= hi:
        goal_line = ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="goal"/>'
                     '<text x="%.1f" y="%.1f" class="goal-label">target %.1f</text>'
                     % (PAD_L, y(target_kg), W - PAD_R, y(target_kg),
                        PAD_L + 4, y(target_kg) - 5, target_kg))
    labels = _x_labels([p.day.strftime("%d/%m") for p in trend], x)
    return _svg_block("Weight — daily readings and smoothed trend",
                      _grid(lo, hi, y) + goal_line + dots +
                      '<polyline points="%s" class="trend"/>' % line + labels)


def _bar_chart(title: str, series: List[Tuple[str, float]], unit: str = "",
               bands: Optional[List[Tuple[float, float, str]]] = None,
               per_day: bool = False) -> str:
    if not series:
        return ""
    values = [v for _, v in series]
    lo = 0.0
    hi = max(values + [b[1] for b in (bands or [])]) * 1.12
    if hi <= lo:
        return ""   # an all-zero series is not a chart, it is an absence
    n = len(series)
    slot = (W - PAD_L - PAD_R) / max(1, n)
    bw = max(2.0, min(26.0, slot * 0.62))

    def y(v): return PAD_T + (1 - (v - lo) / (hi - lo)) * (H - PAD_T - PAD_B)

    band_svg = ""
    for b_lo, b_hi, label in (bands or []):
        band_svg += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="band"/>'
                     '<text x="%.1f" y="%.1f" class="band-label">%s</text>'
                     % (PAD_L, y(b_hi), W - PAD_L - PAD_R, max(1.0, y(b_lo) - y(b_hi)),
                        W - PAD_R - 4, y(b_hi) - 4, html.escape(label)))
        band_svg = band_svg.replace('class="band-label">%s' % html.escape(label),
                                    'class="band-label" text-anchor="end">%s' % html.escape(label))

    bars = ""
    for i, (_, v) in enumerate(series):
        cx = PAD_L + slot * i + slot / 2
        bars += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="bar"><title>%s</title></rect>'
                 % (cx - bw / 2, y(v), bw, max(1.0, y(lo) - y(v)),
                    html.escape("%s: %g %s" % (series[i][0], v, unit))))
    labels = _x_labels([lbl for lbl, _ in series],
                       lambda i: PAD_L + slot * i + slot / 2)
    return _svg_block(title, _grid(lo, hi, y) + band_svg + bars + labels)


def _multi_line(title: str, series: Dict[str, List[Tuple[date, float]]]) -> str:
    all_days = sorted({d for pts in series.values() for d, _ in pts})
    all_vals = [v for pts in series.values() for _, v in pts]
    if not all_days or not all_vals:
        return ""
    lo, hi = _scale(all_vals)
    if hi <= lo:
        return ""
    index = {d: i for i, d in enumerate(all_days)}

    def x(i): return PAD_L + (i / max(1, len(all_days) - 1)) * (W - PAD_L - PAD_R)
    def y(v): return PAD_T + (1 - (v - lo) / (hi - lo)) * (H - PAD_T - PAD_B)

    body = _grid(lo, hi, y)
    legend = ""
    for k, (name, pts) in enumerate(series.items()):
        coords = " ".join("%.1f,%.1f" % (x(index[d]), y(v)) for d, v in pts)
        body += '<polyline points="%s" class="lift lift%d"/>' % (coords, k % 4)
        body += "".join('<circle cx="%.1f" cy="%.1f" r="2.2" class="lift-dot lift%d"/>'
                        % (x(index[d]), y(v), k % 4) for d, v in pts)
        legend += ('<span class="key"><i class="sw lift%d"></i>%s</span>'
                   % (k % 4, html.escape(name)))
    labels = _x_labels([d.strftime("%d/%m") for d in all_days], x)
    return _svg_block(title, body + labels, legend)


def _muscle_chart(sessions, profile: str = "intermediate") -> Optional[str]:
    """Direct sets per muscle in the last complete week, against the landmarks.

    This is the chart that answers "is this program actually balanced" — the
    weekly total cannot, because 60 sets can be four muscles or twelve.
    """
    if not sessions:
        return None
    last_day = max(e.day for e in sessions)
    monday = last_day - timedelta(days=last_day.weekday())
    partial = last_day.weekday() < 6  # the current week has not finished yet

    def week_of(start):
        return [e for e in sessions if start <= e.day <= start + timedelta(days=6)]

    week = week_of(monday)
    if partial:
        previous = week_of(monday - timedelta(days=7))
        # a finished week describes the program; a week two days old describes nothing
        if len(previous) > len(week):
            monday -= timedelta(days=7)
            week = previous
            partial = False
    if not week:
        return None

    program = [{"exercises": [{"name": x["name"], "sets": len(x.get("sets", []))}
                              for x in e.data.get("exercises", []) if x.get("name")]}
               for e in week]
    if not any(p["exercises"] for p in program):
        return None
    try:
        rows = vol.weekly_volume(program, profile=profile)
    except m.InsufficientData:
        return None

    rows = [r for r in rows if r.direct > 0 or vol.LANDMARKS[r.muscle]["mev"] > 0]
    if not rows:
        return None

    hi = max([r.direct for r in rows] + [vol.LANDMARKS[r.muscle]["mrv"] for r in rows]) * 1.1
    slot = (W - PAD_L - PAD_R) / max(1, len(rows))
    bw = max(3.0, min(30.0, slot * 0.6))

    def y(v):
        return PAD_T + (1 - v / hi) * (H - PAD_T - PAD_B)

    body = _grid(0, hi, y)
    for i, r in enumerate(rows):
        lm = vol.LANDMARKS[r.muscle]
        cx = PAD_L + slot * i + slot / 2
        # the productive band for THIS muscle, drawn behind its own bar
        body += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="band"/>'
                 % (cx - slot / 2 + 1, y(lm["mav_high"]), slot - 2,
                    max(1.0, y(lm["mav_low"]) - y(lm["mav_high"]))))
        cls = {"below_mev": "bar low", "low": "bar", "productive": "bar ok",
               "high": "bar warn", "above_mrv": "bar over"}.get(r.verdict, "bar")
        body += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="%s">'
                 '<title>%s</title></rect>'
                 % (cx - bw / 2, y(r.direct), bw, max(1.0, y(0) - y(r.direct)), cls,
                    html.escape("%s: %.0f direct, %.1f indirect — %s"
                                % (r.muscle, r.direct, r.indirect, r.note))))
    # a muscle at zero draws no bar, so the label carries the warning instead
    labels = ""
    for i, r in enumerate(rows):
        cls = "xlab alert" if r.verdict in ("below_mev", "above_mrv") else "xlab"
        labels += ('<text x="%.1f" y="%.1f" class="%s">%s</text>'
                   % (PAD_L + slot * i + slot / 2, H - 6, cls,
                      html.escape(r.muscle.replace("_", " ")[:9])))
    legend = ('<span class="key"><i class="sw ok"></i>productive</span>'
              '<span class="key"><i class="sw low"></i>below MEV</span>'
              '<span class="key"><i class="sw over"></i>above MRV</span>'
              '<span class="key"><i class="sw band-key"></i>adaptive range</span>')
    title = "Direct sets per muscle — week of %s%s" % (
        monday.strftime("%d/%m"), " (in progress)" if partial else "")
    return _svg_block(title, body + labels, legend)


def _grid(lo: float, hi: float, y) -> str:
    out = ""
    for frac in (0.0, 0.5, 1.0):
        v = lo + (hi - lo) * frac
        yy = y(v)
        out += ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="grid"/>'
                '<text x="%.1f" y="%.1f" class="ylab">%s</text>'
                % (PAD_L, yy, W - PAD_R, yy, PAD_L - 6, yy + 3.5, _fmt(v)))
    return out


def _x_labels(labels: Sequence[str], x) -> str:
    n = len(labels)
    if n == 0:
        return ""
    step = max(1, n // 8)
    out = ""
    for i in range(0, n, step):
        out += ('<text x="%.1f" y="%.1f" class="xlab">%s</text>'
                % (x(i), H - 6, html.escape(labels[i])))
    return out


def _fmt(v: float) -> str:
    if abs(v) >= 1000:
        return "%.0fk" % (v / 1000)
    return "%.0f" % v if abs(v) >= 10 else "%.1f" % v


def _svg_block(title: str, body: str, legend: str = "") -> str:
    return ('<section class="chart"><h2>%s</h2>%s'
            '<svg viewBox="0 0 %d %d" role="img" aria-label="%s">%s</svg></section>'
            % (html.escape(title), '<div class="legend">%s</div>' % legend if legend else "",
               W, H, html.escape(title), body))


# --------------------------------------------------------------------------
# page
# --------------------------------------------------------------------------

def _page(client: str, cards, charts, gaps, log_path: Path) -> str:
    card_html = "".join(
        '<div class="card"><span class="k">%s</span><strong>%s</strong><span class="n">%s</span></div>'
        % (html.escape(k), html.escape(v), html.escape(n)) for k, v, n in cards)
    gap_html = ""
    if gaps:
        gap_html = ('<section class="gaps"><h2>Not shown yet</h2><ul>%s</ul>'
                    '<p>These are not errors. Each one names the data it needs.</p></section>'
                    % "".join("<li>%s</li>" % html.escape(g) for g in gaps))
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s — training dashboard</title>
<style>
:root{--bg:#F3F4F6;--surface:#fff;--ink:#14171B;--ink2:#5C6570;--line:#DFE3E8;
--accent:#2B6CB0;--raw:#A9B4C0;--band:#2B6CB01A;--l0:#2B6CB0;--l1:#B7791F;--l2:#2F855A;--l3:#9B2C6F}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14171B;--surface:#1C2026;
--ink:#EDF0F3;--ink2:#9AA4AF;--line:#2C323A;--accent:#63A4E0;--raw:#4A5460;--band:#63A4E026;
--l0:#63A4E0;--l1:#E0B45C;--l2:#68C08A;--l3:#DE84B4}}
*{box-sizing:border-box}
body{margin:0;padding:28px 20px 56px;background:var(--bg);color:var(--ink);
font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:820px;margin:0 auto}
header{margin-bottom:22px}
h1{font-size:22px;margin:0 0 2px}
.sub{color:var(--ink2);font-size:13px;margin:0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:24px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;
display:flex;flex-direction:column;gap:2px}
.card .k{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink2)}
.card strong{font-size:21px;font-weight:600;font-variant-numeric:tabular-nums}
.card .n{font-size:12px;color:var(--ink2)}
.chart{background:var(--surface);border:1px solid var(--line);border-radius:10px;
padding:14px 14px 6px;margin-bottom:16px;overflow-x:auto}
.chart h2{font-size:14px;margin:0 0 8px;font-weight:600}
svg{width:100%%;height:auto;display:block;min-width:520px}
.grid{stroke:var(--line);stroke-width:1}
.ylab,.xlab{fill:var(--ink2);font-size:10px;font-family:inherit}
.ylab{text-anchor:end}.xlab{text-anchor:middle}
.xlab.alert{fill:var(--l1);font-weight:600}
.trend{fill:none;stroke:var(--accent);stroke-width:2.2;stroke-linejoin:round}
.raw{fill:var(--raw)}
.goal{stroke:var(--ink2);stroke-width:1;stroke-dasharray:4 4}
.goal-label{fill:var(--ink2);font-size:10px}
.bar{fill:var(--accent);opacity:.85;rx:2}
.bar.ok{fill:var(--l2)}.bar.low{fill:var(--l1)}.bar.warn{fill:var(--l1)}
.bar.over{fill:var(--l3)}
.sw.ok{background:var(--l2)}.sw.low{background:var(--l1)}.sw.over{background:var(--l3)}
.sw.band-key{background:var(--band);height:9px;border:1px solid var(--line)}
.band{fill:var(--band)}
.band-label{fill:var(--ink2);font-size:10px}
.lift{fill:none;stroke-width:2;stroke-linejoin:round}
.lift0,.sw.lift0{stroke:var(--l0);background:var(--l0)}
.lift1,.sw.lift1{stroke:var(--l1);background:var(--l1)}
.lift2,.sw.lift2{stroke:var(--l2);background:var(--l2)}
.lift3,.sw.lift3{stroke:var(--l3);background:var(--l3)}
.lift-dot.lift0{fill:var(--l0)}.lift-dot.lift1{fill:var(--l1)}
.lift-dot.lift2{fill:var(--l2)}.lift-dot.lift3{fill:var(--l3)}
.legend{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:8px}
.key{display:flex;align-items:center;gap:5px;font-size:12px;color:var(--ink2)}
.sw{width:11px;height:3px;border-radius:2px;display:inline-block}
.gaps{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.gaps h2{font-size:14px;margin:0 0 8px}
.gaps ul{margin:0 0 8px;padding-left:18px;color:var(--ink2);font-size:13px}
.gaps li{margin-bottom:4px}
.gaps p{margin:0;font-size:12px;color:var(--ink2)}
footer{margin-top:22px;font-size:12px;color:var(--ink2)}
</style></head><body><div class="wrap">
<header><h1>%s</h1><p class="sub">%s</p></header>
<div class="cards">%s</div>
%s
%s
<footer>Generated by FitCoach Pro from %s. Every number comes from the tools, not from a model.
Review before sharing with the client.</footer>
</div></body></html>""" % (
        html.escape(client), html.escape(client),
        html.escape("training dashboard · %s" % log_path.name),
        card_html, "".join(charts), gap_html, html.escape(log_path.name))
