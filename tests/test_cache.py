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
        cache.store("https://example.test/a", None, {"ETag": '"1"', "Last-Modified": "Mon, 02 Nov 2026 10:00:00 GMT"}, b"body")
        self.assertEqual(
            cache.validators("https://example.test/a", None),
            {"If-None-Match": '"1"', "If-Modified-Since": "Mon, 02 Nov 2026 10:00:00 GMT"},
        )
        self.assertEqual(cache.body("https://example.test/a", None), b"body")

    def test_survives_a_restart(self):
        Cache(self.path).store("https://example.test/a", None, {"etag": '"1"'}, b"body")
        self.assertEqual(Cache(self.path).validators("https://example.test/a", None), {"If-None-Match": '"1"'})

    def test_query_strings_do_not_share_an_entry(self):
        cache = Cache(self.path)
        cache.store("https://example.test/a?tag=stable", None, {"ETag": '"s"'}, b"stable")
        cache.store("https://example.test/a?tag=beta", None, {"ETag": '"b"'}, b"beta")
        self.assertEqual(cache.body("https://example.test/a?tag=stable", None), b"stable")
        self.assertEqual(cache.validators("https://example.test/a?tag=beta", None), {"If-None-Match": '"b"'})

    def test_credentials_do_not_share_an_entry(self):
        cache = Cache(self.path)
        cache.store("https://example.test/a", "token", {"ETag": '"private"'}, b"private")
        self.assertEqual(cache.validators("https://example.test/a", None), {})
        self.assertIsNone(cache.body("https://example.test/a", None))

    def test_forget_removes_the_entry(self):
        cache = Cache(self.path)
        cache.store("https://example.test/a", None, {"ETag": '"1"'}, b"body")
        cache.forget("https://example.test/a", None)
        self.assertEqual(cache.validators("https://example.test/a", None), {})


if __name__ == "__main__":
    unittest.main()
