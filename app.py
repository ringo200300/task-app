from flask import Flask, request, redirect, render_template_string
import csv
from datetime import datetime
import os

app = Flask(__name__)
CSV_FILE = "tasks.csv"

# 初期化
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["業務内容", "分類", "AI代替", "ステータス", "締切", "更新者", "AI実行結果", "AI実行日時"])

init_csv()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        task = request.form["task"]
        category = "ノンコア" if "資料" in task or "整理" in task else "コア"
        ai_possible = "可能" if "メール" in task or "表作成" in task else "不可"
        deadline = request.form.get("deadline", "")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([task, category, ai_possible, "未着手", deadline, "未更新", "", ""])
        return redirect("/")

    tasks = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            tasks.append(row)
    return render_template_string("""
        <h2>タスク登録</h2>
        <form method="POST">
            <input name="task" placeholder="業務内容" required>
            締切日: <input name="deadline" type="date">
            <button type="submit">追加</button>
        </form>
        <h3>登録済みタスク</h3>
        <table border=1>
            <tr>
                <th>業務内容</th><th>分類</th><th>AI代替</th><th>ステータス</th>
                <th>締切</th><th>更新者</th><th>AI実行結果</th><th>AI実行日時</th>
            </tr>
            {% for row in tasks %}
            <tr>{% for col in row %}<td>{{ col }}</td>{% endfor %}</tr>
            {% endfor %}
        </table>
    """, tasks=tasks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
