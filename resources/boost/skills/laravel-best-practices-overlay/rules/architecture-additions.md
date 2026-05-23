# Architecture Additions

Architectural and naming defaults that Boost does not cover. Boost's `architecture.md`, `controllers.md`, `jobs.md`, and `queues.md` describe *what to do* with each class; this file is about *how to size and name them*.

## No "and" in method names

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

## Names should be contextual

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

## Default to `private`

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

## Thin `handle()` methods

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

## No logic in routes

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

## Named queues

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

## Composes with Boost

- [`architecture.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/architecture.md) — folder structure, namespacing, where a class lives.
- [`controllers.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/controllers.md) — thin-controller doctrine; the "no logic in routes" subsection above is the same rule applied one layer earlier.
- [`jobs.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/jobs.md) and [`queues.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/queues.md) — Boost owns "what a job looks like" and how to dispatch; the named-queues subsection above adds the operational dimension.
