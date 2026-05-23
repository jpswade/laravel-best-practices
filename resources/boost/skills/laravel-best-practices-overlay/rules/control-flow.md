# Control Flow

Opinionated PHP control-flow guidance for cases where Boost is silent. Boost's `error-handling.md` covers how to *report* exceptions; this section covers how to *avoid* using exceptions for control flow in the first place.

## Avoid `switch`/`case`

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

## Exceptions only when exceptional

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

## Avoid bare `\Exception` catches

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

## Avoid `try`/`catch`

A `try`/`catch` is comparatively expensive and is rarely the cleanest answer. Most of the time, an early return, a validated input, or a value object that cannot be in a bad state will keep the failure mode out of the code path entirely. When you find yourself wrapping a method body in `try`/`catch`, ask first whether the throw is necessary at all.

There are legitimate uses — boundaries with third-party SDKs, infrastructure failures, deserialisation of untrusted input — and these should be explicit and narrow. The bar is: "I am handling this exception meaningfully right here", not "I am catching it just to log and rethrow".

## Return early / guard clauses

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

## Consistent return types

Every path through a method should return the same type. Mixing `User` and `false`, or `Collection` and `null`, forces every caller to handle two shapes — and untyped callers will silently get the wrong one.

- Returning an object on the happy path → return `null` on the negative path, not `false`.
- Returning a string → return an empty string `''` on the negative path.
- Returning a collection → return an empty collection, not `null` or `false`.
- If there really is nothing useful to return, consider throwing — but only if the situation is exceptional (see above).

> Consistently returning the same type means that we can always trust the response of a function or method.

See [Functions should use "return" consistently - SonarSource RSPEC-3801](https://rules.sonarsource.com/php/RSPEC-3801).

## Avoid the lone `!` operator

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

## Avoid magic numbers

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

The match expression at the top of this file showed an enum on the left-hand side; that pairing is the canonical modern Laravel shape for branching on a fixed value set.

## Composes with Boost

- [`error-handling.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/error-handling.md) — once you do throw, Boost owns how to report, render and throttle exceptions.
- [`eloquent.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/eloquent.md) — "Define Attribute Casts" covers the casting end of the backed-enum pattern above.
- [`style.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/style.md) — Boost's `blank()` / `filled()` / `Str` / `Arr` helper preferences pair naturally with the lone-`!` guidance here.
