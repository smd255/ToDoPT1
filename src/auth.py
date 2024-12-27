import functools

from flask import Blueprint
from flask import flash
from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import render_template
from flask import url_for

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .db import get_db

MESSAGE_AUTH_USERNAME_BLANK_CHK = "ユーザー名の入力が必要です"   #ユーザー名の空白チェック
MESSAGE_AUTH_PASSWORD_BLANK_CHK = "パスワードの入力が必要です"    #パスワードの入力チェック

MESSAGE_AUTH_USERNAME_VALID_CHK = "ユーザー名が正しくありません"    #ユーザー名の正誤チェック
MESSAGE_AUTH_PASSWORD_VALID_CHK = "パスワードが正しくありません"    #パスワードの正誤チェック

MESSAGE_AUTH_USERNAME_REG_CHK = "既に登録されています"  #ユーザー名登録チェック

bp = Blueprint("auth", __name__, url_prefix="/auth")

#未ログイン時にログイン要求
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        
        return view(**kwargs)
    
    return wrapped_view



#ログイン中は情報取得
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


#新規ユーザー登録画面
@bp.route("/register", methods=("GET","POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        #空白チェック
        if not username:
            error = MESSAGE_AUTH_USERNAME_BLANK_CHK
        elif not password:
            error = MESSAGE_AUTH_PASSWORD_BLANK_CHK

        #DBに入力を保存
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"ユーザー名： {username} は{MESSAGE_AUTH_USERNAME_REG_CHK}"
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


#ログイン画面
@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        #DBからユーザー名取得
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        #空白・パスワードエラーチェック
        if user is None:
            error = MESSAGE_AUTH_USERNAME_VALID_CHK
        elif not check_password_hash(user["password"], password):
            error = MESSAGE_AUTH_PASSWORD_VALID_CHK

        #ユーザー id 取得
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


#ログアウトボタン処理
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))