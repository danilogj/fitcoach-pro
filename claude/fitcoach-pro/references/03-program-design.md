# Program design — building the block

> **Keywords:** build a program, split, full body, upper lower, push pull legs, exercise selection, volume per muscle group, sets, reps, rest, warm-up, ramp sets, exercise substitution, periodization, block, deload, introduction week.

Build order: **available days → split → movement patterns → exercises the equipment allows → volume → block periodization.** Never start from a list of exercises.

---

## 1. Split by available days

Choose from the client's real schedule, bad weeks included.

| Days | Split | Structure | Who for |
| :-: | :--- | :--- | :--- |
| 2 | Full body A / B | Each session covers the whole body, different emphases | Any profile. Volume per group lands at 8-12 sets — enough for a beginner and for maintenance. |
| 3 | Full body A / B / C | Whole body, rotating emphasis | **The best option for a beginner.** Frequency of 3× per movement pattern accelerates motor learning. |
| 3 | Upper / Lower / Full | Alternative for a time-limited intermediate | Allows more volume per upper session. |
| 4 | **Upper / Lower ×2** | Upper A · Lower A · Upper B · Lower B | The gold standard for intermediates. Frequency of 2× per group, distributed volume, axial load easy to concentrate. |
| 4 | Push / Pull / Legs / Upper | Variant when the client wants more arm work | Less elegant for recovery. Only with a reason. |
| 5 | PPL + Upper / Lower | — | Advanced intermediate with proven adherence. Do not prescribe 5 days to someone who fails at 4. |
| 6 | PPL ×2 | — | Advanced. Requires sleep, food and history. Rarely worth it. |

**Sanity rule:** prescribe the split the client completes in a bad week, and treat extra days as a bonus. The reverse produces a program that fails one week in three.

### Weekly distribution when days get missed

Write this into the program; do not leave it to improvisation.

| Situation | What to do |
| :--- | :--- |
| Missed 1 day | Continue in order. The missed day is gone and does not change the outcome. |
| 4-day program, only 3 happened | Odd week: Upper A · Lower A · Upper B — even week: Lower A · Upper B · Lower B. Alternating, nothing is systematically left out. |
| 4-day program, only 2 happened | Odd week: Upper A · Lower A — even week: Upper B · Lower B. |
| Missed the whole week | Resume at the **previous week's** volume, not the scheduled one. A week behind does no harm; coming back over the top does. |

---

## 2. Movement patterns before exercises

Every upper session covers: **horizontal push, vertical push, horizontal pull, vertical pull**, plus lateral and rear delt, plus direct arm work if volume allows.

Every lower session covers: **knee-dominant, hip-dominant, unilateral**, plus calves and core.

Only after the patterns are closed do you pick exercises — and you pick from what the gym has.

### Selection by equipment

| Pattern | Barbell and bench | Dumbbells only | Machines and cables only | No equipment |
| :--- | :--- | :--- | :--- | :--- |
| Horizontal push | Barbell bench press | Dumbbell bench press | Chest press machine, pec deck | Push-up, feet-elevated push-up |
| Vertical push | Overhead press | Dumbbell shoulder press | Shoulder press machine | Pike push-up |
| Vertical pull | Pull-up | Pull-up | Lat pulldown | Pull-up on any solid bar |
| Horizontal pull | Bent-over row | **Supported one-arm row** | Seated cable row, machine row | Inverted row under a table |
| Knee-dominant | Back squat | Goblet squat, Bulgarian split squat | Leg press, hack squat, leg extension | Bodyweight squat, lunge |
| Hip-dominant | Romanian deadlift | Dumbbell RDL, hip thrust | Lying leg curl, cable pull-through | Hip thrust, single-leg RDL |
| Unilateral | Barbell lunge | Bulgarian split squat, lunge, walking lunge | Single-leg press | Split squat on a couch, assisted pistol |

**When the gym has something the catalog does not** — a machine brand, a variation you prescribe under your own name — add it to `clients/<name>/exercises.json` and it is picked up automatically. Local entries add to or override the bundled catalog and survive package updates; the format is in `examples/local-catalog-example.json`. An exercise the catalog cannot resolve is silently absent from the volume audit, which is exactly the error the audit exists to prevent.

**Substitution rule:** swap inside the same pattern, never across patterns. Replacing a squat with a leg press is acceptable; replacing a squat with a leg extension is not — that removes the hips and the core from the equation.

### Substitutions for pain or limitation

| Complaint | Swap to |
| :--- | :--- |
| Shoulder hurts on barbell bench | Dumbbell press (neutral or 45° grip), or light incline. Range of motion to where it stops hurting. |
| Shoulder hurts pressing overhead | Angled press (bench at 60°), lateral raise, or remove the vertical push from the block. |
| Knee hurts on squats | Bulgarian split squat, box squat, leg press with high foot placement, partial-range leg extension. |
| Low back hurts on deadlift or squat | Hip thrust, lying leg curl, light goblet squat. Zero axial load until it resolves. |
| Wrist hurts on the barbell | Dumbbells with a neutral grip. |
| Cannot complete 6 pull-ups | Negatives — jump up, lower over 4 s — or lat pulldown until they get there. Past 12 clean reps, add load. |

---

## 3. Sets, reps, rest

| Goal | Rep range | Rest | Note |
| :--- | :--- | :--- | :--- |
| Strength (main compound) | 3-6 | 3-5 min | Short rest here is the most common error and sabotages the goal itself. |
| Hypertrophy (compound) | 6-10 | 2-3 min | Best cost-benefit zone. |
| Hypertrophy (isolation) | 10-15 | 60-90 s | |
| Endurance, metabolic work | 15-25 | 45-60 s | A complement, not a base. |

**The range matters less than proximity to failure.** Hypertrophy occurs from 5 to 30 reps as long as the set finishes close to failure. The range exists to manage fatigue and time, not because there is a magic window.

**Warm-up.** Before the working sets of heavy compounds: a ramp of 3 sets at roughly 50%, 70% and 85% of the working load, 3-5 reps, far from failure. It costs 4 minutes. On isolation work, one light set is enough. Skip the generic 10 minutes of treadmill — it does not warm up the pattern about to be trained.

**Antagonist supersets** (biceps/triceps, chest/back) save time with no meaningful performance cost. Use them at the end of the session, never on heavy compounds.

---

## 4. Volume — closing the math

Add up **hard sets per muscle group per week** and check against the profile's range (`02-intake-screening.md`).

Indirect sets — biceps in a row, triceps in a press — are usually counted as fractions in the literature. **That is methodological convention, not validated physiological equivalence.** Use it as a signal that a group is not at zero, never as a justification for prescribing low direct volume.

Always build the audit table, and hand it to the trainer with the program:

| Group | Direct sets | Indirect | Total |
| :--- | :-: | :-: | :-: |
| Chest, back, delts (front/side/rear), biceps, triceps, quads, hamstrings, calves, core | … | … | … |

If any major group falls outside the range, the program is not finished. The rear delt is the most forgotten group and the one that most defines shoulder width — check it last, and always.

---

## 5. Block periodization

Standard block: **8 weeks**. For a beginner, 12 weeks of simple linear progression works better.

| Weeks | Phase | What changes |
| :--- | :--- | :--- |
| 1-3 | **Introduction** | One set fewer per exercise, with a **floor of 2**. Cutting a 2-set exercise to 1 is not reduced volume, it is no volume. |
| 4-6 | **Full volume** | The program as written. |
| 7 | **Deload** | Sets at roughly 60% of prescribed (floor of 2), **load maintained**, RIR 3-4. Volume is what taxes recovery; intensity preserves the stimulus. |
| 8 | **Reassessment** | Full volume plus measurements plus the decision on the next block. |

**When to pull the deload forward.** If two or more of these appear together for more than a week: performance dropping in two consecutive sessions on the same exercises, sleep worsening with no other explanation, persistent joint pain that does not clear with the warm-up, appetite falling during a surplus, consistent loss of desire to train.

---

## 6. Contingency plans — write them into the program

The plan assumes flawless execution. Life does not cooperate. These rules exist so the client **adapts instead of skipping** — skipping is the only error that costs the whole block.

### Showed up with no energy — cut in this order

1. Direct arm work
2. The second shoulder exercise
3. Core
4. One set from each accessory
5. One set from each compound

**Never cut the first exercise of the day.** It carries the stimulus. Reducing sets always beats eliminating a movement pattern.

### Only 30-40 minutes — the short version

Write the short version of every session alongside the program: the highest-value movements, reduced volume, same order. Typically the first 3-4 exercises at 2-3 sets. **A short session is infinitely better than a skipped one.**

### Equipment occupied

Write the client's substitution table alongside the sheet, with a swap for every machine-dependent exercise. A client waiting 12 minutes for a pec deck is a client who leaves without finishing.
