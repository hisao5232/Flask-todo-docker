from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os, pymysql, time

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")  # セッション用

db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("MYSQL_USER")
db_password = os.getenv("MYSQL_PASSWORD")
db_name = os.getenv("MYSQL_DATABASE")
db_port = int(os.getenv("DB_PORT", 3306))

def get_conn():
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db(retries=5, delay=3):
    for i in range(retries):
        try:
            conn = get_conn()
            with conn.cursor() as cursor:
                # Todoテーブル
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    task VARCHAR(255) NOT NULL,
                    done BOOLEAN DEFAULT FALSE
                )
                """)
                # ユーザーテーブル
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
                """)
            conn.commit()
            conn.close()
            print("DB initialized successfully")
            return
        except pymysql.err.OperationalError as e:
            print(f"DB not ready, retrying in {delay}s... ({i+1}/{retries})")
            time.sleep(delay)
    print("DB Init failed after retries")


init_db()

# ---------- CRUD API ----------
@app.route("/todos", methods=["GET"])
def get_todos():
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM todos")
            todos = cursor.fetchall()
        conn.close()
        return jsonify(todos)
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.json
    task = data.get("task")
    if not task:
        return {"error": "task is required"}, 400
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO todos (task) VALUES (%s)", (task,))
        conn.commit()
        conn.close()
        return {"message": "Todo created"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.json
    done = data.get("done")
    if done is None:
        return {"error": "done is required"}, 400
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE todos SET done=%s WHERE id=%s", (done, todo_id))
        conn.commit()
        conn.close()
        return {"message": "Todo updated"}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM todos WHERE id=%s", (todo_id,))
        conn.commit()
        conn.close()
        return {"message": "Todo deleted"}
    except Exception as e:
        return {"error": str(e)}, 500

# ---------- HTML表示 ----------
@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("index.html", username=session.get("username"))

# ---------- 認証 ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            conn = get_conn()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                user = cursor.fetchone()
            conn.close()
            if user and check_password_hash(user["password"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("index"))
            else:
                return render_template("login.html", error="Invalid credentials")
        except Exception as e:
            return str(e)
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_pw = generate_password_hash(password)
        try:
            conn = get_conn()
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except pymysql.err.IntegrityError:
            return render_template("register.html", error="Username already exists")
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
