# BMAD Methodology — Exercise Prescription Engineering Architecture

> **BMAD (Behavioral & Multi-Agent Architecture for Development & Prescription)**  
> *How FitCoach Pro adapts advanced software engineering multi-agent frameworks to deliver a virtual multidisciplinary sports board directly in your chat.*

---

## 🏛️ 1. What is the BMAD Methodology?

In professional software development, **BMAD** ensures zero-defect output by dividing complex operations into specialized roles governed by **Quality Gates** and **Adversarial Auditing**:

* ❌ **Standard Generic AI Chat (Monolithic):** A single prompt tries to screen medical conditions, pick exercises, calculate calories, and format messages all at once. This leads to hallucinations, forgotten injuries, and arithmetic drift.
* ✅ **FitCoach Pro with BMAD (Multi-Specialist):** The prescription passes through a **sequential 5-agent pipeline**, where each stage has explicit acceptance criteria and an **Adversarial QA (Quality Assurance) Gatekeeper** that tests the plan before the trainer ever sees it.

---

## 👥 2. The 5 Agents of the FitCoach Pro Pipeline

```
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │                            FITCOACH PRO BMAD PIPELINE                           │
  ├─────────────────────────────────────────────────────────────────────────────────┤
  │                                                                                 │
  │  📋 AGENT 1: CLINICAL INTAKE & SCREENING SPECIALIST                            │
  │     └─► Validates PAR-Q+, joint restrictions, hormonal status (AAS/TRT),        │
  │         and gym equipment. Pauses and prompts if critical data is missing.      │
  │                                                                                 │
  │  📐 AGENT 2: BIOMECHANICAL & KINETIC ARCHITECT                                  │
  │     └─► Distributes movement patterns, prioritizes long muscle length (LML),    │
  │         and manages axial spinal fatigue.                                       │
  │                                                                                 │
  │  🧮 AGENT 3: METABOLIC & ENERGY BALANCE ENGINEER                                │
  │     └─► Executes deterministic math: BMR, TDEE, surplus/deficit, and            │
  │         macronutrient partitioning without hallucinations.                      │
  │                                                                                 │
  │  🔍 AGENT 4: ADVERSARIAL QA AUDITOR / SAFETY LINTER ⚠️                          │
  │     └─► Runs deterministic test battery:                                        │
  │         ✔ Is weekly volume within MEV–MRV landmarks?                            │
  │         ✔ Did a client with patellar chondromalacia get deep squats? (REJECT)   │
  │         ✔ Did an enhanced lifter receive sub-5RM grinding loads? (REJECT)       │
  │         ✔ Are all prescribed exercises available in the gym inventory? (REJECT) │
  │                                                                                 │
  │  📱 AGENT 5: UX & CLIENT EXPERIENCE PACKAGER                                    │
  │     └─► Generates the interactive mobile app (`sheet.html`) and drafts the      │
  │         empathetic, clear WhatsApp check-in message.                            │
  │                                                                                 │
  └─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ 3. The Adversarial QA Gate (The Prescription Linter)

The core strength of BMAD is **Agent 4 (QA Auditor)**, which acts like a code linter for training prescriptions:

| QA Test | Validation Rule | Action on Failure |
| :--- | :--- | :--- |
| **Test 1: Gym Inventory** | Does every exercise exist in the client's verified equipment list? | **REJECT.** Swap for a valid catalog variation. |
| **Test 2: Volume Landmarks** | Are hard sets per muscle between MEV (Minimum) and MRV (Maximum)? | **REJECT.** Rebalance set volume to optimal MAV. |
| **Test 3: Axial Load & Injuries** | Did a client with lumbar issues receive axial loading? | **REJECT.** Enforce chest-supported substitutions. |
| **Test 4: Tendon Safety (AAS/TRT)** | Did an enhanced lifter receive sub-5 RM maximal shock loads? | **REJECT.** Shift to 8–12 reps and enforce 3s eccentric tempo. |
| **Test 5: Workload Spike (ACWR)** | Did the 7-day vs 28-day load ratio exceed 1.5? | **WARN.** Flag injury risk and trim weekly volume by 20%. |
| **Test 6: Caloric Arithmetic** | Do protein, fat, and carbs match the exact caloric target? | **REJECT.** Recalculate using deterministic metrics engine. |

---

## 💬 4. How to Trigger the BMAD Pipeline in Chat

The assistant executes these guardrails natively. For complex cases (elite athletes or clients with multiple orthopedic limitations), you can explicitly request:

> **"FitCoach, run the full BMAD pipeline for this client: execute clinical intake, biomechanical architecture, metabolic math, and run it through the QA auditor before generating the final program and client message."**
