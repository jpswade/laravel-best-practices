---
name: session-scoping
description: >-
  Use this skill when starting substantial AI-agent work in this codebase, or
  partway through a long-running session, to keep the work scoped, verifiable,
  and cheap to resume. Covers defining one bounded deliverable per session,
  writing a complete task contract (goal, relevant area, constraints,
  acceptance criteria, verification command), matching reasoning effort to
  task difficulty, running targeted tests before the full suite, recognising
  when a session has gone unproductive and should be restarted, and
  maintaining a short handoff note for work that spans multiple sessions.
  Governs how the session is run, not what the code should look like — see
  laravel-best-practices-overlay for that.
license: MIT
metadata:
  author: jpswade
when_to_use:
  - Starting any substantial task — more than a trivial fix — in an AI coding session.
  - A session has been running for a while and it is unclear whether it is still making progress.
  - Handing off unfinished work to a new session (context is getting long, or the user says "continue this tomorrow").
  - The user gives an open-ended or vague instruction ("keep building X", "improve the app") and a bounded deliverable needs to be carved out of it first.
when_not_to_use:
  - Trivial one-line fixes, formatting-only changes, or answering a question — the overhead is not worth it.
  - Mid-task follow-up questions within an already-scoped deliverable.
---

# Session Scoping

Long-lived sessions, vague instructions, repeated exploration, and defaulting to
the highest reasoning effort all burn usage without reliably improving the
result. This skill keeps each AI-agent session bounded, verifiable, and cheap
to resume or hand off.

## One deliverable per session

Each session should have a single, clear finishing point that can be
implemented, tested, reviewed, and committed. "Add Stripe Checkout for
purchasing credits: checkout-session creation, success handling, targeted
tests" is a deliverable. "Continue building the app" is not — start a new
session per deliverable rather than running one permanent conversation for a
whole project; a growing history means every turn re-processes decisions and
files that are no longer relevant.

## Open with a task contract

Before implementing, settle:

- **Goal** — the one outcome.
- **Relevant area** — the likely files/directories, plus an existing example to follow if one exists.
- **Constraints** — behaviour to preserve, areas out of scope, "follow the repo's existing patterns", "no new dependencies without asking".
- **Acceptance criteria** — observable requirements, including the error/edge-case ones.
- **Verification** — the exact command that proves it (see Targeted verification below).

Inspect only the relevant area first, then implement. Stop and ask before the
work expands materially beyond this scope — the same stop-and-ask instinct
that `rules/operational-safety.md` applies to destructive database commands
applies here to scope creep.

## Match reasoning effort to the task

Do not default to the highest reasoning/thinking level.

| Work | Effort |
| --- | --- |
| Renaming, formatting, docs, simple CRUD | Low |
| Normal feature implementation | Medium |
| Difficult debugging or architectural decisions | High |
| Exceptionally ambiguous or system-wide work | Very high, temporarily |

Drop back to medium once a hard decision is resolved — high effort is an
escalation, not the default.

## Targeted verification, full suite once

Run the smallest test or check that can validate a change while iterating —
a filtered test, not the whole suite:

```
php artisan test --filter=SomeSpecificTest
```

Run the complete suite once, when the deliverable is finished, and once more
after formatting and static analysis:

```
php artisan test
vendor/bin/pint
vendor/bin/phpstan analyse
```

This composes with `tdd-bug-fixing`, which already runs new-test-then-full-suite
inside its own loop — the same targeted-first, full-once shape applies to any
implementation work, not only bug fixes. It also composes with
`rules/operational-safety.md`: the stop-the-line rule for `RefreshDatabase`
hitting `mysql` applies to every full-suite run, not only bug-fix ones.

## Recognise an unproductive session

Interrupt and restart rather than pushing through when a session:

- repeatedly reads the same files, or explores directories unrelated to the task;
- retries the same failing fix several times;
- rewrites working code without a requirement to;
- keeps re-running the full test suite instead of a targeted one;
- touches files outside the agreed scope;
- keeps going after discovering the original assumption was wrong.

Do not spend context arguing a derailed session back into shape. Capture the
useful facts, start a fresh session, and hand off with a short note (below).

## Handoff for multi-session work

For a deliverable that spans more than one session, keep a short-lived
`docs/current-work.md` (or similar) with Goal / Completed / Next / Decisions /
Known issues. A new session reads this instead of inheriting a full
transcript. Delete it when the work lands, or fold durable decisions into an
ADR (`adrs` skill) if the decision is architecturally significant enough to
outlive the task.

## Keep context deliberate

Point at the likely files rather than asking for a full-repo read. Reference
an existing implementation to copy from when one exists. Paste only the
relevant slice of a log or error — a command and its failure line, not the
full output. A short but ambiguous prompt is not automatically efficient; it
can cause more exploration than a precise one.

## Prevent unsolicited expansion

State boundaries up front when they are not obvious from the acceptance
criteria: do not refactor unrelated code, do not add dependencies without
approval, do not change public interfaces unless the acceptance criteria
require it, do not fix unrelated pre-existing failures — report them
separately instead.

## Definition of done

- Acceptance criteria are satisfied.
- The diff contains no unrelated changes.
- Targeted tests pass; the full suite and formatting/static analysis have been run once.
- Any significant decision is recorded (ADR if architectural, otherwise the handoff note).
- Follow-up ideas are reported separately, not implemented inline.

## Composes with

- `tdd-bug-fixing` — this skill's targeted-verification and stop-the-line rules are the general case of that skill's red-green-refactor loop.
- `adrs` — durable decisions that come out of a handoff note graduate to an ADR; working notes never do.
- `laravel-best-practices-overlay` — governs what the code should look like; this skill governs how the session that writes it should be run.
