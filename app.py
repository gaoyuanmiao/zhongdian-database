from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'   # 为了Flash消息

# 持久化路径
BASE_PERSISTENT = '/persistent'
DB_PATH = os.path.join(BASE_PERSISTENT, 'database.db')
FILES_DIR = os.path.join(BASE_PERSISTENT, 'files')

# 保证持久目录存在
os.makedirs(BASE_PERSISTENT, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_name TEXT,
            data_type TEXT,
            is_available TEXT,
            resolution_remark TEXT,
            filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 主页：显示所有条目
@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM entries')
    rows = c.fetchall()
    conn.close()
    return render_template('entries.html', entries=rows)

# 新增条目
@app.route('/add', methods=['POST'])
def add_entry():
    region_name = request.form['region_name']
    data_type = request.form['data_type']
    is_available = request.form['is_available']
    resolution_remark = request.form['resolution_remark']
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO entries (region_name, data_type, is_available, resolution_remark, filename)
        VALUES (?, ?, ?, ?, ?)
    ''', (region_name, data_type, is_available, resolution_remark, None))
    conn.commit()
    conn.close()
    flash('条目已新增')
    return redirect(url_for('index'))

# 上传文件
@app.route('/upload/<int:entry_id>', methods=['POST'])
def upload_file(entry_id):
    file = request.files['file']
    if file:
        filename = f"{entry_id}_{file.filename}"
        file.save(os.path.join(FILES_DIR, filename))
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE entries SET filename = ? WHERE id = ?', (filename, entry_id))
        conn.commit()
        conn.close()
        flash('文件已上传')
    return redirect(url_for('index'))

# 下载文件
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(FILES_DIR, filename, as_attachment=True)

# 删除文件
@app.route('/delete_file/<int:entry_id>', methods=['POST'])
def delete_file(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename FROM entries WHERE id = ?', (entry_id,))
    result = c.fetchone()
    if result and result[0]:
        filepath = os.path.join(FILES_DIR, result[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        c.execute('UPDATE entries SET filename = NULL WHERE id = ?', (entry_id,))
        conn.commit()
    conn.close()
    flash('文件已删除')
    return redirect(url_for('index'))

# 删除条目
@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename FROM entries WHERE id = ?', (entry_id,))
    result = c.fetchone()
    if result and result[0]:
        filepath = os.path.join(FILES_DIR, result[0])
        if os.path.exists(filepath):
            os.remove(filepath)
    c.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    flash('条目已删除')
    return redirect(url_for('index'))

# 初始化数据库
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
