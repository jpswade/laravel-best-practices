# Decisions

A record of best practices that have been *considered* for inclusion in this overlay and deliberately *not* included, plus the small set of deliberate deviations the overlay takes from widely-repeated Laravel/PHP advice. It exists so that future passes — human or AI — over the same source material don't keep rediscovering the same answer.

If you are reading an older Laravel best-practices RFC, blog post, or checklist and thinking "should this be in the overlay?", check here first.

The filter applied throughout is:

1. **Has it moved on?** — Is the advice still current, or has Laravel/PHP/the community shifted away from it?
2. **Is it actually correct?** — Does the original phrasing describe the right mechanism?
3. **Is Boost already on it?** — If Boost's first-party `laravel-best-practices` skill (or `style.md`, `configuration.md`, etc.) covers it well, this overlay does not duplicate it.

## Practices considered and not included

### Deterministic factories

> *"Factories should be deterministic. If you need randomness, use a seed."*

**Not included.** Laravel itself ships Faker-based factories with random output as the default, and the framework's guidance is that tests should override the values they depend on rather than removing randomness from the factory. The "seed every factory" rule is a minority position the framework argues against. The right framing of the underlying concern ("don't let a test silently depend on a value the factory might change") is covered by general test-authoring discipline, not a factory-level rule.

### Memory-efficient iteration via `each` / `cursor`

> *"Use `eloquent each` — it uses cursors, so it's quicker."*

**Not included.** The original wording is **technically wrong**: `each()` is a `Collection` method that iterates an *already-loaded* collection and does not use cursors. The memory-efficient iteration tools are `cursor()`, `lazy()`, `lazyById()`, `chunk()`, and `chunkById()`. Re-stating the original would codify the confusion. Memory-friendly iteration is Boost's `eloquent.md` territory and is owned correctly there.

### Single-table inheritance with a discriminator column ("extensible tables")

> *"Don't make a table for each type of user — just add a `type` column to the table."*

**Not included.** Dated. The "god table with a discriminator column" pattern is now widely treated as a smell rather than a default; modern Laravel offers polymorphic relations, morph maps, and trait-based composition specifically because single-table inheritance breaks down once subtypes diverge in columns or behaviour. It is also a context-dependent schema-design opinion, not a sensible default for an AI to apply unprompted.

### Cross-boundary naming conventions (snake_case / camelCase / kebab-case)

> *"snake_case for DB columns / URLs / form fields; camelCase for PHP; kebab-case for CSS."*

**Not included.** Boost's `style.md` already covers consistent naming across the database, PHP, and HTTP boundaries. Adding it here would be direct overlap with Boost — exactly what the README says to avoid.

Semantic alignment — using the **same domain word** from the UI through to the schema — is a different rule. That lives in [`rules/naming.md`](resources/boost/skills/laravel-best-practices-overlay/rules/naming.md). Inflection (`order_id` vs `$orderId`) stays Boost's; the overlay owns the stem (`order`, not `purchase` for the same concept).

### System metaphor / desktop metaphor as overlay rules

> *"The system metaphor is a story that everyone — customers, programmers, and managers can tell about how the system works."*

**Not included** as a standalone rule. Kent Beck's system metaphor and the desktop metaphor are product-vocabulary exercises (dashboard vs workbench vs back office), too abstract for an AI coding default. The actionable slice — the same names from the end user through the view to the backend and the database — is encoded as ubiquitous language in [`rules/naming.md`](resources/boost/skills/laravel-best-practices-overlay/rules/naming.md).

### Entity versus value-object taxonomy

> *"Ask a domain expert what this is part of; if they name a proper noun, that is your entity."*

**Not included.** Entity vs value object is DDD design judgement, not an actionable Laravel default for an AI to apply unprompted. The overlay names things as the product names them (`rules/naming.md`); it does not teach when a noun should be a model versus an embedded value.

### Prefer Eloquent over `DB::table()` / raw SQL

> *"Avoid talking directly to the database; use Eloquent."*

**Not included.** Boost's `eloquent.md` owns "use Eloquent, not raw SQL" as part of its core mechanics coverage. Same overlap rule.

### Do not use `env()` outside config files

> *"Once configuration has been cached, `env()` returns null outside config files."*

**Not included.** Core Laravel doctrine, documented in the official manual and surfaced by Larastan. Boost's `configuration.md` is the natural home.

## Deliberate deviations from common Laravel/PHP advice

The overlay also takes a small number of positions that *contradict* widely-repeated advice. Each one is flagged in-file at the point it applies; they are listed here for discoverability.

### Quotes for strings: interpolation over single-quotes-plus-`sprintf`

The traditional PHP advice — *"prefer single quotes; reach for `sprintf` whenever a variable is involved"* — is rejected by [`rules/general-design.md`](resources/boost/skills/laravel-best-practices-overlay/rules/general-design.md). The overlay prefers double-quoted interpolation (`"Hello, {$user->name}"`) for the common case, and reserves `sprintf` for genuinely formatted output (fixed widths, numeric precision). Performance difference is negligible on modern PHP; readability wins.

### Database transactions: avoid by default

Boost's `database.md` recommends transactions for multi-step database changes. [`rules/eloquent-opinions.md`](resources/boost/skills/laravel-best-practices-overlay/rules/eloquent-opinions.md) takes the opposite, stricter line: transactions hold locks, multiply failure modes, and should be reserved for genuine multi-row consistency requirements (canonical example: debit one balance, credit another). The deviation is flagged in-file with an instruction to delete the subsection if your team prefers Boost's default.

## PHPStan config decisions

Decisions about the `phpstan.neon.dist` this package ships. Each entry exists so the same trade-off doesn't keep getting re-debated.

### Allow dynamic calls on Eloquent `Builder<*>`

`phpstan-strict-rules' dynamicCallOnStaticMethod` flags every call where an instance method shadows a static-looking signature. Eloquent makes this idiom unavoidable: `Model::where(…)`, `Model::query()`, `Model::orderByDesc(…)`, `Model::whereNotNull(…)` and friends are forwarded through `Illuminate\Database\Eloquent\Model::__callStatic` to a freshly-constructed Builder. PHPStan correctly resolves the receiver to `Illuminate\Database\Eloquent\Builder<X>` and then complains the call is "dynamic, not static".

The shipped config carries a single narrow `ignoreErrors` entry that suppresses `staticMethod.dynamicCall` **only** when the receiver matches `Illuminate\Database\Eloquent\Builder<…>`. The rule still fires on every other class — factories, helpers, registries — where it retains real signal.

The cleaner-looking alternative — disabling `dynamicCallOnStaticMethod` outright via `strictRules.disallowedDynamicCalls: false` — is rejected here. It cures the symptom by removing all coverage rather than narrowing the noise to the place it's known-safe.

### Treat infrastructure exceptions as unchecked

`phpstan-strict-rules`' `missingCheckedExceptionInThrows` is genuinely valuable on application code: it stops methods silently throwing exceptions their callers can't see. It is *not* valuable on infrastructure throws no user code ever catches — declaring them at every call site is pure tax with no signal.

The shipped config extends `parameters.exceptions.uncheckedExceptionClasses` with the following, all of which fall in the "no Laravel application realistically catches this" category:

* `PHPUnit\Framework\MockObject\Exception` — thrown by every PHPUnit prophecy / mock builder. Test code doesn't catch it; if it fires, the test fails — which is the desired behaviour.
* `Psr\SimpleCache\InvalidArgumentException` — declared by the PSR-16 cache interface and re-thrown by Laravel's cache implementations on malformed keys. We never construct malformed keys, and there is no recovery if we did.
* `Illuminate\Contracts\Container\BindingResolutionException` — the DI container's "unresolvable type" error. Catching it is a programming bug masked as an exception.
* `ReflectionException` — language-level reflection failures. Should be a `LogicException` morally.

Production exceptions — `Illuminate\Validation\ValidationException`, `Illuminate\Http\Client\RequestException`, `JsonException`, `Illuminate\Database\QueryException`, custom domain exceptions, etc. — are **deliberately not** on the list and still require `@throws` annotations. The cut-off is "infrastructure plumbing vs. business-meaningful failure".

#### Candidates considered and rejected

* **`Random\RandomException`** — declared by `random_int()` / `random_bytes()` on PHP 8.2+. Marginal: it's an `Exception` (not `Error`), and methods that use it could reasonably be expected to declare it. Left out so projects that want to declare it can; projects that don't can add it locally. Erring on the side of less editorial.
* **`JsonException`** — encoding/decoding decisions are application-level, not infrastructure. Routinely worth declaring (or catching at the boundary) and so kept *out* of the list.

## How to use this file

When considering a new addition to the overlay:

1. **Check here first.** If the practice is listed above, the reasoning stands unless one of the filter conditions has changed (Boost dropped its coverage, Laravel changed direction, the original phrasing is no longer technically wrong, etc.).
2. **If it's not here and you decide to add it**, that is normal — that is the point of the overlay. Add it in the relevant `rules/*.md`, update `SKILL.md`'s Quick Reference, and add a one-line entry to the rule file's `Composes with Boost` block if a Boost rule sits alongside it.
3. **If it's not here and you decide *not* to add it**, add it here with a one-line rationale, so the next pass benefits.
