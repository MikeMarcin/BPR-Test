"""Conditional-request cache: remembers each URL's validators and body."""

import hashlib
import json
import os
import threading


class Cache:
    """Validators and bodies by source URL, kept in one JSON file."""

    def __init__(self, path):
        self._path = path
        self._lock = threading.Lock()
        self._entries = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                self._entries = json.load(handle)

    @staticmethod
    def key(url):
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def validators(self, url):
        """The conditional headers to send for this request, if any."""
        with self._lock:
            entry = self._entries.get(self.key(url))
        if entry is None:
            return {}
        headers = {}
        if entry.get("etag"):
            headers["If-None-Match"] = entry["etag"]
        if entry.get("modified"):
            headers["If-Modified-Since"] = entry["modified"]
        return headers

    def body(self, url):
        """The body last stored for this request, or None."""
        with self._lock:
            entry = self._entries.get(self.key(url))
        if entry is None:
            return None
        return bytes.fromhex(entry["body"])

    def store(self, url, headers, body):
        """Remember a 200's validators and body, and write the file."""
        lowered = {name.lower(): value for name, value in headers.items()}
        entry = {
            "etag": lowered.get("etag"),
            "modified": lowered.get("last-modified"),
            "body": body.hex(),
        }
        self._entries[self.key(url)] = entry
        self._write()

    def forget(self, url):
        with self._lock:
            self._entries.pop(self.key(url), None)
            self._write()

    def _write(self):
        temporary = self._path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(self._entries, handle)
        os.replace(temporary, self._path)
