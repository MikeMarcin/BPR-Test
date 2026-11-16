"""JSON Feed 1.1 sources."""

import json
import time

from feedsync import legacy_http
from feedsync.errors import AuthError, FetchError, ParseError

MAX_RETRY_AFTER_SECONDS = 120


def fetch(source, settings, cache, sleep=time.sleep):
    """Fetch and parse one JSON Feed source. Returns its entries, or None when
    the source answered 304 and nothing changed."""
    url = legacy_http.build_url(source.url, source.params)
    headers = legacy_http.auth_headers(source.token)
    headers["Accept"] = "application/feed+json, application/json;q=0.9"
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
