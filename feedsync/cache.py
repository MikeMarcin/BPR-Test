"""Conditional-request cache: remembers each URL's validators and body."""

import hashlib
import json
import os
import threading


class Cache:
    """Validators and bodies by request key, kept in one JSON file.

    The key is the full request URL, query string included, plus whether the
    request carried a token: two sources that differ only by a query
    parameter or by credentials never share an entry.
    """

    def __init__(self, path):
        self._path = path
        self._lock = threading.Lock()
        self._entries = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                self._entries = json.load(handle)

    @staticmethod
    def key(url, token):
        digest = hashlib.sha256()
        digest.update(url.encode("utf-8"))
        digest.update(b"\0")
        digest.update(b"auth" if token else b"anon")
        return digest.hexdigest()

    def validators(self, url, token):
        """The conditional headers to send for this request, if any."""
        with self._lock:
            entry = self._entries.get(self.key(url, token))
        if entry is None:
            return {}
        headers = {}
        if entry.get("etag"):
            headers["If-None-Match"] = entry["etag"]
        if entry.get("modified"):
            headers["If-Modified-Since"] = entry["modified"]
        return headers

    def body(self, url, token):
        """The body last stored for this request, or None."""
        with self._lock:
            entry = self._entries.get(self.key(url, token))
        if entry is None:
            return None
        return bytes.fromhex(entry["body"])

    def store(self, url, token, headers, body):
        """Remember a 200's validators and body, and write the file."""
        lowered = {name.lower(): value for name, value in headers.items()}
        entry = {
            "etag": lowered.get("etag"),
            "modified": lowered.get("last-modified"),
            "body": body.hex(),
        }
        with self._lock:
            self._entries[self.key(url, token)] = entry
            self._write()

    def forget(self, url, token):
        with self._lock:
            self._entries.pop(self.key(url, token), None)
            self._write()

    def _write(self):
        temporary = self._path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(self._entries, handle)
        os.replace(temporary, self._path)
