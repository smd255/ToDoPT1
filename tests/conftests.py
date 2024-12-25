import os
import tempfile

import pytest

from src import create_app
from src.db import get_db
from src.db import init_db

#SQL読み出し、テスト実装
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    # テスト毎に一時ファイル作成
    db_fd, db_path = tempfile.mkstemp()
    # テスト設定でアプリ作成
    app = create_app({"TESTING": True, "DATABASE": db_path})

    #DB作成、テストロード
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    #一時ファイルクローズ、削除
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """テストクライアント"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLIテストランナー"""
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
