# Stable Error Grouping

Tools like Sentry group on exception type plus **message**. Unique values in the message (IDs, URLs, query strings, file paths, timestamps, upstream bodies, attempt counts) create one issue per occurrence and hide trends.

Boost's `error-handling.md` already tells you to attach structured data via `context()` on the exception. This file is the counterpart Boost is silent on: the **message itself must stay stable**, so grouping keys on the failure class rather than a per-request fingerprint.

## Messages stay stable

The message names the **failure class** only. It must be identical for every instance of that failure.

- Do not interpolate IDs, URLs, query strings, file paths, timestamps, or upstream body snippets into exception messages or log messages.
- HTTP status belongs in context, not the message, unless you deliberately want separate groups per status.
- Prefer a typed exception with a constant message over `new RuntimeException('…'.$id)`.

Incorrect — splits the tracker per URL and status:

```php
throw new RuntimeException(
    'Upstream request failed for '.$url.' (HTTP '.$response->status().')'
);
```

Correct — one group; URL and status in `context()`:

```php
final class UpstreamRequestException extends RuntimeException
{
    public const REQUEST_FAILED = 'Upstream request failed.';

    public function __construct(
        private readonly string $url,
        private readonly int $status,
    ) {
        parent::__construct(self::REQUEST_FAILED);
    }

    /** @return array{url: string, status: int} */
    public function context(): array
    {
        return [
            'url' => $this->url,
            'status' => $this->status,
        ];
    }
}

throw new UpstreamRequestException($url, $response->status());
```

## Unique details go in context

- Put identifiers on the exception and expose them from `context()` — Laravel includes that array in the log entry automatically.
- On log lines, pass identifiers as the context array, not in the message string.

Incorrect:

```php
Log::error("Upstream request failed for {$url} (HTTP {$response->status()})");
```

Correct:

```php
Log::error('Upstream request failed', [
    'url' => $url,
    'status' => $response->status(),
]);
```

## Tests

Assert message stability: two different IDs or URLs must produce the same `getMessage()`, with the unique values only in context.

```php
$a = new UpstreamRequestException('https://a.example/x', 502);
$b = new UpstreamRequestException('https://b.example/y', 503);

$this->assertSame(UpstreamRequestException::REQUEST_FAILED, $a->getMessage());
$this->assertSame($a->getMessage(), $b->getMessage());
$this->assertSame('https://a.example/x', $a->context()['url']);
$this->assertNotSame($a->context()['url'], $b->context()['url']);
```

## Composes with Boost

- [`error-handling.md`](https://github.com/laravel/boost/blob/main/.ai/laravel/skill/laravel-best-practices/rules/error-handling.md) — Boost owns reporting, rendering, throttling, and attaching structured data via `context()`. This file is the grouping counterpart: keep the message a stable failure-class name so that context does not leak into the grouping key.
