import sqlite3

import pytest

import database


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Point database.py at a fresh temp SQLite file for each test."""
    db_path = str(tmp_path / "test_trc_history.db")
    monkeypatch.setattr(database, "DB_NAME", db_path)
    database.init_db()
    return db_path


def test_save_message_dedups_on_timetoken(db):
    assert database.save_message("general", "alice", "hi", "10:00:00", "tt1") is True
    # A redelivered message with the same timetoken must not create a duplicate row
    assert database.save_message("general", "alice", "hi", "10:00:01", "tt1") is False

    history = database.get_local_history("general", limit=10)
    assert len(history) == 1


def test_save_message_allows_identical_text_with_distinct_timetokens(db):
    # Regression test for #8: identical message text must still be stored
    # twice if the timetokens genuinely differ (real messages, not a redelivery).
    assert database.save_message("general", "bob", "hello", "10:00:00", "tt1") is True
    assert database.save_message("general", "bob", "hello", "10:00:01", "tt2") is True

    history = database.get_local_history("general", limit=10)
    assert len(history) == 2


def test_get_local_history_orders_chronologically_and_respects_limit(db):
    for i in range(5):
        database.save_message("general", "alice", f"msg{i}", f"10:00:0{i}", f"tt{i}")

    history = database.get_local_history("general", limit=3)
    assert [m["message"] for m in history] == ["msg2", "msg3", "msg4"]


def test_get_local_history_is_scoped_to_channel(db):
    database.save_message("general", "alice", "in general", "10:00:00", "tt1")
    database.save_message("random", "alice", "in random", "10:00:00", "tt2")

    history = database.get_local_history("general", limit=10)
    assert [m["message"] for m in history] == ["in general"]


def test_channel_topic_upsert(db):
    assert database.get_channel_topic("general") is None

    database.set_channel_topic("general", "first objective")
    assert database.get_channel_topic("general") == "first objective"

    database.set_channel_topic("general", "revised objective")
    assert database.get_channel_topic("general") == "revised objective"

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM channels WHERE name = 'general'").fetchone()[0]
    conn.close()
    assert count == 1


def test_setting_get_and_update(db):
    assert database.get_setting("nick") is None
    assert database.get_setting("nick", default="anon") == "anon"

    database.update_setting("nick", "alice")
    assert database.get_setting("nick") == "alice"

    database.update_setting("nick", "alice2")
    assert database.get_setting("nick") == "alice2"


def test_get_known_users_excludes_system_and_dedupes(db):
    database.save_message("general", "alice", "hi", "10:00:00", "tt1")
    database.save_message("general", "bob", "yo", "10:00:01", "tt2")
    database.save_message("general", "alice", "again", "10:00:02", "tt3")
    database.save_message("general", "SYSTEM", "alice has joined", "10:00:00", "tt4")

    users = database.get_known_users("general")
    assert set(users) == {"alice", "bob"}
    assert "SYSTEM" not in users


def test_clear_channel_history(db):
    database.save_message("general", "alice", "hi", "10:00:00", "tt1")
    database.save_message("random", "alice", "hi", "10:00:00", "tt2")

    assert database.clear_channel_history("general") is True
    assert database.get_local_history("general", limit=10) == []
    assert len(database.get_local_history("random", limit=10)) == 1
