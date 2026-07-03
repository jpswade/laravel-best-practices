# Page Toolbar

A layout slot for page-level actions in server-rendered dashboards. Boost covers Blade idioms and components; this file covers a structural convention Boost is silent on: **where primary actions live on a page**.

Without a convention, actions drift into the content area — duplicate headers, inconsistent placement, and buttons buried below the fold. A toolbar slot keeps context on the left and actions on the right, on every screen.

## Layout owns the chrome

The dashboard layout renders a page header with three yield points:

| Slot | Role |
| --- | --- |
| `breadcrumbs` | Optional trail — where am I? |
| `title` | Current page name |
| `toolbar` | Page-level actions — what can I do here? |

```blade
{{-- layouts/dashboard.blade.php --}}
<div class="d-flex justify-content-between align-items-center">
    <h4>
        @yield('breadcrumbs')
        @yield('title')
    </h4>
    <div>@yield('toolbar')</div>
</div>
```

Each view declares only what it needs:

```blade
@extends('layouts.dashboard')

@section('title', __('Products'))

@section('breadcrumbs')
    <a href="{{ route('products.index') }}">{{ __('Products') }}</a> >
@endsection

@section('toolbar')
    <div class="btn-toolbar mb-2 mb-md-0">
        <a href="{{ route('products.create') }}" class="btn btn-outline-success">
            <i class="fa fa-plus"></i> {{ __('Create') }}
        </a>
    </div>
@endsection

@section('content')
    {{-- main body; no primary actions here --}}
@endsection
```

Incorrect — primary actions in the content area:

```blade
@section('content')
    <div class="d-flex justify-content-end mb-3">
        <a href="{{ route('products.create') }}" class="btn btn-success">Create</a>
    </div>
    <table>...</table>
@endsection
```

Correct — actions in the toolbar slot; content is data only:

```blade
@section('toolbar')
    <a href="{{ route('products.create') }}" class="btn btn-outline-success">Create</a>
@endsection

@section('content')
    <table>...</table>
@endsection
```

## Composition

Toolbars are built inline, wrapped in Bootstrap `btn-toolbar` / `btn-group` (or equivalent flex containers), or composed from shared partials.

Extract a partial when the same control appears on multiple pages or is non-trivial — for example a section-wide shortcut bar, a standard delete trigger, or an inline quick-add form:

```blade
@section('toolbar')
    @include('admin.partials.toolbar')
    @include('partials.buttons.delete')
@endsection
```

An empty `@section('toolbar')@endsection` is valid when a page has no actions.

## Action order

Place controls left to right in this order:

1. Filters, search, view toggles
2. Create / add actions
3. Navigation to related resources
4. Context actions (edit, export, PDF)
5. Destructive actions last

Use semantic button variants consistently: outline-success for create, outline-secondary for navigation and filters, outline-danger for destructive.

## Toolbar is presentation

The toolbar renders links, buttons, and compact forms. It does not decide which route to use, query models, or reshape collections — that belongs in controllers, view composers, or view models (see `rules/blade-views.md`).

## Porting

The slot name varies by framework; the invariant does not:

| Stack | Mechanism |
| --- | --- |
| Laravel Blade | `@section('toolbar')` / `@yield('toolbar')` |
| Rails | `content_for :toolbar` / `yield :toolbar` |
| Django | `{% block toolbar %}` |
| React / Vue / Inertia | Named slot or `actions` prop on a shared page-header component |

## Composes with Boost

- [`blade-views.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/blade-views.md) — shared partials over duplicated markup; components for repeated button groups.
- [`architecture.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/architecture.md) — layouts live under `resources/views/layouts/`; page views extend them and fill named sections.
- `rules/blade-views.md` (this overlay) — toolbar markup is presentation; business logic stays in PHP.
