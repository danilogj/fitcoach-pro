# Body assessment — what to measure, what to trust, what to ignore

> **Keywords:** bioimpedance, BIA, body composition scale, smartwatch, body fat percentage, lean mass, FFMI, skinfolds, calipers, circumference, tape measure, waist, progress photo, DXA, measurement protocol.

Assessment exists to **confirm** the direction the log and the scale already pointed to. When it becomes a weekly decision metric, it produces adjustments built on noise — and the client loses faith in the process.

---

## 1. How bioimpedance actually works

The device **does not measure muscle or fat.** It measures electrical impedance, estimates total body water, divides by an assumed hydration constant (~0.73) to reach fat-free mass, and derives everything else by subtraction.

Demonstrated on a real reading:

```
Fat-free mass  = weight − fat mass       = 71.0 − 13.3 = 57.7 kg
Water ÷ FFM    = 42.3 ÷ 57.7             = 73.3%   ← the assumed constant
BMR (Katch-McArdle) = 370 + 21.6 × 57.7  = 1,616 kcal  ← matches the screen exactly
BMI            = 71.0 ÷ 1.78²            = 22.4
```

**The seven numbers on the screen are one number — body water — dressed as seven.** If water moves, all of them move together, in the same direction, in proportion.

**What shifts the reading with zero change in tissue:** glycogen (each gram holds ~3 g of water), training the previous day, sodium, coffee, alcohol, sleep, skin temperature, sweat at the electrode, how tight the strap is, menstrual cycle phase.

**Limitation by device type:**

| Device | Current path | What gets extrapolated |
| :--- | :--- | :--- |
| Watch / wristband | Hand to hand | Legs and hips entirely |
| Home scale | Foot to foot | Torso and arms |
| Professional 8-electrode | Segmental | Less extrapolation, same principle and same hydration limits |

**The mistake that produces gross errors:** watches and some devices **do not measure weight** — they use the value stored in the profile. An outdated profile makes fat mass and percentage wrong from the start. Check it before interpreting any reading.

---

## 2. Mandatory protocol

Without a protocol, the series is not comparable and is not worth the time.

- **Same day of the week**, in the morning
- **Fasted**, after voiding, **before drinking water**
- **No leg training the day before** (fluid in the muscle inflates the reading)
- No alcohol in the previous 24-48 h
- No rings; device at the same tightness and position
- Still, arms away from the torso
- **Three consecutive readings — record the average.** Cuts a good share of within-session noise for free

**Every 4 weeks. Never weekly.** At a rate of 0.3 kg/week, real lean tissue gain is 150-250 g per week. The individual error of BIA against DXA runs into **kilograms**. Measuring weekly is measuring noise with the appearance of data.

---

## 3. How to interpret it

**Use fat mass in kilograms, not percentage.** Percentage moves when lean mass moves, so it shifts without fat having shifted — and the client gets confused. Kilograms of fat answer the question that matters.

**Compare trends, never single points.** Three readings in the same direction count; one reading counts for nothing.

**Ignore the app's "excellent" or "high" badge.** It is a percentile against the manufacturer's user base, which is sedentary. It says nothing about the client's potential.

**Off-protocol readings have a predictable bias:** taken in the afternoon, hydrated and fed, they overestimate lean mass and underestimate fat. If a client brings one, state the direction of the error rather than discarding the number — they will keep measuring anyway.

**FFMI** (fat-free mass ÷ height²) is useful for answering "how much room is left": untrained 18-19, well-trained natural 22-23, natural ceiling around 25. It calibrates client expectations; it does not drive prescription.

---

## 4. Alternative methods

| Method | Accuracy | When to use |
| :--- | :--- | :--- |
| **Circumferences** | High as a measure of change | **The best cost-benefit ratio.** Weekly waist answers the one question weight cannot. |
| **Skinfolds** | Good with a trained, consistent assessor | Only if it is always the same assessor and the same protocol. Between-assessor error is enormous. |
| **BIA** | Poor in absolute value, reasonable as a trend under protocol | Confirmation every 4 weeks. |
| **Standardized photo** | Subjective, but the most convincing to the client | Every 4 weeks. It is what keeps the client through month 3. |
| **DXA** | Practical reference standard | Start and end of a long project, if access and budget allow. |

### Circumference protocol

Tape not stretched, resting against the skin without compressing, client relaxed, always the same time of day and the same side.

| Site | Landmark |
| :--- | :--- |
| Waist | At the navel, normal exhale, without sucking in |
| Hip | Widest point of the glutes |
| Arm | Midpoint between acromion and olecranon, arm relaxed at the side |
| Thigh | Midpoint between gluteal fold and patella |
| Chest | At nipple level, normal exhale |
| Calf | Widest point |

Record the **waist-to-height ratio** as well — under 0.5 is the simplest and most defensible marker of cardiometabolic risk available, and it needs no device at all.

---

## 5. Wearable data — using it without being used by it

Most clients already generate sleep, resting heart rate, HRV and a readiness score every night, for free. Ignoring it is leaving instrumentation on the table. Treating it as truth is worse.

| Signal | What it is worth | How to use it |
| :--- | :--- | :--- |
| **Sleep duration** | The most actionable number on the device | Under 6.5 h averaged across a week is a deload signal. Cut a session before cutting sleep |
| **Resting heart rate** | Reliable trend, meaningless single reading | A rise of 5+ bpm sustained over a week alongside another signal supports backing off |
| **HRV** | Highly individual; only the trend matters | Never react to one night. Compare a week against the client's own baseline, never against another person |
| **Readiness / body battery** | A vendor composite, not a measurement | Useful as one input among several. Below 40 averaged across a week counts as one deload signal, never as the decision |
| **Steps** | Underrated | The cheapest fat-loss lever there is. See `07-cardio.md §5` |
| **Calories burned** | The least reliable output on the device | Do not feed it into a calorie target. Wearable expenditure estimates are off by wide margins, and eating back phantom calories is how a deficit disappears |

### Getting the data in without typing it

Every service exports; almost none of them offer an API worth depending on. The importer reads exported files:

```
python3 tools/cli.py ingest <file> --inspect        # what is actually in it
python3 tools/cli.py --client clients/<name> ingest <file> --dry-run
python3 tools/cli.py --client clients/<name> ingest <file>
```

| Source | What to hand it | What arrives |
| :--- | :--- | :--- |
| **Samsung Health** | The zip from Settings, Download personal data | Weight, steps, sleep, heart rate, exercise sessions |
| **Garmin** | `Activities.csv` from Connect, or the full export | Sessions, plus whatever daily files the export includes |
| **Apple Health** | `export.xml` or its zip, from Health, profile, Export All Health Data | Weight, steps, resting HR, HRV |
| **Strava** | `activities.csv` from the bulk export | Cardio sessions only — no sleep, no HRV, no weight |
| **Withings, Oura, Whoop, Fitbit, a gym scale, a spreadsheet** | Any CSV | Whatever columns it recognises |

**Re-importing the same file is a no-op.** Day-granular measurements dedup on the day; sessions dedup on the exact timestamp, so two workouts on one day both survive and neither duplicates.

**When an export does not match**, `--inspect` prints the real column names and what each mapped to. Fix it with one flag: `--map 'weight_kg=Massa (kg),date=Data da Medicao'`. Column names drift between vendor releases — expected, not a failure.

**What the importer will not do:** invent a value it cannot read, or store a number outside physiological range. A 900 kg weigh-in is dropped.

Log what is useful and let the tools weigh it:

```
python3 tools/cli.py --client clients/<name> log add recovery --set hrv_ms=48 --set rhr_bpm=54 --set readiness=38
python3 tools/cli.py --client clients/<name> log add sleep --set hours=6.2 --set quality=2
```

`load deload` accepts these as signals and still requires two of them to agree before recommending anything. **A wearable never overrides what the client reports.** If they feel good and the ring says otherwise, the ring is a data point, not a verdict.

---

## 6. What to tell the client

They will ask about body fat percentage. The honest answer, in three sentences:

> The number on the scale is an estimate with a margin of several percentage points. What we track is its trend over months, alongside your waist and your training log. If all three point the same way, we are right — and if they disagree, this number is not what breaks the tie.

Do not invent precision the method does not have. Clients forgive declared uncertainty; they do not forgive the number that changed its mind.
