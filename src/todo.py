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

#メイン画面
@bp.route("/")
def index():
    db = get_db()
    tasks = db.execute(
        "SELECT t.id, title, is_done, author_id, username"
        " FROM task t JOIN user u ON t.author_id = u.id"
        " ORDER BY t.id DESC"
    ).fetchall()
    
    return render_template("todo/index.html", tasks = tasks)

#メイン画面 状況更新ボタン
@bp.route("/submit_form", methods= ("POST",))
def submit_form():
    #チェックボックスの中身を周回で取得
    checkbox_values = {}
    for key in request.form:
        if request.form.get(key):
            checkbox_values[key] = 'checked'
        else:
            checkbox_values[key] = 'unchecked'
    
    # フラッシュメッセージとしてチェックボックスの状態を表示
    for name, value in checkbox_values.items():
        flash(f'{name} is {value}')
    
    return render_template('todo/index.html', checkbox_count=len(checkbox_values))



#タスク作成画面
@bp.route("/create", methods= ("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        error = None

        #タイトル空欄時の処理
        if not title:
            error = "タイトルの入力が必要です"

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
        #TODO:タスク状況更新
        error = None

        #タイトル空欄時の処理
        if not title:
            error = "タイトルの入力が必要です"

        if error is not None:
            flash(error)
        else:
            #TODO:タスク状況の更新
            db = get_db()
            db.execute(
                "UPDATE task SET title = ? WHERE id = ?", (title, id)
            )
            db.commit()
            return redirect(url_for("todo.index"))
        
    return render_template("/todo/update.html", task=task)


#タスクの消去
@bp.route("/<int:id>/delete", methods=("POST",))
#TODO:未ログイン時のログイン要求
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