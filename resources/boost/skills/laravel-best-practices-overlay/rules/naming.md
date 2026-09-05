# Naming

Functional naming: the *words* used for domain concepts, not the casing. Boost's `style.md` already owns snake_case columns, camelCase methods, kebab-case views, and the rest of Laravel's inflection table. This file is about using the **same stem** for the same thing from the UI through to the schema.

These are defaults for **new** names. Consistency First still applies: do not mass-rename an existing synonym unless the user asked. New code must not introduce a second word for a concept the application already named.

Method-level naming that Boost is also silent on — no "and" in method names, names that do not echo the class — lives in `rules/architecture-additions.md`.

## Ubiquitous language across the stack

Software people and business people should speak the same language, and so should the frontend and the backend. One domain noun per concept, inflected only as Boost requires: `order_id` (column), `$orderId` (PHP), `orders.show` (route name) are the **same word**. `Customer` in the UI, `Client` on the model, and `accounts` in the schema are three languages.

Apply the stem everywhere the concept appears: page heading, form field, Form Request, model, column, route, lang file, Inertia/Livewire prop.

Incorrect — three words for one concept:

```blade
{{-- UI copy --}}
<h1>Customers</h1>
```

```php
class Client extends Model
{
    protected $table = 'accounts';
}

Route::get('/accounts', [AccountController::class, 'index'])->name('accounts.index');
```

```php
// lang/en/clients.php — a fourth stem
'listing' => ['title' => 'Customers'],
```

Correct — one stem, Boost inflection:

```blade
@section('title', __('customers.listing.title'))
```

```php
class Customer extends Model
{
    // table `customers` by convention
}

Route::get('/customers', [CustomerController::class, 'index'])->name('customers.index');
```

```php
// lang/en/customers.php
'listing' => ['title' => 'Customers'],
```

Humanised *display* of a stored value is a different rule. Showing “Pending payment” for the slug `pending_payment` is `rules/display-values.md` — same stem, different form. Ubiquitous language is violated when the UI talks about *Orders* and the schema stores *purchases*.

Lang keys follow the domain word too (`customers.*`, not `accounts.*` for a Customer). Where those strings live is `rules/localization.md`.

One language **per domain**, not one noun for the whole company. A Billing `Customer` need not be a Support `Customer`. Do not flatten bounded contexts into a single company-wide vocabulary.

## Do not invent a parallel vocabulary

Do not keep an “internal” name that only developers use. If the screens say Reservation and the code says `Booking`, every conversation needs a translator.

Incorrect:

```php
class Booking extends Model
{
    // ...
}
```

```blade
@section('title', __('Reservations'))
```

Correct — pick the word the product uses, and use it in code:

```php
class Reservation extends Model
{
    // ...
}
```

```blade
@section('title', __('reservations.listing.title'))
```

If the business name is wrong, change it *with* the business. Do not quietly fork a developer dialect. If the codebase already standardised on the “wrong” word, follow that word for new code until a rename is an explicit task.

## Verbs for behaviour, nouns for things

Methods are actions (verbs). Models, entities, and value objects are things (nouns).

Incorrect:

```php
$orderProcessor->order($payload);   // verb used as a dumping-ground method
$invoice->cancellation();           // noun used as a method
class DoInvoice extends Model {}    // verb phrase used as an entity
```

Correct:

```php
$order->cancel();
$invoice->cancel();

class Invoice extends Model {}
enum InvoiceStatus: string {}
```

Laravel type names are *classes* (things), even when they contain a verb: `CreateOrderAction`, `StoreOrderRequest`, `OrderController`, `SendInvoice`. Do not “correct” those conventions. The rule is: methods *do*, models *are*.

## Name the job, not a Manager

`Manager` only says “looks after stuff”. The name should state the job.

Incorrect:

```php
class UrlManager {}
class SessionManager {}
class OrderProcessor {}
class DateHelper {}
```

Correct — the suffix (or the absence of one) says what the class *does*:

```php
class UrlBuilder {}
class SessionStore {}
class PlaceOrder {}
class DateFormat {}
```

The same smell attaches to vague application `*Helper`, `*Processor`, and `*Handler` classes that only “look after stuff”.

Carve-outs — these are framework patterns, not the smell:

- `Illuminate\Support\Manager` and its extenders (Cache, Queue, Auth, Hash) — the container-driver pattern.
- `ExceptionHandler` / `Handler` as Laravel's exception reporter.
- `handle()` on jobs, listeners, commands, and actions — a dispatch-point method name, not a class suffix.

## Composes with Boost

- [`style.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/style.md) — inflection and case (singular models, snake_case columns, camelCase methods). This file is *which words*, not *which case*.
- [`architecture.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/architecture.md) — where a class lives; this file is what to call the concept it represents.
- This overlay's `rules/architecture-additions.md` — method names with no "and", and names that do not echo the class.
- This overlay's `rules/display-values.md` — humanised labels vs stored slugs; same stem, different form.
- This overlay's `rules/localization.md` — namespaced lang files; keys still use the domain word.
