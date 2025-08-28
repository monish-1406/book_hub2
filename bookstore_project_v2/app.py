from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secretkey"
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

# Ensure uploads folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price TEXT NOT NULL,
            image TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- UTILITY ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def get_all_books():
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    conn.close()
    books = []
    for r in rows:
        books.append({
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "price": r[3],
            "image": r[4]
        })
    return books

def add_book(title, description, price, image):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, description, price, image) VALUES (?, ?, ?, ?)",
                   (title, description, price, image))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/buy')
def buy():
    books = get_all_books()
    return render_template('buy.html', books=books)

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        file = request.files.get('image')
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        add_book(title, description, price, filename)
        return redirect(url_for('buy'))
    return render_template('sell.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "monish" and password == "2779":
            session['admin'] = True
            return redirect(url_for('dashboard'))
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    books = get_all_books()
    return render_template('dashboard.html', books=books)

@app.route('/delete/<int:book_id>')
def delete(book_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    delete_book(book_id)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
