import sqlite3

import click
from flask import current_app
from flask import g

"""
設定済みDBへの接続
リクエスト毎に固有
"""
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

#接続終了
def close_db(e=None):
    db = g.pop("db",None)

    if db is not None:
        db.close()

#DB初期化
def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("データベース初期化完了")

#sqliteとpython のデータタイム型変換
#現状データタイム使ってないので一旦コメントアウト
# sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)