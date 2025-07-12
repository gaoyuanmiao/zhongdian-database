from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# =============== PATH ================
BASE_PERSISTENT = 'persistent'
DB_PATH = os.path.join(BASE_PERSISTENT, 'database.db')
FILES_DIR = os.path.join(BASE_PERSISTENT, 'files')
LITERATURE_FILES_DIR = os.path.join(BASE_PERSISTENT, 'literature_files')

# 确保文件夹存在
os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(LITERATURE_FILES_DIR, exist_ok=True)

# =============== DB INIT ================
def init_db():
    os.makedirs(BASE_PERSISTENT, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 课题三数据库表
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

    # 资料库表
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


# =============== HOME PAGE ================
@app.route('/')
def index():
    return render_template('index.html')


# =============== DATABASE 功能 ================
@app.route('/database')
def database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM database_entries')
    rows = c.fetchall()
    conn.close()
    return render_template('database.html', entries=rows)

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
    flash('已新增条目')
    return redirect(url_for('database'))

@app.route('/upload_database_file/<int:entry_id>', methods=['POST'])
def upload_database_file(entry_id):
    file = request.files['file']
    if file:
        filename = f"{entry_id}_{file.filename}"
        file.save(os.path.join(FILES_DIR, filename))

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE database_entries SET filename = ? WHERE id = ?', (filename, entry_id))
        conn.commit()
        conn.close()
        flash('文件已上传')
    return redirect(url_for('database'))

@app.route('/delete_database_file/<int:entry_id>', methods=['POST'])
def delete_database_file(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename FROM database_entries WHERE id = ?', (entry_id,))
    result = c.fetchone()
    if result and result[0]:
        filepath = os.path.join(FILES_DIR, result[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        c.execute('UPDATE database_entries SET filename = NULL WHERE id = ?', (entry_id,))
        conn.commit()
    conn.close()
    flash('文件已删除')
    return redirect(url_for('database'))

@app.route('/delete_database_entry/<int:entry_id>', methods=['POST'])
def delete_database_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename FROM database_entries WHERE id = ?', (entry_id,))
    result = c.fetchone()
    if result and result[0]:
        filepath = os.path.join(FILES_DIR, result[0])
        if os.path.exists(filepath):
            os.remove(filepath)
    c.execute('DELETE FROM database_entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    flash('条目已删除')
    return redirect(url_for('database'))


# =============== LITERATURE 功能 ================
@app.route('/literature')
def literature():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM literature_entries')
    rows = c.fetchall()
    conn.close()
    return render_template('literature.html', entries=rows)

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
    flash('已新增文献条目')
    return redirect(url_for('literature'))

@app.route('/upload_literature_file/<int:entry_id>', methods=['POST'])
def upload_literature_file(entry_id):
    file = request.files['file']
    if file:
        filename = f"{entry_id}_{file.filename}"
        file.save(os.path.join(LITERATURE_FILES_DIR, filename))

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE literature_entries SET filename = ? WHERE id = ?', (filename, entry_id))
        conn.commit()
        conn.close()
        flash('文献文件已上传')
    return redirect(url_for('literature'))

@app.route('/delete_literature_file/<int:entry_id>', methods=['POST'])
def delete_literature_file(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename FROM literature_entries WHERE id = ?', (entry_id,))
    result = c.fetchone()
    if result and result[0]:
        filepath = os.path.join(LITERATURE_FILES_DIR, result[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        c.execute('UPDATE literature_entries SET filename = NULL WHERE id = ?', (entry_id,))
        conn.commit()
    conn.close()
    flash('文献文件已删除')
    return redirect(url_for('literature'))

@app.route('/delete_literature_entry/<int:entry_id>', methods=['POST'])
def delete_literature_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename FROM literature_entries WHERE id = ?', (entry_id,))
    result = c.fetchone()
    if result and result[0]:
        filepath = os.path.join(LITERATURE_FILES_DIR, result[0])
        if os.path.exists(filepath):
            os.remove(filepath)
    c.execute('DELETE FROM literature_entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    flash('文献条目已删除')
    return redirect(url_for('literature'))


# =============== DOWNLOAD ================
@app.route('/download_database/<path:filename>')
def download_database_file(filename):
    return send_from_directory(FILES_DIR, filename, as_attachment=True)

@app.route('/download_literature/<path:filename>')
def download_literature_file(filename):
    return send_from_directory(LITERATURE_FILES_DIR, filename, as_attachment=True)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
