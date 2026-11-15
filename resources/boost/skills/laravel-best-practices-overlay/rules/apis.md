# APIs

Apply when designing, implementing or reviewing Laravel HTTP JSON APIs. Read the principles and the sections relevant to the change; skip conditional mechanisms the endpoint does not need.

## Rule strength

**MUST** and **MUST NOT** identify requirements; **SHOULD** identifies a default with justified exceptions; **MAY** identifies an option. These uppercase terms follow [BCP 14](https://www.rfc-editor.org/rfc/rfc8174.html). Apply them within the precedence below; they do not override an existing contract or authorize a breaking change.

Record a departure from a default and its reason in the API's documentation. Use the existing ADR practice for significant architectural decisions, not for every implementation choice.

## Precedence and version checks

These rules fill gaps; they do not supersede the application's contract, Laravel or existing package standards.

1. Follow explicit project requirements and preserve existing API contracts unless a contract change is part of the task.
2. Follow established application conventions and this overlay's existing standards, including its explicitly documented deviations from Boost.
3. Use the installed Laravel version's supported mechanisms and the installed Boost guidance for framework mechanics.
4. Apply the defaults below where those sources leave a choice open.

If advice conflicts, state the conflict and the applicable source; do not silently introduce a second convention or preserve a security defect in the name of consistency. Resolve a security or protocol defect explicitly, including a consumer migration when required. This file introduces no additional counter-position to Laravel or Boost.

Before coding, inspect dependency versions, sibling endpoints, resources, policies, tests and the existing contract. Check version-specific documentation before using unfamiliar APIs. Do not upgrade dependencies, replace authentication or change wire formats merely to apply these rules.

## Principles

The ordering and workflow defaults are package opinions. Citations identify supporting standards or framework mechanisms, not a claim that an external source mandates this ranking.

1. **Protect access and data integrity.** Establish who may perform the operation, which records they may touch and which side effects must succeed together. Do this before adding response fields or convenience endpoints. Use [Laravel authorization](https://laravel.com/docs/13.x/authorization) and the existing [transaction rule](eloquent-opinions.md#avoid-database-transactions-unless-you-have-to).
2. **Design every interface with the care of a public contract.** Define inputs, outputs, errors and compatibility for internal consumers too. Keep internal operations private; public-quality design does not mean anonymous access or a promise to publish. Apply [compatibility reasoning](https://google.aip.dev/180) as soon as an independently deployed consumer depends on the API.
3. **Prefer Laravel and established standards over invention.** Reuse the project's mechanisms before adding a framework, protocol or abstraction. Follow Boost's [project conventions](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/style.md) and [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html).
4. **Design from consumer tasks.** Identify a complete caller flow and the requests needed to finish it. Model domain resources, not database tables. Compare request count and response size before adding nesting or includes. See [resource-oriented design](https://google.aip.dev/121); retain Laravel's route conventions rather than importing Google's wire conventions.
5. **Design first; prove the contract early.** Review concrete requests, responses and failures before implementation. For independent consumers, use OpenAPI and a mock when it helps validate the flow. Code-generated contracts are acceptable when reviewed and checked for drift. [OpenAPI](https://spec.openapis.org/oas/latest.html) describes the contract; it does not mandate a design workflow.
6. **Use our own applications as consumers.** Exercise the same supported API flows where useful and feed their friction back into the design. Share application behaviour directly inside a monolith; do not force it through its own HTTP API. This follows the [reuse and YAGNI defaults](general-design.md#yagni-prefer-existing-solutions-delete-unused-code).
7. **Deliver incrementally and design for evolution.** Ship a small complete flow, verify it, then extend it. Review semantics as well as schemas; an internal release is not permission to break independently deployed clients. See [AIP-180](https://google.aip.dev/180).
8. **Respect ownership boundaries.** Between separately owned services, use agreed interfaces rather than another service's private tables. Within one Laravel app, reuse existing application code; do not invent service boundaries. Keep the same domain vocabulary across each boundary using the [naming rules](naming.md#ubiquitous-language-across-the-stack).

## The contract

- Independently consumed APIs **SHOULD** maintain OpenAPI covering authentication, parameters, writable fields, responses, errors and stable operation IDs. For endpoints deployed with their only consumer, existing examples and feature tests may suffice until independent consumers are introduced.
- Maintain one authoritative contract source. Where generated, generation **MUST** be reproducible. Review contract diffs, lint the document and validate representative responses in CI. Compare against the released contract, not just another development branch.
- Contract-only checks **SHOULD** use the chosen linter's configuration rather than custom scripts that duplicate supported rules.
- Every operation **MUST** declare its effective authentication and required abilities or scopes in the contract. Anonymous access **MUST** be explicit; account for inherited OpenAPI security requirements. Reference: [OpenAPI operations and security](https://spec.openapis.org/oas/latest.html#operation-object).
- Sanctum bearer-token authentication **MUST** be represented as HTTP bearer security (`type: http`, `scheme: bearer`), with required abilities described in the operation documentation or an agreed `x-` extension. Abilities **MUST NOT** imply an unimplemented OAuth flow. Declare OAuth scopes through an OAuth2 or OpenID Connect security scheme only when that protocol is implemented. Reference: [OpenAPI security definitions](https://spec.openapis.org/oas/latest.html#security-scheme-object).
- The selected OpenAPI version **MUST** be supported by the actual validators and client generators. Do not prescribe 3.1 as the latest or upgrade a working toolchain solely to follow a version label. Reference: [OpenAPI specification](https://spec.openapis.org/oas/latest.html).

## Evolution and deprecation

- Contract reviews **MUST** treat renamed/removed fields, type changes, required inputs, stricter validation and changed defaults as potential breaks. Test new response enum values against consumer assumptions; adding a value is not automatically harmless. Reference: [compatibility](https://google.aip.dev/180).
- Changes **SHOULD** preserve the existing versioning scheme. For a new independently consumed API without one, prefer a major URL prefix such as `/api/v1`. Coordinate breaking changes or introduce a supported version with a migration plan; never version merely because the schema changed.
- Removal of a supported interface **MUST** have a documented replacement, notice period and retirement date. Measure remaining use. Where headers are used, implement the actual [Deprecation header standard](https://www.rfc-editor.org/rfc/rfc9745.html).

## HTTP methods and status codes

Use Boost's resource routing and controller conventions. Neither `apiResource()` nor an API URL provides authorization or implements a patch document format.

- `GET` **MUST NOT** request business mutations.
- Success responses **SHOULD** use `201` with the new resource's `Location` on creation, `204` with no body on a successful bodyless operation, and `202` only for accepted, unfinished work.
- Ordinary partial updates **MUST** preserve omitted fields and define what explicit `null` means. Advertise `application/merge-patch+json` only when implementing all [JSON Merge Patch semantics](https://www.rfc-editor.org/rfc/rfc7396.html), including member removal and array replacement.
- `PUT`, if exposed, **MUST** replace the documented writable representation. Laravel routes PUT and PATCH to the same resource action; do not infer replacement semantics from the verb registration alone.
- Errors **MUST** use appropriate HTTP statuses: `400` malformed input, `401` unauthenticated, `403` forbidden, `404` missing/concealed, `409` state conflict, `412` failed precondition, `422` field validation and `429` throttling. Include the applicable authentication challenge and retry information. Do not return an error inside `200`.

These are API defaults grounded in [HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html); they are not a replacement for the selected protocol's more specific rules.

## Resources and representations

- Responses **SHOULD** use explicit API Resources rather than serialize raw models. Preserve existing envelopes and field types. For a new ordinary Resource API, retain Laravel's `data` wrapping and paginator output. Define omission separately from `null` and load only authorized, supported relationships. Reference: [API Resources](https://laravel.com/docs/13.x/eloquent-resources).
- API responses **MUST** retain their documented machine values. Apply [display formatting](display-values.md) at the human UI boundary; do not replace API enum values, timestamps or integer money with display strings. Use UTC [RFC 3339 timestamps](https://www.rfc-editor.org/rfc/rfc3339.html) for instants; keep calendar dates and local schedules semantically distinct.
- Money **MUST** follow [integer money across boundaries](eloquent-opinions.md#pass-the-smallest-unit-across-boundaries), including currency and documented scale. Keep identifier types stable; opaque identifiers are not access control. Follow [domain naming](naming.md) and Boost for naming conventions rather than adding another casing policy.
- Responses **SHOULD** return canonical stored values and document intentional normalization; do not promise verbatim input echoing while Laravel trims or normalizes it.
- **If JSON:API is selected:** responses and request handling **MUST** follow the [specification](https://jsonapi.org/format/), including its media type and error format. Laravel 13 documents native [JSON:API Resources](https://laravel.com/docs/13.x/eloquent-resources#jsonapi-resources); check installed-version support before using them. Serialization support alone does not implement all request handling. Do not apply ordinary Resource envelopes or Laravel validation-error shapes to a JSON:API contract.

## Validation and authorization

Use Boost for validation and policy mechanics; add the API-specific checks below.

- Lists **MUST** be scoped to authorized data before pagination. In a tenant app, scope resource lookups, related IDs in writes, caches and queued work to the authorized tenant. Nested binding constrains parentage, not caller access. Return `404` when existence must be concealed; otherwise use `403` for denied access. Reference: [Laravel authorization](https://laravel.com/docs/13.x/authorization).
- Body and query inputs **MUST** be validated, including allowed nested keys and collection sizes. Forward only intended writable fields. Schema-valid data is not necessarily authorized or safe for mass assignment. Reference: [validation](https://laravel.com/docs/13.x/validation).

## Authentication

- Authentication changes **SHOULD** preserve the existing guard. For new simple token APIs, prefer Sanctum; for supported first-party SPAs, use its session-cookie/CSRF flow. Configure expiry and revocation deliberately: Sanctum tokens do not expire by default. Token abilities supplement policies; `tokenCan()` is true for authenticated first-party SPA requests. Reference: [Sanctum](https://laravel.com/docs/13.x/sanctum).
- An app that needs an OAuth2 authorization server **SHOULD** use [Passport](https://laravel.com/docs/13.x/passport#passport-or-sanctum) or retain its established identity provider. Do not build an identity service as incidental endpoint work.
- APIs **MUST** use HTTPS and preserve CSRF for cookie authentication. Configure explicit browser CORS rules. Reveal newly issued credentials only through their intended operation, with `Cache-Control: no-store`. Follow [operational safety](operational-safety.md) and [PII handling](pii-handling.md) for credentials, diagnostics and personal data.

## Lists and limits

- Growing collections **MUST** be paginated with a validated maximum page size. Reuse the application's limits; set documented limits for a new API based on workload rather than assuming a universal page size.
- Lists **SHOULD** use `paginate()` for totals, `simplePaginate()` for next/previous without counting, and `cursorPaginate()` for suitable large ordered lists. Cursor order needs a unique column or combination and does not support null ordering values. Keep native links; retain supported filters. A cursor is not a snapshot or credential. Reference: [pagination](https://laravel.com/docs/13.x/pagination).
- Cursor APIs **MUST** document whether a cursor can be reused with different filters or sorting. Unless the contract supports it, clients **SHOULD** restart pagination when those parameters change. Do not imply Laravel automatically rejects mismatched reuse.
- Filtering, sorting and includes **MUST** be allowlisted; search, bulk requests and relationship expansion **MUST** be bounded. Configure and attach appropriate shared rate limits across instances; do not assume API routes are automatically throttled. Reference: [routing and rate limits](https://laravel.com/docs/13.x/routing#rate-limiting).

## Errors

- Ordinary JSON APIs **SHOULD** keep Laravel's validation `message`/`errors` shape and centralize exception rendering. Return JSON on API paths even when clients omit `Accept`; use the installed version's exception configuration. Keep stable domain error codes separate from localized text. References: [validation responses](https://laravel.com/docs/13.x/validation#validation-error-response-format), [exception rendering](https://laravel.com/docs/13.x/errors#rendering-exceptions), [localization rules](localization.md).
- APIs **MAY** use [RFC 9457 Problem Details](https://www.rfc-editor.org/rfc/rfc9457.html) only when selected for the contract; preserve an existing adoption. Do not combine competing error envelopes. Keep production debugging disabled and exclude internal exception details from responses.

## Conditional: retries, concurrency and background work

Apply only where duplicate effects, lost updates or long-running work matter.

- **Harmful duplicate writes:** operations **MUST** implement durable idempotency scoped to caller/tenant and operation. Bind keys to payloads; reserve atomically, prevent concurrent duplicate effects, replay the outcome and reject mismatched reuse. Define retention, in-progress responses and crash recovery. Propagate downstream idempotency when needed. This is an application design requirement; unique jobs alone do not implement it.
- **Idempotent replay:** authentication and authorization for current access to the protected result **MUST** run before returning a recorded response. A previous success **MUST NOT** bypass token revocation, account suspension or changed tenant/resource permissions. Deny replay when access is no longer allowed; do not execute the original effects again.
- **Atomic state changes:** implementations **MUST** follow the [existing transaction rule](eloquent-opinions.md#avoid-database-transactions-unless-you-have-to). Keep remote calls outside long-held locks. Dispatch dependent jobs after commit. Where crash-safe delivery is required, add a durable outbox or equivalent recovery; after-commit dispatch alone does not guarantee delivery. Reference: [queues and transactions](https://laravel.com/docs/13.x/queues#jobs-and-database-transactions).
- **Lost-update protection:** implementations **MUST** check a version atomically or enforce `ETag`/`If-Match`; reject a stale `If-Match` with `412`. Do not advertise concurrency protection using an unchecked response header. Reference: [HTTP preconditions](https://www.rfc-editor.org/rfc/rfc9110.html#name-preconditions).
- **Async operations:** unfinished work **SHOULD** return `202` with a durable status reference and a documented polling URL, preferably in `Location`. Define result/failure states and authorize their retrieval. Reuse the project's named queues, retry limits and monitoring. Keep the response contract predictable. Reference: [Laravel queues](https://laravel.com/docs/13.x/queues).

## Documentation

- The contract **SHOULD** describe each supported field and parameter's meaning, units, defaults, limits, nullability and writable/read-only status. Include valid examples; use explicit names such as `duration_seconds` where units would otherwise be ambiguous. Reference: [OpenAPI](https://spec.openapis.org/oas/latest.html).
- Independently consumed APIs **SHOULD** provide a working getting-started flow covering authentication, pagination, errors and any supported retries or polling. Document stable error codes and the action callers can take; clients **MUST NOT** branch on localized message text.
- Contract changes **SHOULD** update examples and the consumer-facing changelog in the same change. Documentation tooling and SDKs **MAY** be added when consumers need them; do not make a specific vendor a prerequisite.

## Implementation and verification

Use existing [Laravel HTTP feature tests](https://laravel.com/docs/13.x/http-tests), with isolated databases as required by [operational safety](operational-safety.md). Cover the applicable outcomes: success contract, unauthenticated/forbidden access, cross-tenant and related IDs, invalid inputs, bounded list behaviour, side effects and absence of sensitive fields. Rejected requests must not perform the rejected operation's effects. Exercise retries and races when adding those mechanisms, including denied replays after token revocation or account suspension.

Check representative success and error schemas against the published contract. Test gateways separately where present; Laravel's HTTP tests simulate requests in process. Report what was verified and any remaining contract risk; generated tests do not establish ownership rules by themselves.

## Composes with Boost

Checked against official Laravel 13.x docs, the published OpenAPI specification and Boost's current rule files. The package supports Laravel 10–13; linked 13.x docs are the verification baseline, not permission to use 13.x-only APIs in older apps. Recheck installed versions when implementing. Public references support mechanisms; package defaults remain opinions.

- [Boost routing](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/routing.md) and [style](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/style.md) own route/controller mechanics and naming.
- [Boost validation](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/validation.md) and [security](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/security.blade.php) own input handling, authorization and SQL safety; this file adds contract and tenant-boundary review.
- [Boost queue jobs](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/queue-jobs.md) owns job mechanics; this file adds caller-visible operation and retry contracts.
