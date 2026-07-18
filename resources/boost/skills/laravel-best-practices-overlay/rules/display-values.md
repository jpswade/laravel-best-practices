# Display Values

When text is shown to a user in the UI, show the **display** (humanised) form — never the raw stored value. Machine values belong in the database, APIs, and code; people see labels, titles, and formatted output.

This sits beside `rules/blade-views.md`: that file says *where* formatting lives (accessors, presenters, view models); this file says *what* the user must see.

## Never dump the raw value

Incorrect — status slug, enum case name, ISO timestamp, integer money, or boolean `1`/`0` rendered as-is:

```blade
{{ $order->status }}
{{ $order->status->name }}
{{ $order->created_at }}
{{ $order->total_pence }}
{{ $user->is_active }}
```

Correct — a label or formatter prepared for humans:

```blade
{{ $order->status->label() }}
{{ $order->created_at->timezone(config('app.timezone'))->format('d M Y, H:i') }}
{{ Number::currency($order->total_pence / 100, in: 'GBP') }}
{{ $user->is_active ? __('Active') : __('Inactive') }}
```

The same rule applies outside Blade: Filament columns, Livewire props rendered in the browser, Inertia/React copy, mail templates, and PDF views. If a human reads it, humanise it.

## Prefer a single display home

Do not scatter `match ($status)` or `ucfirst(str_replace('_', ' ', …))` across templates. Put the human form next to the value:

| Kind of value | Typical display home |
| --- | --- |
| Backed enum / status | `label()`, `title()`, or `HasLabel` on the enum |
| Money (integer minor units) | Helper, `Number::currency`, or a money value object at the edge |
| Dates / times | Carbon formatting (or a shared formatter) in the app timezone / locale |
| Booleans / flags | Explicit Active / Inactive (or equivalent) labels — not `true` / `1` |
| Codes, slugs, machine keys | A lookup label or translation key; keep the code for IDs and URLs only |

```php
enum OrderStatus: string
{
    case PendingPayment = 'pending_payment';
    case Fulfilled = 'fulfilled';

    public function label(): string
    {
        return match ($this) {
            self::PendingPayment => __('Pending payment'),
            self::Fulfilled => __('Fulfilled'),
        };
    }
}
```

## Exceptions (explicit only)

Raw values are allowed when the surface is **deliberately** technical:

- Developer tooling, debug panels, Horizon / Telescope-style UIs.
- Support or ops screens that show IDs, hashes, or payload dumps *as their job*.
- Copy-to-clipboard of a machine identifier when the human label is shown alongside it.

Do not treat “admin area” as a blanket exception. Admin users are still users: show “Pending payment”, not `pending_payment`, unless the field is explicitly a technical identifier.

## Composes with Boost

- [`blade-views.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/blade-views.md) — Blade idioms; this overlay's `rules/blade-views.md` owns where presentation logic lives.
- [`eloquent.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/eloquent.md) — accessors and casts are the usual Eloquent home for display-ready attributes.
- This overlay’s `rules/eloquent-opinions.md` — money stays as integers until the display edge; this file is that edge.
