# Localisation

Prefer namespaced lang files with `__()` for user-facing copy. Do not hard-code strings in Blade, controllers, form requests, notifications, mail classes, or HTTP exception messages when a domain lang file already exists (or should).

**Quick check:** if a customer or admin could read it in the browser or an email, it belongs in lang — not a string literal or a `private const` on the class.

Store PHP lang files under `lang/{locale}/` (Laravel's default after `lang:publish`), or `resources/lang/{locale}/` if the application still uses that path. Respect the application's configured locale and fallback — do not invent a second layout.

## Namespaced lang files (preferred)

Domain CRUD and feature screens use short keys in PHP lang files and `__()` with dot syntax:

```php
// lang/en/orders.php
'responses' => ['created' => ':name Order has been successfully added'],
```

```blade
@section('title', __('orders.listing.title'))
{{ __('orders.buttons.download_pdf') }}
```

```php
->with('success', __('orders.responses.created', ['name' => $order->name]));
```

Use `__()` rather than `trans()` — same behaviour for PHP lang keys; `__()` is what Laravel and Boost document.

## Inline strings (exception)

`__('Cancel')` / `__('Edit Report Schedule')` — English text as the key — is permitted for sparse copy, not recommended as the default.

**Rule of three:** once a Blade file (or related partial set) accumulates three or more user-facing strings, move them into a namespaced lang file and switch the call sites to `__('domain.key')`. Until then, inline `__()` is fine for one-off labels.

## Lang file layout

New domain files should follow the established sections:

- `listing` — index title and table headers
- `create`, `edit`, `show` — page titles (use `:name`, `:id` placeholders)
- `buttons` — action labels
- `form` — field labels
- `responses` — flash messages in controllers

Add domain-specific keys as needed (e.g. `orders.types`, `reports.statuses`).

## Not lang files

User- or account-authored content (product names, custom labels, tag names) belongs on the model — e.g. a translatable attribute package — not in application lang files.

Laravel's bundled groups (`auth`, `validation`, `passwords`, `pagination`) are used implicitly — do not duplicate unless publishing overrides.

## Composes with Boost

- [`config.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/config.md) — "Use Constants and Language Files": when lang files exist, use `__()` for user-facing strings (Boost's example is already a namespaced key). This overlay chooses namespaced PHP files as the default and treats inline / JSON-style keys as the sparse exception.
- Laravel [Localization](https://laravel.com/docs/localization) — documents both short keys and translation-strings-as-keys; retrieving either is shown with `__()` first. Short keys are how Laravel itself ships validation and auth copy.
