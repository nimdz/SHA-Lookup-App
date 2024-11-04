from flask import Flask, render_template, request, redirect, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key for production use
DB_PATH = 'database/hashes.db'


# Connect to database
def get_db_connection():
    conn = sqlite3.connect('database/hashes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_input TEXT NOT NULL,
                sha_hash TEXT NOT NULL UNIQUE
            )
        ''')
    print("Database initialized")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add():
    original_input = request.form['original_input']
    sha_hash = hashlib.sha256(original_input.encode()).hexdigest()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO hashes (original_input, sha_hash) VALUES (?, ?)', (original_input, sha_hash))
            conn.commit()
        flash(f'Input "{original_input}" has been hashed and stored.', 'success')
    except sqlite3.IntegrityError:
        flash('This input already exists in the database.', 'warning')
    return redirect('/')


@app.route('/lookup', methods=['POST'])
def lookup():
    sha_hash = request.form['sha_hash']
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT original_input FROM hashes WHERE sha_hash = ?', (sha_hash,))
        result = cursor.fetchone()

    if result:
        flash(f'Original input for the given hash is: {result[0]}', 'success')
    else:
        flash('No match found for the provided SHA hash.', 'danger')
    return redirect('/')

# Route to view all data in the database
@app.route('/view')
def view():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM hashes').fetchall()
    conn.close()
    return render_template('view.html', data=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
