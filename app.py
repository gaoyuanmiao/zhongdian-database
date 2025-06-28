from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FILES_DIR = os.path.join(BASE_DIR, 'files')

DATABASE_CSV = os.path.join(DATA_DIR, '数据库.csv')
LITERATURE_CSV = os.path.join(DATA_DIR, '资料库.csv')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

def load_data(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path, encoding='utf-8-sig').fillna('')

def save_data(df, path):
    df.to_csv(path, index=False, encoding='utf-8-sig')

def list_files():
    return set(os.listdir(FILES_DIR))

#####################
# 首页
#####################
@app.route('/')
def index():
    return render_template('index.html')

#####################
# 文件下载
#####################
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(FILES_DIR, filename, as_attachment=True)

#####################
# 数据库
#####################
@app.route('/database')
def database():
    df = load_data(DATABASE_CSV)
    data = df.to_dict(orient='records')
    existing_files = list_files()
    return render_template('database.html', data=data, existing_files=existing_files)

@app.route('/update_database', methods=['POST'])
def update_database():
    index = int(request.form['index'])
    column = request.form['column']
    value = request.form['value']

    df = load_data(DATABASE_CSV)
    if index < len(df):
        df.at[index, column] = value
        save_data(df, DATABASE_CSV)
        flash(f'已更新第{index + 1}行的{column}')
    return redirect(url_for('database'))

@app.route('/upload_database', methods=['POST'])
def upload_database():
    if 'file' not in request.files or 'target_name' not in request.form:
        flash('没有收到文件或目标文件名')
        return redirect(url_for('database'))

    uploaded_file = request.files['file']
    target_name = request.form['target_name']

    if uploaded_file.filename and target_name:
        uploaded_file.save(os.path.join(FILES_DIR, target_name))
        flash(f'上传成功：{target_name}')
    else:
        flash('上传失败，请检查文件名和目标名')

    return redirect(url_for('database'))

@app.route('/delete_database_row', methods=['POST'])
def delete_database_row():
    index = int(request.form['index'])
    df = load_data(DATABASE_CSV)
    if index < len(df):
        df = df.drop(index).reset_index(drop=True)
        df['序号'] = [str(i+1) for i in range(len(df))]
        save_data(df, DATABASE_CSV)
        flash(f'已删除第{index + 1}行')
    return redirect(url_for('database'))

#####################
# 资料库
#####################
@app.route('/literature')
def literature():
    df = load_data(LITERATURE_CSV)
    data = df.to_dict(orient='records')
    existing_files = list_files()
    return render_template('literature.html', data=data, existing_files=existing_files)

@app.route('/update_literature', methods=['POST'])
def update_literature():
    index = int(request.form['index'])
    column = request.form['column']
    value = request.form['value']

    df = load_data(LITERATURE_CSV)
    if index < len(df):
        df.at[index, column] = value
        save_data(df, LITERATURE_CSV)
        flash(f'已更新第{index + 1}行的{column}')
    return redirect(url_for('literature'))

@app.route('/upload_literature', methods=['POST'])
def upload_literature():
    if 'file' not in request.files or 'index' not in request.form:
        flash('没有收到文件或索引')
        return redirect(url_for('literature'))

    uploaded_file = request.files['file']
    index = int(request.form['index'])

    if uploaded_file.filename == '':
        flash('没有选择文件')
        return redirect(url_for('literature'))

    saved_name = uploaded_file.filename
    uploaded_file.save(os.path.join(FILES_DIR, saved_name))

    df = load_data(LITERATURE_CSV)
    if index < len(df):
        df.at[index, 'FileName'] = saved_name
        save_data(df, LITERATURE_CSV)
        flash(f'上传成功，并已更新文件名为：{saved_name}')
    else:
        flash('上传成功，但索引有误，无法写入记录')

    return redirect(url_for('literature'))

@app.route('/add_literature_row', methods=['POST'])
def add_literature_row():
    df = load_data(LITERATURE_CSV)
    if df.empty:
        flash('表结构无效，无法新增')
        return redirect(url_for('literature'))
    new_row = {col: '' for col in df.columns}
    new_row['序号'] = str(len(df) + 1)
    df.loc[len(df)] = new_row
    save_data(df, LITERATURE_CSV)
    flash('已添加一行')
    return redirect(url_for('literature'))

@app.route('/delete_literature_row', methods=['POST'])
def delete_literature_row():
    index = int(request.form['index'])
    df = load_data(LITERATURE_CSV)
    if index < len(df):
        df = df.drop(index).reset_index(drop=True)
        df['序号'] = [str(i+1) for i in range(len(df))]
        save_data(df, LITERATURE_CSV)
        flash(f'已删除第{index + 1}行')
    return redirect(url_for('literature'))

#####################
# 运行
#####################
if __name__ == '__main__':
    app.run(debug=True)
