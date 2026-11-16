"""One fetch path for every source: request, retry, conditional cache.

Replaces the retry loop each source module carried and the legacy_http
wrapper they called.
"""

import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from feedsync.errors import FetchError


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict
    body: bytes


def build_url(url, params):
    """Append query parameters, keeping any the URL already has."""
    if not params:
        return url
    parts = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    query.extend(sorted(params.items()))
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query)))


def request_once(url, headers, timeout=None):
    """One GET. Returns a Response for any HTTP status, raises OSError when
    no response arrived."""
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as reply:
            return Response(reply.status, dict(reply.headers.items()), reply.read())
    except urllib.error.HTTPError as error:
        return Response(error.code, dict(error.headers.items()), error.read())


def get(source, settings, cache, accept, sleep=time.sleep):
    """Fetch one source's body. Returns None when nothing changed (304)."""
    url = build_url(source.url, source.params)
    headers = {"User-Agent": "feedsync/0.9", "Accept": accept}
    if source.token:
        headers["Authorization"] = f"Bearer {source.token}"
    headers.update(cache.validators(source.url))
    for attempt in range(settings.retries):
        try:
            response = request_once(url, headers)
        except OSError:
            sleep(settings.backoff * (2**attempt))
            continue
        if response.status == 304:
            return None
        if response.status == 200:
            cache.store(source.url, response.headers, response.body)
            return response.body
        if response.status != 429 and response.status < 500:
            raise FetchError(url, response.status, "giving up")
        retry_after = response.headers.get("Retry-After")
        sleep(int(retry_after) if retry_after else settings.backoff * (2**attempt))
    raise FetchError(url, None, "giving up")
