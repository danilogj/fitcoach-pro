# Changelog

## 2.1.0 — 2026-08-26

Data goes in without typing, and comes out as a page.

**`ingest`** — imports exported files from **Samsung Health** (the zip from Download personal data), **Garmin** (Connect CSV), **Apple Health** (`export.xml`, streamed so a 500 MB file does not have to fit in memory), **Strava** (bulk export) and any CSV at all.

Deliberately files rather than APIs: every service exports, Samsung Health has no public API since the SDK became a closed partnership, and every OAuth integration needs credentials and breaks on vendor redesigns. A file importer runs offline, holds no secrets, and survives.

- Re-importing is a no-op — day-granular measurements dedup on the day, sessions on the exact timestamp, so two workouts on one day both survive.
- Columns match by alias with separators flattened, so `com.samsung.health.weight.weight`, `Avg HR` and `Massa (kg)` all land correctly. Portuguese aliases included.
- `--inspect` prints the real headers and what each mapped to; `--map 'weight_kg=Column'` fixes an unrecognised export in one flag.
- `--dry-run` reports what would be written without writing.
- Values outside physiological range are dropped, never stored.

**`dashboard`** — renders the log as one self-contained HTML file. Inline SVG, no CDN, no JavaScript, opens offline and survives being emailed.

- Weight trend with daily readings and the goal line, rate with its safety verdict, measured expenditure, weekly sets, acute:chronic load, sleep, steps, and load progression on the most-trained lifts.
- **Direct sets per muscle against that muscle's own landmarks** — the chart a weekly total cannot replace, with muscles below MEV or above MRV flagged in the axis label so a group at zero is visible instead of hidden.
- Prefers the last finished week, and labels the current one "(in progress)" when it uses it.
- Never invents a section: whatever cannot be computed goes to a "Not shown yet" block naming the missing data.

**31 new tests** (109 total) covering each adapter, re-import idempotency, date and duration formats across vendors, dashboard degradation, HTML escaping and self-containment.

`dashboard.py` is excluded from the GPT knowledge folders — the Builder caps them at 20 files, and rendering a page is better done on the trainer's machine.

## 2.0.0 — 2026-08-26

The model stopped doing arithmetic.

**Deterministic tools** (`claude/fitcoach-pro/tools/`) — standard-library Python, no install step, 78 tests:

- `metrics.py` — BMR by Mifflin and Katch, maintenance by component breakdown or activity multiplier, macro split with calorie floors, EMA weight trend, rate of change with a safety verdict, **measured TDEE from real intake against real weight change**, 1RM, time-to-goal projection.
- `volume.py` — 77-exercise catalog, weekly sets per muscle, MEV/MAV/MRV verdicts scaled by training profile, movement-pattern coverage, substitution chains for shoulder, back, knee, wrist and elbow limitations.
- `load.py` — acute:chronic workload ratio, deload decision requiring two independent signals, session load by sets or tonnage.
- `logstore.py` — append-only JSONL event log with typed schema, range validation and newest-wins dedup. Corrections are appended; a client's history cannot be overwritten.
- `cli.py` — one entry point. Exit code 2 means insufficient data, with the missing piece named.

**The three hard rules** now open both skills: never do mental math, state lives in files, and without enough data refuse rather than guess.

**New reference** `07-cardio.md` — zones, 80/20 intensity distribution, the interference effect handled honestly, steps and NEAT as the fat-loss lever people ignore. Deliverables moved to `08`.

**`INDEX.md`** routes a question to the right file and section instead of loading everything.

**Expanded:** per-muscle volume landmarks (`01`), graceful intake degradation — ask for the one missing field, not the whole interview (`02`), ACWR and the deload decision (`04`), measured versus formula expenditure (`05`), wearable data with explicit limits on what each signal is worth (`06`).

**`build.sh`** replaces `build-gpt.sh`: syncs tools into the pt-BR skill, regenerates both GPT knowledge folders including the runnable Python, and runs the test suite.

**GPT instructions** carry the three hard rules and explain running the tools through Code Interpreter — with the instruction to give ranges and say so when Code Interpreter is unavailable, rather than computing silently.

**Credits** to `Yuvasee/trainer`, `barcia/running-coach-skill`, `revfactory/harness-100` and `H1an1/health-coach`, whose architecture ideas shaped this release.

## 1.0.0 — 2026-08-26

First public release.

**Methodology** — seven reference files: prescription principles, intake with adapted PAR-Q+ screening, program design by equipment and schedule, double progression with an adjustment ladder, metabolic estimation and macro targets, body assessment with a full critique of bioimpedance, and deliverables.

**Claude skill** — `SKILL.md` as a progressive-disclosure router over the references. English and Portuguese.

**Custom GPT** — instructions under the character limit plus knowledge files generated from the same source.

**Client sheet** — offline single-page training diary with set-by-set logging, rest timer, automatic block phasing and Markdown log export.

**Real case** — `examples/case-01-hypertrophy-41m`, a block in progress. Log pending until the data exists.

**Safety** — `DISCLAIMER.md` covering hallucination, the professional's review duty, scope of practice and referral thresholds.
