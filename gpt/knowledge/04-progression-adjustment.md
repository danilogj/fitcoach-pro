# Progression and adjustment — running the block

> **Keywords:** progression, double progression, progressive overload, plateau, stagnation, log analysis, weekly check-in, deload, volume adjustment, progression ladder, closing a block, reassessment.

The program is a hypothesis. The log is the data that confirms or refutes it. This is the part of the job software does not do on its own, and the part the trainer charges for.

---

## 1. Load progression criterion

**Double progression.** The client adds load when they hit **the top of the rep range on every set while holding the target RIR**. Not before.

Example: prescription is 4×6-8 at RIR 1-2. They did 8, 8, 8, 8 at RIR 2 → add load. They did 8, 8, 7, 6 → repeat the load next week.

**Increment:** 2.5 to 5 kg on lower-body compounds, 1 to 2.5 kg on upper-body compounds, the smallest available increment on isolation work. If the gym only has dumbbells in 2 kg steps, going from 10 to 12 kg is a 20% jump — in that case hold the load and build reps to the top of the next range before making the jump.

---

## 2. The progression ladder — when load stalls

One lever at a time, in this order. Skipping steps burns volume you will need later.

1. **Load**, by double progression. The primary lever and the cheapest.
2. **Rep range or tempo**, if load has stalled. Drop the range (8-10 to 6-8, adding weight) or hold 3 s on the eccentric at the same load. New stimulus without new volume.
3. **Sets**, +1 on the group that stalled, up to a ceiling of roughly 18-20 weekly.
4. **New exercise**, only if the movement pattern has genuinely stagnated or is irritating a joint.

**Adding an exercise is not progression — it is a swap. Adding a set is progression.** Do not confuse the two when the client asks for "something different".

---

## 3. Analyzing an exported log

When the trainer pastes a log, look in this order. The order matters: adherence explains more stagnation than any training variable.

1. **Adherence.** How many of the scheduled sessions happened? Which weekdays do they miss? If the same day has failed for three weeks, the problem is the schedule, not the program.
2. **Load progression per exercise**, week over week, comparing the same exercise on the same day.
3. **Progression left on the table.** Did they hit the top of the range on every set at the target RIR and *not* add load the following week? The most common error and the easiest to fix.
4. **Drop-off between the first and last set.** If the gap narrows across weeks at the same load, work capacity is improving. An early adaptation signal almost nobody looks at.
5. **Exercises stalled for 2+ weeks.** Apply the ladder above.
6. **Consistency with the phase.** Introduction weeks should carry one set fewer; the deload week should show maintained load and high RIR. Volume above plan during the introduction is a red flag for missed sessions later.
7. **Gaps in the record.** An exercise with no load logged for several weeks usually means they stopped doing it, not that they forgot to write it down. Ask.

Deliver it as **diagnosis plus a specific adjustment**. "Going well" is not analysis.

---

## 4. Weekly check-in — reading to action

| Reading | Action |
| :--- | :--- |
| All sessions done · recovery good · performance climbing | Add load on the main compounds. Change nothing else. |
| All sessions done · recovery poor | **Cut 20% of the sets for one week, holding load.** Intensity preserves the stimulus; volume is what taxes recovery. |
| Sessions missed due to schedule | Short versions instead of skipping. Adherence beats the perfect session. |
| Performance dropping two weeks running | Pull the deload forward. |
| Weight flat for 3 weeks in a gaining phase | Add roughly 200 kcal (`05-nutrition.md`). |
| Weight flat for 3 weeks in a cutting phase | Check dietary adherence before cutting calories. When in doubt, add steps before removing food. |
| Fat gain above plan | Cut roughly 200 kcal. Leave the training alone. |
| New joint pain | Substitute the pattern using the table in `03`. Do not "train through it". |
| Sleep consistently under 6 h | Cut a session before cutting sleep. At this volume, sleep outweighs any training variable. |

**One variable at a time.** If you move calories and volume in the same week, the next check-in cannot tell you which one worked.

**Three weeks before concluding anything.** Noise from water, salt and glycogen will fool you inside two weeks. Unless the reading is glaring, wait for the third.

---

## 5. Training load, quantified

Judging load by feel works until the client's week gets strange. The acute:chronic workload ratio compares the last 7 days of training against the last 28, using hard sets per day from the log:

```
python3 tools/cli.py --client clients/<name> load acwr
```

| Ratio | Reading | Action |
| :--- | :--- | :--- |
| Under 0.8 | Acute load below the recent norm | A missed week, not a recovery problem. Resume at the previous week's volume |
| 0.8 - 1.3 | Productive band | Where progressive overload happens |
| 1.3 - 1.5 | Climbed faster than adaptation | Hold volume flat for a week before adding |
| Above 1.5 | Spike | The pattern that precedes load-related injury. Cut back this week |

It **refuses below 21 days of history** — before that the ratio is arithmetic without information, and the check-in table below is the better instrument.

### The deload decision

```
python3 tools/cli.py load deload --performance-dropping-weeks 2 --sleep-hours-avg 6.1 \
    --soreness-avg 4 --readiness-avg 38 --weeks-since-deload 7
```

**Two or more independent signals trigger a deload.** One signal is a bad week; two are a pattern. Pass only what was actually measured — an absent input never counts as a signal, which is what stops the tool from manufacturing a reason to deload.

Deload means sets at roughly 60 % of prescribed with a floor of 2, **load held**, RIR 3-4. Volume is what taxes recovery; intensity is what preserves the stimulus.

---

## 6. Plateau — diagnose before adjusting

Before changing the program, rule out the causes that are not the program:

| Cause | How to spot it | Fix |
| :--- | :--- | :--- |
| Adherence | Gaps in the log | Fix the schedule or the split, not the program |
| Food | Flat weight, low energy | Adjust calories |
| Sleep | Self-report, erratic performance | Sleep before anything else |
| Life stress | Context | Reduce volume temporarily, hold load |
| Technique degrading with load | Film the set | Drop the load, fix execution |
| Accumulated fatigue | Performance falling across several exercises at once | Deload |
| Genuinely insufficient stimulus | Everything else ruled out | Progression ladder |

The last item is the least common and the first one everyone assumes.

---

## 7. Closing the block

With 8 weeks of log, the decision stops coming from average literature and starts coming from this client. Assess:

- **Progression by muscle group** — which climbed, which stalled. A stalled group earns a set in the next block; a group that flew can give volume back.
- **Symmetry of stimulus** — did biceps and triceps keep pace with the pulls and presses? Did the rear delt get what was prescribed?
- **Body composition against the goal** (`06-body-assessment.md`).
- **Adherence by weekday** — the data point that most changes the next block.
- **What the client hated.** A hated exercise is a badly executed or skipped exercise. Swap it for another in the same pattern.

Build the next block from those answers. **Never repeat the previous block out of inertia** — and never change everything just to look new. Variation without a reason erases the comparison you spent 8 weeks building.
