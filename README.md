# Laravel Best Practices

An opinionated, additive overlay of Laravel best practices for AI coding assistants. Composes alongside [Laravel Boost](https://github.com/laravel/boost) — it does not replace it.

Boost ships an excellent built-in `laravel-best-practices` skill (19 rules) that covers the mechanics of Laravel and PHP. This package adds the practices Boost is *silent* on (control-flow opinions, architectural defaults, money-handling, named queues) plus a small set of deliberate opinionated counter-positions (clearly flagged where they exist).

## Install

```bash
composer require --dev jpswade/laravel-best-practices
```

Then make sure Laravel Boost is installed and rerun its installer so it picks up the guidelines and skill from this package:

```bash
composer require --dev laravel/boost
php artisan boost:install
```

Boost auto-discovers content from `resources/boost/{guidelines,skills}/` inside any Composer-installed package, so the guideline files and the `tdd-bug-fixing` skill in this package are composed into Boost's `.ai/` output alongside Boost's own rules.

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
├── guidelines/best-practices.md    # four topics in one file (see "Why one file?" below)
└── skills/tdd-bug-fixing/
    └── SKILL.md                    # six-step TDD bug-fix loop
pint.json                            # Laravel preset + strict_types / strict_comparison / is_null / modernize_types_casting
phpstan.neon.dist                    # Larastan + phpstan-strict-rules at level 6 with exception strictness
```

The single `best-practices.md` file is structured as four self-contained H2 sections — **Control Flow**, **Eloquent Opinions**, **Architecture Additions**, **General Design** — each ending with the Boost rules it composes alongside.

## Why one file?

Laravel Boost (v2.4.6 at time of writing) ingests at most one guideline file per third-party package — the per-package keying in `GuidelineComposer::getThirdPartyGuidelines()` overwrites earlier files in the same package, so only the last-sorted file survives. Tracked downstream as [issue #1](https://github.com/jpswade/laravel-best-practices/issues/1) and upstream as [`laravel/boost#822`](https://github.com/laravel/boost/issues/822).

Until the upstream fix lands, all four topics are concatenated into one file. The topic structure is preserved as H2 sections inside `best-practices.md`, and we'll split it back once Boost ingests multiple files per package.

## Position relative to Boost

This package is **strictly additive**. Each H2 section in `best-practices.md` ends with a **Composes with Boost** block that links to the Boost rule it sits alongside. Where this overlay takes an opposite position to Boost (currently only "avoid database transactions" vs. Boost's `database.md`), it is flagged in-file so you can remove that subsection if you prefer Boost's default.

The Pint and PHPStan configs are similarly additive: Pint layers four extra rules on top of the standard `laravel` preset, and the PHPStan config is a baseline you can extend.

## Cursor (or any non-Boost setup)

If you are not using Laravel Boost — for example, you only use Cursor and want raw guideline content — you can reference the markdown directly:

```
vendor/jpswade/laravel-best-practices/resources/boost/guidelines/best-practices.md
vendor/jpswade/laravel-best-practices/resources/boost/skills/tdd-bug-fixing/SKILL.md
```

Either point a Cursor rule at the file, or copy it into `.cursor/rules/`. The guidelines themselves are plain Markdown — they do not depend on Boost to be useful.

## Adding a new practice

Open `resources/boost/guidelines/best-practices.md` and add a new `### H3` subsection under whichever `## H2` topic best fits — Control Flow, Eloquent Opinions, Architecture Additions, or General Design. Follow the existing shape:

- An `### H3` title naming the practice.
- A short rationale paragraph.
- **Incorrect:** / **Correct:** code blocks.
- If the new practice has a direct Boost counterpart, add a bullet to the section's existing **Composes with Boost** list.

If the practice belongs to a genuinely new topic (not one of the four existing H2s), add a new `## H2` topic in the same file rather than creating a new `.md` file — see ["Why one file?"](#why-one-file) for why.

## What this package deliberately does not ship

- No `.ai/` directory — Boost composes content into the consumer's `.ai/` from this package's `resources/boost/`.
- No service-provider beyond `vendor:publish` for the two config files. No Artisan commands, no facades, no migrations.
- No content that overlaps Boost's built-in `laravel-best-practices/rules/*.md` — verified at authoring time.
- No Rector config, no `tomasvotruba/unused-public` in the baseline PHPStan config (both are referenced from the relevant guideline subsections as opt-in follow-ons).

## RFC nature

These are best practices, not coding standards. Coding standards are the things that Pint can mechanically enforce — bracket placement, trailing commas, type-cast syntax. Best practices are the design defaults that need a person (or an AI) to apply judgement.

This package is a working set of opinions. Where the opinions are widely accepted in the Laravel community, they are stated firmly. Where they are deliberately contrarian (e.g. avoiding database transactions by default), they are flagged in-file so you can take the opposite view without rewriting the file.

If you disagree with anything here, open an issue or a pull request — the bar is "is this useful to teach an AI?", not "is this universally correct?".

## Licence

MIT. See [`LICENSE`](LICENSE).
