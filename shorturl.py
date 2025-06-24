from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import string
import random
from datetime import datetime

app = Flask(__name__)

def init_db():
    with sqlite3.connect("urls.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                long_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    db = sqlite3.connect("urls.db")
    db.row_factory = sqlite3.Row

    if request.method == 'POST':
        long_url = request.form.get("long_URL")
        if long_url:
            short_code = generate_short_code()
            db.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
            db.commit()
            short_url = request.host_url + short_code
            urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
            return render_template("index.html", short_url=short_url, urls=urls)

    urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
    return render_template("index.html", urls=urls)

@app.route('/<short_code>')
def redirect_url(short_code):
    db = sqlite3.connect("urls.db")
    db.row_factory = sqlite3.Row
    result = db.execute("SELECT long_url, clicks FROM urls WHERE short_code = ?", (short_code,)).fetchone()
    if result:
        db.execute("UPDATE urls SET clicks = ? WHERE short_code = ?", (result["clicks"] + 1, short_code))
        db.commit()
        return redirect(result["long_url"])
    return redirect('/')

@app.route('/delete/<int:url_id>', methods=['POST'])
def delete_url(url_id):
    with sqlite3.connect("urls.db") as db:
        db.execute("DELETE FROM urls WHERE id = ?", (url_id,))
        db.commit()
    return redirect(url_for('index'))

@app.route('/erase', methods=['POST'])
def erase_all():
    with sqlite3.connect("urls.db") as db:
        db.execute("DELETE FROM urls")
        db.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
