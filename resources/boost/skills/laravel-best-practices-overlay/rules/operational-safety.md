# Operational Safety

Guardrails for AI coding assistants and developers working in a Laravel codebase. These are not design defaults — they are "do not silently destroy the user's data" rules.

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
