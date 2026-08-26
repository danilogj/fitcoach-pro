#!/usr/bin/env python3
"""FitCoach Pro — single entry point for every number.

    python3 cli.py <command> [options]

Commands:
    init        create a client folder from the templates
    log         append or list events (append-only JSONL)
    metrics     bmr, targets, trend, rate, projection, tdee-observed, 1rm
    volume      weekly set count per muscle against MEV/MAV/MRV
    exercise    find, filter by equipment, substitute for a limitation
    load        acute:chronic workload, deload check
    ingest      import a wearable or app export into the log
    sheet       validate a filled-in client sheet before handing it over
    dashboard   render the log as a self-contained HTML page
    checkin     everything the weekly check-in needs, in one call
    cohort      one screen for every client: who needs attention this week

Every command exits 2 when the data cannot support an honest answer, printing
what is missing. That is a feature: a guessed number is worse than no number.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cohort as cohort_mod  # noqa: E402
import dashboard as dash_mod  # noqa: E402
import ingest as ingest_mod  # noqa: E402
import load as load_mod  # noqa: E402
import logstore  # noqa: E402
import sheet as sheet_mod  # noqa: E402
import metrics as m  # noqa: E402
import volume as vol  # noqa: E402

EXIT_INSUFFICIENT = 2
EXIT_INVALID = 3


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="cli.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client", type=Path, help="client folder (holds log.jsonl)")
    parser.add_argument("--log", type=Path, help="path to log.jsonl (overrides --client)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create a client folder")
    p.add_argument("name")

    p = sub.add_parser("log")
    logsub = p.add_subparsers(dest="log_command", required=True)
    a = logsub.add_parser("add")
    a.add_argument("type")
    a.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a.add_argument("--ts")
    l = logsub.add_parser("list")
    l.add_argument("--type")
    l.add_argument("--since")
    l.add_argument("--until")

    p = sub.add_parser("metrics")
    msub = p.add_subparsers(dest="metric", required=True)
    b = msub.add_parser("bmr")
    _profile_args(b)
    t = msub.add_parser("targets")
    _profile_args(t)
    t.add_argument("--activity", default="sedentary")
    t.add_argument("--method", default="components", choices=["components", "multiplier"])
    t.add_argument("--sessions-per-week", type=int, default=0)
    t.add_argument("--neat-pct", type=float, default=0.12)
    t.add_argument("--goal", default="maintain", choices=["loss", "gain", "maintain"])
    t.add_argument("--delta", type=float, help="kcal above/below maintenance (overrides goal default)")
    t.add_argument("--protein-g-kg", type=float, default=1.8)
    t.add_argument("--fat-g-kg", type=float, default=0.9)
    t.add_argument("--meals", type=int, default=4)
    t.add_argument("--adjusted-weight", action="store_true",
                   help="compute Mifflin on adjusted body weight (high adiposity)")
    tr = msub.add_parser("trend")
    tr.add_argument("--alpha", type=float, default=0.25)
    ra = msub.add_parser("rate")
    ra.add_argument("--goal", default="loss", choices=["loss", "gain", "maintain"])
    ra.add_argument("--min-days", type=int, default=14)
    pr = msub.add_parser("projection")
    pr.add_argument("--target-kg", type=float, required=True)
    pr.add_argument("--goal", default="loss", choices=["loss", "gain", "maintain"])
    ob = msub.add_parser("tdee-observed")
    ob.add_argument("--window-days", type=int, default=28)
    ob.add_argument("--goal-delta", type=float)
    om = msub.add_parser("1rm")
    om.add_argument("--load-kg", type=float, required=True)
    om.add_argument("--reps", type=int, required=True)

    p = sub.add_parser("volume")
    vsub = p.add_subparsers(dest="volume_command", required=True)
    vc = vsub.add_parser("check")
    vc.add_argument("--program", type=Path, required=True, help="JSON: [{'exercises':[{'name':..,'sets':N}]}]")
    vc.add_argument("--profile", default="intermediate")
    vc.add_argument("--catalog", type=Path, help="local exercise catalog to add on top of the bundled one")
    vsub.add_parser("landmarks")

    p = sub.add_parser("exercise")
    p.add_argument("--catalog", type=Path, help="local exercise catalog to add on top of the bundled one")
    esub = p.add_subparsers(dest="exercise_command", required=True)
    ef = esub.add_parser("find")
    ef.add_argument("query")
    el = esub.add_parser("filter")
    el.add_argument("--pattern")
    el.add_argument("--equipment", help="comma-separated list of what the gym has")
    es = esub.add_parser("substitute")
    es.add_argument("exercise")
    es.add_argument("--reason", required=True)

    p = sub.add_parser("load")
    lsub = p.add_subparsers(dest="load_command", required=True)
    la = lsub.add_parser("acwr")
    la.add_argument("--acute-days", type=int, default=7)
    la.add_argument("--chronic-days", type=int, default=28)
    la.add_argument("--flat", action="store_true",
                    help="count sets flat instead of weighting them by systemic cost")
    la.add_argument("--catalog", type=Path)
    ld = lsub.add_parser("deload")
    ld.add_argument("--weeks-since-deload", type=int)
    ld.add_argument("--performance-dropping-weeks", type=int, default=0)
    ld.add_argument("--sleep-hours-avg", type=float)
    ld.add_argument("--soreness-avg", type=float)
    ld.add_argument("--readiness-avg", type=float)
    ld.add_argument("--joint-pain", action="store_true")
    ld.add_argument("--appetite-down", action="store_true")
    ld.add_argument("--motivation-down", action="store_true")

    p = sub.add_parser("ingest", help="import an export file (csv, zip, xml)")
    p.add_argument("file", type=Path)
    p.add_argument("--source", default="auto",
                   choices=["auto", "samsung", "garmin", "strava", "apple", "withings", "generic"])
    p.add_argument("--inspect", action="store_true", help="show the file's columns and stop")
    p.add_argument("--dry-run", action="store_true", help="report what would be written, write nothing")
    p.add_argument("--map", dest="mapping", help="canonical=Column,canonical=Column for odd exports")

    p = sub.add_parser("sheet", help="validate a filled-in client sheet")
    ssub = p.add_subparsers(dest="sheet_command", required=True)
    sc = ssub.add_parser("check")
    sc.add_argument("file", type=Path)
    sc.add_argument("--program", type=Path, help="the program JSON the sheet should render")
    sc.add_argument("--catalog", type=Path)

    p = sub.add_parser("dashboard", help="render the log as HTML")
    p.add_argument("--out", type=Path, help="output path (default: <client>/dashboard.html)")
    p.add_argument("--name", default="Client")
    p.add_argument("--goal", default="loss", choices=["loss", "gain", "maintain"])
    p.add_argument("--target-kg", type=float)

    p = sub.add_parser("cohort", help="status of every client at once")
    p.add_argument("--root", type=Path, default=Path("clients"),
                   help="folder holding one directory per client (default: clients)")
    p.add_argument("--stale-days", type=int, default=10)
    p.add_argument("--goal", default="loss", choices=["loss", "gain", "maintain"],
                   help="default goal when a client folder does not state one")

    p = sub.add_parser("checkin")
    _profile_args(p, required=False)
    p.add_argument("--goal", default="loss", choices=["loss", "gain", "maintain"])
    p.add_argument("--target-kg", type=float)
    p.add_argument("--activity", default="sedentary")

    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except m.InsufficientData as exc:
        _fail(args, "insufficient_data", str(exc), EXIT_INSUFFICIENT)
        return EXIT_INSUFFICIENT
    except logstore.ValidationError as exc:
        _fail(args, "invalid_input", str(exc), EXIT_INVALID)
        return EXIT_INVALID


def _profile_args(p, required: bool = True) -> None:
    p.add_argument("--weight-kg", type=float, required=required)
    p.add_argument("--height-cm", type=float, required=required)
    p.add_argument("--age", type=int, required=required)
    p.add_argument("--sex", required=required)
    p.add_argument("--ffm-kg", type=float, help="fat-free mass, enables Katch-McArdle")


def _fail(args, code: str, message: str, status: int) -> None:
    if getattr(args, "json", False):
        print(json.dumps({"error": code, "message": message}, ensure_ascii=False))
    else:
        print("cannot answer: %s" % message, file=sys.stderr)


def _dispatch(args) -> int:
    if args.command == "init":
        return _cmd_init(args)
    if args.command == "log":
        return _cmd_log(args)
    if args.command == "metrics":
        return _cmd_metrics(args)
    if args.command == "volume":
        return _cmd_volume(args)
    if args.command == "exercise":
        return _cmd_exercise(args)
    if args.command == "load":
        return _cmd_load(args)
    if args.command == "ingest":
        return _cmd_ingest(args)
    if args.command == "sheet":
        return _cmd_sheet(args)
    if args.command == "dashboard":
        return _cmd_dashboard(args)
    if args.command == "cohort":
        return _cmd_cohort(args)
    if args.command == "checkin":
        return _cmd_checkin(args)
    raise SystemExit("unknown command")


def _log_path(args) -> Path:
    if args.log:
        return args.log
    if args.client:
        return args.client / "log.jsonl"
    raise m.InsufficientData("pass --client <folder> or --log <file> so I know whose data to read")


def _cmd_init(args) -> int:
    root = (args.client or Path("clients")) / args.name
    (root / "reports").mkdir(parents=True, exist_ok=True)
    templates = Path(__file__).resolve().parent.parent / "assets"
    created = []
    for src, dst in (("template-intake.md", "intake.md"),
                     ("template-program.md", "program.md"),
                     ("template-log.md", "log.md")):
        target = root / dst
        source = templates / src
        if not target.exists() and source.exists():
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            created.append(str(target))
    logf = root / "log.jsonl"
    if not logf.exists():
        logf.touch()
        created.append(str(logf))
    _emit(args, {"client_folder": str(root), "created": created},
          "client folder ready: %s\ncreated: %s" % (root, ", ".join(created) or "nothing new"))
    return 0


def _cmd_log(args) -> int:
    path = _log_path(args)
    if args.log_command == "add":
        data = {}
        for pair in args.set:
            if "=" not in pair:
                raise logstore.ValidationError("--set expects KEY=VALUE, got %r" % pair)
            key, raw = pair.split("=", 1)
            data[key.strip()] = _coerce(raw)
        event = logstore.append(path, args.type, data, ts=args.ts)
        _emit(args, {"logged": event.type, "ts": event.ts, "data": event.data},
              "logged %s at %s: %s" % (event.type, event.ts, event.data))
        return 0

    events = logstore.read(path, args.type, _day(args.since), _day(args.until))
    payload = [{"type": e.type, "ts": e.ts, **e.data} for e in events]
    lines = ["%s  %-12s %s" % (e.ts, e.type, json.dumps(e.data, ensure_ascii=False)) for e in events]
    _emit(args, payload, "\n".join(lines) or "no events")
    return 0


def _cmd_metrics(args) -> int:
    if args.metric == "1rm":
        r = m.one_rep_max(args.load_kg, args.reps)
        _emit(args, r.as_dict(),
              "1RM estimate %.1f kg (Epley %.1f / Brzycki %.1f)%s"
              % (r.mean, r.epley, r.brzycki, "\nnote: " + r.caution if r.caution else ""))
        return 0

    if args.metric in ("bmr", "targets"):
        b = m.bmr(args.weight_kg, args.height_cm, args.age, args.sex, args.ffm_kg,
                  use_adjusted_weight=getattr(args, "adjusted_weight", False))
        if args.metric == "bmr":
            text = _fmt_bmr(b)
            if b.warning:
                text += "\nNOTE: " + b.warning
            _emit(args, b.as_dict(), text)
            return 0
        if args.method == "components":
            breakdown = m.tdee_components(b.used, args.neat_pct, args.sessions_per_week)
            maint = breakdown.total
        else:
            breakdown = None
            maint = m.tdee(b.used, args.activity)
        lo, hi = m.tdee_range(maint)
        delta = args.delta if args.delta is not None else {"loss": -400.0, "gain": 300.0, "maintain": 0.0}[args.goal]
        target = maint + delta
        mac = m.macros(target, args.weight_kg, args.sex, args.protein_g_kg, args.fat_g_kg,
                       meals=args.meals)
        payload = {"bmr": b.as_dict(), "maintenance_kcal": maint,
                   "maintenance_range": [lo, hi], "delta_kcal": delta, "macros": mac.as_dict(),
                   "breakdown": breakdown.as_dict() if breakdown else None}
        text = (_fmt_bmr(b) +
                ("\n  NEAT %+d · training %+d · TEF %+d" % (breakdown.neat, breakdown.training, breakdown.tef)
                 if breakdown else "") +
                "\nmaintenance ~%d kcal (likely %d-%d)\ntarget %d kcal (%+d)"
                "\nprotein %d g · fat %d g · carbs %d g"
                "\nfibre %d g · water %.1f L · %d meals of ~%d g protein"
                % (maint, lo, hi, mac.kcal, delta, mac.protein_g, mac.fat_g, mac.carb_g,
                   mac.fibre_g, mac.water_ml / 1000.0, mac.meals, mac.protein_per_meal_g))
        if b.warning:
            text += "\nNOTE: " + b.warning
        if mac.floor_warning:
            text += "\nWARNING: " + mac.floor_warning
        _emit(args, payload, text)
        return 0

    path = _log_path(args)
    points = logstore.weights(path)
    trend = m.ema_trend(points, getattr(args, "alpha", 0.25))

    if args.metric == "trend":
        payload = [{"day": p.day.isoformat(), "raw": p.raw, "ema": p.ema} for p in trend]
        latest = trend[-1]
        _emit(args, payload,
              "smoothed weight %.2f kg on %s (from %d weigh-ins over %d days)"
              % (latest.ema, latest.day, len(points), len(trend)))
        return 0

    if args.metric == "rate":
        r = m.rate_of_change(trend, args.goal, args.min_days)
        _emit(args, r.as_dict(),
              "%.2f kg/week (%.2f%%/week) over %d days — %s: %s"
              % (r.kg_per_week, r.pct_per_week, r.days, r.verdict, r.note))
        return 0

    if args.metric == "projection":
        r = m.rate_of_change(trend, args.goal)
        p = m.projection(trend, args.target_kg, r)
        text = ("%.1f weeks to %.1f kg from %.1f kg" % (p["weeks"], p["target_kg"], p["current_kg"])
                if p["weeks"] is not None else p["note"])
        _emit(args, p, text)
        return 0

    if args.metric == "tdee-observed":
        intake = logstore.intake_by_day(path)
        r = m.observed_tdee(intake, trend, args.window_days, goal_delta_kcal=args.goal_delta)
        text = ("measured expenditure ~%d kcal/day over %d days (%d days of logged intake, "
                "mean %d kcal, weight %+.2f kg)" % (r.kcal, r.days, r.meal_days,
                                                    r.mean_intake_kcal, r.kg_change))
        if r.suggested_target_kcal:
            text += "\nsuggested target: %d kcal" % r.suggested_target_kcal
        _emit(args, r.as_dict(), text)
        return 0

    raise SystemExit("unknown metric")


def _fmt_bmr(b) -> str:
    if b.katch is None:
        return "BMR %.0f kcal (Mifflin-St Jeor)" % b.used
    return ("BMR %.0f kcal (Mifflin %.0f / Katch %.0f, spread %.0f)"
            % (b.used, b.mifflin, b.katch, b.spread))


def _catalog(args):
    """Bundled catalog, plus the client's or gym's own when one is present."""
    extra = getattr(args, "catalog", None)
    if extra is None and getattr(args, "client", None):
        candidate = args.client / "exercises.json"
        if candidate.exists():
            extra = candidate
    cat = vol.Catalog(extra=extra)
    if cat.local_ids or cat.overridden_ids:
        parts = []
        if cat.local_ids:
            parts.append("%d added" % len(cat.local_ids))
        if cat.overridden_ids:
            parts.append("%d overridden" % len(cat.overridden_ids))
        print("local catalog: %s" % ", ".join(parts), file=sys.stderr)
    return cat


def _cmd_sheet(args) -> int:
    program = None
    if args.program:
        raw = json.loads(args.program.read_text(encoding="utf-8"))
        program = raw.get("sessions", []) if isinstance(raw, dict) else raw
    report = sheet_mod.check(args.file, program, _catalog(args))
    _emit(args, report.as_dict(), report.summary())
    return 0 if report.ok else EXIT_INVALID


def _cmd_volume(args) -> int:
    if args.volume_command == "landmarks":
        _emit(args, vol.LANDMARKS,
              "\n".join("%-11s MEV %2d · MAV %2d-%2d · MRV %2d"
                        % (k, v["mev"], v["mav_low"], v["mav_high"], v["mrv"])
                        for k, v in sorted(vol.LANDMARKS.items())))
        return 0

    program = json.loads(args.program.read_text(encoding="utf-8"))
    if isinstance(program, dict):
        program = program.get("sessions", [])
    cat = _catalog(args)
    rows = vol.weekly_volume(program, cat, args.profile)
    coverage = vol.check_coverage(program, cat)
    total = sum(r.direct for r in rows)
    payload = {"total_direct_sets": total, "muscles": [r.as_dict() for r in rows],
               "coverage": coverage}
    lines = ["%-11s %5.1f direct %5.1f indirect  %-11s %s"
             % (r.muscle, r.direct, r.indirect, r.verdict, r.note) for r in rows]
    lines.append("total direct hard sets: %.0f" % total)
    if coverage["missing"]:
        lines.append("MISSING PATTERNS: " + ", ".join(coverage["missing"]))
    _emit(args, payload, "\n".join(lines))
    return 0


def _cmd_exercise(args) -> int:
    cat = _catalog(args)
    if args.exercise_command == "find":
        ex = cat.find(args.query)
        _emit(args, ex, _fmt_exercise(ex))
        return 0
    if args.exercise_command == "filter":
        equip = args.equipment.split(",") if args.equipment else None
        found = cat.filter(args.pattern, equip)
        _emit(args, found, "\n".join(_fmt_exercise(e) for e in found) or "nothing matches")
        return 0
    subs = cat.substitute(args.exercise, args.reason)
    _emit(args, subs, "\n".join(_fmt_exercise(e) for e in subs))
    return 0


def _fmt_exercise(e: dict) -> str:
    tags = []
    if e.get("axial"):
        tags.append("axial")
    if e.get("unilateral"):
        tags.append("unilateral")
    return ("%-34s %-18s %-24s primary: %s%s"
            % (e["name"], e["pattern"], "/".join(e["equipment"]),
               ", ".join(e["primary"]), "  [%s]" % ",".join(tags) if tags else ""))


def _cmd_load(args) -> int:
    if args.load_command == "acwr":
        path = _log_path(args)
        if args.flat:
            by_day = {d: float(v) for d, v in logstore.hard_sets_by_day(path).items()}
            unit = "sets/day"
        else:
            by_day = logstore.weighted_load_by_day(path, _catalog(args))
            unit = "load/day"
        r = load_mod.acwr(by_day, acute_days=args.acute_days, chronic_days=args.chronic_days)
        _emit(args, r.as_dict(),
              "ACWR %.2f (acute %.1f vs chronic %.1f %s) — %s: %s"
              % (r.ratio, r.acute_per_day, r.chronic_per_day, unit, r.verdict, r.note))
        return 0

    r = load_mod.deload_check(
        weeks_since_deload=args.weeks_since_deload,
        performance_dropping_weeks=args.performance_dropping_weeks,
        sleep_hours_avg=args.sleep_hours_avg,
        soreness_avg=args.soreness_avg,
        readiness_avg=args.readiness_avg,
        joint_pain=args.joint_pain,
        appetite_down=args.appetite_down,
        motivation_down=args.motivation_down,
    )
    _emit(args, r.as_dict(),
          "%s\nsignals: %s\n%s" % ("DELOAD" if r.should_deload else "keep going",
                                   "; ".join(r.signals) or "none", r.note))
    return 0


def _cmd_ingest(args) -> int:
    if args.inspect:
        print(ingest_mod.inspect(args.file))
        return 0

    mapping = None
    if args.mapping:
        mapping = {}
        for pair in args.mapping.split(","):
            if "=" not in pair:
                raise logstore.ValidationError("--map expects canonical=Column, got %r" % pair)
            k, v = pair.split("=", 1)
            mapping[k.strip()] = v.strip()

    source = None if args.source == "auto" else args.source
    report = ingest_mod.parse(args.file, source, mapping)

    if args.dry_run:
        _emit(args, {"source": report.source, "files": report.files,
                     "candidates": len(report.candidates),
                     "skipped": len(report.skipped),
                     "unmapped_columns": sorted(set(report.unmapped_columns))},
              report.summary() + "\n\n(dry run — nothing written)")
        return 0

    path = _log_path(args)
    written, skipped = ingest_mod.write(report, path, logstore)
    _emit(args, {"source": report.source, "written": written, "already_present": skipped,
                 "files": report.files},
          report.summary() + "\n\nwritten: %d · already present: %d\n"
                             "re-running this import is a no-op." % (written, skipped))
    return 0


def _cmd_dashboard(args) -> int:
    path = _log_path(args)
    out = args.out or ((args.client / "dashboard.html") if args.client
                       else path.parent / "dashboard.html")
    result = dash_mod.render(path, out, client=args.name, goal=args.goal,
                             target_kg=args.target_kg)
    text = ["dashboard written to %s" % result["path"],
            "sections: %s" % ", ".join(result["sections"])]
    if result["gaps"]:
        text.append("not shown yet:\n  - " + "\n  - ".join(result["gaps"]))
    _emit(args, result, "\n".join(text))
    return 0


def _cmd_cohort(args) -> int:
    root = args.root if args.root.is_absolute() or args.root.exists() else (args.client or Path(".")) / args.root
    rows = cohort_mod.scan(root if root.exists() else args.root,
                           goal_by_client=None, stale_days=args.stale_days)
    _emit(args, [r.as_dict() for r in rows], cohort_mod.render(rows))
    return 0


def _cmd_checkin(args) -> int:
    """Everything the weekly check-in needs, with each piece degrading on its own."""
    path = _log_path(args)
    out = {}
    notes = []

    try:
        trend = m.ema_trend(logstore.weights(path))
        out["trend_kg"] = trend[-1].ema
        out["trend_day"] = trend[-1].day.isoformat()
    except m.InsufficientData as exc:
        trend = None
        out["trend"] = {"unavailable": str(exc)}
        notes.append("weight trend: %s" % exc)

    if trend:
        try:
            r = m.rate_of_change(trend, args.goal)
            out["rate"] = r.as_dict()
        except m.InsufficientData as exc:
            out["rate"] = {"unavailable": str(exc)}
            notes.append("rate: %s" % exc)

        try:
            obs = m.observed_tdee(logstore.intake_by_day(path), trend)
            out["observed_tdee"] = obs.as_dict()
        except m.InsufficientData as exc:
            out["observed_tdee"] = {"unavailable": str(exc)}
            notes.append("observed TDEE: %s" % exc)

        if args.target_kg:
            try:
                out["projection"] = m.projection(trend, args.target_kg,
                                                 m.rate_of_change(trend, args.goal))
            except m.InsufficientData as exc:
                out["projection"] = {"unavailable": str(exc)}

    try:
        by_day = logstore.weighted_load_by_day(path, vol.Catalog())
        out["acwr"] = load_mod.acwr(by_day).as_dict()
    except m.InsufficientData as exc:
        out["acwr"] = {"unavailable": str(exc)}
        notes.append("ACWR: %s" % exc)

    if args.weight_kg and args.height_cm and args.age and args.sex:
        b = m.bmr(args.weight_kg, args.height_cm, args.age, args.sex, args.ffm_kg)
        out["formula_maintenance_kcal"] = m.tdee(b.used, args.activity)

    sessions = logstore.read(path, "session")
    out["sessions_logged"] = len(sessions)

    text_lines = []
    if "trend_kg" in out:
        text_lines.append("weight trend %.2f kg (%s)" % (out["trend_kg"], out["trend_day"]))
    if isinstance(out.get("rate"), dict) and "kg_per_week" in out["rate"]:
        r = out["rate"]
        text_lines.append("rate %.2f kg/wk (%.2f%%/wk) — %s" % (r["kg_per_week"], r["pct_per_week"], r["verdict"]))
    if isinstance(out.get("observed_tdee"), dict) and "kcal" in out["observed_tdee"]:
        text_lines.append("measured expenditure ~%d kcal/day" % out["observed_tdee"]["kcal"])
    if isinstance(out.get("acwr"), dict) and "ratio" in out["acwr"]:
        text_lines.append("ACWR %.2f — %s" % (out["acwr"]["ratio"], out["acwr"]["verdict"]))
    text_lines.append("%d sessions logged" % out["sessions_logged"])
    if notes:
        text_lines.append("\nnot computable yet:\n  - " + "\n  - ".join(notes))

    _emit(args, out, "\n".join(text_lines))
    return 0


def _emit(args, payload, text: str) -> None:
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, default=str))
    else:
        print(text)


def _coerce(raw: str):
    v = raw.strip()
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    if v.startswith(("[", "{")):
        return json.loads(v)
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v


def _day(value):
    if not value:
        return None
    return datetime.fromisoformat(value).date()


if __name__ == "__main__":
    sys.exit(main())
