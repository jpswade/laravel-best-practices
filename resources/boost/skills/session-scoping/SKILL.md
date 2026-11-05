---
name: session-scoping
description: >-
  Scope substantial AI coding tasks, choose proportionate verification, recover
  stalled work, and hand off unfinished tasks. Use at the start of substantial
  implementation or when resuming work across sessions. Skip simple questions,
  trivial edits, and follow-ups within an already scoped task. Respects the
  host application's planning, permissions, effort controls, and task state.
license: MIT
metadata:
  author: jpswade
---

# Session Scoping

## When to use

- Starting any substantial task — more than a trivial fix — in an AI coding session.
- A session has been running for a while and it is unclear whether it is still making progress.
- Handing off unfinished work to a new session (context is getting long, or the user says "continue this tomorrow").
- The user gives an open-ended or vague instruction ("keep building X", "improve the app") and a bounded deliverable needs to be carved out of it first.

## When not to use

- Trivial one-line fixes, formatting-only changes, or answering a question — the overhead is not worth it.
- Mid-task follow-up questions within an already-scoped deliverable.

Long-lived sessions, vague instructions, repeated exploration, and defaulting to
the highest reasoning effort all burn usage without reliably improving the
result. This skill keeps each AI-agent session bounded, verifiable, and cheap
to resume or hand off.

## One bounded deliverable at a time

Define a finishing point that can be implemented and verified. "Add Stripe
Checkout for purchasing credits" is a deliverable; "keep building the app"
needs a concrete next outcome. For larger requests, use milestones while
preserving the user's full objective. Continue within the existing thread
when it still contains useful context; a milestone does not require a new
conversation.

## Work with the host

Use the active application's available planning, task tracking, and handoff
facilities. In T3 Code, follow its supplied orchestration instructions and use
the current thread's working directory or worktree. Do not assume tools,
provider names, model settings, or delegation capabilities exist just because
another host offers them. This skill does not itself authorize delegation,
new conversations, changes to permissions, or external actions.

Explicit user instructions and established project conventions take precedence
over these workflow defaults. Reuse an existing task plan rather than creating
a duplicate. Ask only when missing information or a material scope change
requires a user decision; routine implementation choices do not need approval.

## Open with a task contract

Before implementing, settle:

- **Goal** — the one outcome.
- **Relevant area** — the likely files/directories, plus an existing example to follow if one exists.
- **Constraints** — behaviour to preserve, areas out of scope, "follow the repo's existing patterns", "no new dependencies without asking".
- **Acceptance criteria** — observable requirements, including the error/edge-case ones.
- **Verification** — the exact command that proves it (see Targeted verification below).

Inspect only the relevant area first, then implement. Stop and ask before the
work expands materially beyond this scope — the same stop-and-ask instinct
that `../laravel-best-practices-overlay/rules/operational-safety.md` applies to destructive database commands
applies here to scope creep.

## Match reasoning effort to the task

Do not default to the highest reasoning/thinking level.

| Work | Effort |
| --- | --- |
| Renaming, formatting, docs, simple CRUD | Low |
| Normal feature implementation | Medium |
| Difficult debugging or architectural decisions | High |
| Exceptionally ambiguous or system-wide work | Very high, temporarily |

Treat these as recommendations for hosts that expose effort controls. Respect
the user's selected model and effort; do not claim to change a setting without
a supported control. If settings are unavailable, adjust the depth of the
investigation to the task instead.

## Targeted verification, required checks before completion

### Verify behaviour and contracts

Test observable behaviour and meaningful outcomes across languages and tools.
Do not add tests or verification scripts that merely read implementation files
and assert expected strings, code fragments, declarations, or configuration
literals. Such checks can pass while the implementation is broken and fail
after a harmless refactor.

- **Infrastructure as code:** use native validation and test resulting resource
  properties or policy semantics in an isolated environment; do not search source
  text for declarations or apply infrastructure to a live environment to test it.
- **Shell:** execute with controlled inputs and stubbed external commands; assert
  exit codes, output, side effects, and failure handling.
- **Python/PHP:** exercise functions, commands, and application flows through
  inputs, outputs, side effects, and error paths, rather than checking source code.
- **Configuration and fixtures:** use parsers, schemas, and native validators;
  test effective settings or exercise consumers with synthetic fixtures where
  meaningful coverage is needed.

Use the appropriate native tools for syntax, formatting, schema, and static
validation. These complement behaviour tests; syntax validity alone does not
prove runtime behaviour. Use synthetic data and isolated environments, following
the existing credential and database safety boundaries.

Content assertions remain appropriate when the content itself is the contract,
such as generated configuration, a public output format, skill metadata, bundled
references, or a required security policy. Verify parsed semantics where practical;
assert exact text only when wording or bytes are part of the contract. A policy
text check does not establish that a host enforces that policy.

During relevant test reviews, remove tests whose only purpose is to mirror
implementation details and which provide no independent assurance. Replace them
with behaviour tests where meaningful coverage would otherwise be lost. Preserve
checks that independently verify behaviour, security invariants, or contractual
output; reading a file does not by itself make a test redundant. Keep cleanup
within the area under review.

### Compose with Test Enforcement instructions

When generated project instructions require every change to be programmatically
tested, meet that requirement with meaningful verification at the affected layer.
This package does not assume that the generated wording originates here. Reuse
existing sufficient checks rather than adding a new test merely to accompany
every edit. Add or update tests when behaviour or a contract lacks coverage.
For an application bug fix, an existing test that reproduces the defect can supply
the red step in `tdd-bug-fixing`; run it and confirm it fails for the right reason
before implementing the fix.

This guidance does not waive required project checks or explicit test requirements.
If a requirement cannot be met, report the gap instead of substituting a source-text
assertion or claiming verification that did not run.

### Run proportionate checks

Use the repository's documented commands and test environment. While iterating,
run the smallest check that validates the change, for example:

```bash
php artisan test --filter=SomeSpecificTest
```

Before completion, run the required project checks appropriate to the change,
including the full suite when required by project policy or the impact of the
change. Run formatting before final verification; repeat affected checks if
formatting changes code. Once checks pass, rerun them only when new changes,
failures, or unresolved concerns justify it. Documentation-only changes need
content and link checks, not an unrelated application test suite.

Use Pint and PHPStan only when installed and configured in the project. Report
which checks ran and any unavailable or failing checks accurately. Do not
silently fix unrelated pre-existing failures.

This policy also applies to the `tdd-bug-fixing` loop. Before database tests,
verify isolation; if output shows `Connection: mysql`, follow the overlay's
`../laravel-best-practices-overlay/rules/operational-safety.md` stop-the-line instructions before rerunning.

## Recognise an unproductive session

Pause and reassess the approach when work:

- repeatedly reads the same files, or explores directories unrelated to the task;
- retries the same failing fix several times;
- rewrites working code without a requirement to;
- keeps re-running the full test suite instead of a targeted one;
- touches files outside the agreed scope;
- keeps going after discovering the original assumption was wrong.

Record what failed and choose a different approach. Use the host's compaction
or resume facilities when available. Suggest a fresh session only if useful
context cannot be recovered; do not abandon the requested outcome or create a
new thread automatically.

## Handoff for multi-session work

For work spanning sessions, prefer the host's existing task state or handoff
artifact. When a file is needed, use the repository's convention with Goal /
Completed / Next / Decisions / Known issues. For concurrent tasks, use a
task-specific path rather than overwriting a shared `docs/current-work.md`. A new session reads
this instead of inheriting a full transcript. Delete it when the work lands, or fold durable decisions into an
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
- Relevant verification and required project checks pass; any limitations are disclosed.
- Any significant decision is recorded (ADR if architectural, otherwise the handoff note).
- Follow-up ideas are reported separately, not implemented inline.

## Composes with

- `tdd-bug-fixing` — uses the same targeted-first verification policy within its red-green-refactor loop.
- `adrs` — durable decisions that come out of a handoff note graduate to an ADR; working notes never do.
- `laravel-best-practices-overlay` — governs what the code should look like; this skill governs how the session that writes it should be run.
