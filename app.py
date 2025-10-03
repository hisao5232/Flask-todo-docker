import os
from flask import Flask, render_template_string, request, redirect
from models import db, Todo  # db とモデルをここからインポート

app = Flask(__name__)

# 環境変数から MySQL 接続情報を取得
db_user = os.getenv("MYSQL_USER", "root")
db_pass = os.getenv("MYSQL_PASSWORD", "")
db_host = os.getenv("DB_HOST", "mysql_db")  # docker-compose のサービス名
db_name = os.getenv("MYSQL_DATABASE", "todo_db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:3306/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db を Flask アプリにバインド（ここで初期化）
db.init_app(app)

# シンプルなテンプレート
TEMPLATE = """
<!doctype html>
<title>TODO App</title>
<h1>TODO List</h1>
<form method="post" action="/add">
  <input type="text" name="task" placeholder="New task">
  <input type="submit" value="Add">
</form>
<ul>
{% for todo in todos %}
  <li>
    {{ todo.task }} {% if todo.done %}(done){% endif %}
    <a href="/done/{{todo.id}}">[done]</a>
    <a href="/delete/{{todo.id}}">[delete]</a>
  </li>
{% endfor %}
</ul>
"""

@app.route("/")
def index():
    todos = Todo.query.all()
    return render_template_string(TEMPLATE, todos=todos)

@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task")
    if task:
        new_todo = Todo(task=task)
        db.session.add(new_todo)
        db.session.commit()
    return redirect("/")

@app.route("/done/<int:todo_id>")
def done(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        todo.done = True
        db.session.commit()
    return redirect("/")

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
