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
├── guidelines/best-practices/
│   ├── architecture-additions.md   # naming, default-private, thin handle(), routes, named queues
│   ├── control-flow.md             # no switch/case, exceptions-only-when-exceptional, return early, ...
│   ├── eloquent-opinions.md        # soft-deletes-default, integer-money, transactions-as-exception
│   └── general-design.md           # YAGNI, helpers, strings/interpolation, redundant DocBlocks
└── skills/tdd-bug-fixing/
    └── SKILL.md                    # six-step TDD bug-fix loop
pint.json                            # Laravel preset + strict_types / strict_comparison / is_null / modernize_types_casting
phpstan.neon.dist                    # Larastan + phpstan-strict-rules at level 6 with exception strictness
```

## Position relative to Boost

This package is **strictly additive**. Every section in every guideline file ends with a `## Composes with Boost` block that links to the Boost rule it sits alongside. Where this overlay takes an opposite position to Boost (currently only "avoid database transactions" vs. Boost's `database.md`), it is flagged in-file so you can remove that section if you prefer Boost's default.

The Pint and PHPStan configs are similarly additive: Pint layers four extra rules on top of the standard `laravel` preset, and the PHPStan config is a baseline you can extend.

## Cursor (or any non-Boost setup)

If you are not using Laravel Boost — for example, you only use Cursor and want raw guideline files — you can reference the markdown directly:

```
vendor/jpswade/laravel-best-practices/resources/boost/guidelines/best-practices/*.md
vendor/jpswade/laravel-best-practices/resources/boost/skills/tdd-bug-fixing/SKILL.md
```

Either point your Cursor rules at the directory, or copy the files into `.cursor/rules/`. The guidelines themselves are plain Markdown — they do not depend on Boost to be useful.

## Adding a new guideline

Drop a new `.md` file into `resources/boost/guidelines/best-practices/`. Follow the existing shape:

- One `# H1` title matching the file's topic.
- A one-paragraph intro that explains how the file sits next to Boost.
- One `## H2` per practice, with **Incorrect:** / **Correct:** code blocks.
- A `## Composes with Boost` footer linking back to any Boost rule the file sits alongside.

Topic-named, kebab-cased filenames (no numeric prefixes). Boost's own rules are organised the same way.

## What this package deliberately does not ship

- No `.ai/` directory — Boost composes content into the consumer's `.ai/` from this package's `resources/boost/`.
- No service-provider beyond `vendor:publish` for the two config files. No Artisan commands, no facades, no migrations.
- No file that overlaps Boost's built-in `laravel-best-practices/rules/*.md` — verified by an in-repo overlap check.
- No Rector config, no `tomasvotruba/unused-public` in the baseline PHPStan config (both are referenced from the relevant guideline sections as opt-in follow-ons).

## RFC nature

These are best practices, not coding standards. Coding standards are the things that Pint can mechanically enforce — bracket placement, trailing commas, type-cast syntax. Best practices are the design defaults that need a person (or an AI) to apply judgement.

This package is a working set of opinions. Where the opinions are widely accepted in the Laravel community, they are stated firmly. Where they are deliberately contrarian (e.g. avoiding database transactions by default), they are flagged in-file so you can take the opposite view without rewriting the file.

If you disagree with anything here, open an issue or a pull request — the bar is "is this useful to teach an AI?", not "is this universally correct?".

## Licence

MIT. See [`LICENSE`](LICENSE).
