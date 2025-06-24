import sqlite3
import string
import random
from flask import Flask, render_template, request, redirect, g, url_for
from datetime import datetime

app = Flask(__name__)
DATABASE = 'urls.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short TEXT UNIQUE NOT NULL,
            long TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()

def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    db = get_db()

    if request.method == 'POST':
        long_url = request.form.get('long_URL')
        short_url = generate_short_url()
        while db.execute("SELECT 1 FROM urls WHERE short=?", (short_url,)).fetchone():
            short_url = generate_short_url()
        db.execute("INSERT INTO urls (short, long) VALUES (?, ?)", (short_url, long_url))
        db.commit()
        return redirect(url_for('index'))

    urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
    return render_template("index4.html", urls=urls)

@app.route("/<short_url>")
def redirect_url(short_url):
    db = get_db()
    row = db.execute("SELECT long FROM urls WHERE short=?", (short_url,)).fetchone()
    if row:
        db.execute("UPDATE urls SET clicks = clicks + 1 WHERE short=?", (short_url,))
        db.commit()
        return redirect(row["long"])
    return "URL not found", 404

@app.route("/delete/<int:url_id>", methods=["POST"])
def delete_url(url_id):
    db = get_db()
    db.execute("DELETE FROM urls WHERE id=?", (url_id,))
    db.commit()
    return redirect(url_for("index"))

@app.route("/clear", methods=["POST"])
def clear_all():
    db = get_db()
    db.execute("DELETE FROM urls")
    db.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
