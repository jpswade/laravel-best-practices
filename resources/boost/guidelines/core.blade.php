# jpswade/laravel-best-practices

This package contributes opinionated, additive Laravel best-practices via the **`laravel-best-practices-overlay`** skill in this same package.

Activate the `laravel-best-practices-overlay` skill whenever you are writing, reviewing, or refactoring PHP or Laravel code in this application. It composes with — and does not replace — Boost's first-party `laravel-best-practices` skill, and covers ground Boost is silent on: control-flow opinions, Eloquent design defaults (including integer-money handling), architectural and naming defaults, general design habits, UI display values (humanised, never raw), and operational safety guardrails.

**Always-on guardrail:** never run `php artisan migrate:fresh`, `db:wipe`, `schema:drop`, or any other destructive database command unless the user has **explicitly** asked for it in this conversation. The full rationale lives in the overlay skill's `operational-safety.md`.
