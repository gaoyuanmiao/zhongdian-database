from flask import Flask, render_template, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# 自动适配本地路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FILES_DIR = os.path.join(BASE_DIR, 'files')

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path, encoding='utf-8-sig').fillna('')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/database')
def database():
    data = load_csv('数据库.csv').to_dict(orient='records')
    return render_template('database.html', data=data)

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

if __name__ == '__main__':
    app.run(debug=True)
