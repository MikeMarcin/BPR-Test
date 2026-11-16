"""The urllib wrapper every source module calls.

Each source module owns its retry loop; this module only performs one
request and reports what came back.
"""

import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


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


def request_once(url, headers, timeout):
    """One GET. Returns a Response for any HTTP status, raises OSError when
    no response arrived (DNS, refused connection, timeout)."""
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as reply:
            return Response(reply.status, dict(reply.headers.items()), reply.read())
    except urllib.error.HTTPError as error:
        return Response(error.code, dict(error.headers.items()), error.read())


def auth_headers(token):
    headers = {"User-Agent": "feedsync/0.8", "Accept": "*/*"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def is_retryable(status):
    """429 and every 5xx are worth another try; other 4xx are not."""
    return status == 429 or 500 <= status <= 599
