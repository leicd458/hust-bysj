#!/usr/bin/env python3
"""
配置文件
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

# 模型配置
MODEL_PATH = str(BASE_DIR / 'src/experiment/stage4/outputs/exp1_seed2024/best_model.pth')

# 上传配置
UPLOAD_FOLDER = str(BASE_DIR / 'src/app/uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# Flask配置
SECRET_KEY = os.environ.get('SECRET_KEY') or 'breast-cancer-diagnosis-secret-key-2024'

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
