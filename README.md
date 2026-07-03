# Laravel Best Practices

An opinionated, additive overlay of Laravel best practices for AI coding assistants. Composes alongside [Laravel Boost](https://github.com/laravel/boost) — it does not replace it.

Boost ships an excellent built-in `laravel-best-practices` skill (19 rules) that covers the mechanics of Laravel and PHP. This package adds the practices Boost is *silent* on (control-flow opinions, architectural defaults, money-handling, named queues) plus a small set of deliberate opinionated counter-positions (clearly flagged where they exist).

## Install

```bash
composer require --dev jpswade/laravel-best-practices
```

Then make sure Laravel Boost is installed and rerun its installer so it picks up the breadcrumb guideline and the two skills shipped by this package:

```bash
composer require --dev laravel/boost
php artisan boost:install
```

When Boost prompts *"Which third-party AI guidelines/skills would you like to install?"*, tick **`jpswade/laravel-best-practices`**. That writes the choice into `boost.json` so subsequent runs (including non-interactive CI) pick it up automatically.

> **Non-interactive installs require explicit opt-in.** `php artisan boost:install --no-interaction` will silently skip every third-party package by default, because the multiselect defaults to the empty list saved in `boost.json`. If you want to run the installer non-interactively from CI, commit a `boost.json` first with:
>
> ```json
> {
>     "agents": ["cursor"],
>     "guidelines": true,
>     "mcp": false,
>     "packages": ["jpswade/laravel-best-practices"],
>     "skills": ["laravel-best-practices", "laravel-best-practices-overlay", "tdd-bug-fixing"]
> }
> ```

Boost auto-discovers content from `resources/boost/{guidelines,skills}/` inside any Composer-installed package, so once opted in, the breadcrumb in this package's `core.blade.php` is composed into the consumer's always-on `AGENTS.md`, and the two skills (`laravel-best-practices-overlay` and `tdd-bug-fixing`) are written to the agent's skills directory (e.g. `.cursor/skills/`) for on-demand activation.

### Optional: publish the bundled configs

The package also ships a recommended `pint.json` and `phpstan.neon.dist`. Publish either or both into your application root:

```bash
# Pint config only
php artisan vendor:publish --tag=laravel-best-practices-pint

# PHPStan config only
php artisan vendor:publish --tag=laravel-best-practices-phpstan

# Both at once
php artisan vendor:publish --tag=laravel-best-practices-all
```

For the PHPStan config, install the matching analysers (suggested in `composer.json`):

```bash
composer require --dev larastan/larastan phpstan/phpstan-strict-rules
vendor/bin/phpstan analyse
```

## What's inside

```
resources/boost/
├── guidelines/
│   └── core.blade.php                              # thin breadcrumb pointing at the overlay skill
└── skills/
    ├── laravel-best-practices-overlay/
    │   ├── SKILL.md                                # frontmatter + Quick Reference index
    │   └── rules/
    │       ├── control-flow.md
    │       ├── eloquent-opinions.md
    │       ├── architecture-additions.md
    │       ├── general-design.md
    │       ├── operational-safety.md
    │       ├── blade-views.md
    │       ├── page-toolbar.md
    │       └── flash-messages.md
    └── tdd-bug-fixing/
        └── SKILL.md                                # six-step TDD bug-fix loop
pint.json                                           # Laravel preset + strict_types / strict_comparison / is_null / modernize_types_casting
phpstan.neon.dist                                   # Larastan + phpstan-strict-rules at level 6 with exception strictness
```

The overlay's eight topic files — **Control Flow**, **Eloquent Opinions**, **Architecture Additions**, **General Design**, **Operational Safety**, **Blade Views**, **Page Toolbar**, **Flash Messages** — each end with the Boost rules they compose alongside. `SKILL.md` is a thin Quick-Reference index that points at them; agents read it first (via its `description` and `when_to_use`) to decide whether to activate the skill.

## Why a skill rather than one big guideline?

Boost composes content into the consumer at install time, but it routes the two source directories differently:

- `resources/boost/guidelines/` → concatenated into the agent's always-on instructions file (e.g. `AGENTS.md` for Cursor). One file per package — additional `.md` files are silently dropped (see [`laravel/boost#822`](https://github.com/laravel/boost/issues/822)).
- `resources/boost/skills/<name>/` → written verbatim into the agent's skills directory (e.g. `.cursor/skills/<name>/`), preserving any subdirectories. The agent loads each `SKILL.md` frontmatter at startup and activates the body **on demand** when its `description` or `when_to_use` matches the current task.

The four topics in this overlay live as separate `rules/*.md` files inside the `laravel-best-practices-overlay` skill rather than as one big guideline because that lets each topic be a self-contained file (better diffs, better navigation, easier to remove an opinion you disagree with) without colliding with Boost's one-file-per-package guideline limit.

The trade-off is honest: skill content is **not** always-on. The agent only loads the body of `laravel-best-practices-overlay` after it decides the skill is relevant — driven by the frontmatter `description` in [`SKILL.md`](resources/boost/skills/laravel-best-practices-overlay/SKILL.md), which is written to be broad enough to fire on any Laravel PHP work. The thin breadcrumb in `core.blade.php` is what *is* always-on, and its job is to nudge the agent towards the skill if its description matching ever misses.

## Position relative to Boost

This package is **strictly additive**. Each `rules/*.md` file inside `laravel-best-practices-overlay` ends with a **Composes with Boost** block that links to the Boost rule it sits alongside. Where this overlay takes an opposite position to Boost (currently only "avoid database transactions" vs. Boost's `database.md`), it is flagged in-file so you can delete that subsection if you prefer Boost's default.

The Pint and PHPStan configs are similarly additive: Pint layers four extra rules on top of the standard `laravel` preset, and the PHPStan config is a baseline you can extend.

## Cursor (or any non-Boost setup)

If you are not using Laravel Boost — for example, you only use Cursor and want raw content — you can reference the markdown directly:

```
vendor/jpswade/laravel-best-practices/resources/boost/guidelines/core.blade.php
vendor/jpswade/laravel-best-practices/resources/boost/skills/laravel-best-practices-overlay/SKILL.md
vendor/jpswade/laravel-best-practices/resources/boost/skills/laravel-best-practices-overlay/rules/*.md
vendor/jpswade/laravel-best-practices/resources/boost/skills/tdd-bug-fixing/SKILL.md
```

Either point a Cursor rule at the files, or copy them into `.cursor/rules/`. The content is plain Markdown — it does not depend on Boost to be useful.

## Adding a new practice

Open the relevant file under `resources/boost/skills/laravel-best-practices-overlay/rules/` (or create a new one if the practice opens a new topic) and add a new `## H2` subsection. Follow the existing shape:

- An `## H2` title naming the practice.
- A short rationale paragraph.
- **Incorrect:** / **Correct:** code blocks where they aid understanding.
- If the new practice has a direct Boost counterpart, add a bullet to the file's existing **Composes with Boost** list.

After adding or renaming a rule, also update the **Quick Reference** in `resources/boost/skills/laravel-best-practices-overlay/SKILL.md` so the one-line summary stays in sync.

## What this package deliberately does not ship

- No `.ai/` directory — Boost composes content into the consumer's `.ai/` from this package's `resources/boost/`.
- No service-provider beyond `vendor:publish` for the two config files. No Artisan commands, no facades, no migrations.
- No content that overlaps Boost's built-in `laravel-best-practices/rules/*.md` — verified at authoring time.
- No Rector config, no `tomasvotruba/unused-public` in the baseline PHPStan config (both are referenced from the relevant overlay subsections as opt-in follow-ons).

For per-practice rejections — specific best-practices that were considered and deliberately left out, plus the small set of deliberate deviations from common Laravel advice — see [`DECISIONS.md`](DECISIONS.md). Consult it before proposing a new rule, so the project doesn't keep rediscovering the same answers.

## RFC nature

These are best practices, not coding standards. Coding standards are the things that Pint can mechanically enforce — bracket placement, trailing commas, type-cast syntax. Best practices are the design defaults that need a person (or an AI) to apply judgement.

This package is a working set of opinions. Where the opinions are widely accepted in the Laravel community, they are stated firmly. Where they are deliberately contrarian (e.g. avoiding database transactions by default), they are flagged in-file so you can take the opposite view without rewriting the file.

If you disagree with anything here, open an issue or a pull request — the bar is "is this useful to teach an AI?", not "is this universally correct?".

## Licence

MIT. See [`LICENSE`](LICENSE).
