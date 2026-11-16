"""Command line: feedsync run, feedsync status."""

import argparse
import sys
import time

from feedsync import config, scheduler
from feedsync.cache import Cache
from feedsync.store import Store


def main(argv=None):
    parser = argparse.ArgumentParser(prog="feedsync")
    parser.add_argument("command", choices=("run", "status"))
    parser.add_argument("--config", default="feeds.toml")
    parser.add_argument("--cache", default="feedsync-cache.json")
    arguments = parser.parse_args(argv)
    settings = config.load(arguments.config)
    store = Store(settings.store_path)
    if arguments.command == "status":
        for source in settings.sources:
            last = store.last_poll(source.name)
            state = "never polled" if last is None else ("ok" if last[1] else "failed")
            print(f"{source.name}: {store.count(source.name)} entries, {state}")
        return 0
    cache = Cache(arguments.cache)
    new, failed, needs_credentials = scheduler.run_once(settings, store, cache, now=time.time)
    print(f"{new} new entries")
    if needs_credentials:
        print("credentials refused: " + ", ".join(needs_credentials), file=sys.stderr)
        return 3
    if failed:
        print("failed: " + ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
