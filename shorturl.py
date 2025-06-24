import os
import sqlite3
import string
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = 'urls.db'

# ✅ Ensure database and table exist
def init_db():
    with sqlite3.connect(DB_NAME) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            long_url TEXT NOT NULL,
            short_code TEXT NOT NULL UNIQUE,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

init_db()

# ✅ Generate short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    db = sqlite3.connect(DB_NAME)
    db.row_factory = sqlite3.Row

    if request.method == 'POST':
        long_url = request.form['long_URL']
        short_code = generate_short_code()
        
        while db.execute("SELECT 1 FROM urls WHERE short_code=?", (short_code,)).fetchone():
            short_code = generate_short_code()

        db.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
        db.commit()

        short_url = request.host_url + short_code
        urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
        return render_template("index.html", short_url=short_url, urls=urls)

    urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
    return render_template("index.html", urls=urls)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    db = sqlite3.connect(DB_NAME)
    result = db.execute("SELECT * FROM urls WHERE short_code=?", (short_code,)).fetchone()
    
    if result:
        db.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code=?", (short_code,))
        db.commit()
        return redirect(result[1])
    return "URL not found", 404

@app.route('/delete/<int:url_id>', methods=['POST'])
def delete_url(url_id):
    db = sqlite3.connect(DB_NAME)
    db.execute("DELETE FROM urls WHERE id=?", (url_id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_all():
    db = sqlite3.connect(DB_NAME)
    db.execute("DELETE FROM urls")
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
