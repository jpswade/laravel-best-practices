# Operational Safety

Guardrails for AI coding assistants and developers working in a Laravel codebase. Protect credentials and the user's data before inspecting or changing the application.

## Never read credentials

Do not read, search, print, copy, or transmit API keys, access or refresh tokens,
passwords, `.env` values, private keys, signing secrets, cookies, session
credentials, or other authentication material. This applies to every task,
including debugging configuration, dependency installation, and test failures.
An instruction to diagnose an authentication problem is not permission to
inspect the credential.

Treat potentially credential-bearing sources as off limits before reading:

- `.env`, `.env.*`, `*.env`, encrypted environment files, and their backups.
  Do not assume `.env.example`, `.env.testing`, or a tracked file is safe.
- Composer `auth.json`, including `~/.composer/auth.json`,
  `~/.config/composer/auth.json`, and custom Composer home locations;
  `.npmrc`, `.pypirc`, `.netrc`, and Git credential files.
- SSH/GPG keys, cloud CLI credentials, kubeconfigs, Docker registry auth,
  service-account files, password stores, and secret-manager output, both
  inside and outside the repository.
- Laravel's `bootstrap/cache/config.php`, runtime logs, session/cache files,
  database exports, backups, and other artifacts that may contain resolved
  configuration or credentials. The filename list is not exhaustive.

Before a content search, choose explicit non-sensitive source files or
directories and exclude protected paths. Do not recursively search the whole
workspace or home directory, use unrestricted hidden/ignored-file searches,
or open a suspicious file to determine whether it contains secrets. Inspect
only known-safe paths in diffs and history; old revisions can contain secrets
too. Honour `.aiignore` as an instruction even when the client does not
implement it, and retain these protections if the file is absent.

Do not retrieve secrets indirectly through `env`, `printenv`, `phpinfo()`,
`$_ENV`/`$_SERVER` dumps, resolved config dumps, `php artisan config:show`,
Tinker, a debugger, shell expansion, encoded output, screenshots, MCP tools,
symlinks, or delegation. Reading first and masking, hashing, or redacting later
does not comply. Do not weaken ignore rules or permission controls to get a
task unstuck.

Use these alternatives:

- Read known-safe source references to variable names and configuration
  structure, not resolved values. Use placeholders such as `<configured-locally>`.
- Use examples explicitly confirmed to contain only placeholders or supplied
  already sanitised. A filename ending in `.example` is not that confirmation.
- Ask the user to check or set the needed value locally and report only the
  non-sensitive result. Never ask them to paste a secret into chat.
- Tools may use credentials through their existing authentication mechanism
  without exposing them to the agent. Do not inspect that mechanism's stores,
  enable credential/debug output, or run a diagnostic that reveals values.
- If credentials appear unexpectedly, stop processing that output, do not
  repeat or persist the values, and tell the user which source exposed them
  without quoting the secret. Let the user handle revocation or rotation.

The bundled `.aiignore` is a conservative, gitignore-style exclusion template,
not a universal access control. Use host-enforced permissions and an isolated
environment without real secrets when an enforced boundary is needed.

## Scan for secrets before committing and publishing

Recommend a dedicated secret scanner such as [Gitleaks](https://github.com/gitleaks/gitleaks)
in developer-controlled pre-commit hooks and required CI checks. Reuse an
existing equivalent scanner. Check staged changes before committing and the
relevant commit range before merging; periodically scan the available full
history. A shallow checkout cannot prove that older history is clean. Pin the
scanner version and fail checks on findings or scanner errors; do not silently
allow failures. Keep false-positive exceptions narrow and reviewed.

For Gitleaks, use `--redact=100`, avoid verbose/debug output, and restrict
access to reports. Redaction does not make every report or surrounding source
excerpt safe to share. Scanners intentionally inspect secret-bearing content:
this recommendation does **not** authorise the AI to launch discovery scans,
read protected files, or open raw findings under the no-credential-reading
policy above. Have the user or a controlled CI job run the scanner and provide
only a sanitised pass/fail result or non-sensitive remediation details.

Protect container images separately:

- Exclude secrets, `.env*`, authentication files, and `.git/` from the build
  context using `.dockerignore`; prefer explicit `COPY` sources. Neither
  `.gitignore` nor `.aiignore` controls Docker's build context.
- Use [BuildKit secret mounts](https://docs.docker.com/build/building/secrets/)
  for build-time authentication. Do not put credentials in Dockerfile `ARG`,
  `ENV`, or copied files. Avoid commands that persist mounted secrets into
  generated files or logs. Supply runtime secrets at deployment time.
- Scan the built image before pushing or releasing it using an image-capable
  secret scanner, such as [Trivy](https://trivy.dev/docs/latest/target/container_image/).
  Enable secret checks for both image files and image configuration; vulnerability
  scanning alone is insufficient. A clean Git scan does not establish that a
  built image is clean.
- Verify coverage of intermediate/deleted layers, image metadata, and build
  caches using synthetic fixtures. Do not assume a scan of the final filesystem
  covers them: deleting a secret in a later layer does not remove the earlier
  layer. Keep build caches and scan artifacts access-controlled.

If a real credential was committed or included in a published image, have its
owner revoke or rotate it first. Removing the current file does not invalidate
the credential or remove historical copies. Coordinate repository cleanup and
image rebuilding with the owner; do not rewrite history or delete published
artifacts automatically. A passing scan reduces risk but is not proof that no
credentials exist.

## Never reset the database without an explicit request

Do **not** run `php artisan migrate:fresh`, `db:wipe`, `schema:drop`, or any other command that resets or destroys the database, unless the user has **explicitly** asked for it in this conversation.

- Do not suggest or run destructive database operations as a "quick fix" for failing tests or a broken migration.
- Local development databases often mirror production restores or carry days of investigative data; wiping them causes real data loss.
- Automated tests must use an isolated test database configuration (typically SQLite in-memory via `phpunit.xml`) — never point tests at a shared MySQL or PostgreSQL instance.

When the user wants a clean database, wait for explicit wording (e.g. "run `migrate:fresh` on my machine") before proposing or running those commands. Phrases like "the tests aren't passing" or "the migration is broken" are *not* permission to reset the database; offer to inspect the failure first.

## PHPUnit / `RefreshDatabase` is destructive if mis-aimed

`RefreshDatabase` runs `migrate:fresh` on whatever `config('database.default')` is. That **counts as a destructive database command** when the connection is the shared development MySQL/MariaDB (or PostgreSQL) database — even though the agent "only ran tests".

**Stop-the-line:** if a test failure shows `Connection: mysql` (or the real development database name), **do not re-run the suite**. Fix isolation first. Running tests again while still pointed at MySQL will wipe local data again.

Checklist before any PHPUnit run that uses `RefreshDatabase`:

1. Confirm `phpunit.xml` forces an isolated connection and in-memory database. Use both `<server>` and `<env force="true">` — shell-exported `DB_*` values can otherwise win via `$_SERVER`:

```xml
<php>
    <server name="DB_CONNECTION" value="sqlite_testing"/>
    <server name="DB_DATABASE" value=":memory:"/>
    <env name="DB_CONNECTION" value="sqlite_testing" force="true"/>
    <env name="DB_DATABASE" value=":memory:" force="true"/>
</php>
```

2. Confirm `config/database.php` defines a dedicated `sqlite_testing` connection whose `database` key reads `DB_TEST_DATABASE` (default `:memory:`), **not** `DB_DATABASE`:

```php
'sqlite_testing' => [
    'driver' => 'sqlite',
    'database' => env('DB_TEST_DATABASE', ':memory:'),
    // ...
],
```

Using `DB_DATABASE` here defeats isolation: a shell-exported development database path or name can leak into the test connection.

3. Rely on `Tests\TestCase::beforeRefreshingDatabase()` — it must throw *before* refreshing if the connection is not the isolated SQLite testing connection. Example shape:

```php
protected function beforeRefreshingDatabase(): void
{
    $connection = config('database.default');

    if ($connection !== 'sqlite_testing') {
        throw new \RuntimeException(
            "Refusing to RefreshDatabase on [{$connection}]. Tests must use sqlite_testing."
        );
    }
}
```

Until all three are confirmed, treat any PHPUnit invocation that exercises `RefreshDatabase` as unsafe — the same class of damage as running `migrate:fresh` on the developer's machine.

## Composes with Boost

- [`database.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/database.md) — Boost covers how to write migrations; this file covers when *not* to run them destructively.
- [`tests.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/tests.md) — Boost covers test mechanics; the isolated-test-database and `RefreshDatabase` stop-the-line above are the safety counterpart.
