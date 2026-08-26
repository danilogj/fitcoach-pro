# Deliverables — sheet, report and communication

> **Keywords:** workout sheet, training diary, client app, html sheet, progress report, presenting results, message to client, export log, template, handoff.

What the trainer hands over is half the perceived value. A correct prescription in an unreadable PDF becomes a client who does not execute.

---

## 1. The workout sheet — the pocket document

The client uses this standing up, phone in hand, between sets. Real constraints:

- **One session per screen.** They will not navigate tabs with sweaty hands.
- **Last session's load and reps visible** next to today's field. Without it there is no progression — they do not remember.
- Prescribed sets, rep range, RIR and rest on every line.
- A short execution cue only on the exercises where it changes the outcome. A cue on every exercise is read on none.
- Set-by-set logging, not "load for the day".

### Included template

`assets/client-sheet.template.html` — single page, works offline, stores the record on the client's phone and exports the log as Markdown at the end of the week. Works opened as a local file, hosted at a URL, or published as a Claude Artifact (which adds persistence across devices).

**To fill the template, replace only the marked blocks:**

| Placeholder | What goes in |
| :--- | :--- |
| `{{CLIENT}}` | Client name — appears in the header, the title and the export |
| `{{SLUG}}` | Identifier without spaces, e.g. `maria-silva`. Isolates this client's record in the browser |
| `{{SUBTITLE}}` | e.g. `Upper / Lower · 8-week block` |
| `{{CLIENT_SUMMARY}}` | One profile line at the top of the exported log, e.g. `Female, 34, 62 kg → 58 kg goal · fat loss` |
| `/* {{PROGRAM}} */` | The `PROGRAM` array holding the sessions — schema below |
| `{{START}}` | Monday of week 1, format `YYYY-MM-DD` |
| `{{TOTAL_WEEKS}}` | Number of weeks in the block |
| `{{INTRO_UNTIL}}` | Last week of the introduction phase (0 disables it) |
| `{{DELOAD_WEEK}}` | Deload week (0 disables it) |
| `/* {{DAYS}} */` | Weekday → session index map |
| `<!-- {{RULES}} -->` | The block rules that matter more than exercise selection |
| `<!-- {{TARGETS}} -->` | The client's nutrition targets, as `<dt>`/`<dd>` pairs. Remove the whole block if there are none |
| `{{TRAINER}}` and `{{CERT}}` | Trainer name and credential, in the footer. **Do not remove** — this is what makes clear to the client who prescribed and reviewed the program |
| `/* {{EXPORT_HEADER}} */` | Header of the exported log — assembles itself from `{{CLIENT}}` and `{{CLIENT_SUMMARY}}` |

Before filling it, run the program through `python3 tools/cli.py volume check --program FILE.json` — the sheet is the last place you want to discover that the week has 4 chest sets and no vertical push.

Schema for each exercise in `PROGRAM`:

```js
{
  n: "Barbell bench press",   // name
  s: 4,                        // sets at full volume
  r: "6-8",                    // rep range (or "45-60 s" for isometrics)
  rir: "1-2",                  // target RIR — empty string for isometrics and bodyweight
  t: "hold",                   // "hold" = amber RIR (hold back) · "go" = green RIR (failure is fine)
  side: "/side",               // optional, for unilateral work
  f: "pc",                     // optional: "pc" = bodyweight (no load field)
                               //           "tempo" = isometric (no rep field)
  d: 150,                      // rest in seconds, drives the timer
  dl: "2-3 min",               // rest as text
  ss: true,                    // optional, marks a superset with the next item
  cue: "Ramp first: 50% · 70% · 85%."   // optional, accepts simple HTML
}
```

**Before handing it over, check:** the `PROGRAM` matches the client's `program.md`, `START` is a Monday, and the exercises marked `f: "pc"` genuinely have no external load (a load field on a bodyweight exercise is the first error clients report).

### If the sheet is published as an Artifact — the rule that prevents data loss

The page stores the record **inside the HTML itself**, in the `<script id="initial-state">` block. The trainer's local copy goes stale every time the client trains.

Before any edit and republish:

1. Fetch the published version
2. Extract the contents of `<script id="initial-state">`
3. Paste it over the corresponding block in the local copy
4. Only then apply edits and republish

Publishing without that step **erases the client's entire history**. A conflict on publish means they saved mid-edit — merge and republish, never force.

---

## 2. The dashboard

```
python3 tools/cli.py --client clients/<name> dashboard --name "Maria Silva" \
    --goal loss --target-kg 62
```

Writes a single self-contained HTML file — no CDN, no JavaScript, no build step. It opens offline, survives being emailed, and still works in five years.

What it shows, when the data supports it: the weight trend with daily readings behind it and the goal line, rate of change with its safety verdict, measured expenditure, total weekly sets, **direct sets per muscle against that muscle's own landmarks**, acute:chronic load, sleep, steps, and load progression on the most-trained lifts.

**The per-muscle chart is the one to look at first.** A weekly total of 60 sets can be four muscles or twelve; only this chart tells you which. Muscles below minimum effective volume or above maximum recoverable get their label flagged, so a group sitting at zero — the most common programming error — is visible at a glance instead of hidden behind a healthy-looking total.

**It never invents a section.** Anything it cannot compute goes into a "Not shown yet" block naming the data it needs: *"Measured expenditure: only 4 days with logged intake in the last 28; need at least 10."* Hand that to the trainer as the reason to log more, not as a defect.

Regenerate it after any import or check-in — it reads the log at render time and does not update itself.

## 3. Progress report

Deliver every 4 weeks, and always at the end of a block. Five parts, in this order:

1. **What changed** — two or three lines, concrete numbers. Load that went up, a measurement that moved, adherence.
2. **The numbers** — a table comparing baseline, last month and today: average weight, waist, loads on the main lifts, adherence as a percentage.
3. **What explains it** — the trainer's read on why it moved, or why it did not.
4. **What changes next block** — specific, with the reason for each change.
5. **What I need from you** — the action that depends on the client. One, two at most.

**Writing rules:** number before adjective. "Your bench went from 60 to 72.5 kg in 8 weeks" communicates more than "great progress". If the result was poor, say it in the first line — the client already knows, and hiding it costs the trust that sustains the renewal.

**Adherence always goes in the report.** It is the data point that hands responsibility back to the client without accusation: 22 of 32 sessions is a sentence, not a judgment.

---

## 4. Messages to the client

The trainer will ask you to write them. Three rules:

- **One message, one subject.** A load change and a diet change in the same message become neither.
- **State the action, not the theory.** "Take the bench to 65 kg this week" — the why comes after, in one line, if at all.
- **No infantilizing and no hype.** An adult paying for a technical service does not need fire emojis.

When a client has missed weeks in a row, the message that works does not chase them: it shrinks the ask. Offer the short version of the session and a target of two sessions this week. Chasing produces disappearance; lowering friction produces return.

---

## 5. Client file structure

```
clients/<client-name>/
  intake.md    ← assets/template-intake.md
  program.md   ← assets/template-program.md
  log.md       ← assets/template-log.md
  sheet.html   ← assets/client-sheet.template.html, filled in
  reports/
    2026-09.md
```

Keep `program.md` as the source of truth. The sheet is a **rendering** of it — when the two diverge, `program.md` wins and the sheet is regenerated.
