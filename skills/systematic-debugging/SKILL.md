---
name: systematic-debugging
description: >-
  Root-cause investigation discipline. ALWAYS activate when something is BROKEN,
  REGRESSED, or DOESN'T ADD UP and the cause is not yet known — code bugs AND data/behavior
  anomalies alike. Trigger on: "por qué se rompió", "por qué bajó/subió", "no cuadra",
  "esto no tiene sentido", "está fallando", "regresión", "dejó de funcionar", "root cause",
  "de dónde viene este número", "why is X broken", "this doesn't match", "find the bug",
  "debug this", "qué cambió", "cuándo se rompió", or when a metric/flow/pipeline moved
  and nobody knows why (e.g. a checkout conversion rate that dropped, a cache hit rate that
  collapsed, a tool returning wrong output, a prototype behaving off-spec). Forces reproduce → localize →
  ONE verifiable root cause → fix → prove-fixed, and refuses to guess or fix blind. Distinct from
  a spec pass (shapes new work) and a verification pass (proves "done"): this finds WHY something is wrong.
---

# Systematic Debugging

You are running a **root-cause investigation**, not patching symptoms. The output is a *verified
cause with evidence*, then a fix — never a plausible guess that "should" work. Two rules hold
throughout: **every claim cites a source (span, log line, commit, row, config), and "I don't know yet"
beats a confident invention.** Pairs with `skeptical-kit` (validate the evidence),
a spec-verification pass (prove the fix).

Applies to BOTH failure classes:
- **Code/system bugs** — prototype off-spec, script wrong output, integration failing.
- **Data/behavior anomalies** — a conversion rate dropped, a number doesn't reconcile, a cache
  stops hitting when nothing obvious changed. In practice the second class is the more expensive one: nothing crashes,
  so nobody looks.

---

## CARDINAL RULES (read first — these override the instinct to "just fix it")

1. **No fix before a reproduced, localized, evidence-backed cause.** If you cannot point to the exact
   line / span / commit / config / row that produces the wrong behavior, you have a HYPOTHESIS, not a
   root cause. Say so. A fix applied to a hypothesis is a guess wearing a diff.

2. **Reproduce first, always.** A bug you cannot trigger on demand you cannot prove you fixed. For
   data anomalies, "reproduce" = pin the exact query/cohort/time-window that shows the wrong number
   deterministically. No repro → the job is *build the repro*, not fix.

3. **Bisect in time and in space.** WHEN did it break (last-good vs first-bad: commit, deploy marker,
   config flip, date) and WHERE (which component/layer/field). One binary question at a time halves
   the space. Don't read the whole system; cut it in half.

4. **One root cause, stated as a causal chain.** "X changed on <date/commit> → caused Y → observed Z."
   If you have two candidate causes, you have not finished localizing. Resist the multi-cause
   hand-wave; it usually means you stopped early.

5. **Distinguish the change from the trigger.** The thing that *changed* (a deploy, a rule, a data
   shift) is not always the thing that's *wrong* — sometimes a latent bug was exposed by a benign
   change. Name both: what changed, and what it exposed.

6. **The absence of a symptom is data.** What *didn't* break narrows the cause as much as what did.
   If region A broke and region B didn't, the cause lives in what differs between them.

7. **Grade cause by evidence tier, and label it.** CONFIRMED (I reproduced it / found the exact line
   or commit) > TRIANGULATED (≥2 independent sources agree) > PLAUSIBLE (fits, unproven) > GUESS.
   Never present PLAUSIBLE as CONFIRMED. An investigation lives or dies on this label.

8. **Fix the cause, then prove it — don't declare victory from a green run.** Re-run the *original
   repro*; confirm the symptom is gone AND that you didn't just move it. Then check what else the
   fix touches (the "grade the action" reflex: did the fix change behavior it shouldn't?).

---

## THE LOOP (four phases — don't skip forward)

### Phase 1 — REPRODUCE (make it deterministic)
- State the expected vs actual behavior in one line each, with the source of "expected".
- Build the smallest reliable trigger: a failing test, a command, a pinned query + window + cohort.
- If it's intermittent, find the axis that flips it (input, timing, tenant, identifier, channel, concurrency).
- **Exit gate:** you can make it fail on demand and make a healthy case pass on demand. If not, stop
  here and say the blocker is reproduction.

### Phase 2 — LOCALIZE (bisect to the crux)
- **Time bisect:** last-known-good → first-bad. Use commits (`git log`/`bisect`), deploy markers
  (infrastructure, vendor platform, config), the exact date a metric stepped. Get to a single boundary.
- **Space bisect:** which layer/component/field? Add a probe (log line, print, span inspect, an
  intermediate query) at the midpoint and halve. Follow the *data*, not the theory.
- Read the actual values at the boundary. Contradiction between two fields = a **VERIFY flag**, not
  proof — go find the authoritative source before scoring it. Often the crux is what a field
  actually means, not the verdict built on it.
- **Exit gate:** one location + one change/trigger identified, with the evidence pinned.

### Phase 3 — ROOT CAUSE (the verifiable causal chain)
- Write it as: **`<change on X>` → `<mechanism>` → `<observed symptom>`**, each link citable.
- Explain the *whole* symptom, not part of it. If the symptom is a metric falling to zero, a cause that only
  explains it halving is incomplete.
- Actively try to REFUTE your own cause (dispatch an independent critic or a skeptical pass): what would this
  cause NOT predict that we nevertheless see? If it survives refutation, tier it CONFIRMED/TRIANGULATED.
- **Exit gate:** the chain predicts the symptom precisely and you couldn't break it.

### Phase 4 — FIX & PROVE
- Smallest change that addresses the CAUSE (not the symptom). Surgical — match surrounding style,
  touch only what the cause requires.
- Re-run the Phase-1 repro: symptom gone.
- Check for displacement: did the fix break an adjacent case? Run the healthy case too.
- If this was a spec'd deliverable, hand it to your verification pass. Record the cause + fix in the project's
  notes so it's not re-litigated.

---

## ANTI-PATTERNS (stop if you catch yourself here)

- **Guess-and-check patching** — changing things to see what helps *before* localizing. Reset; bisect.
- **Fixing the first thing that looks wrong.** "Looks wrong" ≠ "is the cause." Prove it produces THIS
  symptom or move on.
- **Correlation as cause.** Two things moved on the same day ≠ one caused the other. Find the mechanism.
- **Blaming the null / the flaky field** to avoid finding the real cause. A null is only a fault if it
  was decisive. Contradictions get a VERIFY flag, not a verdict.
- **Declaring fixed off a green test suite** without re-running the original repro.
- **Reading the whole codebase/dataset** instead of bisecting. Half the space per question.
- **Stopping at a plausible story** because it's satisfying. Tier it honestly; PLAUSIBLE is not done.

---

## OUTPUT SHAPE

**Symptom:** expected vs actual (one line each, cite the source of "expected").
**Repro:** the exact trigger (test / command / query+window+cohort).
**Localization:** WHEN (commit/deploy/date) + WHERE (component/field), with evidence.
**Root cause:** the causal chain, tiered `CONFIRMED | TRIANGULATED | PLAUSIBLE`.
**Fix:** the surgical change + proof the repro now passes + adjacent-case check.
**Open/VERIFY:** anything unproven, flagged for confirmation — never smuggled in as fact.
