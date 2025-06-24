import os
import sqlite3
import string
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_FILE = "urls.db"

# ✅ Ensure table is created
def init_db():
    with sqlite3.connect(DB_FILE) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_url TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

init_db()

# ✅ Generate short code
def generate_short_url(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


@app.route("/", methods=["GET", "POST"])
def index():
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row

    if request.method == "POST":
        long_url = request.form["long_URL"]
        short_url = generate_short_url()
        while db.execute("SELECT * FROM urls WHERE short_url = ?", (short_url,)).fetchone():
            short_url = generate_short_url()

        db.execute("INSERT INTO urls (short_url, long_url) VALUES (?, ?)", (short_url, long_url))
        db.commit()

        full_short_url = request.url_root + short_url
        urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
        return render_template("index4.html", short_url=full_short_url, urls=urls)

    urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
    return render_template("index4.html", short_url=None, urls=urls)


@app.route("/<short_url>")
def redirect_url(short_url):
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT long_url FROM urls WHERE short_url = ?", (short_url,)).fetchone()
    if row:
        db.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_url = ?", (short_url,))
        db.commit()
        return redirect(row["long_url"])
    return "URL not found", 404


@app.route("/delete/<short_url>", methods=["POST"])
def delete_url(short_url):
    db = sqlite3.connect(DB_FILE)
    db.execute("DELETE FROM urls WHERE short_url = ?", (short_url,))
    db.commit()
    return redirect(url_for("index"))


@app.route("/clear", methods=["POST"])
def clear_all():
    db = sqlite3.connect(DB_FILE)
    db.execute("DELETE FROM urls")
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
