import unittest
from unittest import mock

from feedsync.config import Settings, Source
from feedsync.errors import FetchError, ParseError
from feedsync.sources import rss
from tests.fakes import MemoryCache, Script, ok, status

BODY = b"""<rss version="2.0"><channel><title>t</title>
<item><guid>a1</guid><title>First</title><link>https://example.test/1</link><pubDate>Mon, 02 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>No guid</title><link>https://example.test/2</link></item>
<item><title>Nothing to identify it</title></item>
</channel></rss>"""

SOURCE = Source(name="news", url="https://example.test/feed", kind="rss")
SETTINGS = Settings(sources=(SOURCE,), retries=3, backoff=1.0)


class RssTests(unittest.TestCase):
    def fetch(self, answers, source=SOURCE, cache=None):
        script = Script(answers)
        sleeps = []
        with mock.patch("feedsync.client.request_once", script):
            entries = rss.fetch(source, SETTINGS, cache or MemoryCache(), sleep=sleeps.append)
        return entries, script, sleeps

    def test_parses_items_and_falls_back_to_the_link(self):
        entries, script, _ = self.fetch([ok(BODY)])
        self.assertEqual([entry["id"] for entry in entries], ["a1", "https://example.test/2"])

    def test_retries_a_server_error_with_backoff(self):
        entries, script, sleeps = self.fetch([status(503), status(502), ok(BODY)])
        self.assertEqual(len(entries), 2)
        self.assertEqual(sleeps, [1.0, 2.0])

    def test_gives_up_after_the_configured_retries(self):
        with self.assertRaises(FetchError):
            self.fetch([status(500)] * 3)

    def test_honours_retry_after(self):
        _, _, sleeps = self.fetch([status(429, {"Retry-After": "30"}), ok(BODY)])
        self.assertEqual(sleeps, [30])

    def test_credentials_refused_is_not_retried(self):
        with self.assertRaises(FetchError):
            self.fetch([status(401)])

    def test_a_404_is_not_retried(self):
        script = Script([status(404)])
        with mock.patch("feedsync.client.request_once", script):
            with self.assertRaises(FetchError):
                rss.fetch(SOURCE, SETTINGS, MemoryCache(), sleep=lambda _: None)
        self.assertEqual(len(script.calls), 1)

    def test_not_modified_returns_none_and_sends_the_validator(self):
        cache = MemoryCache()
        self.fetch([ok(BODY, {"ETag": '"v1"'})], cache=cache)
        entries, script, _ = self.fetch([status(304)], cache=cache)
        self.assertIsNone(entries)
        self.assertEqual(script.calls[0]["headers"]["If-None-Match"], '"v1"')

    def test_a_connection_failure_is_retried(self):
        entries, _, sleeps = self.fetch([OSError("refused"), ok(BODY)])
        self.assertEqual(len(entries), 2)
        self.assertEqual(sleeps, [1.0])

    def test_not_rss_is_a_parse_error(self):
        with self.assertRaises(ParseError):
            self.fetch([ok(b"<html/>")])


if __name__ == "__main__":
    unittest.main()
