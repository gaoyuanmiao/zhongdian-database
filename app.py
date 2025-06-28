from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your-super-secret-key'  # 任何非空字符串都行，用来支持flash消息

# 自动适配本地路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FILES_DIR = os.path.join(BASE_DIR, 'files')

def load_csv(filename):
    """读取CSV并返回DataFrame"""
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path, encoding='utf-8-sig').fillna('')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/database')
def database():
    try:
        df = load_csv('数据库.csv')

        # 自动适配「文件名或链接」列 → 统一为 FileName
        if '文件名或链接' in df.columns and 'FileName' not in df.columns:
            df = df.rename(columns={'文件名或链接': 'FileName'})

        data = df.to_dict(orient='records')
    except Exception as e:
        flash(f'读取数据库出错: {e}')
        data = []

    # 获取files目录下所有已上传的文件名
    existing_files = set()
    if os.path.exists(FILES_DIR):
        existing_files = set(os.listdir(FILES_DIR))

    return render_template('database.html', data=data, existing_files=existing_files)

@app.route('/literature')
def literature():
    data = load_csv('资料库.csv').to_dict(orient='records')
    return render_template('literature.html', data=data)

@app.route('/tools')
def tools():
    data = load_csv('工具库.csv').to_dict(orient='records')
    return render_template('tools.html', data=data)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(FILES_DIR, filename, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'target_name' not in request.form:
        flash('没有收到文件或目标文件名')
        return redirect(url_for('database'))

    uploaded_file = request.files['file']
    target_name = request.form['target_name'].strip()

    if uploaded_file.filename == '':
        flash('没有选择文件')
        return redirect(url_for('database'))

    if not target_name or target_name.lower() in ['请上传', '-']:
        flash('没有指定有效的保存文件名，请检查表格配置。')
        return redirect(url_for('database'))

    # 保存文件，覆盖
    try:
        if not os.path.exists(FILES_DIR):
            os.makedirs(FILES_DIR)
        uploaded_file.save(os.path.join(FILES_DIR, target_name))
        flash(f'上传成功，已保存为：{target_name}')
    except Exception as e:
        flash(f'上传失败：{e}')

    return redirect(url_for('database'))

@app.route('/update_note', methods=['POST'])
def update_note():
    row_id = request.form.get('序号')
    new_note = request.form.get('new_note')

    if not row_id or new_note is None:
        flash('请填写完整的信息')
        return redirect(url_for('database'))

    try:
        path = os.path.join(DATA_DIR, '数据库.csv')
        df = pd.read_csv(path, encoding='utf-8-sig').fillna('')
        df.loc[df['序号'] == int(row_id), '时空分辨率/备注'] = new_note
        df.to_csv(path, index=False, encoding='utf-8-sig')
        flash(f'序号 {row_id} 的时空分辨率/备注 已更新成功！')
    except Exception as e:
        flash(f'更新失败：{e}')

    return redirect(url_for('database'))

if __name__ == '__main__':
    app.run(debug=True)
