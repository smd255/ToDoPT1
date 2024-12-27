import pytest

from src.db import get_db

from src.todo import (
    TEXT_TODO_INDEX_REGSTER,
    TEXT_TODO_INDEX_LOGIN,
    MESSAGE_TODO_UPDATE_TITLE_BLANK_CHK,
    INDEX_CHECKBOX
)

def test_index(client, auth):
    response = client.get("/")
    assert TEXT_TODO_INDEX_LOGIN.encode('utf-8') in response.data
    assert TEXT_TODO_INDEX_REGSTER.encode('utf-8')  in response.data

    auth.login()
    response = client.get("/")
    assert b"test title" in response.data
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
        db.execute("UPDATE task SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
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
    client.post("/create", data={"title": "created"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM task").fetchone()[0]
        assert count == 2


#更新処理チェック
def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM task WHERE id = 1").fetchone()
        assert task["title"] == "updated"


#作成・更新チェック
@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": ""})
    assert MESSAGE_TODO_UPDATE_TITLE_BLANK_CHK.encode('utf-8') in response.data


#消去チェック
def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM task WHERE id = 1").fetchone()
        assert task is None


#チェックボックステスト
@pytest.mark.parametrize("chk", ("on", None))
def test_submit_form(client, auth, app, chk):

    auth.login()
    # assert client.get("/1/submit_form").status_code == 200
    client.post("/1/submit_form", data={INDEX_CHECKBOX: chk})

    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM task WHERE id = 1").fetchone()
        if chk == 'on':
            assert task['is_done'] == True
        else:
            assert task['is_done'] == False

 
# def test_submit_form(client, monkeypatch):
#     # モックデータを設定
#     class MockDB:
#         def execute(self, query, params):
#             pass
#         def commit(self):
#             pass
#         def fetchall(self):
#             return [
#                 {'id': 1, 'title': 'Task 1', 'is_done': False, 'author_id': 1, 'username': 'user1'},
#                 {'id': 2, 'title': 'Task 2', 'is_done': True, 'author_id': 2, 'username': 'user2'}
#             ]

#     def mock_get_db():
#         return MockDB()

#     monkeypatch.setattr('src.db.get_db', mock_get_db)

#     # テストデータを送信
#     response = client.post('/1/submit_form', data={INDEX_CHECKBOX: 'on'})
#     assert response.status_code == 200
#     assert 'Task 1' in response.data.decode('utf-8')
#     assert 'Task 2' in response.data.decode('utf-8')




    

