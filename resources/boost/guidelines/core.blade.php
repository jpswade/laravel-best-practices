# jpswade/laravel-best-practices

This package contributes opinionated, additive Laravel best-practices via the **`laravel-best-practices-overlay`** skill in this same package, plus a **`session-scoping`** skill for how to run AI-agent sessions in this repo.

Activate the `laravel-best-practices-overlay` skill whenever you are writing, reviewing, or refactoring PHP or Laravel code in this application. It composes with — and does not replace — Boost's first-party `laravel-best-practices` skill, and covers ground Boost is silent on: control-flow opinions, Eloquent design defaults (including integer-money handling), architectural defaults, ubiquitous naming across UI and schema, general design habits, UI display values (humanised, never raw), and operational safety guardrails.

Activate the `session-scoping` skill before starting substantial work: scope one bounded deliverable per session, open with a task contract (goal, relevant area, constraints, acceptance criteria, verification command), match reasoning effort to the task, and verify with a targeted test before running the full suite. It governs how the session is run, not what the code should look like.

**Always-on guardrail:** never run `php artisan migrate:fresh`, `db:wipe`, `schema:drop`, or any other destructive database command unless the user has **explicitly** asked for it in this conversation. `RefreshDatabase` in PHPUnit is the same class of risk when pointed at MySQL — if a test failure shows `Connection: mysql`, stop and fix isolation before re-running. The full rationale lives in the overlay skill's `operational-safety.md`.
