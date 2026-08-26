"""Import wearable and app exports into the event log.

Design decision worth stating: this reads **exported files**, not APIs.

Every fitness service lets you export your data — data-portability law
guarantees it — and every API needs credentials, an OAuth dance, and breaks
when the vendor changes it. A file importer runs offline, needs no secrets,
works the same in five years, and covers services that have no public API at
all (Samsung Health being the one that matters most in practice).

Column names drift between vendor releases. Every adapter matches columns by
alias and reports what it could not place instead of silently dropping it. When
a real export does not match, `--inspect` prints the actual headers so the
mapping can be fixed in one line.

Standard library only.
"""
from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

from metrics import InsufficientData

# --------------------------------------------------------------------------
# column aliases: lowercase substrings matched against the real header
# --------------------------------------------------------------------------

ALIASES: Dict[str, Sequence[str]] = {
    "date": ("date", "day", "day time", "day_time", "start_time", "start time", "activity date",
             "create_time", "start", "timestamp", "data", "data da medicao"),
    "weight_kg": ("weight", "body mass", "peso", "massa", "com.samsung.health.weight.weight"),
    "steps": ("steps", "step count", "total steps", "passos", "step count"),
    "sleep_hours": ("sleep duration", "total sleep", "sleep_duration", "asleep time",
                    "sono", "duracao do sono"),
    "sleep_score": ("sleep score", "score", "sleep quality"),
    "rhr": ("resting heart rate", "resting hr", "rhr", "min heart rate"),
    "hrv": ("hrv", "heart rate variability", "rmssd"),
    "readiness": ("readiness", "body battery", "recovery score", "energy score"),
    "activity_type": ("activity type", "exercise type", "type", "sport", "workout type"),
    "duration_min": ("duration", "elapsed time", "moving time", "total time", "time", "exercise_duration"),
    "calories": ("calories", "calorie", "kcal", "active calories", "energy"),
    "distance_km": ("distance", "distance (km)", "total distance"),
    "avg_hr": ("avg hr", "average heart rate", "mean heart rate", "avg heart rate"),
    "fat_mass_kg": ("fat mass", "body fat mass", "fat (kg)"),
    "body_fat_pct": ("body fat", "fat ratio", "% fat", "gordura corporal", "gordura"),
}

# Samsung exports one file per data type, named by the type itself.
SAMSUNG_FILE_KINDS = {
    "weight": "weight",
    "step_daily_trend": "steps",
    "pedometer_day_summary": "steps",
    "step_count": "steps",
    "sleep": "sleep",
    "exercise": "session",
    "heart_rate": "recovery",
}

APPLE_TYPES = {
    "HKQuantityTypeIdentifierBodyMass": "weight",
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierRestingHeartRate": "rhr",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv",
    "HKQuantityTypeIdentifierBodyFatPercentage": "body_fat_pct",
    "HKCategoryTypeIdentifierSleepAnalysis": "sleep",
}


@dataclass
class Candidate:
    """One event the importer wants to write, before it touches the log."""
    type: str
    ts: str
    data: dict
    source_row: int

    def key(self) -> Tuple[str, str]:
        """Dedup key.

        Day-granular measurements collapse to one per day. Sessions and meals
        key on the exact timestamp, so two workouts on the same day both
        survive while a re-import of the same workout does not duplicate it.
        """
        if self.type in ("session", "meal"):
            return (self.type, self.ts)
        return (self.type, self.ts[:10])


@dataclass
class Report:
    source: str
    files: List[str]
    candidates: List[Candidate]
    skipped: List[str]
    unmapped_columns: List[str]

    def summary(self) -> str:
        by_type: Dict[str, int] = {}
        for c in self.candidates:
            by_type[c.type] = by_type.get(c.type, 0) + 1
        parts = ", ".join("%d %s" % (n, t) for t, n in sorted(by_type.items())) or "nothing"
        out = ["source detected: %s" % self.source,
               "files read: %s" % ", ".join(self.files),
               "events found: %s" % parts]
        if self.unmapped_columns:
            out.append("columns not mapped: %s" % ", ".join(sorted(set(self.unmapped_columns))[:12]))
        if self.skipped:
            out.append("rows skipped: %d (first: %s)" % (len(self.skipped), self.skipped[0]))
        return "\n".join(out)


# --------------------------------------------------------------------------
# entry points
# --------------------------------------------------------------------------

def detect_source(path: Path) -> str:
    """Guess the export's origin from its filename and first bytes."""
    name = path.name.lower()
    if name.endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            names = " ".join(n.lower() for n in zf.namelist()[:200])
        if "com.samsung" in names:
            return "samsung"
        if "export.xml" in names or "apple_health" in names:
            return "apple"
        if "activities.csv" in names and "media" in names:
            return "strava"
        if "activities.csv" in names:
            return "garmin"
        return "generic"
    if "com.samsung" in name:
        return "samsung"
    if name.endswith(".xml"):
        return "apple"
    if name.startswith("activities"):
        head = _head(path)
        return "strava" if "activity id" in head else "garmin"
    if "withings" in name or name.startswith("weight"):
        return "withings"
    return "generic"


def parse(path: Path, source: Optional[str] = None,
          mapping: Optional[Dict[str, str]] = None) -> Report:
    """Read an export and return the events it would write. Writes nothing."""
    if not path.exists():
        raise InsufficientData("no such file: %s" % path)
    src = (source or detect_source(path)).lower()
    handlers: Dict[str, Callable[[Path, Optional[Dict[str, str]]], Report]] = {
        "samsung": _parse_samsung,
        "apple": _parse_apple,
        "garmin": _parse_garmin,
        "strava": _parse_strava,
        "withings": _parse_generic,
        "generic": _parse_generic,
    }
    if src not in handlers:
        raise InsufficientData(
            "unknown source %r; use one of %s, or 'generic' with --map"
            % (src, ", ".join(sorted(handlers)))
        )
    return handlers[src](path, mapping)


def inspect(path: Path) -> str:
    """Print what is actually in the file, for when an adapter needs fixing."""
    src = detect_source(path)
    lines = ["detected source: %s" % src, ""]
    for name, text in _tabular_members(path):
        rows = _read_csv(text)
        if not rows:
            lines.append("%s: no rows" % name)
            continue
        header = list(rows[0].keys())
        lines.append("%s — %d rows" % (name, len(rows)))
        for col in header:
            field = _match_alias(col)
            lines.append("    %-42s -> %s" % (col[:42], field or "(unmapped)"))
        lines.append("    first row: %s" % json.dumps(rows[0], ensure_ascii=False)[:160])
        lines.append("")
    if not lines[2:]:
        lines.append("no tabular data found; if this is an Apple Health export, "
                     "point at export.xml directly")
    return "\n".join(lines)


def write(report: Report, log_path: Path, logstore_module) -> Tuple[int, int]:
    """Append the candidates. Returns (written, skipped_as_duplicate).

    Re-importing the same export is a no-op: day-granular events dedup on
    (type, day) in the log itself, and this checks before writing so the file
    does not grow without bound on repeated runs.
    """
    existing = set()
    for event in logstore_module.read(log_path):
        if event.type in ("session", "meal"):
            existing.add((event.type, event.ts))
        else:
            existing.add((event.type, event.ts[:10]))

    written = skipped = 0
    for cand in report.candidates:
        if cand.key() in existing:
            skipped += 1
            continue
        try:
            logstore_module.append(log_path, cand.type, cand.data, ts=cand.ts)
            existing.add(cand.key())
            written += 1
        except logstore_module.ValidationError:
            skipped += 1
    return written, skipped


# --------------------------------------------------------------------------
# adapters
# --------------------------------------------------------------------------

def _parse_samsung(path: Path, mapping) -> Report:
    """Samsung Health: one CSV per data type, with a metadata line on top."""
    cands: List[Candidate] = []
    skipped: List[str] = []
    unmapped: List[str] = []
    files: List[str] = []

    for name, text in _tabular_members(path):
        kind = None
        for token, k in SAMSUNG_FILE_KINDS.items():
            if token in name.lower():
                kind = k
                break
        if kind is None:
            continue
        files.append(name)
        rows = _read_csv(text)
        for i, row in enumerate(rows, 1):
            fields, missed = _map_row(row, mapping)
            unmapped.extend(missed)
            when = fields.get("date")
            if not when:
                skipped.append("%s row %d: no date column" % (name, i))
                continue
            cand = _candidate_for(kind, when, fields, i)
            if cand:
                cands.append(cand)
            else:
                skipped.append("%s row %d: no usable value" % (name, i))

    if not files:
        raise InsufficientData(
            "no recognisable Samsung Health files inside %s. Export again from "
            "Samsung Health > Settings > Download personal data, and pass the zip." % path.name
        )
    return Report("samsung", files, cands, skipped, unmapped)


def _parse_garmin(path: Path, mapping) -> Report:
    cands, skipped, unmapped, files = [], [], [], []
    for name, text in _tabular_members(path):
        files.append(name)
        rows = _read_csv(text)
        for i, row in enumerate(rows, 1):
            fields, missed = _map_row(row, mapping)
            unmapped.extend(missed)
            when = fields.get("date")
            if not when:
                skipped.append("%s row %d: no date" % (name, i))
                continue
            made = False
            for kind in ("weight", "steps", "sleep", "recovery", "session"):
                cand = _candidate_for(kind, when, fields, i)
                if cand:
                    cands.append(cand)
                    made = True
            if not made:
                skipped.append("%s row %d: nothing recognisable" % (name, i))
    if not files:
        raise InsufficientData("no CSV found in %s" % path.name)
    return Report("garmin", files, cands, skipped, unmapped)


def _parse_strava(path: Path, mapping) -> Report:
    """Strava exports activities only — no sleep, no HRV, no weight."""
    cands, skipped, unmapped, files = [], [], [], []
    for name, text in _tabular_members(path):
        if "activities" not in name.lower():
            continue
        files.append(name)
        for i, row in enumerate(_read_csv(text), 1):
            fields, missed = _map_row(row, mapping)
            unmapped.extend(missed)
            when = fields.get("date")
            if not when:
                skipped.append("%s row %d: no date" % (name, i))
                continue
            cand = _candidate_for("session", when, fields, i)
            if cand:
                cands.append(cand)
            else:
                skipped.append("%s row %d: no duration" % (name, i))
    if not files:
        raise InsufficientData(
            "no activities.csv in %s. Strava's bulk export puts it at the archive root." % path.name)
    return Report("strava", files, cands, skipped, unmapped)


def _parse_apple(path: Path, mapping) -> Report:
    """Apple Health export.xml, streamed — the file runs to hundreds of MB."""
    import xml.etree.ElementTree as ET

    cands: List[Candidate] = []
    skipped: List[str] = []
    daily: Dict[Tuple[str, str], float] = {}

    handle = _open_xml(path)
    try:
        for _, elem in ET.iterparse(handle, events=("end",)):
            if elem.tag != "Record":
                continue
            kind = APPLE_TYPES.get(elem.get("type", ""))
            raw_date = elem.get("startDate", "")
            value = elem.get("value")
            elem.clear()
            if not kind or not raw_date:
                continue
            day = raw_date[:10]
            if kind == "sleep":
                continue  # sleep needs interval stitching; use the daily summary instead
            try:
                v = float(value)
            except (TypeError, ValueError):
                skipped.append("non-numeric %s on %s" % (kind, day))
                continue
            key = (kind, day)
            if kind == "steps":
                daily[key] = daily.get(key, 0.0) + v
            else:
                daily[key] = v  # last reading of the day wins
    finally:
        handle.close()

    for (kind, day), value in sorted(daily.items()):
        ts = day + "T12:00:00"
        if kind == "weight":
            cands.append(Candidate("weight", ts, {"kg": round(value, 2), "source": "apple"}, 0))
        elif kind == "steps":
            cands.append(Candidate("steps", ts, {"count": int(value), "source": "apple"}, 0))
        elif kind in ("rhr", "hrv"):
            field = "rhr_bpm" if kind == "rhr" else "hrv_ms"
            cands.append(Candidate("recovery", ts, {field: round(value, 1), "source": "apple"}, 0))

    if not cands:
        raise InsufficientData(
            "no importable records found in %s. Export from Health > profile > "
            "Export All Health Data, and point at export.xml inside the zip." % path.name)
    return Report("apple", [path.name], cands, skipped, [])


def _parse_generic(path: Path, mapping) -> Report:
    """Any CSV. With --map, any column layout at all."""
    cands, skipped, unmapped, files = [], [], [], []
    for name, text in _tabular_members(path):
        files.append(name)
        for i, row in enumerate(_read_csv(text), 1):
            fields, missed = _map_row(row, mapping)
            unmapped.extend(missed)
            when = fields.get("date")
            if not when:
                skipped.append("%s row %d: no date column recognised" % (name, i))
                continue
            made = False
            for kind in ("weight", "steps", "sleep", "recovery", "body_comp", "session"):
                cand = _candidate_for(kind, when, fields, i)
                if cand:
                    cands.append(cand)
                    made = True
            if not made:
                skipped.append("%s row %d: no recognised measurement" % (name, i))
    if not files:
        raise InsufficientData("no CSV data found in %s" % path.name)
    if not cands:
        raise InsufficientData(
            "read %d rows but recognised no measurements. Run with --inspect to see the "
            "columns, then pass --map 'weight_kg=Your Column,date=Your Date Column'."
            % len(skipped))
    return Report("generic", files, cands, skipped, unmapped)


# --------------------------------------------------------------------------
# row -> candidate
# --------------------------------------------------------------------------

def _candidate_for(kind: str, when: str, f: Dict[str, str], row_no: int) -> Optional[Candidate]:
    ts = _to_ts(when)
    if ts is None:
        return None

    if kind == "weight":
        kg = _num(f.get("weight_kg"))
        if kg and 25 <= kg <= 400:
            return Candidate("weight", ts, {"kg": round(kg, 2), "source": "import"}, row_no)
        return None

    if kind == "steps":
        n = _num(f.get("steps"))
        if n and n >= 0:
            return Candidate("steps", ts, {"count": int(n), "source": "import"}, row_no)
        return None

    if kind == "sleep":
        hours = _sleep_hours(f.get("sleep_hours"))
        if hours and 0 < hours <= 24:
            data = {"hours": round(hours, 2), "source": "import"}
            score = _num(f.get("sleep_score"))
            if score is not None and 0 <= score <= 100:
                data["score"] = int(score)
            return Candidate("sleep", ts, data, row_no)
        return None

    if kind == "recovery":
        data = {}
        rhr = _num(f.get("rhr"))
        hrv = _num(f.get("hrv"))
        readiness = _num(f.get("readiness"))
        if rhr and 25 <= rhr <= 140:
            data["rhr_bpm"] = round(rhr, 1)
        if hrv and 5 <= hrv <= 300:
            data["hrv_ms"] = round(hrv, 1)
        if readiness is not None and 0 <= readiness <= 100:
            data["readiness"] = int(readiness)
        if data:
            data["source"] = "import"
            return Candidate("recovery", ts, data, row_no)
        return None

    if kind == "body_comp":
        kg = _num(f.get("weight_kg"))
        fat = _num(f.get("fat_mass_kg"))
        pct = _num(f.get("body_fat_pct"))
        if kg and (fat or pct):
            data = {"weight_kg": round(kg, 2), "method": "import"}
            if not fat and pct and 3 <= pct <= 70:
                fat = kg * pct / 100.0
            if fat:
                data["fat_mass_kg"] = round(fat, 2)
                data["ffm_kg"] = round(kg - fat, 2)
            return Candidate("body_comp", ts, data, row_no)
        return None

    if kind == "session":
        minutes = _duration_minutes(f.get("duration_min"))
        if not minutes or not 5 <= minutes <= 300:
            return None
        label = (f.get("activity_type") or "cardio").strip().lower().replace(" ", "_")[:40] or "cardio"
        return Candidate("session", ts, {"session_id": label,
                                         "duration_min": round(minutes, 1),
                                         "notes": "imported"}, row_no)
    return None


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _tabular_members(path: Path) -> Iterator[Tuple[str, str]]:
    """Yield (name, text) for every CSV in a file, folder or zip."""
    if path.is_dir():
        for child in sorted(path.rglob("*.csv")):
            yield child.name, child.read_text(encoding="utf-8", errors="replace")
        return
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if info.filename.lower().endswith(".csv") and not info.is_dir():
                    with zf.open(info) as fh:
                        yield Path(info.filename).name, fh.read().decode("utf-8", errors="replace")
        return
    if path.suffix.lower() == ".csv":
        yield path.name, path.read_text(encoding="utf-8", errors="replace")


def _open_xml(path: Path):
    if path.suffix.lower() == ".zip":
        zf = zipfile.ZipFile(path)
        for info in zf.infolist():
            if info.filename.lower().endswith("export.xml"):
                return zf.open(info)
        raise InsufficientData("no export.xml inside %s" % path.name)
    return path.open("rb")


def _read_csv(text: str) -> List[dict]:
    """Read a CSV, finding the real header row.

    Vendors put junk above it: Samsung Health writes the data-type name on line
    one and the header on line two; some exports add a title or a blank line.
    Rather than guessing from punctuation, try each of the first few lines as
    the header and keep whichever yields the most recognisable columns.
    """
    lines = text.splitlines()
    if not lines:
        return []

    best: Tuple[int, List[dict]] = (-1, [])
    for start in range(min(3, len(lines))):
        body = "\n".join(lines[start:])
        if not body.strip():
            continue
        try:
            dialect = csv.Sniffer().sniff(body[:4096], delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        try:
            rows = [dict(r) for r in csv.DictReader(io.StringIO(body), dialect=dialect)]
        except csv.Error:
            continue
        if not rows:
            continue
        header = [h for h in rows[0].keys() if h]
        score = sum(1 for h in header if _match_alias(h))
        if score > best[0]:
            best = (score, rows)
        if score >= 3:
            break
    return best[1]


def _match_alias(column: str) -> Optional[str]:
    """Map a real column header to a canonical field name.

    Headers arrive as "Avg HR", "avg_hr", "com.samsung.health.weight.weight",
    "Massa (kg)" and every other shape a vendor invents, so separators are
    flattened before matching and the longest alias hit wins.
    """
    col = (column or "").strip().lower().replace("_", " ").replace(".", " ")
    col = re.sub(r"[()\[\]]", " ", col)
    col = re.sub(r"\s+", " ", col).strip()
    if not col:
        return None
    best = None
    for field, aliases in ALIASES.items():
        for raw_alias in aliases:
            alias = raw_alias.replace("_", " ").replace(".", " ")
            if col == alias:
                return field
            if alias in col and (best is None or len(alias) > best[1]):
                best = (field, len(alias))
    return best[0] if best else None


def _map_row(row: dict, mapping: Optional[Dict[str, str]]) -> Tuple[Dict[str, str], List[str]]:
    """Column values keyed by canonical field, plus the columns nothing matched."""
    out: Dict[str, str] = {}
    unmapped: List[str] = []
    reverse = {v.strip().lower(): k for k, v in (mapping or {}).items()}
    for col, value in row.items():
        if value is None or str(value).strip() == "":
            continue
        col_l = (col or "").strip().lower()
        field = reverse.get(col_l) or _match_alias(col)
        if field:
            out.setdefault(field, str(value).strip())
        else:
            unmapped.append(col or "")
    return out, unmapped


def _to_ts(raw: str) -> Optional[str]:
    s = (raw or "").strip().replace("/", "-")
    if not s:
        return None
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if not m:
        m2 = re.match(r"(\d{1,2})-(\d{1,2})-(\d{4})", s)  # dd-mm-yyyy
        if not m2:
            return None
        d, mo, y = m2.groups()
    else:
        y, mo, d = m.groups()
    try:
        day = date(int(y), int(mo), int(d))
    except ValueError:
        return None
    clock = re.search(r"(\d{1,2}):(\d{2})", s)
    hh, mm = (clock.group(1), clock.group(2)) if clock else ("12", "00")
    return "%sT%02d:%s:00" % (day.isoformat(), int(hh), mm)


def _num(raw) -> Optional[float]:
    if raw is None:
        return None
    s = str(raw).strip().replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def _sleep_hours(raw) -> Optional[float]:
    """Sleep arrives as hours, as minutes, or as HH:MM depending on the vendor."""
    if raw is None:
        return None
    s = str(raw).strip()
    clock = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", s)
    if clock:
        return int(clock.group(1)) + int(clock.group(2)) / 60.0
    v = _num(s)
    if v is None:
        return None
    if v > 24:            # minutes
        return v / 60.0
    return v


def _duration_minutes(raw) -> Optional[float]:
    if raw is None:
        return None
    s = str(raw).strip()
    clock = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", s)
    if clock:
        h, mi, sec = clock.group(1), clock.group(2), clock.group(3)
        if sec is None:
            return int(h) * 60 + int(mi)          # HH:MM
        return int(h) * 60 + int(mi) + int(sec) / 60.0
    v = _num(s)
    if v is None:
        return None
    if v > 600:           # seconds
        return v / 60.0
    return v


def _head(path: Path, n: int = 2048) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:n].lower()
    except OSError:
        return ""
