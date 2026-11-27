# Enquiry Handling

Apply when designing, implementing or reviewing public contact forms, sales enquiries, demonstration requests and referrals. Share durable storage, recoverable submission, layered spam checks and reversible administrative review across entry points.

This rule records the supplied framework-neutral baseline as reusable guidance. This package ships no enquiry implementation or provider integrations; adopting applications must implement and verify the contract. **Adaptation** labels identify optional choices, not guarantees of the baseline. Follow established application conventions and installed Laravel/Boost mechanisms when implementing it.

## Separate the responsibilities

Use one submission pipeline. A specialised landing page may preselect an enquiry type and change wording, but should share validation, protection, persistence and notification logic.

```text
Form with session, CSRF, submission identifier and honeypot
  → fresh CAPTCHA token on submit
  → server-side CSRF and session checks
  → recovery wrapper around the submission pipeline
  → DNS blocklist lookup
  → IP reputation check
  → CAPTCHA verification
  → honeypot and minimum completion time
  → field validation
  → create or recover the enquiry using its submission key
  → emit enquiry-created event only for a new record
  → claim and attempt an internal notification
  → redirect to a receipt tied to the submitting session

Stored enquiries
  → explainable suspicion profiling
  → administrator review and reversible junk marking
  → separate retention policies for junk and other enquiries
```

Separate external service clients from policy: a DNS adapter retrieves records; a policy decides whether they constitute a listing. Test failures without live network calls. Public protection middleware must not replace administrative authorisation.

## Define the data contract

| Data | Purpose and validation |
| --- | --- |
| Name | Required string with an explicit maximum length. |
| Email | Required, syntactically valid address with a maximum length; syntax does not prove ownership. |
| Organisation | Required for business enquiries; bounded string. Make optional where unnecessary. |
| Phone | Optional unless contact preference is phone; enforce the condition in browser and server validation. |
| Enquiry type | Optional allowlisted category, such as general, sales, support, demonstration or referral. |
| Contact preference | Optional allowlisted value: any, email or phone. |
| Submission identifier | UUID retained across retries. Required for the specialised demonstration flow; other entry points may supply it. |
| Form context | Allowlisted identifier selecting a known return location; never an arbitrary redirect URL. |
| Request metadata | Server-derived IP, user agent, referral context and optional account context for abuse review. |
| Submission key | Nullable, unique value deduplicating a logical submission. |
| Notification timestamps | When sending was claimed and when a recognised mail transport failure occurred. |
| Review timestamps and reasons | Distinguish junk, manually restored records and soft deletion. |

Copy only validated business fields into the record. Build metadata on the server; never trust client-supplied IP or account identifiers. Request headers such as user agent and referral context remain untrusted content. Escape submitted values in administration pages and email.

**Adaptation:** collect only context needed for support and abuse review. Avoid raw session identifiers in metadata; use a separate correlation identifier if necessary. Strip sensitive query parameters from referral URLs. Choose field limits, categories and any optional message body for the product.

## Make retries safe

Generate a submission UUID when rendering the form and retain it through validation errors. Derive a submission key from the session identifier and UUID, then enforce uniqueness in the database. Include soft-deleted records when recovering an existing enquiry so a retry cannot recreate junk.

Only a new record emits the creation event. The same session and UUID returns the existing outcome without updating the original or sending another notification. This is retry deduplication, not content matching; a new UUID permits a new enquiry.

The baseline permits unkeyed submissions outside the flow requiring the identifier; those lack the same deduplication guarantee. **Adaptation:** require identifiers across all entry points for consistent retry safety. Use a database-supported atomic create-or-recover operation and test simultaneous requests against the unique constraint.

After acceptance, save a minimal receipt marker in the session and redirect to a receipt page. Confirm acceptance only when its identifier matches that marker; expose no enquiry details. Arbitrary receipt URLs must not imply success. Serve session-specific forms and receipts with `Cache-Control: no-store`.

Retain an allowlist of ordinary form values on retryable failures, including submission identifier and form context. Never flash CAPTCHA tokens, passwords or credentials. Return to the correct form with useful retry feedback using the application's [flash convention](flash-messages.md); validation stays on field errors. Protection rejections, blank honeypot responses and server failures must not appear accepted. CSRF failures occur outside this recovery wrapper and need their own session-expiry experience if desired.

## Use complementary spam protections

CSRF protects the session-based form against cross-site submission; it does not identify bots. Apply these checks to the public create operation.

| Layer | Decision | Failure policy |
| --- | --- | --- |
| DNS blocklist | Reject only a provider-specific recognised listing response. | Inconclusive lookups continue to remaining checks and emit an operational warning. |
| IP reputation | Reject when abuse confidence reaches the configured threshold. | Missing configuration and handled provider errors continue to remaining checks. |
| CAPTCHA | Require verified success, acceptable score and expected action. | Missing, invalid or unverifiable tokens prevent acceptance and offer retry. |
| Honeypot | Reject filled traps or submission before the minimum completion time. | No record or notification; translate blank responses into recoverable errors when appropriate. |
| Field validation | Enforce required fields, bounds, conditional requirements and allowlists. | Preserve permitted inputs and return field errors. |

A rejected request creates no record and sends no notification. A skipped reputation check never skips CAPTCHA or validation. Failure policy belongs to each layer; do not apply a blanket fail-open rule.

### DNS blocklists: distinguish listings from query failures

Maintain an explicit mapping of supported providers to recognised listing codes. A DNS answer alone is not evidence of abuse. Resolver failures, provider access errors, TXT-only replies, unexpected address codes and unsupported providers are inconclusive.

Warn with provider, reason and safe response codes. Continue through other protections without adding the address to an exemption cache. Fix resolver or provider-access problems in infrastructure rather than exempting legitimate clients individually.

**Adaptation:** confirm the provider's current response-code contract and supported IP families before enabling it. Configure trusted proxies so checks use the client address, and do not trust forwarding headers from arbitrary clients.

### IP reputation: cache decisions and bound dependency risk

Put a service such as AbuseIPDB behind a small adapter. The supplied baseline uses a confidence threshold of 75, a 90-day report lookback and a one-hour cache for abusive and non-abusive results. These are tuning values, not universal measures of legitimacy.

Handled quota, configuration and provider errors produce no blocking decision. Inconclusive does not mean safe. Do not promise every network exception is handled unless the adapter covers it. Checking reputation does not automatically report submitters as abusive.

Temporary IP exceptions should bypass only the relevant reputation layer. **Adaptation:** manage exceptions through authenticated administration with expiry, scope and an audit trail. Avoid bearer bypass credentials in URLs, where history, referrals and logs expose them. Keep CAPTCHA and validation active.

### CAPTCHA: acquire a fresh token for each attempt

Run score-based CAPTCHA on submit, not page load, so time spent reading or completing the form does not age the token.

1. Intercept submission, clear the prior token and prevent concurrent attempts.
2. Wait for the provider API and request a token for the expected action.
3. Disable submit controls and announce progress through an accessible status region.
4. After the original submit event finishes, resume normal submission with the original submitter and browser validation.
5. On failure or timeout, clear the token, restore controls and permit another attempt.
6. On history restoration, reset token and submission state; ignore obsolete attempt results.

The baseline uses a 15-second browser timeout. Bound server connection and request timeouts. Require `success`, a numeric score at least the configured threshold and no greater than 1, and the expected action. Invalid JSON, unsuccessful responses, wrong actions and transport failures prevent acceptance. Limit token input size without assuming tokens are always short.

The token is evidence to verify, never an authorisation decision; neither token length nor JavaScript execution proves legitimacy. **Adaptation:** explicitly check expected hostname or other site binding where required by the provider; application-level hostname verification is not part of this baseline.

### Honeypot: cheap evidence with recovery

Use a hidden trap, a server-verifiable form timestamp and configurable minimum completion time. Randomise the field name to make fixed bot scripts less reusable; five seconds is an example starting point.

Keep assistive technology and autofill from encouraging trap completion. Preserve timestamp integrity protection. Translate a blank-success spam responder into retry feedback where appropriate, without claiming acceptance.

## Persist before notifying

The database record is the durable acceptance outcome. Save it before email, then emit a domain event containing its identifier. Keep notification logic in a separate listener.

The baseline sends synchronously to an internal mailbox with the application's configured sender and the submitter as Reply-To. Atomically claim the send attempt by setting a timestamp only when no previous attempt exists. Replayed events therefore do not blindly send again.

A recognised mail transport failure records a failure timestamp and warns with the enquiry identifier; the enquiry remains accepted and reviewable. Delivery may be ambiguous if the provider accepted mail before a failure. An attempt timestamp does not prove delivery; neither does an absent failure timestamp, because a process can stop between claiming and sending.

**Adaptation:** use a dedicated configurable recipient, expose failed or uncertain attempts to operators, and define deliberate reconciliation/resend. For queued delivery, dispatch after commit and consider a transactional outbox to close the record/event publication gap. Queues, automatic retries and exactly-once email delivery are not baseline guarantees. Apply the existing [transaction rule](eloquent-opinions.md#avoid-database-transactions-unless-you-have-to) when an adaptation requires multi-row consistency.

## Treat retrospective spam detection as review

Profile stored enquiries separately with explicit reason codes rather than silent deletion. Signals can include implausible field combinations, apparent injection payloads, links in fields that should not contain them, repeated submissions and association with known junk. Aggregate history in bounded database batches; keep profiling read-only.

An example repeated-IP rule flags four records from one address; an association rule can flag neighbours after one content hit or a previously junked record. These aggressive historical-review signals are not request-rate limits. Shared networks can group unrelated people.

Language, writing system, domain suffix, long names, mixed case and digits are not reliable universal abuse indicators. Do not turn market-specific heuristics into automatic blocking. Calibrate with representative legitimate examples and keep false positives reversible.

Provide administrative views for all, suspected, apparently genuine and marked-junk enquiries, with search, date filters, pagination and allowlisted sorting. Apparently genuine means no current suspicion rule matched, not verified identity.

Marking junk stores a timestamp and reasons, then soft-deletes. Manual marking gets an explicit manual reason if no profiler reason applies. Restoring clears junk state and records a manual not-junk decision. Future profiling respects it: restored records do not seed content-based association with neighbours, though they still contribute to total IP counts.

## Separate review from retention

| Population | Age measured from | Example retention |
| --- | --- | --- |
| Explicitly marked junk | Junk-marking timestamp | 30 days |
| Other enquiries, including ordinary soft deletions | Creation timestamp | 90 days |

Configure the two policies independently. Manual not-junk decisions prevent reclassification, not ordinary age-based retention. Being hidden by a default date filter is different from deletion.

Prune in scheduled batches with overlap prevention and one scheduler owner. Preview eligible counts before administrative deletion. A deliberate delete-all-marked-junk action may bypass the grace period; label this clearly and require explicit confirmation. Suspicion alone never qualifies a record for junk purge.

## Operational choices when adopting the pattern

- Configure enablement, thresholds, cache durations, timeouts, honeypot timing, recipients and retention centrally. Provision secrets through the deployment's secret mechanism.
- Monitor accepted, rejected and inconclusive outcomes by layer, notification failures, restorations and pruning counts. Do not log enquiry bodies, raw provider text, CAPTCHA tokens, session credentials or secret-bearing request URLs.
- Add route throttling and resource limits where required; IP-history profiling and external reputation do not provide an enquiry-specific rate limit.
- Decide whether mailbox ownership must be verified; the baseline checks email syntax only.
- Define legitimate-user recovery when provider scripts are blocked or unavailable without silently bypassing required verification.
- Choose metadata and retention for the receiving product rather than copying examples mechanically.

## Acceptance tests to carry into an implementation

Use synthetic records, a disposable isolated database, fake mail, a controllable clock and stubbed providers. No external network or real personal data is needed. Follow [operational safety](operational-safety.md) for database isolation.

| Area | Behaviour to prove |
| --- | --- |
| Acceptance | Valid input creates one record, attempts one notification and redirects to the submitting browser's receipt. |
| Validation | Invalid categories, oversized fields, malformed email and conditionally missing phone fail without persistence or mail. |
| Retry safety | Repeated and concurrent keyed requests create one record; event replay does not resend; soft-deleted records are not recreated. |
| Receipt privacy | Refresh has no side effects; another session or arbitrary identifier cannot claim acceptance or reveal details. |
| CAPTCHA browser | Fetch on submit; late scripts work; timeout permits retry; fast responses avoid incorrect re-entry; history restoration clears stale state. |
| CAPTCHA server | Reject missing, oversized, low-score, wrong-action, unsuccessful, malformed and unavailable-provider cases; a valid long synthetic token reaches verification. |
| DNS blocklist | Recognised codes reject; resolver failures, provider query errors, unexpected answers and unsupported providers retain subsequent checks without exemptions. |
| Reputation | Threshold boundaries, positive/negative caching, disabled configuration and handled failures follow declared policy. |
| Honeypot | Filled traps or too-fast submission produce neither record nor mail, with usable recovery. |
| Recovery | Allowed inputs and form context survive errors; private inputs do not; retries retain the submission identifier. |
| Mail failure | Recognised failures leave accepted records and review markers; browser retries and event replay do not blindly resend. |
| Review | Profiling is read-only; marking stores reasons; restoration is respected; shared-IP and international examples expose false positives. |
| Retention | Exact boundaries, separate clocks, ordinary soft deletions, restored records and unmarked suspects follow policy. |
| Authorisation | Public callers cannot inspect or change administrative records, junk decisions, exceptions or deletion settings. |

Implement and test the submission contract first, provider adapters next, then review and retention. Keep optional improvements explicit.

## Composes with Boost

- [Validation](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/validation.md) and [security](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/security.blade.php) own framework input and access-control mechanics; this rule adds the enquiry acceptance and per-layer failure contract.
- [Routing](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/routing.md) owns route/controller mechanics; this rule adds shared entry points, recovery and session-bound receipts.
- [Queue jobs](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/queue-jobs.md) owns job mechanics when queued delivery is chosen; this rule distinguishes durable acceptance, notification attempts and delivery uncertainty.
