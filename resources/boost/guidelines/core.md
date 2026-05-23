# Laravel Best Practices (Overlay)

Opinionated, additive best-practices that compose alongside Laravel Boost's built-in `laravel-best-practices` skill. Boost covers the mechanics of Laravel and PHP excellently; this overlay covers the ground Boost is silent on (control-flow opinions, architectural defaults, money-handling, named queues) plus a small set of deliberate opinionated counter-positions (clearly flagged where they exist).

Four topics, each a self-contained section: **Control Flow**, **Eloquent Opinions**, **Architecture Additions**, **General Design**. Each section ends with the Boost rules it sits alongside.

> **Why one file?** Laravel Boost's convention for third-party packages is one guideline file per package, mirroring the first-party `core.blade.php` pattern. See [`laravel/boost#822`](https://github.com/laravel/boost/issues/822) for the design context. Topics that outgrow this shape should be split out as a Boost skill rather than as a second guideline file.

## Control Flow

Opinionated PHP control-flow guidance for cases where Boost is silent. Boost's `error-handling.md` covers how to *report* exceptions; this section covers how to *avoid* using exceptions for control flow in the first place.

### Avoid `switch`/`case`

`switch`/`case` is uniquely error-prone in PHP — it uses loose comparison (`==`), fall-through is implicit, and adding a new branch tends to grow the structure rather than clarifying it. Prefer `match` (PHP 8+) for value mapping, or polymorphic dispatch for branching by type.

Incorrect:

```php
switch ($order->status) {
    case 'pending':
        $message = 'Awaiting payment.';
        break;
    case 'paid':
        $message = 'Thanks!';
        break;
    default:
        $message = 'Unknown.';
}
```

Correct (value mapping):

```php
$message = match ($order->status) {
    OrderStatus::Pending => 'Awaiting payment.',
    OrderStatus::Paid    => 'Thanks!',
};
```

`match` is strict-comparison by default, has no fall-through, and an unhandled value throws — all three of which are improvements on `switch`.

When the branches grow real logic (not just a value), reach for polymorphic dispatch: a small interface and one implementation per case keeps each branch isolated and testable.

### Exceptions only when exceptional

An exception signals that the program cannot meaningfully continue along its happy path. Using `throw` to signal an expected business outcome ("user not found", "form invalid", "stock unavailable") conflates "this thing failed because something is wrong" with "this thing returned a negative answer", and forces every caller into a `try`/`catch` mindset.

Incorrect:

```php
public function findActiveUser(int $id): User
{
    $user = User::find($id);

    if ($user === null || ! $user->isActive()) {
        throw new UserNotActiveException();
    }

    return $user;
}
```

Correct:

```php
public function findActiveUser(int $id): ?User
{
    return User::active()->find($id);
}
```

Reserve exceptions for *exceptional* situations — invariants violated, external systems unreachable, programming errors. For expected negative outcomes, return `null`, an empty collection, or a typed result.

### Avoid bare `\Exception` catches

`\Exception` is the root of almost every PHP exception. Catching it is equivalent to "catch absolutely everything and hide it", which is rarely what is intended. Always catch the narrowest exception type that matches the situation you are actually handling.

Incorrect:

```php
try {
    $client->charge($amount);
} catch (\Exception $e) {
    Log::error($e->getMessage());
}
```

Correct:

```php
try {
    $client->charge($amount);
} catch (PaymentDeclinedException $e) {
    Log::warning('Payment declined', ['user' => $userId]);
}
```

See [the PHP manual on exception handling](https://www.php.net/manual/en/language.exceptions.php) for the SPL exception hierarchy.

### Avoid `try`/`catch`

A `try`/`catch` is comparatively expensive and is rarely the cleanest answer. Most of the time, an early return, a validated input, or a value object that cannot be in a bad state will keep the failure mode out of the code path entirely. When you find yourself wrapping a method body in `try`/`catch`, ask first whether the throw is necessary at all.

There are legitimate uses — boundaries with third-party SDKs, infrastructure failures, deserialisation of untrusted input — and these should be explicit and narrow. The bar is: "I am handling this exception meaningfully right here", not "I am catching it just to log and rethrow".

### Return early / guard clauses

Flat code is easier to read than nested code. Validate inputs and bail out at the top of the method; the happy path is then the unindented body.

Incorrect:

```php
public function process(Order $order): void
{
    if ($order->isPaid()) {
        if ($order->hasStock()) {
            if (! $order->isCancelled()) {
                $this->ship($order);
            }
        }
    }
}
```

Correct:

```php
public function process(Order $order): void
{
    if (! $order->isPaid()) {
        return;
    }

    if (! $order->hasStock()) {
        return;
    }

    if ($order->isCancelled()) {
        return;
    }

    $this->ship($order);
}
```

See [Return early - DEV Community](https://dev.to/jpswade/return-early-12o5) for more.

### Consistent return types

Every path through a method should return the same type. Mixing `User` and `false`, or `Collection` and `null`, forces every caller to handle two shapes — and untyped callers will silently get the wrong one.

- Returning an object on the happy path → return `null` on the negative path, not `false`.
- Returning a string → return an empty string `''` on the negative path.
- Returning a collection → return an empty collection, not `null` or `false`.
- If there really is nothing useful to return, consider throwing — but only if the situation is exceptional (see above).

> Consistently returning the same type means that we can always trust the response of a function or method.

See [Functions should use "return" consistently - SonarSource RSPEC-3801](https://rules.sonarsource.com/php/RSPEC-3801).

### Avoid the lone `!` operator

`if (! $value)` is concise but it does not communicate intent and it is not type-safe. It returns true for `false`, `null`, `0`, `'0'`, `''`, `[]` — six very different conditions that almost certainly should not all be handled identically.

Incorrect:

```php
if (! $value) {
    return;
}
```

Correct, when the type is known:

```php
if ($value === null) { /* ... */ }   // object-or-null
if ($value === false) { /* ... */ }  // boolean
if ($value === 0) { /* ... */ }      // int
if ($value === '') { /* ... */ }     // string
```

Or use Laravel's intent-revealing helpers when "empty-ish in any sense" is genuinely what you mean:

```php
if (blank($value)) { /* ... */ }
if (filled($value)) { /* ... */ }
```

See the [PHP type comparison tables](https://www.php.net/manual/en/types.comparisons.php) for why the lone `!` is dangerous in practice.

### Avoid magic numbers

A literal `1`, `7`, or `'normal'` scattered through code carries no meaning. Extract every fixed value into a named constant or a backed enum.

Incorrect:

```php
if ($user->role === 1) { /* ... */ }
```

Correct (class constants):

```php
if ($user->role === User::ROLE_ADMIN) { /* ... */ }
```

Better still, for a fixed set of values (status, type, role, kind), use a PHP 8.1 backed enum. Enums carry the type through every signature, play naturally with `match`, and cast directly in Eloquent.

```php
enum Role: string
{
    case Admin    = 'admin';
    case Customer = 'customer';
    case Guest    = 'guest';
}

class User extends Model
{
    protected function casts(): array
    {
        return ['role' => Role::class];
    }
}

if ($user->role === Role::Admin) { /* ... */ }
```

The match expression at the top of this section showed an enum on the left-hand side; that pairing is the canonical modern Laravel shape for branching on a fixed value set.

**Composes with Boost:**

- [`error-handling.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/error-handling.md) — once you do throw, Boost owns how to report, render and throttle exceptions.
- [`eloquent.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/eloquent.md) — "Define Attribute Casts" covers the casting end of the backed-enum pattern above.
- [`style.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/style.md) — Boost's `blank()` / `filled()` / `Str` / `Arr` helper preferences pair naturally with the lone-`!` guidance here.

## Eloquent Opinions

Opinionated Eloquent positions that Boost's `eloquent.md` does not take a side on. Boost covers the *mechanics* (relationships, casting, scopes, mass-assignment) excellently; this section is about *defaults* — what you should reach for first when designing a model or query.

### Consider soft deletes when undo matters

For most user-owned data, "delete" is really "hide from the user, keep the paper trail". Soft deletes (`Illuminate\Database\Eloquent\SoftDeletes`) give you that for free: the row stays, queries exclude it by default, audit and recovery remain possible.

Default to soft deletes on user-facing or auditable entities (orders, posts, comments, accounts). Skip them where retention is not desired or is actively harmful — short-lived join rows, GDPR-sensitive personal data with a "right to be forgotten" requirement, transient sessions, ephemeral caches.

```php
use Illuminate\Database\Eloquent\SoftDeletes;

class Order extends Model
{
    use SoftDeletes;
}
```

This is a default, not a mandate — make a deliberate choice per model, and write down the reason on the ones where you opt out.

### Don't needlessly access relationships from models

Loading a whole related model just to read a foreign key on the *owning* model is gratuitous I/O. The foreign key already lives on the parent row.

Incorrect:

```php
$accountId = $user->account->id;
```

Correct:

```php
$accountId = $user->account_id;
```

The first version issues an extra query (or pulls a hydrated model out of the identity map) for a value that was already on `$user`. This compounds badly inside loops. Boost's `eloquent.md` already calls out the N+1 problem via `with()` — this is the same family of mistake one level down.

### Avoid database transactions unless you have to

Transactions are a powerful but heavy tool: they hold locks, they can deadlock under load, and they multiply the failure modes you have to reason about. Use them when you have a genuine multi-statement consistency requirement — the canonical example is "debit one balance and credit another". Do **not** wrap every write in `DB::transaction()` reflexively.

> **In-file flag for Boost users**: this is a deliberate opposite to Boost's `database.md`, which says to use transactions for multi-step database changes. Both are defensible; this overlay takes the stricter "transactions are an exception, not a default" line. If your team prefers Boost's default, remove this subsection.

Correct (one is genuinely transactional, the other doesn't need to be):

```php
DB::transaction(function () use ($from, $to, $amount): void {
    $from->decrement('balance', $amount);
    $to->increment('balance', $amount);
});

Post::create(['title' => $title, 'body' => $body]);
```

See [Transactionless - Martin Fowler](https://martinfowler.com/bliki/Transactionless.html) for the broader rationale.

### Use integers, not floats, for money

Floating-point arithmetic rounds. `0.1 + 0.2 !== 0.3`. For anything that touches money, store the smallest unit (pence, cents, micros) as an integer and format for display only at the very edge.

Incorrect:

```php
Schema::create('orders', function (Blueprint $table) {
    $table->float('total');
});

$order->total = 19.99;
```

Correct:

```php
Schema::create('orders', function (Blueprint $table) {
    $table->unsignedBigInteger('total_pence');
});

$order->total_pence = 1999;
```

Stripe stores [zero-decimal amounts as integers](https://stripe.com/docs/currencies#zero-decimal); Google Standard Payments uses [micros](https://developers.google.com/standard-payments/reference/glossary#micros) (1/1,000,000 of a unit). Pick a unit, declare it in the column name, never silently convert.

A dedicated money value object (e.g. `Money\Money`) is the next step up: it wraps the integer plus a currency and refuses to mix currencies. Worth the dependency on any real e-commerce or fintech codebase.

### Pass the smallest unit across boundaries

The integer-money rule extends past the database. Job payloads, queue messages, API responses, cache values — anything that crosses a serialisation boundary should carry the integer minor unit (and ideally a currency code), not a float.

Incorrect:

```php
ProcessRefund::dispatch(['amount' => 19.99]);
```

Correct:

```php
ProcessRefund::dispatch(['amount_pence' => 1999, 'currency' => 'GBP']);
```

Same reasoning as the previous subsection, applied at every boundary: the moment a float touches money, rounding errors become possible, and they tend to surface later, in production, under load.

**Composes with Boost:**

- [`eloquent.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/eloquent.md) — mechanics of relationships, casts, scopes, mass-assignment.
- [`database.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/database.md) — Boost recommends transactions for multi-step writes; the "avoid transactions" subsection above is the opinionated counter-position.
- [`migration.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/migration.md) — when you adopt integer-money, declare the column with `unsignedBigInteger` (or `unsignedInteger` where it definitely fits) and name it with the unit suffix.

## Architecture Additions

Architectural and naming defaults that Boost does not cover. Boost's `architecture.md`, `controllers.md`, `jobs.md`, and `queues.md` describe *what to do* with each class; this section is about *how to size and name them*.

### No "and" in method names

A method name with "and" in it almost always names two responsibilities glued together. The single-responsibility principle is easy to apply at the method level — split it.

Incorrect:

```php
$service->validateAndSaveUser($payload);
```

Correct:

```php
$service->validate($payload);
$service->save($payload);
```

If the two operations are genuinely a single atomic concept ("register" being both "create user" and "send welcome email"), name the concept, not the conjunction: `$service->register($payload)`.

### Names should be contextual

A method's name should make sense in the context of the class it lives on. Once you know you are calling a method on a `Person`, repeating `Person` in the method name is noise.

Incorrect:

```php
$person->getPerson();
$user->isUserActive();
$order->cancelOrder();
```

Correct:

```php
$person->get();
$user->isActive();
$order->cancel();
```

The class name is already on the left-hand side at the call site; the method should add new information, not echo what's already there.

### Default to `private`

Visibility is part of the public API of a class. `public` means "callers everywhere may depend on this"; `protected` means "subclasses may depend on this"; `private` means "only this class depends on this". Start at `private`. Widen only when there is a concrete need.

Incorrect:

```php
class OrderService
{
    public function calculateTotal(Order $order): int { /* ... */ }
    public function applyDiscount(Order $order): int { /* ... */ }
}
```

Correct:

```php
class OrderService
{
    public function totalFor(Order $order): int { /* ... */ }

    private function calculateTotal(Order $order): int { /* ... */ }
    private function applyDiscount(Order $order): int { /* ... */ }
}
```

The narrower the public surface, the easier the class is to refactor, test, and reason about. See [Make everything private in your PHP classes](https://www.exakat.io/make-everything-private-php-classes/).

A static analyser like [`tomasvotruba/unused-public`](https://github.com/TomasVotruba/unused-public) can find `public` methods that nothing outside the class actually calls — a useful tool when adopting this practice in an existing codebase. See `phpstan.neon.dist` in this package for an opt-in hint.

### Thin `handle()` methods

`handle()` on a job, listener or console command is a dispatch point, not a place for business logic. Treat it like a controller action: pull in dependencies, delegate, return.

Incorrect:

```php
class SendInvoice implements ShouldQueue
{
    public function handle(): void
    {
        $invoice = Invoice::find($this->invoiceId);
        $pdf = PDF::loadView('invoices.pdf', ['invoice' => $invoice]);
        $path = storage_path("invoices/{$invoice->id}.pdf");
        $pdf->save($path);

        Mail::to($invoice->customer)
            ->send(new InvoiceMail($invoice, $path));

        $invoice->update(['sent_at' => now()]);
    }
}
```

Correct:

```php
class SendInvoice implements ShouldQueue
{
    public function handle(InvoiceMailer $mailer): void
    {
        $mailer->send(Invoice::findOrFail($this->invoiceId));
    }
}
```

The mailer class owns the logic, can be unit-tested without queueing, and can be reused from a controller or another job.

### No logic in routes

Route files declare the shape of the URL space. Keep them declarative — a path, an HTTP verb, and a controller method. Closures that contain real logic (database calls, conditionals, mutations) make routes harder to test, harder to cache, and tend to grow.

Incorrect:

```php
Route::get('/orders/{id}', function (int $id) {
    $order = Order::with('items')->find($id);

    if ($order === null) {
        abort(404);
    }

    return view('orders.show', ['order' => $order]);
});
```

Correct:

```php
Route::get('/orders/{order}', [OrderController::class, 'show']);
```

`route:cache` only works when all route definitions are serialisable, which excludes closures with bound variables. Controllers also pick up explicit route-model binding, form requests, middleware, and policies for free.

### Named queues

The default queue collects every kind of work — fast and slow, retryable and one-shot, customer-facing and internal. As soon as one job type backs up, every other job sitting behind it in the default queue is delayed too. Name your queues by purpose so they can be scaled, throttled and prioritised independently.

Incorrect:

```php
SendInvoice::dispatch($invoice);
```

Correct:

```php
SendInvoice::dispatch($invoice)->onQueue('emails');
ProcessImport::dispatch($file)->onQueue('imports-slow');
```

```bash
php artisan queue:work --queue=emails
php artisan queue:work --queue=imports-slow
```

The names should describe the *kind of work*, not the *kind of class* — `emails`, `webhooks`, `reports`, `imports-slow` are good; `jobs`, `mailables`, `default` are not.

**Composes with Boost:**

- [`architecture.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/architecture.md) — folder structure, namespacing, where a class lives.
- [`controllers.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/controllers.md) — thin-controller doctrine; the "no logic in routes" subsection above is the same rule applied one layer earlier.
- [`jobs.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/jobs.md) and [`queues.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/queues.md) — Boost owns "what a job looks like" and how to dispatch; the named-queues subsection above adds the operational dimension.

## General Design

Cross-cutting design defaults that sharpen Boost's PHP core. Boost's `foundation.blade.php` and `php/core.blade.php` cover the syntactic basics; this section is about higher-level habits — when to add code, where to put it, and when to delete it.

### YAGNI: remove unused code

Unused code is a liability. It has no tests (because nothing exercises it), it carries no behaviour guarantees, and it tends to drift out of sync with the parts of the system that *are* exercised. When AI tooling sees it in context, it will faithfully replicate the now-wrong patterns it implies.

The fix is simple: when you find unused code, delete it. Git keeps the history. If you genuinely need it back, `git log -S` will find it. "You ain't gonna need it" applies just as forcefully to keeping dead code as it does to writing speculative code in the first place.

Static analysis helps automate this: tools like [`tomasvotruba/unused-public`](https://github.com/TomasVotruba/unused-public) (a PHPStan extension) flag `public` methods nothing calls.

### Helpers for cross-cutting, immutable logic

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

### Strings: prefer interpolation; reach for `sprintf` for formatted output

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

### Drop redundant DocBlocks

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

**Composes with Boost:**

- [`foundation.blade.php`](https://github.com/laravel/boost/blob/main/.ai/foundation.blade.php) and [`php/core.blade.php`](https://github.com/laravel/boost/blob/main/.ai/php/core.blade.php) — Boost's universal "type-hint everything, prefer modern PHP" base. The DocBlock and interpolation guidance above is the natural next step once Boost's typing rules are in place.
- [`tests.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/tests.md) — Boost covers test mechanics; the YAGNI subsection above is the design counterpart (delete the code that has no test).
