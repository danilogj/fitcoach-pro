# Cardio alongside lifting

> **Keywords:** cardio, aerobic, conditioning, zone 2, Z2, HIIT, intervals, interference effect, concurrent training, steps, NEAT, heart rate zones, VO2max, running, cycling.

Most clients who hire a personal trainer want to lose fat, and most of them will do cardio whether it is prescribed or not. Leaving it out of the program does not mean it is not happening — it means it is happening unmanaged, next to the training that actually drives the result.

---

## 1. What cardio is for, per goal

| Goal | Role of cardio | Dose |
| :--- | :--- | :--- |
| Fat loss | Adds expenditure without touching food; protects adherence | 2-4 sessions, mostly easy |
| Hypertrophy | Health, recovery capacity, appetite regulation | 2 easy sessions, kept short |
| Health / sedentary client | The primary intervention | 150 min/week moderate, built gradually |
| Strength | Minimal, easy only | 1-2 short easy sessions |

**Cardio is not the fat-loss lever people think it is.** A 40-minute run buys 350-450 kcal, which one generous meal erases. Its value is cardiovascular health, work capacity, and the appetite and mood effects that keep a deficit survivable — not the calories.

---

## 2. Intensity zones, individualized

Prescribe by **zone**, never by fixed heart rates — a prescription in beats per minute is wrong for everyone except the person it was written for.

| Zone | Effort | Talk test | Purpose |
| :--- | :--- | :--- | :--- |
| Z1 | Very easy | Full conversation, nose breathing | Recovery, warm-up |
| Z2 | Easy | Full sentences, slightly strained | Aerobic base. **Where most of the volume lives** |
| Z3 | Moderate | Short sentences | The grey zone — too hard to recover from, too easy to drive adaptation |
| Z4 | Hard | A few words | Threshold work |
| Z5 | Maximal | Cannot speak | VO2max intervals |

**If there is no heart-rate data, use the talk test.** It is more reliable for an untrained client than a formula-derived maximum, and it costs nothing. Age-predicted max heart rate (220 − age) carries an error of ±10-12 beats per person — say so if you use it.

---

## 3. Distribution: mostly easy, a little hard

Roughly **80 % of cardio time in Z1-Z2 and 20 % in Z4-Z5**, with Z3 avoided as a default destination.

The grey zone is where under-supervised clients spend all their time: hard enough to accumulate fatigue that steals from the lifting sessions, easy enough that it drives little adaptation. Z3 is not forbidden — controlled tempo work is a legitimate tool — but arriving there by running easy days too fast is a mistake, not a plan.

**HIIT is a time-efficiency tool, not a superior stimulus.** Its recovery cost is real and it competes directly with leg training. Two sessions a week is the ceiling for someone lifting four times.

---

## 4. The interference effect, honestly

Concurrent endurance and resistance training can blunt strength and hypertrophy gains if unmanaged. The size of that effect is routinely overstated in gym lore and clarified in recent meta-analyses (**Schumann et al. 2022, Lundberg et al. 2022**):

- **Hypertrophy & Maximal Strength are preserved:** Concurrent training does NOT compromise muscle hypertrophy ($p = 0.919$) or maximal strength ($p = 0.446$) compared to lifting alone.
- **Explosive strength attenuation:** Power and rate of force development (RFD) are attenuated primarily when endurance and lifting occur in the same session without $\ge 3$ hours of recovery.
- **Modality matters:** Cycling produces essentially zero myofiber interference compared to high-impact running.
- **Volume matters:** Interference scales with cardio volume and intensity. Two easy 30-minute Z2 sessions interfere with nothing. Six hard hours of running a week is a different conversation.

**Practical rules to write into the program:**

1. Hard cardio never on the day before a heavy lower-body session.
2. If cardio and lifting land on the same day, **lift first** — unless the client's goal is the cardio.
3. Easy cardio on rest days or after upper-body sessions.
4. When strength is stalling and cardio volume recently climbed, cut the cardio before cutting lifting volume.

---

## 5. Steps and NEAT — the lever people ignore

For fat loss, a daily step target is usually worth more than a cardio session. It is spread across the day, costs almost no recovery, does not interfere with lifting, and is trivially trackable — every client already carries the sensor.

| Baseline | Target |
| :--- | :--- |
| Under 4,000/day | 6,000, then reassess |
| 4,000-7,000 | 8,000-10,000 |
| Above 8,000 | Hold; add cardio instead of more steps |

**In a deficit, NEAT falls on its own.** The client moves less without noticing, and part of the expected deficit evaporates. A step target is how you notice that happening — and it is why `metrics tdee-observed` eventually reads lower than the formula predicted. That is not a broken calculation; it is the adaptation, measured.

**Prefer adding steps to cutting calories** when a fat-loss client stalls. Food is a finite resource in a diet — once it is spent, there is nowhere left to go.

---

## 6. Programming templates

**Hypertrophy, 4 lifting days:** 2 × 25-30 min Z2 on rest days or after upper sessions. Step target. No HIIT during a surplus — it costs recovery for calories you are deliberately eating back.

**Fat loss, 4 lifting days:** step target first, then 2-3 × 30-40 min Z2, then optionally 1 × 15-20 min intervals on a non-leg day. Add the cardio only after the step target is being met — otherwise you are prescribing a session to replace movement that was free.

**Sedentary client starting out:** walking only, 3-4 × 20-30 min, building to 150 min/week before anything harder. The goal is that they still be doing this in month six.

**Recording it.** Cardio sessions go in the log like anything else: `log add session --set session_id=z2_run --set duration_min=30`. It counts toward training load, and load that is not logged is load you cannot manage.
