import json
import unittest
from unittest import mock

from feedsync.config import Settings, Source
from feedsync.errors import FetchError, ParseError
from feedsync.sources import jsonfeed
from tests.fakes import MemoryCache, Script, ok, status

BODY = json.dumps(
    {
        "version": "https://jsonfeed.org/version/1.1",
        "items": [
            {"id": 7, "title": "Seven", "url": "https://example.test/7", "date_published": "2026-11-02T10:00:00Z"},
            {"id": "x", "external_url": "https://elsewhere.test/x"},
            {"title": "no id"},
        ],
    }
).encode()

SOURCE = Source(name="blog", url="https://example.test/feed.json", kind="json")
SETTINGS = Settings(sources=(SOURCE,), retries=2, backoff=1.0)


class JsonFeedTests(unittest.TestCase):
    def fetch(self, answers):
        script = Script(answers)
        sleeps = []
        with mock.patch("feedsync.client.request_once", script):
            entries = jsonfeed.fetch(SOURCE, SETTINGS, MemoryCache(), sleep=sleeps.append)
        return entries, script, sleeps

    def test_parses_items_and_stringifies_ids(self):
        entries, _, _ = self.fetch([ok(BODY)])
        self.assertEqual([entry["id"] for entry in entries], ["7", "x"])
        self.assertEqual(entries[1]["link"], "https://elsewhere.test/x")

    def test_retries_twice_then_gives_up(self):
        script = Script([status(503)] * 2)
        with mock.patch("feedsync.client.request_once", script):
            with self.assertRaises(FetchError):
                jsonfeed.fetch(SOURCE, SETTINGS, MemoryCache(), sleep=lambda _: None)
        self.assertEqual(len(script.calls), 2)

    def test_a_timeout_is_retried(self):
        entries, _, sleeps = self.fetch([TimeoutError("timed out"), ok(BODY)])
        self.assertEqual(len(entries), 2)
        self.assertEqual(sleeps, [1.0])

    def test_not_a_feed_is_a_parse_error(self):
        with self.assertRaises(ParseError):
            self.fetch([ok(b'{"items": []}')])


if __name__ == "__main__":
    unittest.main()
