# Principles — how prescription decides

> **Keywords:** principles, doctrine, weekly volume, frequency, RIR, proximity to failure, axial load, dose-response, room to progress, decision metrics, evidence hierarchy.

These six principles govern everything the other files prescribe. When two rules collide, the principle decides.

---

## 1. Weekly volume is the variable that decides, not frequency

With volume equated, training a muscle group once, twice or three times a week produces equivalent hypertrophy. Frequency exists to **distribute** volume across the week, not to create extra stimulus.

**Practical consequence:** "how many days does the client have?" does not determine the outcome — it determines the split. What determines the outcome is how many hard sets per muscle group fit in the week, and whether the client can execute them with quality.

**Working range:** 10 to 20 hard sets per muscle group per week covers most hypertrophy cases. Below 8, the stimulus is maintenance. Above 20, returns fall off and the recovery cost climbs fast — with wide individual variation at both ends.

**Per-muscle landmarks** — minimum effective volume, the adaptive range, and maximum recoverable volume — are in `tools/volume.py` and printable with `python3 tools/cli.py volume landmarks`. They are population averages scaled by training profile, not personal prescriptions.

**Never total sets by hand.** `python3 tools/cli.py volume check --program FILE.json` sums direct sets per muscle, reports indirect separately, judges each group against its landmarks, and flags movement patterns the week does not cover. A program that has not been through it is not finished.

**Per-session ceiling:** past roughly 8-10 sets for the same muscle group in a single session, the final sets contribute little. If the target volume does not fit in one session, split it across two.

---

## 2. RIR on every set, calibrated to the cost of the exercise

RIR (reps in reserve) is how many reps the client **could still perform** when they end the set. It is the intensity variable a log can actually record.

| Exercise type | Target RIR | Why |
| :--- | :-: | :--- |
| Heavy barbell compounds, pull-ups, deadlifts | **1-2** | Never to failure. Hypertrophy improves as sets approach failure, but absolute failure here creates systemic fatigue that compromises the rest of the session and the week. |
| Isolation, machines, cables | **0-1** | Failure is fine. Low recovery cost, low technical risk — this is where maximal effort is worth collecting. |
| Beginner, first three months | **2-3** everywhere | They cannot estimate RIR yet and overestimate what is left in the tank. The margin protects them while technique settles. |

**Caveat about the measurement:** beginners' RIR estimates are systematically off in one direction — they say "two left" when five were left. The fix is not a lecture: it is filming the set, or taking one set to genuine failure under supervision to calibrate perception.

---

## 3. Axial load concentrated, not distributed

Back squats, deadlifts and heavy squat variants load the spine. Spreading those patterns across four days a week is where the low-back injury that interrupts six weeks of training comes from.

**Rule:** concentrate heavy axial loading in **one or two days**, and use non-compressive variants on the others — unilateral, supported, machine-based, hip-dominant with lighter load.

**How heavily the principle applies:**

| Profile | Application |
| :--- | :--- |
| Young, no history of back pain | Up to 2 heavy axial days. Comfortable margin. |
| Over 40, or detrained and returning | One day. The limiter stops being muscle and becomes joint and connective tissue. |
| History of disc herniation, recurrent low-back pain, post-surgery | No barbell on the back until cleared. Substitutes in `03-program-design.md`. |

Derived rule: do not put free bent-over rows the day before squat day. The same back volume comes out of a supported row at zero spinal cost.

---

## 4. Volume with room to grow

Volume is the main progression lever for the coming months. If the block starts at the ceiling of what the client tolerates, there is nothing left to add when they stall in week 12.

**Start at the low end of the productive range** — 10 to 14 sets per group — and climb with the response. A program that opens at 22 sets per group produces fast results and a dead end.

Corollary: **adding an exercise is not progression, it is a swap.** Adding a set is progression. Do not confuse the two when the client asks for "something new".

---

## 5. Training log, weight average and waist decide — the rest confirms

Confidence hierarchy, in order:

1. **Training log** — load × reps × RIR per session. The best indicator of strength progress and the most reliable proxy for hypertrophy over a horizon of weeks. No sensor beats it.
2. **Weekly weight average** — daily weigh-ins, same time, fasted, post-void; compare average against average. A single weekly weigh-in is off by up to 1 kg on water and salt alone.
3. **Weekly waist circumference** — answers the one question weight cannot: is the surplus too large, or is the deficit working?
4. **Standardized photo every 4 weeks** — same light, place, pose, time of day, fasted.
5. **Bioimpedance every 4 weeks, never weekly** — a confirmation signal, never a decision metric. See `06-body-assessment.md`.

If 1, 2 and 3 point the same way, bioimpedance is unnecessary. If they disagree, it will not settle the argument — adjusting and waiting three weeks will.

---

## 6. Adherence beats optimization

A program 20% worse that the client executes 90% of weeks delivers more than the optimal program executed 50% of weeks. Every prescription decision passes this filter before it ships:

- Does the client have this equipment **today**, at their gym, at the hour they train?
- Does it fit the real session length, rest periods included?
- Can they execute the technique without constant supervision?
- Will they actually eat this on an ordinary Tuesday?

If any answer is no, the plan is wrong — however correct the physiology.

**There is no such thing as a make-up session.** A missed session is gone. Stacking two in one day or training three days straight to compensate trades one lost day for a compromised week.
