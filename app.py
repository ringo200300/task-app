from flask import Flask, request, redirect, render_template_string, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import csv
import os

app = Flask(__name__)
app.secret_key = 'secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

USER_CSV = 'users.csv'

# 初期ユーザー作成
if not os.path.exists(USER_CSV):
    with open(USER_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password", "role"])
        writer.writerow(["admin", "adminpass", "admin"])
        writer.writerow(["user", "userpass", "user"])

class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    with open(USER_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == user_id:
                return User(user_id, row["role"])
    return None

def get_all_users():
    users = []
    with open(USER_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = request.form["username"]
        pw = request.form["password"]
        with open(USER_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"] == uid and row["password"] == pw:
                    login_user(User(uid, row["role"]))
                    return redirect("/")
    return render_template_string("""
        <h2>ログイン</h2>
        <form method="POST">
            <input name="username" placeholder="ユーザー名"><br>
            <input name="password" type="password" placeholder="パスワード"><br>
            <button type="submit">ログイン</button>
        </form>
    """)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/admin/users", methods=["GET", "POST"])
@login_required
def manage_users():
    if current_user.role != "admin":
        return "アクセス権がありません"

    msg = ""
    if request.method == "POST":
        if "add_user" in request.form:
            new_user = request.form["new_user"]
            new_pass = request.form["new_pass"]
            new_role = request.form["new_role"]
            with open(USER_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([new_user, new_pass, new_role])
            msg = f"{new_user} を追加しました。"
        elif "delete_user" in request.form:
            del_user = request.form["delete_user"]
            rows = get_all_users()
            with open(USER_CSV, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["username", "password", "role"])
                writer.writeheader()
                for row in rows:
                    if row["username"] != del_user:
                        writer.writerow(row)
            msg = f"{del_user} を削除しました。"

    users = get_all_users()
    return render_template_string("""
        <h2>ユーザー管理（管理者専用）</h2>
        <p>{{ msg }}</p>
        <form method="POST">
            <h3>ユーザー追加</h3>
            <input name="new_user" placeholder="ユーザー名" required>
            <input name="new_pass" placeholder="パスワード" required>
            <select name="new_role">
                <option value="user">user</option>
                <option value="admin">admin</option>
            </select>
            <button name="add_user" type="submit">追加</button>
        </form>
        <h3>ユーザー一覧</h3>
        <ul>
            {% for u in users %}
                <li>{{ u.username }} ({{ u.role }}) 
                {% if u.username != 'admin' %}
                    <form method="POST" style="display:inline;">
                        <input type="hidden" name="delete_user" value="{{ u.username }}">
                        <button name="delete_btn" type="submit">削除</button>
                    </form>
                {% endif %}
                </li>
            {% endfor %}
        </ul>
        <a href="/">← タスク一覧へ</a>
    """, users=users, msg=msg)

@app.route("/")
@login_required
def home():
    return f"ようこそ、{current_user.id} さん！ <a href='/admin/users'>ユーザー管理</a> | <a href='/logout'>ログアウト</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
