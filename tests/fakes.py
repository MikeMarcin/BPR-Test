"""Shared fakes: a scripted transport and a cache that lives in memory."""

from feedsync.legacy_http import Response


class Script:
    """Replaces legacy_http.request_once: answers from a list, recording
    every call. An OSError instance in the list is raised."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def __call__(self, url, headers, timeout):
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
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

    def validators(self, url, token):
        entry = self.entries.get((url, bool(token)))
        return {"If-None-Match": entry["etag"]} if entry and entry["etag"] else {}

    def body(self, url, token):
        entry = self.entries.get((url, bool(token)))
        return entry["body"] if entry else None

    def store(self, url, token, headers, body):
        self.entries[(url, bool(token))] = {"etag": headers.get("ETag"), "body": body}
