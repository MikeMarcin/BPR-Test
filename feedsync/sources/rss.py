"""RSS 2.0 sources."""

import time
import xml.etree.ElementTree as ElementTree

from feedsync import legacy_http
from feedsync.errors import AuthError, FetchError, ParseError

MAX_RETRY_AFTER_SECONDS = 120


def fetch(source, settings, cache, sleep=time.sleep):
    """Fetch and parse one RSS source. Returns its entries, or None when
    the source answered 304 and nothing changed."""
    url = legacy_http.build_url(source.url, source.params)
    headers = legacy_http.auth_headers(source.token)
    headers["Accept"] = "application/rss+xml, application/xml;q=0.9"
    headers.update(cache.validators(url, source.token))
    attempt = 0
    while True:
        try:
            response = legacy_http.request_once(url, headers, settings.timeout)
        except OSError as error:
            if attempt >= settings.retries:
                raise FetchError(url, None, str(error)) from error
            sleep(settings.backoff * (2**attempt))
            attempt += 1
            continue
        if response.status == 304:
            return None
        if response.status in (401, 403):
            raise AuthError(url, response.status, "credentials refused")
        if response.status == 200:
            cache.store(url, source.token, response.headers, response.body)
            return parse(url, response.body)
        if not legacy_http.is_retryable(response.status) or attempt >= settings.retries:
            raise FetchError(url, response.status, "giving up")
        retry_after = response.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            sleep(min(int(retry_after), MAX_RETRY_AFTER_SECONDS))
        else:
            sleep(settings.backoff * (2**attempt))
        attempt += 1


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
