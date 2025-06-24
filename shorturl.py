from flask import Flask, render_template, request, redirect
import sqlite3
import random
import string
import os

app = Flask(__name__)

# Initialize database and create table if not exists
def init_db():
    with sqlite3.connect("urls.db") as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                long_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
        """)
        db.commit()

init_db()

# Generate short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    db = sqlite3.connect("urls.db")
    db.row_factory = sqlite3.Row

    if request.method == 'POST':
        long_url = request.form['long_URL']
        short_code = generate_short_code()

        while db.execute("SELECT 1 FROM urls WHERE short_code = ?", (short_code,)).fetchone():
            short_code = generate_short_code()

        db.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
        db.commit()
        short_url = request.url_root + short_code
        urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
        return render_template("index.html", short_url=short_url, urls=urls)

    urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
    return render_template("index.html", short_url=None, urls=urls)

# Redirect shortened URL
@app.route('/<short_code>')
def redirect_short_url(short_code):
    db = sqlite3.connect("urls.db")
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()

    if row:
        db.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,))
        db.commit()
        return redirect(row['long_url'])
    else:
        return "URL not found", 404

# Delete one URL
@app.route('/delete/<int:id>', methods=['POST'])
def delete_url(id):
    with sqlite3.connect("urls.db") as db:
        db.execute("DELETE FROM urls WHERE id = ?", (id,))
        db.commit()
    return redirect('/')

# Erase all
@app.route('/delete_all', methods=['POST'])
def delete_all():
    with sqlite3.connect("urls.db") as db:
        db.execute("DELETE FROM urls")
        db.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
