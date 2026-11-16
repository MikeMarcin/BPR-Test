import unittest
from unittest import mock

from feedsync.config import Settings, Source
from feedsync.errors import FetchError
from feedsync.sources import atom
from tests.fakes import MemoryCache, Script, ok, status

BODY = b"""<feed xmlns="http://www.w3.org/2005/Atom"><title>t</title>
<entry><id>urn:1</id><title>One</title><link href="https://example.test/1"/><updated>2026-11-02T10:00:00Z</updated></entry>
<entry><id>urn:2</id><title>Two</title><link rel="self" href="https://example.test/self"/><link rel="alternate" href="https://example.test/2"/></entry>
<entry><title>No id</title></entry>
</feed>"""

SOURCE = Source(name="releases", url="https://example.test/atom", kind="atom", token="s3cret", params={"tag": "stable"})
SETTINGS = Settings(sources=(SOURCE,), retries=3, backoff=0.5)


class AtomTests(unittest.TestCase):
    def fetch(self, answers, cache=None):
        script = Script(answers)
        sleeps = []
        with mock.patch("feedsync.client.request_once", script):
            entries = atom.fetch(SOURCE, SETTINGS, cache or MemoryCache(), sleep=sleeps.append)
        return entries, script, sleeps

    def test_parses_entries_and_their_alternate_links(self):
        entries, _, _ = self.fetch([ok(BODY)])
        self.assertEqual([entry["link"] for entry in entries], ["https://example.test/1", "https://example.test/2"])

    def test_sends_the_token_and_the_query_parameters(self):
        _, script, _ = self.fetch([ok(BODY)])
        self.assertEqual(script.calls[0]["url"], "https://example.test/atom?tag=stable")
        self.assertEqual(script.calls[0]["headers"]["Authorization"], "Bearer s3cret")

    def test_backoff_doubles_from_the_configured_base(self):
        _, _, sleeps = self.fetch([status(500), status(500), ok(BODY)])
        self.assertEqual(sleeps, [0.5, 1.0])

    def test_forbidden_is_not_retried(self):
        with self.assertRaises(FetchError):
            self.fetch([status(403)])

    def test_gives_up_after_the_configured_retries(self):
        with self.assertRaises(FetchError):
            self.fetch([status(500)] * 3)


if __name__ == "__main__":
    unittest.main()
