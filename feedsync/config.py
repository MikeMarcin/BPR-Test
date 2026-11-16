"""Configuration: the sources to poll and how hard to try."""

import tomllib
from dataclasses import dataclass, field

DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 1.0
DEFAULT_INTERVAL_SECONDS = 900


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    kind: str
    interval: int = DEFAULT_INTERVAL_SECONDS
    token: str | None = None
    params: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Settings:
    sources: tuple
    retries: int = DEFAULT_RETRIES
    backoff: float = DEFAULT_BACKOFF_SECONDS
    store_path: str = "feedsync.db"


def load(path):
    """Read settings from a TOML file. Unknown source kinds are refused."""
    with open(path, "rb") as handle:
        raw = tomllib.load(handle)
    sources = []
    for name, entry in raw.get("source", {}).items():
        kind = entry.get("kind", "rss")
        if kind not in ("rss", "atom", "json"):
            raise ValueError(f"source {name}: unknown kind {kind!r}")
        sources.append(
            Source(
                name=name,
                url=entry["url"],
                kind=kind,
                interval=int(entry.get("interval", DEFAULT_INTERVAL_SECONDS)),
                token=entry.get("token"),
                params=dict(entry.get("params", {})),
            )
        )
    fetch = raw.get("fetch", {})
    return Settings(
        sources=tuple(sources),
        retries=int(fetch.get("retries", DEFAULT_RETRIES)),
        backoff=float(fetch.get("backoff", DEFAULT_BACKOFF_SECONDS)),
        store_path=raw.get("store", {}).get("path", "feedsync.db"),
    )
