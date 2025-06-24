import sqlite3
import random
import string
from flask import Flask, render_template, request, redirect, g, url_for

app = Flask(__name__)
DATABASE = 'urls.db'

# ---------- DB Connection ----------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        try:
            db.execute("ALTER TABLE urls ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except:
            pass
        try:
            db.execute("ALTER TABLE urls ADD COLUMN clicks INTEGER DEFAULT 0")
        except:
            pass
        db.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short TEXT UNIQUE,
                long TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
        ''')
        db.commit()

# ---------- Short Code Generator ----------
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ---------- Home + URL Shortener ----------
@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    short_url = None

    if request.method == "POST":
        long_url = request.form["long_URL"].strip()
        short_code = generate_short_code()
        while db.execute("SELECT 1 FROM urls WHERE short = ?", (short_code,)).fetchone():
            short_code = generate_short_code()

        db.execute("INSERT INTO urls (short, long) VALUES (?, ?)", (short_code, long_url))
        db.commit()
        short_url = request.url_root + short_code

    urls = db.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
    return render_template("index4.html", short_url=short_url, urls=urls)

# ---------- Redirection ----------
@app.route("/<short_code>")
def redirect_to_long(short_code):
    db = get_db()
    result = db.execute("SELECT * FROM urls WHERE short = ?", (short_code,)).fetchone()
    if result:
        db.execute("UPDATE urls SET clicks = clicks + 1 WHERE short = ?", (short_code,))
        db.commit()
        return redirect(result["long"])
    return "URL not found", 404

# ---------- Erase One ----------
@app.route("/erase", methods=["POST"])
def erase_url():
    short_url = request.form.get("short_url")
    if short_url:
        short_code = short_url.strip().split("/")[-1]
        db = get_db()
        db.execute("DELETE FROM urls WHERE short = ?", (short_code,))
        db.commit()
    return redirect("/")

# ---------- Clear All ----------
@app.route("/clear_all", methods=["POST"])
def clear_all():
    db = get_db()
    db.execute("DELETE FROM urls")
    db.commit()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
