DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS task;

--ユーザー情報
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

--リストの課題
CREATE TABLE task(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  is_done BOOLEAN,
  FOREIGN KEY (author_id) REFERENCES user (id)
);