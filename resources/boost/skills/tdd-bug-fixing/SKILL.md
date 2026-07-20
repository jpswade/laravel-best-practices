---
name: tdd-bug-fixing
description: Use this skill whenever you are about to fix a bug, regression, or any reported defect in a Laravel application. The skill enforces a strict red-green-refactor loop with the failing test written before the fix.
when_to_use:
  - The user reports a bug, exception, regression, or "this used to work" defect.
  - The user asks you to investigate or reproduce an unexpected behaviour in code.
  - The user asks you to "fix" anything in production code.
when_not_to_use:
  - Greenfield feature work where there is nothing to reproduce yet — write tests-first, but the bug-specific loop below does not apply.
  - Pure refactors where behaviour is intentionally unchanged.
  - Configuration, infrastructure, or third-party-dependency fixes outside the application code path.
---

# TDD Bug-Fixing

When fixing a bug in this repository, follow the red-green-refactor loop below. Skipping the failing-test step is not allowed except in the narrow exceptions listed at the bottom.

## The loop

1. **Reproduce the bug.** Before touching production code, work out the exact conditions that trigger it. Stack trace, request payload, model state, environment, timing — whichever apply. If you cannot reproduce it, you cannot fix it. Answer these before moving on:
    - What exactly is happening, and what should happen instead?
    - Under what exact conditions does it happen (user role, data shape, feature flag, timing, environment)?
    - Who or what is affected?
    - Is this new behaviour, or a regression of something that used to work?
2. **Write a failing test.** Encode the reproduction as a test in the appropriate suite (`tests/Feature`, `tests/Unit`, etc.). Run it. It must fail for the *right reason* — the same assertion the bug violates in production. A test that fails for a setup reason is not a reproduction.
3. **Implement the minimal fix.** Change only what is required to turn the test green. Fix the root cause, not the symptom — if the test passes only because you suppressed the failure (caught the exception, short-circuited the path, loosened the assertion), the test is wrong or the fix is. Do not refactor in the same step. Do not silently widen the scope of the change.
4. **Verify the fix.** Run the new test (green) and the *full* suite. Both must pass. If anything else now fails, the fix has side effects — treat each one as a separate failing test to address before moving on. **Stop-the-line:** if output shows `Connection: mysql` (or the shared development database), do **not** re-run PHPUnit — `RefreshDatabase` will wipe local data. Fix test isolation (`phpunit.xml`, `sqlite_testing` / `DB_TEST_DATABASE`, `beforeRefreshingDatabase()`) first; see the overlay's `operational-safety.md`.
5. **Add edge-case tests.** Write further tests for the obvious neighbouring cases: the boundary conditions, the empty input, the duplicate input, the related-but-different code path. These pin down the *scope* of the fix.
6. **Refactor.** With the test suite green and the fix locked in, tidy the code: rename, extract, simplify. Run the suite after each refactor; if anything goes red, undo the last change.

## Conventions for the failing test

- **Name it after the bug.** `test_subscription_renewal_charges_correctly_after_proration` is useful; `test_bug_fix` is not.
- **One assertion per behaviour.** A test that asserts six things is six tests in a trenchcoat — when it fails, you don't know which behaviour broke.
- **Test both positive and negative cases.** Confirm the fix works *and* that the previously-working paths still work.
- **Reproduce, don't approximate.** If the bug only manifests with a specific user role, specific timezone, or specific feature flag — set those up in the test. A reproduction that doesn't reproduce the bug isn't one.

## Output expected of the agent

When this skill is active and you have completed a bug fix, your final message should include:

- A one-line summary of the bug.
- The name of the failing test you wrote (and its path).
- A short note on what made the test fail before the fix.
- Confirmation that the full suite passed after the fix.
- Reference the bug source (Sentry event ID, issue link, ticket reference) in the commit message and the failing test's docblock — not in production code comments.

## Narrow exceptions to the "test first" rule

These are genuinely rare and require explicit justification:

- **A live production outage requires an immediate fix.** In that case, ship the fix first and write the test before the next deploy — and treat that test as part of the post-incident review.
- **The bug is in a third-party dependency.** Write the test against your application's *use* of the dependency, not against the dependency itself.
- **The bug is in infrastructure outside the application code path.** Reproduce it in whichever layer it actually lives, not in PHPUnit.

If none of these apply, the failing test is not optional.
