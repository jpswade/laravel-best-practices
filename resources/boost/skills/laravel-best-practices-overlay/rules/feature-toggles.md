# Feature Toggles

Make feature availability explicit. Check capabilities and configuration rather
than environment names, and separate deployment from release where independent
rollout is needed. Reuse the application's existing mechanism and conventions.

## Check the condition you actually need

An environment name does not establish whether a dependency is installed, an
integration is configured, or a feature is ready for use. Express that condition
directly so the same behaviour can be exercised in any environment.

Incorrect:

```php
if (app()->environment('production')) {
    $this->sendWebhook($event);
}
```

Correct:

```php
if (config('services.webhooks.enabled') === true) {
    $this->sendWebhook($event);
}
```

This example is an operational switch; it does not establish that the endpoint
is configured or that the caller is authorised. Check those prerequisites
where needed. Likewise, check for an optional dependency's availability when
that is the real requirement, but do not treat its presence as permission to
enable debugging or other restricted behaviour.

Environment-specific configuration values are fine. Avoid scattering checks
for `local`, `staging` or `production` through application behaviour. Retain
framework safety guards; this rule does not require removing production
confirmation checks or exposing development tools.

## Decouple deployment and release where it helps

When a feature needs independent release timing or controlled rollout, deploy
it disabled and enable it through a release flag separately. The release
control must be changeable without deploying new application code. Do not add
a flag to every refactor, bug fix or routine change.

Use the existing feature evaluator rather than querying flag storage at each
call site. Keep keys stable and descriptive. Do not mandate a database schema,
admin interface, package, cache strategy or speculative rollout states.

Define how quickly changes take effect, including caches and long-running
workers. Configuration-based operational switches may require configuration
refreshes or process restarts; do not promise immediate runtime release
control unless the implementation provides it.

## Keep availability, operations and permissions distinct

- **Release flag:** controls exposure of a feature, globally or to a supported audience.
- **Operational switch:** controls supporting services or infrastructure-facing behaviour.
- **Account preference:** records whether an account wants to use an available feature.
- **Authorisation:** determines whether a caller may perform the action.

A flag never grants authorisation. Preserve authentication, ownership, tenant
and policy checks even when a feature is enabled. Where availability depends
on several conditions, centralise their combination in the application's
existing capability method or service.

Gate relevant server-side entry points as well as presentation. Hiding a button
does not prevent direct requests. Define whether each control gates APIs,
webhooks, jobs and administrative paths; turning off a user-facing feature
does not automatically stop its supporting operations.

## Define defaults and verify both paths

For a new release flag, default to disabled until explicitly enabled. Define
missing-key behaviour separately from evaluator failures: a missing flag and
an unavailable flag store are different conditions. Do not silently convert
database or service failures into disabled results. Use the project's explicit
failure policy and make failures observable.

Test enabled, disabled and missing-flag behaviour through the existing
evaluator's test controls, without changing the environment name. Include a
direct server-side request with the flag disabled and verify that enabled
flags still respect authorisation. Where failure fallback is supported, test
that contract too. Exercise audience boundaries only when targeting exists.

## Plan rollback and removal

A flag affects subsequent evaluations. Disabling it does not undo completed
actions, reverse migrations or automatically cancel queued work. Define what
happens to in-flight and queued operations, and keep schema and data changes
compatible with the paths that can still run during rollout or rollback.

Give each temporary release flag an owner and a tracked removal condition.
Once rollout is complete and the rollback window has closed, remove the flag
checks, obsolete path and associated tests, then retire the stored flag after
remaining deployed consumers no longer need it. Keep deliberate long-lived
operational controls and account preferences where they still serve a purpose.

## Composes with Boost

- `configuration.md` — configuration mechanics remain Boost's; this rule covers which conditions should control application behaviour.
- `tests.md` — test mechanics remain Boost's; this rule adds flag-state and server-side availability expectations.

See also this overlay's [general design rules](general-design.md) for reuse and
tracked follow-up work, and [control-flow rules](control-flow.md) for exception handling.
