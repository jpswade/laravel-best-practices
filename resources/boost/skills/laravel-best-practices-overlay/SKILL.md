---
name: laravel-best-practices-overlay
description: >-
  Apply Laravel and PHP best-practice opinions when writing, reviewing, or
  refactoring PHP or Blade code. Complements Laravel Boost with control flow,
  Eloquent and money handling, architecture, domain naming, operational safety,
  Blade views, display formatting, toolbars, flash messages, and localisation.
  Follow existing project conventions and load only the topic rules relevant
  to the task. Excludes non-Laravel work and session workflow planning.
license: MIT
metadata:
  author: jpswade
---

# Laravel Best Practices (Overlay)

Opinionated, additive best-practices that compose alongside Boost's built-in `laravel-best-practices` skill. Boost covers the mechanics of Laravel and PHP excellently; this overlay covers the ground Boost is silent on, plus a small set of deliberate opinionated counter-positions (clearly flagged in-file where they exist).

## Consistency First

Before applying any rule, check what this application already does. These rules are defaults for new code in projects without an established convention — they should not override patterns the codebase already uses. Inconsistency is worse than a suboptimal pattern.

Check sibling files, related controllers, models, or tests for established patterns. If one exists, follow it — don't introduce a second way.

## Read only the relevant rules

Use the index below to select the `rules/*.md` files needed for the current
change. Paths are relative to this skill directory. Read those files before
applying their detailed guidance; do not load every rule by default. These
instructions also work as plain Markdown when the host has no skill loader.

## Quick Reference

### 1. Control Flow → `rules/control-flow.md`

- Prefer `match` over `switch`/`case`
- Reserve exceptions for genuinely exceptional situations
- Catch the narrowest exception, never bare `\Exception`
- Question every `try`/`catch` before writing it
- Do not swallow exceptions (log-and-continue) — especially in console `handle()` methods
- Keep exception and log messages stable; unique values go in `context()`, not the message
- Return early; flat code is easier to read than nested code
- Every path through a method should return the same type
- Avoid the lone `!` operator; compare explicitly
- Replace magic numbers with class constants or backed enums

### 2. Eloquent Opinions → `rules/eloquent-opinions.md`

- Default to soft deletes on user-facing or auditable entities
- Read foreign keys directly, not via relationships
- Avoid `DB::transaction()` unless multi-row consistency is required (opinionated counter-position to Boost's `database.md`)
- Store money as integers in the smallest unit (pence, cents, micros)
- Pass the integer minor unit across every serialisation boundary

### 3. Architecture Additions → `rules/architecture-additions.md`

- No "and" in method names — split the responsibilities
- Method names should add information, not echo the class name
- Default visibility to `private`; widen only with reason
- `handle()` is a dispatch point, not a business-logic home
- No closures in route files; keep routes declarative
- Name queues by the kind of work they carry

### 4. Naming → `rules/naming.md`

- Same domain word from UI copy through Blade/Inertia, PHP, routes, lang keys, and the schema
- Do not invent a parallel developer vocabulary for a concept the product already named
- Methods are verbs; models and entities are nouns — do not “correct” Laravel types such as `CreateOrderAction`
- Name the job, not a `*Manager` (carve out `Illuminate\Support\Manager`, `ExceptionHandler`, and `handle()`)

### 5. General Design → `rules/general-design.md`

- YAGNI: climb the reuse ladder before writing; delete unused code
- Reach for a free function only for cross-cutting, pure logic
- Prefer double-quoted interpolation; use `sprintf` only for genuinely formatted output
- Comments explain *why*, not *what* — don't narrate code, don't annotate diffs
- Drop DocBlocks that only restate the signature

### 6. Operational Safety → `rules/operational-safety.md`

- Never read credentials or potentially secret-bearing files (`.env*`, Composer `auth.json`, keys, logs, cached config); no indirect reads or read-then-redact workarounds
- Respect `.aiignore` exclusions; use variable names and explicitly sanitised examples instead of secret values
- Recommend Gitleaks or equivalent in pre-commit and CI; scan built images separately, exclude secrets from build contexts, and use BuildKit secret mounts
- Never run destructive database commands (`migrate:fresh`, `db:wipe`, `schema:drop`) without an explicit user request
- Tests use an isolated database configuration; never a shared instance
- `RefreshDatabase` runs `migrate:fresh` on `database.default` — stop-the-line if output shows `Connection: mysql`; fix `phpunit.xml` / `sqlite_testing` / `beforeRefreshingDatabase()` before re-running

### 7. Blade Views → `rules/blade-views.md`

- Blade is for presentation; no business logic, queries, or routing decisions in `@php` blocks
- Use view composers for variables shared across partials of the same screen
- Use presenters / accessors / view models for computed or formatted display values
- Never expose Artisan or raw CLI in product UI; prefer plain-language outcomes

### 8. Display Values → `rules/display-values.md`

- Never render raw stored values (slugs, enum case names, ISO dates, integer money, bare booleans) in the UI
- Always show the humanised form via enum labels, formatters, accessors, or presenters
- Exceptions only for explicit developer tooling / debug surfaces — not "admin" in general

### 9. Page Toolbar → `rules/page-toolbar.md`

- Layout header: breadcrumbs + title left, `@section('toolbar')` right
- Primary page actions in the toolbar slot, not in `@section('content')`
- Compose from shared partials when controls repeat across pages

### 10. Flash Messages → `rules/flash-messages.md`

- One typed flash convention per app — no feature-specific session keys
- `Flash::success()` / `info()` / `warning()` / `danger()` returning a single `flash` session key
- Avoid `session('status')` when Fortify is installed
- One shared Blade partial; validation stays on `$errors`

### 11. Localisation → `rules/localization.md`

- Prefer namespaced PHP lang files with `__('domain.key')`
- Prefer `__()` over `trans()`
- Browser/email copy (including form requests, notifications, HTTP exceptions) belongs in lang — not literals or `private const`
- Inline `__('Cancel')`-style keys are permitted but not recommended; apply the rule of three in Blade

## Composes with Boost

This skill is additive to, not a replacement for, Boost's first-party `laravel-best-practices` skill. Each rule file ends with a **Composes with Boost** block linking the specific Boost rules it sits alongside.

The only deliberate counter-position is "avoid database transactions unless you have to" in `rules/eloquent-opinions.md`, which opposes Boost's `database.md`. Remove that subsection if your team prefers Boost's default.
