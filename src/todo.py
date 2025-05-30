from flask import Blueprint
from flask import flash
from flask import g
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from werkzeug.exceptions import abort


from .db import get_db
from .auth import login_required

bp = Blueprint("todo", __name__)

INDEX_CHECKBOX = "checkbox"   #index.htmlチェックボックスのname

TEXT_TODO_INDEX_REGSTER = "ユーザー登録"
TEXT_TODO_INDEX_LOGIN = "ログイン"

MESSAGE_TODO_CREATE_TITLE_BLANK_CHK = "タイトルの入力が必要です"
MESSAGE_TODO_UPDATE_TITLE_BLANK_CHK = "タイトルの入力が必要です"

#メイン画面
@bp.route("/")
def index():
    db = get_db()
    tasks = db.execute(
        "SELECT t.id, title, is_done, author_id, username"
        " FROM task t JOIN user u ON t.author_id = u.id"
        " ORDER BY t.id DESC"
    ).fetchall()
    
    return render_template("todo/index.html", tasks = tasks, 
                           register_text = TEXT_TODO_INDEX_REGSTER, 
                           login_text = TEXT_TODO_INDEX_LOGIN)

#メイン画面 状況更新ボタン
@bp.route("/<int:id>/submit_form", methods= ("POST",))
def submit_form(id):
    #タスク状況更新
    db = get_db()
    if request.form.get(INDEX_CHECKBOX) != None:
        is_done = True
    else:
        is_done = False

    db.execute(
            "UPDATE task SET is_done = ? WHERE id = ?", (is_done, id)
        )
    db.commit()   

    #更新後情報取得
    tasks = db.execute(
        "SELECT t.id, title, is_done, author_id, username"
        " FROM task t JOIN user u ON t.author_id = u.id"
        " ORDER BY t.id DESC"
    ).fetchall()

    return render_template("todo/index.html", tasks = tasks, 
                           register_text = TEXT_TODO_INDEX_REGSTER, 
                           login_text = TEXT_TODO_INDEX_LOGIN)


#タスク作成画面
@bp.route("/create", methods= ("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        error = None

        #タイトル空欄時の処理
        if not title:
            error = MESSAGE_TODO_CREATE_TITLE_BLANK_CHK

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO task (title, author_id, is_done) VALUES (?, ?, ?)",
                (title, g.user["id"], False),
            )
            db.commit()
            return redirect(url_for("todo.index"))
        
    return render_template("todo/create.html")


#タスク内容更新画面
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    task = _get_task(id)    #task取得
    if request.method == "POST":
        title = request.form["title"]
        error = None

        #タイトル空欄時の処理
        if not title:
            error = MESSAGE_TODO_UPDATE_TITLE_BLANK_CHK

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE task SET title = ? WHERE id = ?", (title, id)
            )
            db.commit()
            return redirect(url_for("todo.index"))
        
    return render_template("/todo/update.html", task=task)


#タスクの消去
@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    _get_task(id)   #戻り値の使用ではなく、エラーチェック用。関数分けるのもあり。
    db = get_db()
    db.execute("DELETE FROM task WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("todo.index"))


#タスク取得
def _get_task(id, check_author=True):
    """
    idとauthor_idからtaskを取得
    :引数 id: taskのid
    :引数 check_author: 現在のユーザーのauthorの一致確認
    :戻り値: task
    :エラー 404: 指定のid のtaskが無い場合
    :エラー 403: 現在のユーザーが著者で無い場合
    """
    task =(
        get_db()
        .execute(
            "SELECT t.id, title, author_id, username"
            " FROM task t JOIN user u ON t.author_id = u.id"
            " WHERE t.id = ?",
            (id,),
        )
        .fetchone()
    )
    
    if task is None:
        abort(404, f"タスク id {id} は存在しません。")

    if check_author and task["author_id"] != g.user["id"]:
        abort(403)

    return task