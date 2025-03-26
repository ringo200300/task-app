from flask import Flask, render_template_string, request, redirect, session, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

CSV_FILE = "tasks.csv"

USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "user": {"password": "userpass", "role": "user"}
}

class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user = USERS.get(user_id)
    if user:
        return User(user_id, user["role"])
    return None

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["業務内容", "分類", "AI代替", "ステータス", "締切", "登録者", "更新者"])

init_csv()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = request.form["username"]
        pw = request.form["password"]
        user = USERS.get(uid)
        if user and user["password"] == pw:
            login_user(User(uid, user["role"]))
            return redirect("/")
    return render_template_string("""
        <h2>ログイン</h2>
        <form method="POST">
            <input name="username" placeholder="ユーザー名" required><br>
            <input name="password" type="password" placeholder="パスワード" required><br>
            <button type="submit">ログイン</button>
        </form>
    """)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        task = request.form["task"]
        deadline = request.form.get("deadline", "")
        category = "ノンコア" if "入力" in task or "整理" in task or "部品" in task else "コア"
        ai_flag = "可能" if "メール" in task or "表作成" in task else "不可"
        status = "未着手"
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([task, category, ai_flag, status, deadline, current_user.id, ""])
        return redirect("/")

    tasks = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            tasks.append(row)

    return render_template_string("""
        <style>
            body { font-family: sans-serif; max-width: 800px; margin: auto; padding: 1rem; }
            input, button { padding: 5px; margin: 5px; width: 100%%; }
            table { width: 100%%; border-collapse: collapse; }
            th, td { border: 1px solid #ccc; padding: 4px; text-align: left; }
            @media (max-width: 600px) {
                table, thead, tbody, th, td, tr { display: block; }
                td { margin-bottom: 10px; }
            }
        </style>
        <h2>タスク登録（ようこそ {{ current_user.id }} さん）</h2>
        <form method="POST">
            <input name="task" placeholder="業務内容" required>
            <input name="deadline" type="date">
            <button type="submit">登録</button>
        </form>
        <h3>登録済みタスク</h3>
        <table>
            <tr><th>業務内容</th><th>分類</th><th>AI代替</th><th>ステータス</th><th>締切</th><th>登録者</th><th>更新者</th></tr>
            {% for row in tasks %}
            <tr>{% for col in row %}<td>{{ col }}</td>{% endfor %}</tr>
            {% endfor %}
        </table>
        <p><a href="/logout">ログアウト</a></p>
    """, tasks=tasks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
