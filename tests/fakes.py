"""Shared fakes: a scripted transport and a cache that lives in memory."""

from feedsync.client import Response


class Script:
    """Replaces client.request_once: answers from a list, recording every
    call. An OSError instance in the list is raised."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def __call__(self, url, headers, timeout=None):
        self.calls.append({"url": url, "headers": dict(headers)})
        answer = self.answers.pop(0)
        if isinstance(answer, OSError):
            raise answer
        return answer


def ok(body, headers=None):
    return Response(200, headers or {}, body)


def status(code, headers=None):
    return Response(code, headers or {}, b"")


class MemoryCache:
    def __init__(self):
        self.entries = {}

    def validators(self, url):
        entry = self.entries.get(url)
        return {"If-None-Match": entry["etag"]} if entry and entry["etag"] else {}

    def body(self, url):
        entry = self.entries.get(url)
        return entry["body"] if entry else None

    def store(self, url, headers, body):
        self.entries[url] = {"etag": headers.get("ETag"), "body": body}
