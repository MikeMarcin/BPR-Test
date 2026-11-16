# feedsync

Polls RSS, Atom and JSON Feed sources and writes new entries to a local store.

## Layout

- `feedsync/sources/` one module a feed format; each fetches and parses its own format.
- `feedsync/legacy_http.py` the urllib wrapper every source module calls.
- `feedsync/cache.py` conditional-request cache (ETag and Last-Modified) keyed by URL.
- `feedsync/scheduler.py` decides which sources are due and runs them.
- `feedsync/cli.py` `feedsync run` and `feedsync status`.

## Retries

Each source retries a failed request three times with exponential backoff
(1s, 2s, 4s) and gives up on a 4xx other than 429. A request times out after
ten seconds.

## Running

    python -m feedsync.cli run --config feeds.toml
    python -m unittest discover tests
