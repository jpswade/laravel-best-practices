---
name: laravel-best-practices-overlay
description: "Apply this skill whenever writing, reviewing, or refactoring Laravel PHP or Blade code. Complements Boost's first-party laravel-best-practices skill with opinionated additive rules where Boost is silent. Triggers for control-flow choices (switch vs. match, early returns, exception use, exception swallowing in console handle(), lone-`!` operator, magic numbers vs. enums), Eloquent design (soft deletes, redundant relationship access, transaction discipline, integer-money handling, money on job/queue/API boundaries), architectural defaults (method-naming with no 'and', context-free method names, default-private visibility, thin handle() in jobs/listeners, no logic in routes, named queues by purpose), general design (YAGNI/dead-code removal, when to use a free-function helper, double-quoted interpolation vs. sprintf, in-body code comments, dropping signature-redundant DocBlocks), operational safety (destructive database commands such as migrate:fresh, db:wipe, schema:drop; test-database isolation), Blade view design (no business logic, queries or routing decisions in @php blocks; view composers for shared partial data; presenters/accessors for computed display values), display values (never show raw stored values in the UI — always humanised labels/formatters unless an explicit debug/devtools exception), page toolbar layout (title and breadcrumbs left, page-level actions in a toolbar slot right; shared partials for repeated controls), and flash messages (single typed session convention, shared Blade partial, avoid Fortify's status key). Also use for Laravel/PHP/Blade code reviews and refactoring of existing code to align with these defaults."
license: MIT
metadata:
  author: jpswade
---

# Laravel Best Practices (Overlay)

Opinionated, additive best-practices that compose alongside Boost's built-in `laravel-best-practices` skill. Boost covers the mechanics of Laravel and PHP excellently; this overlay covers the ground Boost is silent on, plus a small set of deliberate opinionated counter-positions (clearly flagged in-file where they exist).

## Consistency First

Before applying any rule, check what this application already does. These rules are defaults for new code in projects without an established convention — they should not override patterns the codebase already uses. Inconsistency is worse than a suboptimal pattern.

Check sibling files, related controllers, models, or tests for established patterns. If one exists, follow it — don't introduce a second way.

## Quick Reference

### 1. Control Flow → `rules/control-flow.md`

- Prefer `match` over `switch`/`case`
- Reserve exceptions for genuinely exceptional situations
- Catch the narrowest exception, never bare `\Exception`
- Question every `try`/`catch` before writing it
- Do not swallow exceptions in console `handle()` methods
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

### 4. General Design → `rules/general-design.md`

- YAGNI: delete unused code; git remembers
- Reach for a free function only for cross-cutting, pure logic
- Prefer double-quoted interpolation; use `sprintf` only for genuinely formatted output
- Comments explain *why*, not *what* — don't narrate code, don't annotate diffs
- Drop DocBlocks that only restate the signature

### 5. Operational Safety → `rules/operational-safety.md`

- Never run destructive database commands (`migrate:fresh`, `db:wipe`, `schema:drop`) without an explicit user request
- Tests use an isolated database configuration; never a shared instance

### 6. Blade Views → `rules/blade-views.md`

- Blade is for presentation; no business logic, queries, or routing decisions in `@php` blocks
- Use view composers for variables shared across partials of the same screen
- Use presenters / accessors / view models for computed or formatted display values

### 7. Display Values → `rules/display-values.md`

- Never render raw stored values (slugs, enum case names, ISO dates, integer money, bare booleans) in the UI
- Always show the humanised form via enum labels, formatters, accessors, or presenters
- Exceptions only for explicit developer tooling / debug surfaces — not "admin" in general

### 8. Page Toolbar → `rules/page-toolbar.md`

- Layout header: breadcrumbs + title left, `@section('toolbar')` right
- Primary page actions in the toolbar slot, not in `@section('content')`
- Compose from shared partials when controls repeat across pages

### 9. Flash Messages → `rules/flash-messages.md`

- One typed flash convention per app — no feature-specific session keys
- `Flash::success()` / `info()` / `warning()` / `danger()` returning a single `flash` session key
- Avoid `session('status')` when Fortify is installed
- One shared Blade partial; validation stays on `$errors`

## Composes with Boost

This skill is additive to, not a replacement for, Boost's first-party `laravel-best-practices` skill. Each rule file ends with a **Composes with Boost** block linking the specific Boost rules it sits alongside.

The only deliberate counter-position is "avoid database transactions unless you have to" in `rules/eloquent-opinions.md`, which opposes Boost's `database.md`. Remove that subsection if your team prefers Boost's default.
