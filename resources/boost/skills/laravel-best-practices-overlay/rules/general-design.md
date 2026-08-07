# General Design

Cross-cutting design defaults that sharpen Boost's PHP core. Boost's `foundation.blade.php` and `php/core.blade.php` cover the syntactic basics; this file is about higher-level habits — when to add code, where to put it, and when to delete it.

## YAGNI: prefer existing solutions; delete unused code

### Before writing: stop at the first rung that holds

After reading the code the change touches (see Consistency First in this skill's `SKILL.md`), climb this ladder and stop at the first rung that holds:

1. **Need it at all?** — Skip speculative features and unused abstractions.
2. **Already in this codebase?** — Reuse the helper, pattern, or base class that is already here. Do not introduce a second way.
3. **PHP / Illuminate already does it?** — Prefer Collections, `Str`, `Arr`, `Number`, `blank()` / `filled()`, Carbon, and the rest of the framework helpers over a hand-rolled equivalent.
4. **Laravel or platform feature?** — Prefer Form Requests / `Rule`, Eloquent scopes, Blade / `@csrf`, and native HTML (e.g. `<input type="date">`) before reaching for a new widget package.
5. **Already-installed dependency?** — Use Composer packages already in the app. Do not add a new dependency for a thin wrapper around something the stack already covers.
6. **Only then** — Write the smallest change that works: fewest files, no unrequested abstraction.

Do not shrink the diff by cutting trust-boundary validation, security, accessibility, or data-loss handling. Those are not on the chopping block.

### After the fact: remove unused code

Unused code is a liability. It has no tests (because nothing exercises it), it carries no behaviour guarantees, and it tends to drift out of sync with the parts of the system that *are* exercised. When AI tooling sees it in context, it will faithfully replicate the now-wrong patterns it implies.

The fix is simple: when you find unused code, delete it. Git keeps the history. If you genuinely need it back, `git log -S` will find it. "You ain't gonna need it" applies just as forcefully to keeping dead code as it does to writing speculative code in the first place.

Static analysis helps automate this: tools like [`tomasvotruba/unused-public`](https://github.com/TomasVotruba/unused-public) (a PHPStan extension) flag `public` methods nothing calls.

## Helpers for cross-cutting, immutable logic

When a small piece of logic is used in many places, is genuinely immutable (no I/O, no state, deterministic output for the same input), and does not belong on any one model or service, a free function is often the cleanest home. Laravel already does this — `now()`, `collect()`, `route()`, `tap()`, `value()`, `blank()`, `filled()` are all helpers.

Reach for a helper when the alternative is:

- A static method on a `*Helper` class that exists only to hold the method.
- A trait that lives next to every consumer.
- Repeating the same three-line snippet in twenty controllers.

Keep helpers small, pure, and namespaced. Define them in a dedicated file, autoload it via `composer.json`'s `autoload.files`, and protect each with `function_exists()` so they survive autoload cache rebuilds.

```php
// composer.json
{
    "autoload": {
        "files": ["app/helpers.php"]
    }
}

// app/helpers.php
declare(strict_types=1);

if (! function_exists('money_format_pence')) {
    function money_format_pence(int $pence, string $currency = 'GBP'): string
    {
        return Number::currency($pence / 100, in: $currency);
    }
}
```

If the logic touches state, the database, the filesystem, or any service — it is not a helper. Put it on a class.

## Strings: prefer interpolation; reach for `sprintf` for formatted output

For inserting one or two values into a string, double-quoted interpolation is almost always the most readable choice in modern PHP.

```php
$greeting = "Hello, {$user->name}!";
```

For genuinely formatted output — fixed widths, padding, numeric precision, locale-aware number formatting — `sprintf` (or a Laravel/`Stringable` helper) remains the right tool:

```php
$line = sprintf('%-20s %8.2f', $item->name, $item->price);
```

Concatenation with `.` is fine for joining a small number of literal-with-variable fragments; once there are three or more `.` operators in one expression, refactor to interpolation or `sprintf`.

The "single quotes only, sprintf everywhere" advice from older PHP guides is dated — performance differences are negligible, and the readability win of seeing `{$user->name}` inline outweighs the loose convention of "literals are single-quoted". Use double quotes when the string genuinely contains an expression; single quotes otherwise.

## Do not narrate the code

A comment should explain *why* the code is the way it is, not *what* it is doing. Comments that translate the next line into English add no information and drift the moment the line beneath them changes. If a reader needs the comment to follow the code, rename the symbol or extract a method instead.

Incorrect:

```php
// Check if the user is active
if ($user->active) {
    // Send email
    Mail::to($user)->send(new WelcomeEmail());
}
```

Correct:

```php
if ($user->isActive()) {
    $this->sendWelcomeEmail($user);
}
```

## Do not annotate diffs

`// new: …`, `// updated to support X`, `// previously …` belong in the commit message, not in the file. They go stale immediately, and AI tools will read them as current truth.

## When a comment earns its place

Keep a comment only when the reason is not derivable from the code itself:

- Non-obvious business rules or product constraints.
- External constraints (RFC quirks, third-party API behaviour, race-condition windows, browser bugs).
- Deliberate trade-offs ("O(n²) is acceptable here because n ≤ 50").
- Warnings ("must run before listener X subscribes", "do not call from inside a transaction").
- Links to issues, RFCs, or upstream tickets that explain the choice.

Example of a comment that earns its place — it explains an external constraint the code cannot:

```php
// Stripe occasionally delivers webhook events out of order; an
// out-of-sequence "payment_intent.succeeded" before "charge.captured" is
// usually transient and the next event reconciles the state.
```

## Drop redundant DocBlocks

PHP has had type hints on parameters since 5.0, return types since 7.0, property types since 7.4, readonly properties since 8.1, and enums since 8.1. Any DocBlock that only restates information already in the signature is noise.

Incorrect:

```php
/**
 * Calculate the total.
 *
 * @param Order $order
 * @return int
 */
public function calculateTotal(Order $order): int
{
    // ...
}
```

Correct:

```php
public function calculateTotal(Order $order): int
{
    // ...
}
```

DocBlocks remain useful for things the type system cannot express: `@throws` (the checked-exception contract), `@var` on properties whose type cannot be expressed in PHP (`array<string, MyDto>`), the `@deprecated` marker, or genuine narrative documentation. Anything else — delete it.

Boost's `php/core.blade.php` already enforces "type hint everything"; this subsection is the natural follow-on: once the signatures are typed, the DocBlocks that duplicate them are dead weight.

## Composes with Boost

- [`foundation.blade.php`](https://github.com/laravel/boost/blob/main/.ai/foundation.blade.php) and [`php/core.blade.php`](https://github.com/laravel/boost/blob/main/.ai/php/core.blade.php) — Boost's universal "type-hint everything, prefer modern PHP" base. The DocBlock and interpolation guidance above is the natural next step once Boost's typing rules are in place.
- [`tests.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/tests.md) — Boost covers test mechanics; the YAGNI subsection above is the design counterpart: do not write what nothing will exercise, and delete code that has no test.
