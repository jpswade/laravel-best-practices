# Flash Messages

Post-redirect feedback for server-rendered apps. Boost covers validation (`withErrors()` / `$errors`) and Fortify covers auth flows, but neither defines how application controllers should flash success, info, warning, or danger messages. Without a convention, each feature invents its own session key (`import_status`, `override_status`, `account_label_status`, …) and Blade templates sprout duplicate `@if (session('…'))` blocks.

Pick **one** convention per application and stick to it. The recommended shape is a single session key with an explicit type:

```php
// App\Support\Flash (or equivalent in the application)
final class Flash
{
    /** @return array{flash: array{type: string, message: string}} */
    public static function success(string $message): array
    {
        return ['flash' => ['type' => 'success', 'message' => $message]];
    }

    /** @return array{flash: array{type: string, message: string}} */
    public static function info(string $message): array
    {
        return ['flash' => ['type' => 'info', 'message' => $message]];
    }

    // warning(), danger() — same shape
}
```

Incorrect — a new session key per feature:

```php
return redirect()
    ->route('user.overrides.index')
    ->with('override_status', 'Override saved.');
```

Correct — typed flash via the shared helper:

```php
return redirect()
    ->route('user.overrides.index')
    ->with(Flash::success('Override saved.'));
```

## Types

Use a small, fixed set of types that map to alert styling:

| Type | Use for |
| --- | --- |
| `success` | Saved, updated, deleted, import complete |
| `info` | Onboarding, neutral guidance |
| `warning` | Reversible caution |
| `danger` | Failure or destructive outcome (when not using validation errors) |

Do not invent ad-hoc types per screen.

## Avoid `status` for application flashes

Laravel's own docs and Breeze often use `->with('status', '…')`. That collides with **Fortify**, which stores auth-specific values in `session('status')` (for example `verification-link-sent`). Prefer a dedicated application key (`flash`, or separate keys per severity such as `success` / `danger`) rather than `status`.

Validation failures stay on `withErrors()` / `$errors`. Do not duplicate validation messages in flash.

## One Blade partial

Render flashes in one shared partial; do not add per-page `@if (session('…'))` alert blocks.

```blade
@if ($flash = session('flash'))
    <x-ui.alert :variant="$flash['type']">{{ $flash['message'] }}</x-ui.alert>
@endif
```

If the application uses severity-as-key instead (`session('success')`, `session('danger')`), the partial should still be the single place that reads those keys — not scattered conditionals in every view.

## Tests

Assert the unified flash shape, not feature-specific session keys:

```php
->assertSessionHas('flash.type', 'success')
->assertSessionHas('flash.message', 'Override saved.');
```

## Composes with Boost

- [`validation.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/validation.md) — validation errors belong in `$errors`, not flash.
- [`blade-views.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/blade-views.md) — shared partial over duplicated view logic; components for alerts.
- [`routing.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/routing.md) — thin controllers flash and redirect; no flash logic in route closures.
- Fortify's `fortify-development` skill — auth flows may use `session('status')`; application flashes should not compete for that key.
