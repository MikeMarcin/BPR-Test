import unittest

from feedsync import scheduler
from feedsync.config import Settings, Source
from feedsync.errors import AuthError, FetchError
from feedsync.store import Store
from tests.fakes import MemoryCache


def entries(*ids):
    return [{"id": identity, "title": identity} for identity in ids]


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.sources = (
            Source(name="a", url="https://example.test/a", kind="rss", interval=600),
            Source(name="b", url="https://example.test/b", kind="atom", interval=600),
        )
        self.settings = Settings(sources=self.sources)
        self.saved = dict(scheduler.FETCHERS)
        self.lines = []

    def tearDown(self):
        scheduler.FETCHERS.clear()
        scheduler.FETCHERS.update(self.saved)

    def run_with(self, rss, atom, at):
        scheduler.FETCHERS["rss"] = rss
        scheduler.FETCHERS["atom"] = atom
        return scheduler.run_once(self.settings, self.store, MemoryCache(), now=lambda: at, log=self.lines.append)

    def test_adds_new_entries_and_counts_them(self):
        new, failed, credentials = self.run_with(lambda *a, **k: entries("1", "2"), lambda *a, **k: None, 1000.0)
        self.assertEqual((new, failed, credentials), (2, [], []))
        self.assertIn("b: not modified", self.lines)

    def test_a_failed_source_is_due_after_a_quarter_interval(self):
        def failing(source, *a, **k):
            raise FetchError(source.url, 500, "giving up")

        self.run_with(failing, lambda *a, **k: None, 1000.0)
        self.assertEqual([source.name for source in scheduler.due(self.sources, self.store, 1100.0)], [])
        self.assertEqual([source.name for source in scheduler.due(self.sources, self.store, 1150.0)], ["a"])

    def test_refused_credentials_are_reported_apart(self):
        def refused(source, *a, **k):
            raise AuthError(source.url, 401, "credentials refused")

        new, failed, credentials = self.run_with(refused, lambda *a, **k: entries("1"), 1000.0)
        self.assertEqual((new, failed, credentials), (1, [], ["a"]))


if __name__ == "__main__":
    unittest.main()
