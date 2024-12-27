import sqlite3

import pytest
from src.db import get_db

from src.db import MESSAGE_DB_INIT

#接続、接続解除テスト
def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)


#コマンドラインinit-dbのテスト
def test_init_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("src.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert MESSAGE_DB_INIT in result.output
    assert Recorder.called