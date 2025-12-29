from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("todo.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            important INTEGER DEFAULT 0,
            assigned_to TEXT DEFAULT 'me'
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    view = request.args.get("view", "tasks")
    search = request.args.get("search", "")
    today = date.today().isoformat()

    conn = get_db()
    query = "SELECT * FROM tasks WHERE title LIKE ?"
    params = [f"%{search}%"]

    if view == "myday":
        query += " AND due_date = ?"
        params.append(today)
    elif view == "important":
        query += " AND important = 1"
    elif view == "planned":
        query += " AND due_date IS NOT NULL"
    elif view == "assigned":
        query += " AND assigned_to = 'me'"

    query += " ORDER BY id DESC"
    tasks = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("index.html", tasks=tasks, view=view, today=today, search=search)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    due_date = request.form.get("due_date")
    if title:
        conn = get_db()
        conn.execute("INSERT INTO tasks (title, due_date) VALUES (?, ?)", (title, due_date))
        conn.commit()
        conn.close()
    return redirect(request.referrer or "/")

@app.route("/toggle/<int:id>")
def toggle(id):
    conn = get_db()
    conn.execute("UPDATE tasks SET completed = 1-completed WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or "/")

@app.route("/important/<int:id>")
def important(id):
    conn = get_db()
    conn.execute("UPDATE tasks SET important = 1-important WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or "/")

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or "/")

if __name__ == "__main__":
    app.run(debug=True)
