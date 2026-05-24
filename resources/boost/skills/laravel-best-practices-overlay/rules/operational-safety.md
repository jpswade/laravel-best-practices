# Operational Safety

Guardrails for AI coding assistants and developers working in a Laravel codebase. These are not design defaults — they are "do not silently destroy the user's data" rules.

## Never reset the database without an explicit request

Do **not** run `php artisan migrate:fresh`, `db:wipe`, `schema:drop`, or any other command that resets or destroys the database, unless the user has **explicitly** asked for it in this conversation.

- Do not suggest or run destructive database operations as a "quick fix" for failing tests or a broken migration.
- Local development databases often mirror production restores or carry days of investigative data; wiping them causes real data loss.
- Automated tests must use an isolated test database configuration (typically SQLite in-memory via `phpunit.xml`) — never point tests at a shared MySQL or PostgreSQL instance.

When the user wants a clean database, wait for explicit wording (e.g. "run `migrate:fresh` on my machine") before proposing or running those commands. Phrases like "the tests aren't passing" or "the migration is broken" are *not* permission to reset the database; offer to inspect the failure first.

## Composes with Boost

- [`database.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/database.md) — Boost covers how to write migrations; this file covers when *not* to run them destructively.
- [`tests.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/tests.md) — Boost covers test mechanics; the isolated-test-database line above is the safety counterpart.
