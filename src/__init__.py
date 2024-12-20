import os
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    #アプリ設定
    app.config.from_mapping(
        #仮の秘密鍵
        SECRET_KEY="dev",
        #データベースのパス設定
        DATABASE=os.path.join(app.instance_path, "todo.sqlite"),
    )

    #config読み取り設定
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    #DB格納ディレクトリ作成
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #データベース初期化
    from . import db

    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp) #認証機能 登録

    from . import todo
    app.register_blueprint(todo.bp) #アプリ全体 登録
  
    app.add_url_rule("/", endpoint="index")
    return app
