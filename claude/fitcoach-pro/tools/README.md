# tools — every number the assistant reports

Standard library Python, 3.9+. No install step, no dependencies, no network.

```
python3 cli.py [--client DIR | --log FILE] [--json] <command>
```

## Why this exists

A language model performs arithmetic fluently and incorrectly. It will sum four sessions of sets and be off by three; it will divide a calorie target into macros and produce numbers that do not add back up; it will do both with complete confidence and no signal that anything went wrong.

Everything here is deterministic, tested, and refuses when the data cannot support an answer. **A refusal is a feature.** `metrics tdee-observed` exiting with code 2 and "6 of the last 28 days have logged meals, this needs 10" is worth more than a confident number built on nothing.

## Exit codes

| Code | Meaning |
| :-: | :--- |
| 0 | Success |
| 2 | Insufficient data — the message says exactly what is missing |
| 3 | Invalid input — out of range, wrong type, unknown field |

## Modules

| File | Contents |
| :--- | :--- |
| `metrics.py` | BMR (Mifflin, Katch), maintenance by components or multiplier, macros, EMA weight trend, rate of change with safety verdict, measured TDEE, 1RM, projection |
| `volume.py` | Exercise catalog, weekly sets per muscle, MEV/MAV/MRV verdicts, movement-pattern coverage, substitution by limitation |
| `load.py` | Acute:chronic workload ratio, deload decision, session load by sets or tonnage |
| `logstore.py` | Append-only JSONL event log with typed schema, range checks and newest-wins dedup |
| `ingest.py` | Import Samsung Health, Garmin, Apple Health, Strava and generic CSV exports |
| `dashboard.py` | Render the log as a self-contained HTML page, inline SVG, no dependencies |
| `sheet.py` | Validate a filled-in client sheet against the program it should render |
| `cli.py` | Single entry point |
| `../data/exercises.json` | 77 exercises: movement pattern, equipment, primary and secondary muscles, axial flag, substitution chains |

## Design notes worth knowing

**Maintenance defaults to the component method** — BMR + NEAT + training + thermic effect — instead of one activity multiplier. A multiplier gives a single number and hides which term is the guess. It is always NEAT, and summing the parts shows it.

**The weight trend is an EMA on a daily grid**, alpha 0.25, which behaves like a 7-day window. Missing days carry the previous value forward, so a skipped weigh-in does not tilt the slope. Rate of change is a least-squares fit over the smoothed series, not first-value-minus-last.

**Measured TDEE uses 7,700 kcal/kg**, which is a working convention rather than a constant, and a 28-day window because early weight change is mostly glycogen and water at a very different energy cost.

**Indirect sets are reported in their own column at half weight.** That is a reporting convention from the literature, not validated physiological equivalence, and the tool keeps them separate so nobody can quietly use them to justify low direct volume.

**The log is append-only.** Corrections are appended and the newest event for a key wins. Day-granular types (weight, sleep, steps) dedup on `(type, day)` so a re-import is a no-op; session and meal events key on the timestamp so two on the same day both survive. Nothing is ever rewritten, so a mistake cannot destroy a client's history.

**Validation refuses rather than coerces.** A weight of 900 kg, a soreness of 9 on a 1-5 scale, or a field the schema does not know are all errors, and nothing is written to the file when one occurs.

## Why file imports and not APIs

Every fitness service lets you export your data, and every API needs credentials, an OAuth flow, a refresh-token dance, and breaks when the vendor reorganises it. Samsung Health — the one that matters most for Android users — has no public API at all since the SDK became a closed partnership.

A file importer runs offline, needs no secrets, covers services that have no API, and still works after the vendor redesigns their platform. The cost is that the trainer downloads a file. That is a good trade.

Column names do drift between vendor releases, so every adapter matches by alias, reports what it could not place, and `--inspect` prints the real headers when a mapping needs fixing. The bundled fixtures are synthetic — no real vendor export was available while writing this — so the first real file from a given service may still need an alias added. That is a one-line change in `ALIASES`.

## Tests

```
python3 -m unittest discover -s tools/tests -t tools
```

137 tests covering hand-checked BMR fixtures, macro arithmetic, EMA smoothing, every rate verdict, the refusal thresholds, append-only and idempotency guarantees, volume landmarks by profile, ACWR bands, deload signal counting, each import adapter, re-import idempotency, the dashboard's degradation, escaping and self-containment, sheet validation, local-catalog merging and validation, and structural parity between the two language versions.

The repository's `build.sh` runs them. If they fail, the numbers cannot be trusted and nothing downstream matters.
