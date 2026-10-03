# Reviewer Skills

Claude Code skills that review rather than produce.
**The problem:** an agent's output is fluent, formatted and confident whether or not it is right, so its mistakes pass review because they read as right.
**For:** people who use Claude Code to reach a call (a number, a bug fix, a decision, a network diagnosis) and need it checked before anyone acts on it.
**Why it is not obvious:** asking the same agent "are you sure?" mostly buys agreement. These skills fire on their own triggers and apply a written method: label each claim, reproduce before fixing, grade the action rather than the prose.

[![skill lint](https://github.com/decano5107-boop/reviewer-skills/actions/workflows/tests.yml/badge.svg)](https://github.com/decano5107-boop/reviewer-skills/actions/workflows/tests.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## Install

```
/plugin marketplace add decano5107-boop/reviewer-skills
/plugin install reviewer-skills
```

Or copy any single directory under `skills/` into your own `~/.claude/skills/`. They are
mostly independent (a few reference each other) — take one, take all three.

---

## What is in here

### `skeptical-kit` — the one to install first

Five passes before an answer with a number in it is allowed out: **epistemic** (label every claim
VERIFIED / DERIVED / RECALLED / ESTIMATED / UNKNOWN), **question** (is this the real question?),
**sources** (in line, dated, primary over aggregator), **arithmetic** (show the work or drop the
number), **judgment** (say the uncomfortable thing).

The failure it prevents: a figure recalled from training data, presented with the confidence of one
that was just verified. That is the most common way a good-looking answer turns out to be fiction.

### `systematic-debugging` — refuses to guess

Forces reproduce → localize → **one** verifiable root cause → fix → prove-fixed. Covers both
failure classes: code that breaks loudly, and data or behavior that drifts quietly. Never presents
PLAUSIBLE as CONFIRMED — that label is the whole discipline.

### `strategic-advisor` — strategy sparring, not cheerleading

Pressure-tests a decision instead of polishing it, with a method you can see and argue with:
define the decision and its scoreboard, state a hypothesis and what would disprove it, break the
question into an issue tree, answer pyramid-first. Judges initiatives on whether they will survive
contact with the organization — sponsorship, scoreboard, ownership, politics — rather than on
whether the analysis is tidy. For AI initiatives it asks where the work stops and waits, and who
signs what the agent proposes. It claims no credentials; the method carries the weight.

Put a short profile of yourself or your team in your own `CLAUDE.md` (role, industry, what you
own, what a win looks like) — not in the plugin's files, which are overwritten on every update.
The skill reads that context from the conversation or `CLAUDE.md`, asks for it when it is absent,
and will not invent a profile for you.

---

## Why these are skills and not prompts

A prompt is something you remember to type. A skill fires on its own trigger conditions, carries its
reference material with it, and applies the same discipline on the day you are tired. The whole
value of `skeptical-kit` is that it runs when you did *not* think to ask for skepticism.

## What CI checks (and what it does not)

The skills are instructions, so most of what can break is judgment, and no CI run can grade that.
What CI does check, on every push (Python 3.11–3.13), is structure: each `SKILL.md` has valid
frontmatter, its `name` matches its directory, its description is between 50 and 1024 characters,
every file it references exists, the plugin is listed in the marketplace manifest, and the README lists exactly the
skills that ship. The linter first proves it catches broken fixtures:

```
python3 scripts/lint_skills.py --self-test
python3 scripts/lint_skills.py
```

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
