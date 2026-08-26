# Baseline assessment — Client A

**Date:** 2026-08-26, 13:46 · Wrist bioimpedance (smartwatch)

| Weight | Fat mass | Body fat | Skeletal muscle | Water | FFM | FFMI | BMR |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 71.0 kg | 13.3 kg | 18.7% | 31.0 kg | 42.3 kg | 57.7 kg | 18.2 | 1,616 |

## What this reading actually says

The device does not measure muscle or fat. It measures impedance, estimates body water, and derives the rest:

```
Fat-free mass  = 71.0 − 13.3        = 57.7 kg
Water ÷ FFM    = 42.3 ÷ 57.7        = 73.3%   ← the assumed hydration constant
BMR (Katch)    = 370 + 21.6 × 57.7  = 1,616 kcal   ← matches the screen exactly
BMI            = 71.0 ÷ 1.78²       = 22.4
```

**The seven numbers on the screen are one number — body water — dressed as seven.**

## Protocol violation, and the direction of the error

This reading was taken at 13:46, fed and hydrated. That inflates body water, which **overestimates lean mass and underestimates fat**.

**Corrected estimate: real body fat between 21% and 23%**, not the 18.7% on the screen.

The reading is kept in the record anyway, marked as off-protocol. Discarding it would leave no baseline at all; presenting it as accurate would be worse. Subsequent readings follow the protocol in `06-body-assessment.md`: Sunday morning, fasted, before water, no leg training the day before, three consecutive readings averaged.

## What gets ignored

The **"High" badge on skeletal muscle** is a percentile against the manufacturer's user base, which is sedentary. It does not mean he is near any ceiling.

**FFMI 18.2** says the opposite: untrained sits at 18-19, well-trained natural at 22-23, natural ceiling around 25. Despite years in the gym, no large accumulation of lean mass ever happened — which means roughly 8-9 kg is available. The 78 kg goal is an intermediate waypoint, not a final target.

## Tracking metric

**Fat mass in kilograms, not percentage.** Percentage moves when lean mass moves, so it shifts without fat having shifted. The ceiling for this block is 16 kg of fat mass, and that is the number that triggers a calorie cut.
