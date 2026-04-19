#!/usr/bin/env python3
"""
Flask主应用
乳腺癌超声图像诊断系统

API 路由:
- GET  /                  首页
- POST /predict           标准预测（单图）
- POST /predict_tta       TTA 增强预测（单图，更准）
- POST /predict_batch     批量预测（多图）
- GET  /health            健康检查
- GET  /api/model_info    当前模型信息
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os
import time

from config import (
    MODEL_TYPE, MODEL_PATH, MODEL_META,
    UPLOAD_FOLDER, MAX_CONTENT_LENGTH, SECRET_KEY, ALLOWED_EXTENSIONS,
    HOST, PORT, DEBUG, allowed_file as _allowed_file, MAX_BATCH_FILES
)
from model_handler import ModelHandler

# 创建 Flask 应用
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = SECRET_KEY

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化模型
print("\n" + "="*70)
print("初始化模型...")
print("="*70)
model_handler = ModelHandler(MODEL_PATH)
print(f"模型初始化完成: {model_handler.model_type}\n")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """标准单图预测接口"""
    file = _get_file_from_request()
    if isinstance(file, tuple):
        return file  # 错误响应

    try:
        image = Image.open(file.stream).convert('RGB')
        result = model_handler.analyze(image, use_tta=False)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': f'分析失败: {str(e)}'}), 500


@app.route('/predict_tta', methods=['POST'])
def predict_tta():
    """TTA 增强预测接口（使用7种增强取平均，准确率更高）"""
    file = _get_file_from_request()
    if isinstance(file, tuple):
        return file

    try:
        t0 = time.time()
        image = Image.open(file.stream).convert('RGB')
        result = model_handler.analyze(image, use_tta=True)
        result['inference_time_ms'] = round((time.time() - t0) * 1000, 1)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': f'TTA分析失败: {str(e)}'}), 500


@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """批量图像预测接口
    
    支持一次上传多张图片，返回每个文件的诊断结果和统计摘要。
    """
    if 'files' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': '没有选择文件'}), 400

    # 限制数量
    valid_files = [f for f in files if f.filename and allowed_file(f.filename)]
    if len(valid_files) > MAX_BATCH_FILES:
        return jsonify({
            'error': f'最多支持{MAX_BATCH_FILES}张图片同时分析',
            'count': len(valid_files)
        }), 400

    results = []
    errors = []
    class_counts = {'benign': 0, 'malignant': 0, 'normal': 0}

    for f in valid_files:
        try:
            image = Image.open(f.stream).convert('RGB')
            result = model_handler.analyze(image, use_tta=True)
            result['filename'] = secure_filename(f.filename)
            results.append(result)

            pred_cls = result['predicted_class']
            class_counts[pred_cls] = class_counts.get(pred_cls, 0) + 1
        except Exception as e:
            errors.append({'filename': secure_filename(f.filename), 'error': str(e)})

    summary = {
        'total': len(results),
        'class_distribution': class_counts,
        'malignant_ratio': round(class_counts.get('malignant', 0) / max(len(results), 1), 2),
    }

    return jsonify({
        'success': True,
        'results': results,
        'summary': summary,
        'errors': errors if errors else None,
    })


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'model': model_handler.model_type,
        'device': str(model_handler.device),
    })


@app.route('/api/model_info')
def api_model_info():
    """当前模型信息 API"""
    info = dict(model_handler.model_info)
    info['device'] = str(model_handler.device)
    info['supports_tta'] = True
    return jsonify(info)


# ==================== 工具函数 ====================

def _get_file_from_request():
    """从请求中提取并验证文件，返回文件对象或错误响应元组"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not _allowed_file(file.filename):
        return jsonify({'error': f'不支持的格式，支持: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    return file


if __name__ == '__main__':
    print("\n" + "="*70)
    print("启动乳腺癌超声图像诊断系统")
    print("="*70)
    print(f"访问地址: http://{HOST}:{PORT}")
    print("="*70 + "\n")

    app.run(host=HOST, port=PORT, debug=DEBUG)
