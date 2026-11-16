"""The entries already seen, by source."""

import sqlite3


class Store:
    def __init__(self, path):
        self._db = sqlite3.connect(path)
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS entry ("
            "source TEXT NOT NULL, id TEXT NOT NULL, title TEXT, link TEXT, published TEXT,"
            " PRIMARY KEY (source, id))"
        )
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS poll (source TEXT PRIMARY KEY, at REAL NOT NULL, ok INTEGER NOT NULL)"
        )

    def add(self, source, entries):
        """Insert entries not seen before; returns how many were new."""
        new = 0
        for entry in entries:
            cursor = self._db.execute(
                "INSERT OR IGNORE INTO entry (source, id, title, link, published) VALUES (?, ?, ?, ?, ?)",
                (source, entry["id"], entry.get("title"), entry.get("link"), entry.get("published")),
            )
            new += cursor.rowcount
        self._db.commit()
        return new

    def record_poll(self, source, at, ok):
        self._db.execute(
            "INSERT INTO poll (source, at, ok) VALUES (?, ?, ?)"
            " ON CONFLICT(source) DO UPDATE SET at = excluded.at, ok = excluded.ok",
            (source, at, 1 if ok else 0),
        )
        self._db.commit()

    def last_poll(self, source):
        row = self._db.execute("SELECT at, ok FROM poll WHERE source = ?", (source,)).fetchone()
        return (row[0], bool(row[1])) if row else None

    def count(self, source):
        return self._db.execute("SELECT COUNT(*) FROM entry WHERE source = ?", (source,)).fetchone()[0]
