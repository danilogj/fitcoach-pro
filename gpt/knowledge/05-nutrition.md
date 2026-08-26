# Nutrition — calorie target, macros and adjustment

> **Keywords:** calories, BMR, basal metabolic rate, Mifflin-St Jeor, Katch-McArdle, TDEE, maintenance, surplus, deficit, macros, protein, carbohydrate, fat, meal plan, supplements, creatine, whey, hydration, weight adjustment.

**Scope limit, first.** Individualized dietary prescription is restricted to registered dietitians in many jurisdictions, Brazil included. What this module produces is **macronutrient targets and nutrition education** — legitimate work for a personal trainer in most places. Pathology, medication, aggressive restriction, pregnancy, suspected eating disorder: refer out, and say so to the trainer in plain terms.

---

## 1. Estimating maintenance

Two equations, because the convergence between them is what signals reliability.

**Do not compute these by hand.** `python3 tools/cli.py metrics targets --weight-kg 71 --height-cm 178 --age 41 --sex male --ffm-kg 57.7 --sessions-per-week 4 --goal gain` returns BMR by both equations, the component breakdown, maintenance with its range, and the macro split. The formulas are documented here so you can explain them, not so you can execute them.

**Mifflin-St Jeor** (needs weight, height, age, sex):

```
Male:    BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age + 5
Female:  BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age − 161
```

**Katch-McArdle** (needs fat-free mass — use when body composition data exists):

```
BMR = 370 + 21.6 × FFM(kg)
```

If the two land close together, BMR is the trustworthy part of the calculation. If they diverge sharply, the body-fat estimate is wrong — not the BMR.

**From BMR to maintenance**, summing components instead of applying a single activity multiplier (a multiplier hides where the error is):

| Component | Estimate |
| :--- | :--- |
| NEAT — non-exercise activity | +10% of BMR for a sedentary routine, up to +25% for standing work or heavy walking |
| Training expenditure | ~250-400 kcal per resistance session, **spread across all 7 days** |
| Thermic effect of food | ~10% of total intake |

**The real error lives in NEAT.** It runs into the hundreds of kcal and no formula solves it. That is why the weekly weight average outranks the estimate — the math picks the starting point, it does not have to be right.

Communicate it as a range: "maintenance estimated around 2,350 kcal, likely range 2,290 to 2,420". Never "2,347 kcal".

---

## 2. Setting the target

| Goal | Adjustment over maintenance | Expected rate |
| :--- | :--- | :--- |
| Hypertrophy, beginner or detrained | +300 to +500 kcal | 0.25 to 0.5% of body weight per week |
| Hypertrophy, intermediate/advanced | +200 to +350 kcal | 0.2 to 0.35 kg/week |
| Fat loss | −300 to −500 kcal | 0.5 to 1.0% of body weight per week |
| Fat loss, obesity | −500 to −750 kcal | Up to 1% per week, with supervision |
| Maintenance / recomposition | ±0 | Weight stable, measurements moving |

**Floors that do not get crossed:** never below estimated BMR in a prolonged deficit; never below roughly 1,200 kcal for women or 1,500 for men without medical and dietetic supervision. An aggressive deficit buys speed with lean mass, and is the number-one cause of weight regain the following year.

**Gaining too fast is fat.** Above roughly 0.5% of body weight per week in a surplus, the fraction arriving as fat climbs quickly. In someone returning from a long layoff, the first 2-3 kg arrive in 6-8 weeks — part glycogen and water, part genuine muscle memory. Do not calibrate expectations on that stretch.

---

## 3. Macros

Order of definition: **protein → fat → carbohydrate fills the rest.**

| Macro | Target | Note |
| :--- | :--- | :--- |
| **Protein** | 1.6 to 2.2 g/kg of body weight | Above 2.2 g/kg there is no demonstrated additional benefit for hypertrophy. In an aggressive deficit or in a lean client, use the top of the range (up to 2.4 g/kg of lean mass) to protect muscle. |
| **Fat** | 0.8 to 1.0 g/kg | Floor of roughly 0.6 g/kg for hormonal function and vitamin absorption. Do not go below it. |
| **Carbohydrate** | The remaining calories | Fuel for resistance training. In a gaining phase, this is where most of the surplus should land. |
| **Fiber** | 25 to 38 g/day | Satiety and transit. Almost always forgotten in deficit plans. |
| **Water** | 30 to 40 ml/kg | More in heat and at high training volume. |

**Protein distribution:** 3 to 5 meals at 0.3-0.4 g/kg each stimulates protein synthesis better than two large meals. This is second-order optimization — total daily intake drives most of the result.

**Pre- and post-workout:** the 30-minute "anabolic window" does not survive the data. What matters is daily intake and not training after a prolonged fast when volume is high. Carbohydrate 1-2 h before improves session performance, and session performance is what creates the stimulus.

---

## 4. Building the meal structure

Never build a meal plan before you have the answers from Block 4 of the intake — who cooks, budget, allergies, what they hate.

**A structure that works:** 4 to 5 meals, each with a defined protein source, a defined carbohydrate source and vegetables, plus an audit table summing the macros at the end. Without the audit table, a meal plan is guesswork wearing the appearance of precision.

**Hand it over with quick adjustment levers**, not with a brand-new plan every week:

| I need | Do this |
| :--- | :--- |
| +200 kcal | 1 tbsp olive oil plus ~50 g cooked rice |
| −200 kcal | Cut ~30 g of nuts and ~100 g of cooked rice |
| Hit protein without eating the same meat again | 1 scoop of whey replaces part of a meal |

**Swaps by food group** are worth more than a fixed list: any lean meat ≈ any other at an equivalent portion; rice, potato, pasta and oats are interchangeable by approximate cooked weight. Teach the swap instead of rewriting the plan.

---

## 5. Supplements — what has evidence

| Item | Dose | Verdict |
| :--- | :--- | :--- |
| **Creatine monohydrate** | 3-5 g/day, every day | The best-evidenced supplement for strength and hypertrophy. No loading phase needed, timing irrelevant, safe in continuous use for healthy people. A 1-2 kg weight bump in the first week is intramuscular water — warn them beforehand, or they will think they got fat. |
| **Whey / casein** | As needed | Convenience for hitting protein, not a requirement. Food covers it. |
| **Caffeine** | 3-6 mg/kg, 45 min before | Consistently improves performance. Watch sleep, and watch clients with hypertension. |
| **Vitamin D, omega 3** | As deficiency dictates | General health. Direct effect on hypertrophy: not demonstrated. |
| **Beta-alanine** | 3-6 g/day | Small effect, limited to 1-4 minute efforts. Barely relevant for standard resistance training. |
| **BCAA, glutamine, "fat burners"** | — | Do not recommend. With adequate protein, isolated BCAA adds nothing. |

Supplements are the last lever on the list, after training, food, sleep and adherence. A trainer who opens with supplementation is solving the wrong problem.

---

## 6. Decision rules — when to move calories

1. **Weight flat for 3 weeks** (comparing weekly averages) in a gaining phase → add roughly 200 kcal.
2. **Weight climbing above the target rate consistently** → cut roughly 200 kcal. Beyond that rate, the fraction arriving as fat climbs quickly.
3. **Fat gain passed the agreed ceiling before weight reached the goal** → cut roughly 200 kcal and revisit the target.
4. **In a deficit, weight flat for 3 weeks with confirmed adherence** → cut 150-200 kcal or add steps. Prefer the steps: it preserves food for when you genuinely need to cut.
5. **On reaching the weight goal** → maintenance rose along with the new mass. Recalculate before deciding whether to hold or continue.

**Always 200 kcal at a time, always waiting 3 weeks.** A large adjustment produces swings you cannot interpret at the next check-in.

---

## 7. Measured expenditure beats the formula

Once there is enough logged data, stop arguing with the estimate and measure it:

```
python3 tools/cli.py --client clients/<name> metrics tdee-observed --goal-delta -400
```

It takes mean daily intake over a 28-day window, takes the change in the smoothed weight trend across the same window, converts that change at roughly 7,700 kcal per kilogram, and returns the expenditure that reconciles the two. This is the number that corrects a formula estimate that drifted — and it drifts, because NEAT is unknowable in advance and falls on its own during a deficit.

**It refuses below 10 days of logged intake in the window.** Relay that refusal instead of falling back to the formula silently: "I can't measure your real expenditure yet — 6 of the last 28 days have meals logged and it needs 10. Until then we're working from the estimate, which is a range, not a number."

Two caveats worth stating to the trainer:

- **7,700 kcal/kg is a working convention**, not a constant. Early weight change includes glycogen and water at a very different energy cost, which is why the window is four weeks and not one.
- **It is only as good as the food logging.** Under-reporting intake — which is the norm, not the exception — makes measured expenditure read lower than it is. If the number comes back implausibly low, suspect the log before suspecting the metabolism.
