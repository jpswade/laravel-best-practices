# Blade Views

Opinionated separation-of-concerns guidance for Blade templates. Boost's `blade-views.md` owns Blade *idioms* — `$attributes->merge()`, `@pushOnce`, components over `@include`, `@aware`, fragments. This file covers the higher-level principle Boost is silent on: **Blade is for presentation; logic belongs in PHP**.

It is the same family of rule as *No logic in routes* and *Thin `handle()` methods* in `rules/architecture-additions.md`, applied one layer further out — at the rendering boundary.

## No business logic in Blade

A Blade template renders data; it should not decide what data to fetch, which route to link to, or how to reshape a collection. A `@php` block that holds real logic — queries, route resolution, conditionals on application state, mutation of collections — makes the view harder to test, hides N+1 risks, can't be reused by another consumer of the same model, and tends to grow.

Incorrect:

```blade
@php
    $paymentsShowRoute = $area === 'admin' ? 'admin.payments.show' : 'manager.payments.show';
    $primaryPayment = $order->payments->first(fn ($p) => $p->payment_id);
@endphp

<a href="{{ route($paymentsShowRoute, $primaryPayment) }}">
    Payment #{{ $primaryPayment->id }}
</a>
```

Correct — the controller (or a view composer) prepares the data; the template only renders:

```blade
<a href="{{ route($paymentsShowRoute, $primaryPayment) }}">
    Payment #{{ $primaryPayment->id }}
</a>
```

The template did not change; the difference is where `$paymentsShowRoute` and `$primaryPayment` are *resolved*.

## Where each kind of logic belongs

| Concern | Home |
| --- | --- |
| Routing decisions (which named route to link to) | Controller, form-request resolver, or a dedicated view-model class |
| Data fetching (queries, `find`, `where`) | Controller or service; pass results into the view |
| Finding "the primary X" / "the first matching Y" | Method on the model (e.g. `$order->primaryPayment()`) |
| Variables shared by partials of the same screen | A view composer registered in `AppServiceProvider` |
| Computed / formatted display values | Eloquent accessor, presenter, or a `toViewModel()` method |

The shared rule: *the template is told what to render; it does not decide what to render.*

What the user *sees* must be humanised — never the raw stored value. That principle lives in `rules/display-values.md`.

## Allowed in Blade

Presentation primitives, with no decision-making:

- `@if`, `@foreach`, `@switch`, `@include`, `@component`, `<x-*>`.
- Simple property access: `{{ $order->reference }}`, `{{ $payment->display_card }}`.
- Calling presentation accessors already on a model or presenter: `{{ $order->present()->subtotal }}`.
- `route()`, `__()` (prefer over `trans()`), `asset()`, `config()` — with the values passed in from a controller or view composer.
- `@php` blocks that contain only IDE hints (no runtime statements), for example:

```blade
@php
    /** @var \App\Models\Payment $payment */
@endphp
```

## Use view composers for shared partial data

When the same partial is included from multiple parents and each one needs to pre-compute the same variables, register a view composer in `AppServiceProvider` rather than duplicating a `@php` block at the top of every including parent.

```php
View::composer('orders.partials.payment-summary', OrderPaymentSummaryComposer::class);
```

The composer is a normal PHP class, can be unit-tested in isolation, and keeps the partial's contract explicit: *I expect these variables; here is the one place that supplies them*.

## Composes with Boost

- [`blade-views.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/blade-views.md) — Boost owns Blade idioms (`$attributes->merge()`, `@pushOnce`, components over `@include`, `@aware`, fragments). The rule above is the separation-of-concerns principle that sits above those idioms.
- [`architecture.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/architecture.md) — folder structure and where presenters, view models or view composer classes should live.
