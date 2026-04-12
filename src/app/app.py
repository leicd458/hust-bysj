#!/usr/bin/env python3
"""
Flask主应用
乳腺癌超声图像诊断系统
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os
from pathlib import Path

from config import *
from model_handler import ModelHandler

# 创建Flask应用
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = SECRET_KEY

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化模型处理器
print("\n" + "="*70)
print("初始化模型...")
print("="*70)
model_handler = ModelHandler(MODEL_PATH)
print("✓ 模型初始化完成\n")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """预测接口"""
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({'error': f'不支持的文件格式，支持: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    try:
        # 读取图像
        image = Image.open(file.stream).convert('RGB')
        
        # 分析图像
        result = model_handler.analyze(image)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'分析失败: {str(e)}'
        }), 500


@app.route('/health')
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'model': 'loaded'
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("启动乳腺癌超声图像诊断系统")
    print("="*70)
    print(f"访问地址: http://{HOST}:{PORT}")
    print("="*70 + "\n")
    
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )
