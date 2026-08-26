# Changelog

## 2.4.0 — 2026-08-26

Six blind spots closed, from a physiological and operational review.

**ACWR now weights sets by systemic cost.** Four sets of heavy deadlift and four of lateral raise were counted identically, so a client could trade arm work for axial loading and never trip the ratio — the exact spike it exists to catch. Axial compounds count 1.4, supported compounds 1.0, unilateral 0.8, isolation 0.5, core 0.4; unknown exercises weigh 1.0, never zero. A regression test swaps three weeks of curls for a week of deadlifts: flat counting reads 1.00, weighted reads a spike.

**Expenditure corrected for high adiposity.** Above BMI 30 with no body-composition data, `metrics targets` now warns that Mifflin-St Jeor takes total body weight and overestimates by 200-400 kcal — enough to turn a prescribed deficit into maintenance. With fat-free mass known it uses Katch-McArdle alone; `--adjusted-weight` applies the Devine-based clinical convention otherwise.

**1RM refuses above 10 reps** instead of 12, with an explanation: a 15-rep set measures fatigue resistance, not maximal force. Writing the test surfaced that Epley and Brzycki intersect exactly at 10 reps, so formula agreement is worthless as a confidence signal there — the caution is now driven by rep count, and the crossing point is documented in the test.

**Hydration, fibre and per-meal protein** now come out of `metrics targets`. They were in the reference file and computed by nobody, so they quietly got dropped. A protein split too thin across too many meals raises a warning.

**Catalog grown from 77 to 110 exercises** — adductor and abductor machines, hip thrust machine, Smith variations, T-bar rows, preacher curls, rope pushdowns, French press, 45° leg press, standing leg curl and more, with Portuguese names where a Brazilian gym uses them. Substitution chains extended to match.

**`cohort`** — one screen for every client. The rest of the CLI operates on one at a time, which is right for prescribing and wrong for Monday morning. It ranks the whole roster by severity: load spikes, unsafe rate of change, stalled progress, and anyone who stopped logging. Measured against a roster-wide reference date, because using each client's own last entry reported everyone as current — including the one who disappeared three weeks ago.

**Client sheet gained backup and restore.** The record lived only in `localStorage`, which the browser clears without warning and which does not survive a new phone — and outside claude.ai there was no export route at all. A copy-and-paste text panel works in every browser, and the `.md` export falls back to it instead of just reporting failure.

**Portion equivalence tables** in the nutrition reference: what delivers 20 g of protein, 30 g of carbohydrate, 10 g of fat, in the foods people actually buy. A macro target is useless to a client who cannot turn it into a plate. Marked as education, not prescription, with the 10-20% variation stated.

35 new tests (172 total).

## 2.3.1 — 2026-08-26

**The test suite now runs from either language copy.** It ships inside both skills, but had the English template filename, placeholder names and folder layout hard-coded — so running it from `fitcoach-pro-pt-BR` produced 16 errors and a failure, and the parity class silently compared the translated copy against itself.

The suite now discovers which copy it is running in, picks the matching template and placeholder set, and locates both skills explicitly rather than relative to itself. When only one language version is installed, the parity tests skip with a reason instead of passing vacuously.

`build.sh` runs the suite from **both** copies, so this cannot regress. A trainer who installs only the Portuguese skill can verify their install.

Reported by an external review; the failure was larger than described.

## 2.3.0 — 2026-08-26

Three gaps closed, from an external review of the package structure.

**`sheet check`** — validates a filled-in client sheet before it reaches anyone. Until now nothing verified the rendered file: a `{{PLACEHOLDER}}` that was never substituted, the template's bundled example program left in place, a load field on a bodyweight exercise, an isometric asking for repetitions, a start date that is not a Monday, or an exercise that diverges from `program.md` all reached the client looking finished. Exit code 3 means do not send it.

**Extensible exercise catalog** — a local `clients/<name>/exercises.json` (picked up automatically) or a file passed with `--catalog` adds to or overrides the bundled 77 entries and survives package updates. No packaged list survives contact with a real gym: machines vary by brand and trainers have their own variations. Local entries are validated against the same pattern and muscle vocabularies as bundled ones, and refuse with the valid list when they do not match. Example in `examples/local-catalog-example.json`.

**Better exercise-name resolution** — "one-arm dumbbell row" now resolves to "One-arm supported dumbbell row" through word-overlap matching when a contiguous substring fails. Previously it was rejected, and those sets vanished from the volume audit — the exact failure the audit exists to prevent.

**Translation parity tests** — the two language versions are now guarded against drifting apart: same file count, same section count per file, identical tool copies, and both skills declaring the three hard rules. The test caught a stale copy on its first run.

28 new tests (137 total).

## 2.2.0 — 2026-08-26

Documentation for the people this was built for.

**[`docs/TRAINER-GUIDE.md`](docs/TRAINER-GUIDE.md)** and **[`docs/GUIA-DO-PERSONAL.md`](docs/GUIA-DO-PERSONAL.md)** — a guide for personal trainers with no technical background. Every other document in this repository assumes a terminal, JSON and Python; the audience assumes none of them.

Covers: what the package changes about an AI assistant's behaviour, an honest comparison of the three ways to run it, step-by-step installation on Claude and ChatGPT with no command line, a full first-client conversation showing exactly what to type, the weekly routine, why the tool sometimes refuses to answer, a troubleshooting table, and a glossary of every term that appears in output — RIR, MEV, ACWR, EMA, NEAT.

Includes the honest caveat that ChatGPT cannot always execute the bundled calculators, and what to do about it.

Both guides are linked from the top of both READMEs, above the technical install instructions.

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
