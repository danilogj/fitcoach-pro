# Contributing

## What is welcome

**Corrections to the methodology**, especially with a source. If a range, a rule or a claim in `references/` is wrong or outdated, open an issue with the correction and the reference. Being wrong in public is the fastest way this gets better.

**Field reports.** You ran this with a real client and something broke — the skill prescribed equipment the gym did not have, the volume audit missed a group, the log analysis went generic. Open an issue describing what you asked and what came back.

**Translations.** English and Portuguese exist. Another language means a full `references/` set plus the skill router.

**Exercise substitutions** for equipment or limitations not covered in `03-program-design.md`.

## What is not

Adding exercises for the sake of variety, protocols without evidence, or "advanced" methods whose main effect is looking advanced. The bar is the same one the skill applies to itself: say what is established, what is convention, and what is an estimate.

## Ground rules

**Source your claims.** "Everybody knows" is not a source. Neither is a YouTube video. If the evidence is weak, say it is weak — the project already does that in several places and it is a feature.

**Do not add false precision.** No body fat percentages to one decimal place, no calorie targets to the single digit, no fractional set counting presented as physiology.

**Keep the safety limits intact.** Screening, red flags, referral thresholds and scope-of-practice boundaries are not up for negotiation in a pull request.

## Editing workflow

The source of truth is `claude/fitcoach-pro/` (English). Everything else is generated:

```bash
./build.sh
```

It copies `tools/` and `data/` into the pt-BR skill, rebuilds both GPT knowledge folders, and runs the test suite. Run it after editing anything under `claude/fitcoach-pro/` and include the regenerated files in the same commit — otherwise the copies drift apart in silence, which is the exact failure this script exists to prevent.

Both language versions should stay in sync. If you can only do one, say so in the PR and open an issue for the other.

## Changing the tools

Every number the assistant reports comes from `tools/`. Two rules:

1. **A behavior change needs a test.** New calculation, new threshold, new refusal — the test comes with it. `build.sh` fails the build if the suite fails.
2. **Prefer refusing to guessing.** If a function cannot answer honestly with the data it has, it raises `InsufficientData` with a message naming what is missing. `metrics tdee-observed` refusing below 10 logged meal-days is not a limitation to work around; it is the most valuable line in the module.

```bash
cd claude/fitcoach-pro && python3 -m unittest discover -s tools/tests -t tools
```

Standard library only. No dependency gets added to this package without a very good reason — a personal trainer should be able to run it on whatever Python their machine already has.

## Adding exercises

`data/exercises.json` is the catalog. An entry needs an id, a name, a movement pattern, the equipment required, and primary and secondary muscles. Mark `axial: true` if it loads the spine — the substitution logic for back pain depends on that flag being right.

If the exercise substitutes for something in a specific limitation, add it to the relevant chain under `substitutions`. Substitutes must stay inside the same movement pattern; the tests enforce it.

## The client sheet

`client-sheet.template.html` is plain HTML with no build step and no dependencies. If you change the JavaScript, verify it:

```bash
node --check <(sed -n '/<script>/,/<\/script>/p' client-sheet.template.html)
```

and open the filled template in a browser before opening the PR. It is the one file where a syntax error reaches a client mid-workout.
