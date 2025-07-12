import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Persistent storage path
BASE_PERSISTENT = 'persistent'
DB_PATH = os.path.join(BASE_PERSISTENT, 'database.db')
FILES_PATH = os.path.join(BASE_PERSISTENT, 'files')

# Ensure folders exist
os.makedirs(FILES_PATH, exist_ok=True)

# ------------- DB INIT -------------
def init_db():
    os.makedirs(BASE_PERSISTENT, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Table for Database entries
    c.execute('''
        CREATE TABLE IF NOT EXISTS database_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_name TEXT,
            data_type TEXT,
            is_available TEXT,
            resolution_remark TEXT,
            filename TEXT
        )
    ''')

    # Table for Literature entries
    c.execute('''
        CREATE TABLE IF NOT EXISTS literature_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            type TEXT,
            author TEXT,
            note TEXT,
            filename TEXT
        )
    ''')

    conn.commit()
    conn.close()


# ------------- Routes -------------
@app.route('/')
def index():
    return render_template('index.html')


# ===========================
# DATABASE ROUTES
# ===========================

@app.route('/database')
def database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM database_entries')
    entries = c.fetchall()
    conn.close()
    return render_template('database.html', entries=entries)


@app.route('/add_database_row', methods=['POST'])
def add_database_row():
    region_name = request.form['region_name']
    data_type = request.form['data_type']
    is_available = request.form['is_available']
    resolution_remark = request.form['resolution_remark']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO database_entries (region_name, data_type, is_available, resolution_remark, filename)
        VALUES (?, ?, ?, ?, ?)
    ''', (region_name, data_type, is_available, resolution_remark, None))
    conn.commit()
    conn.close()
    flash('条目已添加。')
    return redirect(url_for('database'))


@app.route('/upload_database_file/<int:entry_id>', methods=['POST'])
def upload_database_file(entry_id):
    if 'file' not in request.files:
        flash('没有选择文件')
        return redirect(url_for('database'))

    file = request.files['file']
    if file.filename == '':
        flash('文件名为空')
        return redirect(url_for('database'))

    save_name = f"db_{entry_id}_{file.filename}"
    file.save(os.path.join(FILES_PATH, save_name))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE database_entries SET filename = ? WHERE id = ?', (save_name, entry_id))
    conn.commit()
    conn.close()

    flash('文件上传成功')
    return redirect(url_for('database'))


@app.route('/download_database_file/<path:filename>')
def download_database_file(filename):
    return send_from_directory(FILES_PATH, filename, as_attachment=True)


@app.route('/delete_database_file/<int:entry_id>', methods=['POST'])
def delete_database_file(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename FROM database_entries WHERE id = ?', (entry_id,))
    row = c.fetchone()
    if row and row[0]:
        try:
            os.remove(os.path.join(FILES_PATH, row[0]))
        except FileNotFoundError:
            pass
        c.execute('UPDATE database_entries SET filename = NULL WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    flash('文件已删除')
    return redirect(url_for('database'))


@app.route('/delete_database_entry/<int:entry_id>', methods=['POST'])
def delete_database_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM database_entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    flash('条目已删除')
    return redirect(url_for('database'))


# ===========================
# LITERATURE ROUTES
# ===========================

@app.route('/literature')
def literature():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM literature_entries')
    entries = c.fetchall()
    conn.close()
    return render_template('literature.html', entries=entries)


@app.route('/add_literature_row', methods=['POST'])
def add_literature_row():
    title = request.form['title']
    type_ = request.form['type']
    author = request.form['author']
    note = request.form['note']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO literature_entries (title, type, author, note, filename)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, type_, author, note, None))
    conn.commit()
    conn.close()
    flash('文献条目已添加。')
    return redirect(url_for('literature'))


@app.route('/upload_literature_file/<int:entry_id>', methods=['POST'])
def upload_literature_file(entry_id):
    if 'file' not in request.files:
        flash('没有选择文件')
        return redirect(url_for('literature'))

    file = request.files['file']
    if file.filename == '':
        flash('文件名为空')
        return redirect(url_for('literature'))

    save_name = f"lit_{entry_id}_{file.filename}"
    file.save(os.path.join(FILES_PATH, save_name))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE literature_entries SET filename = ? WHERE id = ?', (save_name, entry_id))
    conn.commit()
    conn.close()

    flash('文件上传成功')
    return redirect(url_for('literature'))


@app.route('/download_literature_file/<path:filename>')
def download_literature_file(filename):
    return send_from_directory(FILES_PATH, filename, as_attachment=True)


@app.route('/delete_literature_file/<int:entry_id>', methods=['POST'])
def delete_literature_file(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename FROM literature_entries WHERE id = ?', (entry_id,))
    row = c.fetchone()
    if row and row[0]:
        try:
            os.remove(os.path.join(FILES_PATH, row[0]))
        except FileNotFoundError:
            pass
        c.execute('UPDATE literature_entries SET filename = NULL WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    flash('文件已删除')
    return redirect(url_for('literature'))


@app.route('/delete_literature_entry/<int:entry_id>', methods=['POST'])
def delete_literature_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM literature_entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    flash('条目已删除')
    return redirect(url_for('literature'))


# ===========================
# App Start
# ===========================

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
