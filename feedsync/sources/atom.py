"""Atom 1.0 sources."""

import time
import xml.etree.ElementTree as ElementTree

from feedsync import client
from feedsync.errors import ParseError

ATOM = "{http://www.w3.org/2005/Atom}"

def fetch(source, settings, cache, sleep=time.sleep):
    """Fetch and parse one Atom source; None when nothing changed."""
    body = client.get(source, settings, cache, "application/atom+xml, application/xml;q=0.9", sleep=sleep)
    return None if body is None else parse(source.url, body)


def parse(url, body):
    """The entries of an Atom document. An entry with no id is skipped."""
    try:
        root = ElementTree.fromstring(body)
    except ElementTree.ParseError as error:
        raise ParseError(url, f"not XML: {error}") from error
    if root.tag != ATOM + "feed":
        raise ParseError(url, "no atom feed")
    entries = []
    for entry in root.findall(ATOM + "entry"):
        identity = _text(entry, "id")
        if not identity:
            continue
        entries.append(
            {
                "id": identity,
                "title": _text(entry, "title"),
                "link": _link(entry),
                "published": _text(entry, "published") or _text(entry, "updated"),
            }
        )
    return entries


def _link(entry):
    """The alternate link; a link with no rel is an alternate."""
    for link in entry.findall(ATOM + "link"):
        if link.get("rel", "alternate") == "alternate":
            return link.get("href")
    return None


def _text(element, tag):
    found = element.find(ATOM + tag)
    if found is None or found.text is None:
        return None
    return found.text.strip() or None
