import os
import sqlite3
import secrets
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

DATABASE = os.path.join(app.root_path, "app.db")

# --------------- Azure OpenAI client ---------------
ai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
)
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.2")

# --------------- Database helpers ---------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS fortunes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)
    db.close()


# --------------- Auth decorator ---------------

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# --------------- Routes ---------------

@app.route("/")
@login_required
def index():
    db = get_db()
    rows = db.execute(
        "SELECT question, answer, created_at FROM fortunes "
        "WHERE user_id = ? ORDER BY id DESC LIMIT 30",
        (session["user_id"],),
    ).fetchall()
    return render_template("index.html", history=rows)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("用户名和密码不能为空。", "danger")
            return redirect(url_for("register"))
        db = get_db()
        if db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
            flash("用户名已存在。", "danger")
            return redirect(url_for("register"))
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
        flash("注册成功，请登录。", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        flash("用户名或密码错误。", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/divine", methods=["POST"])
@login_required
def divine():
    data = request.get_json(force=True)
    question = (data.get("question") or "").strip()
    birth_info = (data.get("birth_info") or "").strip()
    if not question:
        return jsonify(error="请输入您的问题。"), 400

    prompt = f"你是一位精通易经、八卦、紫微斗数和塔罗牌的算命大师。用户的问题如下：\n{question}"
    if birth_info:
        prompt += f"\n用户提供的出生信息：{birth_info}"
    prompt += "\n请给出详细的占卜结果，用通俗易懂的中文回答，可以适当使用 emoji 增添趣味。"

    try:
        resp = ai_client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "你是一位专业的算命大师，回答风格神秘而有趣。"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1024,
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        return jsonify(error=f"AI 服务调用失败：{e}"), 502

    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO fortunes (user_id, question, answer, created_at) VALUES (?, ?, ?, ?)",
        (session["user_id"], question, answer, now),
    )
    db.commit()
    return jsonify(answer=answer, created_at=now)


# --------------- Main ---------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
