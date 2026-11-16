import os
import tempfile
import unittest

from feedsync.cache import Cache


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "cache.json")

    def tearDown(self):
        self.folder.cleanup()

    def test_stores_and_returns_validators(self):
        cache = Cache(self.path)
        cache.store("https://example.test/a", {"ETag": '"1"', "Last-Modified": "Mon, 02 Nov 2026 10:00:00 GMT"}, b"body")
        self.assertEqual(
            cache.validators("https://example.test/a"),
            {"If-None-Match": '"1"', "If-Modified-Since": "Mon, 02 Nov 2026 10:00:00 GMT"},
        )
        self.assertEqual(cache.body("https://example.test/a"), b"body")

    def test_survives_a_restart(self):
        Cache(self.path).store("https://example.test/a", {"etag": '"1"'}, b"body")
        self.assertEqual(Cache(self.path).validators("https://example.test/a"), {"If-None-Match": '"1"'})

    def test_forget_removes_the_entry(self):
        cache = Cache(self.path)
        cache.store("https://example.test/a", {"ETag": '"1"'}, b"body")
        cache.forget("https://example.test/a")
        self.assertEqual(cache.validators("https://example.test/a"), {})


if __name__ == "__main__":
    unittest.main()
