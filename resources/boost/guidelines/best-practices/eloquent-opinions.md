# Eloquent Opinions

Opinionated Eloquent positions that Boost's `eloquent.md` does not take a side on. Boost covers the *mechanics* (relationships, casting, scopes, mass-assignment) excellently; this file is about *defaults* — what you should reach for first when designing a model or query.

## Consider soft deletes when undo matters

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

## Don't needlessly access relationships from models

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

## Avoid database transactions unless you have to

Transactions are a powerful but heavy tool: they hold locks, they can deadlock under load, and they multiply the failure modes you have to reason about. Use them when you have a genuine multi-statement consistency requirement — the canonical example is "debit one balance and credit another". Do **not** wrap every write in `DB::transaction()` reflexively.

> **In-file flag for Boost users**: this is a deliberate opposite to Boost's `database.md`, which says to use transactions for multi-step database changes. Both are defensible; this overlay takes the stricter "transactions are an exception, not a default" line. If your team prefers Boost's default, remove this section.

Correct (one is genuinely transactional, the other doesn't need to be):

```php
DB::transaction(function () use ($from, $to, $amount): void {
    $from->decrement('balance', $amount);
    $to->increment('balance', $amount);
});

Post::create(['title' => $title, 'body' => $body]);
```

See [Transactionless - Martin Fowler](https://martinfowler.com/bliki/Transactionless.html) for the broader rationale.

## Use integers, not floats, for money

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

## Pass the smallest unit across boundaries

The integer-money rule extends past the database. Job payloads, queue messages, API responses, cache values — anything that crosses a serialisation boundary should carry the integer minor unit (and ideally a currency code), not a float.

Incorrect:

```php
ProcessRefund::dispatch(['amount' => 19.99]);
```

Correct:

```php
ProcessRefund::dispatch(['amount_pence' => 1999, 'currency' => 'GBP']);
```

Same reasoning as the previous section, applied at every boundary: the moment a float touches money, rounding errors become possible, and they tend to surface later, in production, under load.

## Composes with Boost

- [`eloquent.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/eloquent.md) — mechanics of relationships, casts, scopes, mass-assignment.
- [`database.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/database.md) — Boost recommends transactions for multi-step writes; the "avoid transactions" section above is the opinionated counter-position.
- [`migration.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/migration.md) — when you adopt integer-money, declare the column with `unsignedBigInteger` (or `unsignedInteger` where it definitely fits) and name it with the unit suffix.
