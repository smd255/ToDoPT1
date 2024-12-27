import pytest
from flask import g
from flask import session

from src.db import get_db

from src.auth import (
    MESSAGE_AUTH_USERNAME_BLANK_CHK,
    MESSAGE_AUTH_PASSWORD_BLANK_CHK,
    MESSAGE_AUTH_USERNAME_VALID_CHK,
    MESSAGE_AUTH_PASSWORD_VALID_CHK,
    MESSAGE_AUTH_USERNAME_REG_CHK
)

def test_register(client, app):
    #ページの表示チェック
    assert client.get("/auth/register").status_code == 200

    #リダイレクトのチェック
    response = client.post("/auth/register", data={"username": "a", "password": "a"})
    assert response.headers["Location"] == "/auth/login"

    #ユーザー追加チェック
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'a'").fetchone()
            is not None
        )


#ユーザー名、パスワードの登録チェック
@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", MESSAGE_AUTH_USERNAME_BLANK_CHK.encode('utf-8')),
        ("a", "", MESSAGE_AUTH_PASSWORD_BLANK_CHK.encode('utf-8')),
        ("test", "test", MESSAGE_AUTH_USERNAME_REG_CHK.encode('utf-8')),
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth):
    #ページの表示チェック
    assert client.get("/auth/login").status_code == 200

    #indexページへのリダイレクトチェック
    response = auth.login()
    assert response.headers["Location"] == "/"

    # セッション中のユーザーID、ユーザー名チェック
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


#ユーザー名、パスワードの認証チェック
@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", MESSAGE_AUTH_USERNAME_VALID_CHK.encode('utf-8')), 
     ("test", "a", MESSAGE_AUTH_PASSWORD_VALID_CHK.encode('utf-8'))),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
