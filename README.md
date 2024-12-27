## 説明
練習用のflask ToDoアプリ

## 使い方
データベース初期化
flask --app src init-db

実行
flask --app src --debug run

テスト
pytest

カバレッジ計測
coverage run -m pytest

HTMLファイル出力
coverage html