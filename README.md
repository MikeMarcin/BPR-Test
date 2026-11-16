# feedsync

Polls RSS, Atom and JSON Feed sources and writes new entries to a local store.

## Layout

- `feedsync/sources/` one module a feed format; each parses its own format.
- `feedsync/client.py` the one fetch path: request, retry and conditional cache.
- `feedsync/cache.py` conditional-request cache (ETag and Last-Modified) keyed by URL.
- `feedsync/scheduler.py` decides which sources are due and runs them.
- `feedsync/cli.py` `feedsync run` and `feedsync status`.

## Retries

The client retries a failed request three times with exponential backoff
(1s, 2s, 4s) and gives up on a 4xx other than 429.

## Running

    python -m feedsync.cli run --config feeds.toml
    python -m unittest discover tests
