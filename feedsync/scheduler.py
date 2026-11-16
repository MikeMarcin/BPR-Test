"""Decides which sources are due and runs them."""

import time

from feedsync.errors import AuthError, FetchError, ParseError
from feedsync.sources import atom, jsonfeed, rss

FETCHERS = {"rss": rss.fetch, "atom": atom.fetch, "json": jsonfeed.fetch}


def due(sources, store, now):
    """The sources whose interval has passed since their last poll. A source
    whose last poll failed is due again after a quarter of its interval."""
    result = []
    for source in sources:
        last = store.last_poll(source.name)
        if last is None:
            result.append(source)
            continue
        at, ok = last
        wait = source.interval if ok else source.interval / 4
        if now - at >= wait:
            result.append(source)
    return result


def run_once(settings, store, cache, now=time.time, sleep=time.sleep, log=print):
    """Poll every due source once. Returns (new entries, failed sources).

    An AuthError disables nothing but is reported apart from other failures:
    it needs a person, not a retry.
    """
    new = 0
    failed = []
    needs_credentials = []
    for source in due(settings.sources, store, now()):
        fetch = FETCHERS[source.kind]
        try:
            entries = fetch(source, settings, cache, sleep=sleep)
        except AuthError as error:
            log(f"{source.name}: credentials refused ({error.status})")
            needs_credentials.append(source.name)
            store.record_poll(source.name, now(), False)
            continue
        except (FetchError, ParseError) as error:
            log(f"{source.name}: {error}")
            failed.append(source.name)
            store.record_poll(source.name, now(), False)
            continue
        if entries is not None:
            added = store.add(source.name, entries)
            new += added
            log(f"{source.name}: {added} new of {len(entries)}")
        else:
            log(f"{source.name}: not modified")
        store.record_poll(source.name, now(), True)
    return new, failed, needs_credentials
