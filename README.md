# FitCoach Pro

**A prescription methodology for personal trainers, packaged as an AI skill — with the arithmetic taken away from the model.** Runs on Claude and on ChatGPT. Portuguese version: [`docs/README.pt-BR.md`](docs/README.pt-BR.md).

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

> ### 👋 Not a developer?
> **[Read the trainer's guide](docs/TRAINER-GUIDE.md)** — installation with no terminal, a real conversation from first client to finished sheet, and a glossary. Written for people who have never installed anything like this.
> Em português: **[Guia do personal trainer](docs/GUIA-DO-PERSONAL.md)**.

---

Most "AI personal trainer" prompts fail the same way: ask for a program and you get twelve exercises, four sets each, no idea which gym the client trains at, no screening, and a body fat percentage quoted to one decimal place from a wrist sensor.

This repository is the opposite bet. It does not try to replace the trainer's judgment — it structures it. Screening before prescription. Split chosen from the client's real schedule, including the bad week. Exercises chosen from equipment that actually exists. Weekly volume audited per muscle group. Progression by an explicit criterion instead of vibes. And, throughout, an instruction the model does not follow on its own: **say when a number is an estimate.**

## What makes it different

**The model never does the math.** Calories, macros, BMR, TDEE, weight trends, weekly set counts per muscle, 1RM, training load — every number comes from tested Python in [`tools/`](claude/fitcoach-pro/tools), not from the model's head. This is the difference between a prompt that warns about hallucination and a package that removes the opportunity for it.

**It refuses instead of guessing.** `metrics tdee-observed` exits with an error and "6 of the last 28 days have logged meals, this needs 10" rather than producing a confident number from nothing. Same for a rate of change under 14 days, or an ACWR under 21 days of history. The refusals are tested.

**It refuses to prescribe without an intake.** Ask for a program without giving days, equipment, training history, age and injuries, and it asks first. A plan built on assumption is guaranteed rework.

**Progressive disclosure.** `SKILL.md` is a router. The model loads the volume rules when it is building a block and the bioimpedance critique when it is reading a body composition report — not all 45 KB on every message.

**It tells you what it made up.** Every deliverable closes with a line naming what was estimated, inferred or filled in — the starting load, the exercise depending on unconfirmed equipment, the calculation built on an approximate input. That is what makes review possible instead of theatrical.

**It came out of an audit, not a brainstorm.** The methodology was extracted from a real 8-week block, built by auditing an AI-generated training report that was full of false precision. Several rules in `references/` are written as warnings because of specific errors that report made. [`06-body-assessment.md`](claude/fitcoach-pro/references/06-body-assessment.md) exists almost entirely for that reason.

## The numbers, deterministically

```console
$ python3 tools/cli.py metrics targets --weight-kg 71 --height-cm 178 --age 41 \
      --sex male --ffm-kg 57.7 --sessions-per-week 4 --goal gain
BMR 1619 kcal (Mifflin 1622 / Katch 1616, spread 6)
  NEAT +194 · training +183 · TEF +222
maintenance ~2218 kcal (likely 2085-2351)
target 2518 kcal (+300)
protein 128 g · fat 64 g · carbs 358 g

$ python3 tools/cli.py --client clients/maria metrics tdee-observed
measured expenditure ~2665 kcal/day over 28 days (28 days of logged intake,
mean 2100 kcal, weight -1.98 kg)

$ python3 tools/cli.py --client clients/joao metrics rate --goal loss
cannot answer: need at least 14 days of weight data; have 5. Water and
glycogen noise dominates shorter windows.
```

Maintenance defaults to the **component method** — BMR plus NEAT plus training plus the thermic effect of food — instead of one activity multiplier, because a multiplier hides which term is the guess. It is always NEAT.

`volume check` sums weekly sets per muscle from a program file, judges each group against minimum effective and maximum recoverable volume, reports indirect sets in a separate column, and names any movement pattern the week does not cover. 77 exercises in [`data/exercises.json`](claude/fitcoach-pro/data/exercises.json), with substitution chains for shoulder, back, knee, wrist and elbow limitations.

Full documentation in [`tools/README.md`](claude/fitcoach-pro/tools/README.md). 109 tests, standard library only, no install step.

## Wearable data, without an API

```console
$ python3 tools/cli.py --client clients/maria ingest samsung_health_export.zip
source detected: samsung
events found: 7 session, 20 sleep, 20 steps, 20 weight
written: 67 · already present: 0
re-running this import is a no-op.
```

| Source | Hand it | What arrives |
| :--- | :--- | :--- |
| **Samsung Health** | The zip from Settings → Download personal data | Weight, steps, sleep, heart rate, sessions |
| **Garmin** | `Activities.csv` from Connect, or the full export | Sessions and daily files |
| **Apple Health** | `export.xml` from Health → profile → Export All Health Data | Weight, steps, resting HR, HRV |
| **Strava** | `activities.csv` from the bulk export | Cardio sessions only |
| **Withings, Oura, Whoop, Fitbit, a gym scale, a spreadsheet** | Any CSV | Whatever columns it recognises |

**Files, not APIs** — deliberately. Every service exports; Samsung Health has had no public API since the SDK became a closed partnership; and every OAuth integration needs credentials and breaks when the vendor reorganises it. A file importer runs offline, needs no secrets, and still works in five years.

Re-importing the same file is a no-op. When an export does not match, `ingest --inspect` prints the real column names and `--map 'weight_kg=Massa (kg)'` fixes it in one flag.

## The dashboard

`dashboard` renders the log as one self-contained HTML file — inline SVG, no CDN, no JavaScript, opens offline.

The chart that earns its place is **direct sets per muscle against that muscle's own landmarks**. A weekly total of 60 sets can be four muscles or twelve; only this tells you which, and it flags the group sitting at zero that a healthy-looking total hides.

Nothing is invented: whatever cannot be computed goes into a "Not shown yet" block naming the data it needs.

## Install

Not comfortable with a terminal? Use the **[trainer's guide](docs/TRAINER-GUIDE.md)** instead — it covers Claude and ChatGPT without a single command.

### Claude Code

```bash
git clone https://github.com/danilogj/fitcoach-pro.git
cp -r fitcoach-pro/claude/fitcoach-pro ~/.claude/skills/
```

The skill loads on its own when the topic is a client, a sheet, a prescription, load, RIR, volume, a check-in, macros or body composition. Force it with `/fitcoach-pro`.

For the Portuguese version, copy `claude/fitcoach-pro-pt-BR` instead.

### Claude app

Settings → Capabilities → Skills → Upload, with `claude/fitcoach-pro` zipped.

### ChatGPT

1. Explore GPTs → Create → Configure
2. **Instructions:** paste [`gpt/instructions.md`](gpt/instructions.md) (6.9k of the 8k character limit)
3. **Conversation starters:** the four lines in [`gpt/conversation-starters.md`](gpt/conversation-starters.md)
4. **Knowledge:** upload the 10 files in [`gpt/knowledge/`](gpt/knowledge)
5. **Capabilities:** Code Interpreter only — browsing and image generation add nothing here

Portuguese equivalents live in [`gpt/pt-BR/`](gpt/pt-BR).

**Verify the install** by asking for an intake for a new client. It should open with seven screening questions, not with a training plan.

## What is inside

| | |
| :--- | :--- |
| [`01-principles.md`](claude/fitcoach-pro/references/01-principles.md) | The six principles that govern every other rule |
| [`02-intake-screening.md`](claude/fitcoach-pro/references/02-intake-screening.md) | Adapted PAR-Q+, red flags, profile classification, constraints |
| [`03-program-design.md`](claude/fitcoach-pro/references/03-program-design.md) | Splits by available days, selection by equipment, volume audit, periodization |
| [`04-progression-adjustment.md`](claude/fitcoach-pro/references/04-progression-adjustment.md) | Double progression, the ladder, log analysis, check-in, plateau |
| [`05-nutrition.md`](claude/fitcoach-pro/references/05-nutrition.md) | Metabolic estimate, macro targets, supplements, adjustment rules |
| [`06-body-assessment.md`](claude/fitcoach-pro/references/06-body-assessment.md) | Bioimpedance taken apart, protocol, circumferences, wearables, imports |
| [`07-cardio.md`](claude/fitcoach-pro/references/07-cardio.md) | Zones, intensity distribution, the interference effect, steps and NEAT |
| [`08-deliverables.md`](claude/fitcoach-pro/references/08-deliverables.md) | Sheet, progress report, client messaging |

[`INDEX.md`](claude/fitcoach-pro/references/INDEX.md) routes a question to the right file and section, so the model loads what it needs instead of everything.

Plus fillable templates for intake, program and log, the deterministic tools, and the client sheet below.

## The client sheet

[`client-sheet.template.html`](claude/fitcoach-pro/assets/client-sheet.template.html) — a single offline page the client uses on their phone during the session.

It shows the prescription for every set, logs load and reps set by set, displays last week's numbers underneath for comparison, runs a rest timer, applies the week's phase automatically (introduction, full volume, deload) and exports the log as Markdown — which is exactly the format the skill analyzes at the check-in.

Works as a local file, hosted at a URL, or published as a Claude Artifact. Fill in the `{{PLACEHOLDERS}}` documented in [`08-deliverables.md`](claude/fitcoach-pro/references/08-deliverables.md).

## Real case

[`examples/case-01-hypertrophy-41m`](examples/case-01-hypertrophy-41m) — a real block in progress, published with consent, numbers unchanged: intake, program, nutrition target and baseline assessment, with the reasoning behind each decision.

**The training log is not there yet**, because the block started recently and the data does not exist. It gets published when it does. Every methodology looks convincing in a case study written after the outcome is known.

## Read this before installing

**[`DISCLAIMER.md`](DISCLAIMER.md)** — the short version:

You are the responsible professional, always. AI hallucinates, and it does so with a straight face — inventing loads, set volumes, calorie math, contraindications and citations. That is inherent to the technology and no update fixes it. **Every output must pass through your eyes before it reaches a client.** This project does not diagnose, does not clear anyone to train, and does not replace a registered dietitian.

## Credits

The architecture owes specific debts to four open-source projects, read closely while building this:

- **[Yuvasee/trainer](https://github.com/Yuvasee/trainer)** (MIT) — the "never do mental math" contract, the append-only log with a typed schema, adaptive TDEE from real intake, and refusing rather than guessing. The strongest of the skills surveyed.
- **[barcia/running-coach-skill](https://github.com/barcia/running-coach-skill)** (MIT) — quantified load management and prescribing by individualized zones rather than fixed heart rates.
- **[revfactory/harness-100](https://github.com/revfactory/harness-100)** (Apache 2.0) — per-muscle volume landmarks and periodization models.
- **[H1an1/health-coach](https://github.com/H1an1/health-coach)** (MIT) — wearable ingestion and longitudinal reporting patterns.

No code was copied; the ideas were, and they made this better.

## Contributing

Corrections to the methodology are welcome, especially with a source. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

After editing anything under `claude/`, run `./build-gpt.sh` to regenerate the GPT knowledge folders from the same source.

## License

Apache License 2.0 — commercial use and forks allowed, attribution preserved via [`NOTICE`](NOTICE).

Built by **Danilo Gouveia Jorge**, São Paulo, Brazil.
