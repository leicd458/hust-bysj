#!/usr/bin/env python3
"""
配置文件
支持本地开发和Docker容器化部署
"""

import os
from pathlib import Path

# 项目根目录（支持环境变量覆盖，用于 Docker 部署）
# 默认行为：
#   - Docker 内（/app/backend/config.py）: BASE_DIR = /app
#   - 本地开发（src/app/backend/config.py）: BASE_DIR = src/app/backend
# 可通过 APP_BASE_DIR 环境变量覆盖
_DEFAULT_BASE = Path(__file__).resolve().parent  # .../backend
if Path('/app').exists() and Path('/app/app.py').exists():
    _DEFAULT_BASE = Path('/app')
BASE_DIR = Path(os.environ.get('APP_BASE_DIR', str(_DEFAULT_BASE)))

# ==================== 模型配置 ====================

# 当前使用的模型: efficientnet_b0 (Stage5最优, 94.87%) / resnet18 (Stage4, 88.89%)
MODEL_TYPE = 'efficientnet_b0'  # 可选: resnet18, efficientnet_b0

MODEL_PATHS = {
    'resnet18': str(BASE_DIR / 'models/best_resnet18.pth'),
    'efficientnet_b0': str(BASE_DIR / 'models/best_model.pth'),
}

MODEL_PATH = MODEL_PATHS.get(MODEL_TYPE, MODEL_PATHS['efficientnet_b0'])

# 模型元信息（用于仪表盘展示）
MODEL_META = {
    'resnet18': {
        'name': 'ResNet-18',
        'test_acc': '88.89%',
        'params': '11.7M',
        'input_size': 224,
        'description': '基线模型，混合数据增强 + FocalLoss'
    },
    'efficientnet_b0': {
        'name': 'EfficientNet-B0',
        'test_acc': '94.87%',
        'params': '4.0M',
        'input_size': 300,
        'description': '最优模型，Stratified划分+均衡采样+LabelSmoothing+TTA'
    }
}

# ==================== 上传配置 ====================
UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_BATCH_FILES = 10  # 批量上传最大文件数

# ==================== 数据库配置 ====================
DB_PATH = str(BASE_DIR / 'data/history.db')

# ==================== Flask配置 ====================
SECRET_KEY = os.environ.get('SECRET_KEY') or 'breast-cancer-diagnosis-secret-key-2024'

# ==================== 服务器配置 ====================
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
