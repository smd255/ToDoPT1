import pytest

from src.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    #TODO:パラメータ見直し
    auth.login()
    response = client.get("/")
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data


#ログインページへのリダイレクトチェック
@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


#author_id の判定チェック
def test_author_required(app, client, auth):
    #ユーザー変更
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    #TODO:つくりこみ段階で現ユーザー以外に見えないようになっている？
    #現在のユーザーでは表示されない
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    #現ユーザーには表示が見えないようになっているかチェック
    assert b'href="/1/update"' not in client.get("/").data


#ユーザーごとの編集・削除アクセスチェック
@pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


#新規タスク作成チェック
def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    #TODO:テーブル内容変更
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


#更新処理チェック
def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"


#作成・更新チェック
@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    #TODO:テーブル変更
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


#消去チェック
def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        #TODO:テーブル変更
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None
