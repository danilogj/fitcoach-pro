"""One screen for every client a trainer has.

The rest of the CLI operates on one client at a time, which is right for
prescribing and wrong for Monday morning. With twenty-five clients, the
question is not "how is Maria doing" — it is "which four need me this week".

Standard library only.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import load as load_mod
import logstore
import metrics as m

# severity order drives the sort: the trainer reads top-down and stops when they run out of time
SEVERITY = {"risk": 0, "attention": 1, "stale": 2, "ok": 3, "no_data": 4}


@dataclass
class ClientRow:
    name: str
    status: str
    days_since_activity: Optional[int]
    sessions_last_7d: int
    trend_kg: Optional[float]
    rate_kg_week: Optional[float]
    rate_verdict: Optional[str]
    acwr: Optional[float]
    acwr_verdict: Optional[str]
    alerts: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def scan(root: Path, goal_by_client: Optional[Dict[str, str]] = None,
         today: Optional[date] = None, stale_days: int = 10) -> List[ClientRow]:
    """Read every client folder under root and rank them by who needs attention.

    A folder without a log is reported as no_data, not skipped: a client who
    never got set up is exactly the one who falls through the cracks.
    """
    if not root.exists():
        raise m.InsufficientData(
            "no client folder at %s. Create one with `cli.py --client %s init <name>`."
            % (root, root))

    folders = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not folders:
        raise m.InsufficientData("%s has no client folders in it yet" % root)

    goals = goal_by_client or {}

    # One reference date for the whole roster. Using each client's own last
    # entry would report everyone as current — including the one who stopped
    # logging three weeks ago, who is the entire reason to run this.
    reference = today or _latest_activity(folders)

    rows: List[ClientRow] = []
    for folder in folders:
        rows.append(_scan_one(folder, goals.get(folder.name, "loss"), reference, stale_days))

    rows.sort(key=lambda r: (SEVERITY.get(r.status, 9), -(r.days_since_activity or 0)))
    return rows


def _latest_activity(folders: List[Path]) -> Optional[date]:
    latest: Optional[date] = None
    for folder in folders:
        log = folder / "log.jsonl"
        if not log.exists():
            continue
        try:
            events = logstore.read(log)
        except Exception:
            continue
        if events:
            day = max(e.day for e in events)
            latest = day if latest is None else max(latest, day)
    return latest


def _scan_one(folder: Path, goal: str, today: Optional[date], stale_days: int) -> ClientRow:
    log = folder / "log.jsonl"
    row = ClientRow(name=folder.name, status="no_data", days_since_activity=None,
                    sessions_last_7d=0, trend_kg=None, rate_kg_week=None,
                    rate_verdict=None, acwr=None, acwr_verdict=None)

    if not log.exists():
        row.alerts.append("no log.jsonl — this client was never set up")
        return row

    events = logstore.read(log)
    if not events:
        row.alerts.append("log is empty — nothing recorded yet")
        return row

    reference = today or max(e.day for e in events)
    last = max(e.day for e in events)
    row.days_since_activity = (reference - last).days

    week_ago = reference - timedelta(days=6)
    row.sessions_last_7d = len([e for e in events if e.type == "session" and e.day >= week_ago])

    try:
        trend = m.ema_trend(logstore.weights(log))
        row.trend_kg = trend[-1].ema
        try:
            rate = m.rate_of_change(trend, goal)
            row.rate_kg_week = rate.kg_per_week
            row.rate_verdict = rate.verdict
        except m.InsufficientData:
            pass
    except m.InsufficientData:
        pass

    try:
        catalog = _catalog_for(folder)
        by_day = logstore.weighted_load_by_day(log, catalog)
        acwr = load_mod.acwr(by_day, reference=reference)
        row.acwr = acwr.ratio
        row.acwr_verdict = acwr.verdict
    except (m.InsufficientData, Exception):
        pass

    row.status, row.alerts = _judge(row, stale_days)
    return row


def _catalog_for(folder: Path):
    import volume as vol
    local = folder / "exercises.json"
    try:
        return vol.Catalog(extra=local if local.exists() else None)
    except m.InsufficientData:
        return None


def _judge(row: ClientRow, stale_days: int):
    alerts: List[str] = []
    status = "ok"

    if row.acwr_verdict == "spike":
        alerts.append("training load spiked (ACWR %.2f) — the pattern that precedes injury" % row.acwr)
        status = "risk"
    elif row.acwr_verdict == "watch":
        alerts.append("load climbed faster than adaptation (ACWR %.2f)" % row.acwr)
        status = "attention"

    if row.rate_verdict == "too_fast":
        alerts.append("weight moving %.2f kg/week — too fast" % row.rate_kg_week)
        status = "risk" if status != "risk" else status
    elif row.rate_verdict in ("stalled", "wrong_direction"):
        alerts.append("weight %s (%.2f kg/week)" % (row.rate_verdict.replace("_", " "), row.rate_kg_week))
        status = "attention" if status == "ok" else status

    if row.days_since_activity is not None and row.days_since_activity >= stale_days:
        alerts.append("nothing logged for %d days" % row.days_since_activity)
        status = "stale" if status == "ok" else status

    if row.sessions_last_7d == 0 and (row.days_since_activity or 0) < stale_days:
        alerts.append("no training sessions in the last 7 days")
        status = "attention" if status == "ok" else status

    if not alerts:
        alerts.append("on plan")
    return status, alerts


def render(rows: List[ClientRow]) -> str:
    """A table a trainer reads top-down on Monday morning."""
    header = ("%-18s %-10s %6s %5s %9s %7s  %s"
              % ("client", "status", "last", "7d", "trend", "ACWR", "what needs attention"))
    lines = [header, "-" * len(header)]
    for r in rows:
        lines.append("%-18s %-10s %6s %5d %9s %7s  %s" % (
            r.name[:18],
            r.status,
            ("%dd" % r.days_since_activity) if r.days_since_activity is not None else "—",
            r.sessions_last_7d,
            ("%.1f kg" % r.trend_kg) if r.trend_kg is not None else "—",
            ("%.2f" % r.acwr) if r.acwr is not None else "—",
            "; ".join(r.alerts),
        ))

    counts: Dict[str, int] = {}
    for r in rows:
        counts[r.status] = counts.get(r.status, 0) + 1
    summary = " · ".join("%d %s" % (n, s) for s, n in sorted(counts.items(), key=lambda kv: SEVERITY.get(kv[0], 9)))
    lines.append("")
    lines.append("%d clients: %s" % (len(rows), summary))
    needs = [r for r in rows if r.status in ("risk", "attention")]
    if needs:
        lines.append("start with: %s" % ", ".join(r.name for r in needs[:5]))
    return "\n".join(lines)
