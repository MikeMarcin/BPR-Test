"""RSS 2.0 sources."""

import time
import xml.etree.ElementTree as ElementTree

from feedsync import client
from feedsync.errors import ParseError


def fetch(source, settings, cache, sleep=time.sleep):
    """Fetch and parse one RSS source; None when nothing changed."""
    body = client.get(source, settings, cache, "application/rss+xml, application/xml;q=0.9", sleep=sleep)
    return None if body is None else parse(source.url, body)


def parse(url, body):
    """The items of an RSS 2.0 document, oldest last as the feed gives them."""
    try:
        root = ElementTree.fromstring(body)
    except ElementTree.ParseError as error:
        raise ParseError(url, f"not XML: {error}") from error
    channel = root.find("channel")
    if root.tag != "rss" or channel is None:
        raise ParseError(url, "no rss channel")
    entries = []
    for item in channel.findall("item"):
        link = _text(item, "link")
        identity = _text(item, "guid") or link
        if not identity:
            continue
        entries.append(
            {
                "id": identity,
                "title": _text(item, "title"),
                "link": link,
                "published": _text(item, "pubDate"),
            }
        )
    return entries


def _text(element, tag):
    found = element.find(tag)
    if found is None or found.text is None:
        return None
    return found.text.strip() or None
