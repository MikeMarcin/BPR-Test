"""JSON Feed 1.1 sources."""

import json
import time

from feedsync import client
from feedsync.errors import ParseError


def fetch(source, settings, cache, sleep=time.sleep):
    """Fetch and parse one JSON Feed source; None when nothing changed."""
    body = client.get(source, settings, cache, "application/feed+json, application/json;q=0.9", sleep=sleep)
    return None if body is None else parse(source.url, body)


def parse(url, body):
    """The items of a JSON Feed. An item with no id is skipped."""
    try:
        document = json.loads(body)
    except ValueError as error:
        raise ParseError(url, f"not JSON: {error}") from error
    if not isinstance(document, dict) or not str(document.get("version", "")).startswith("https://jsonfeed.org/version/"):
        raise ParseError(url, "no jsonfeed version")
    entries = []
    for item in document.get("items", []):
        identity = item.get("id")
        if identity is None:
            continue
        entries.append(
            {
                "id": str(identity),
                "title": item.get("title"),
                "link": item.get("url") or item.get("external_url"),
                "published": item.get("date_published"),
            }
        )
    return entries
