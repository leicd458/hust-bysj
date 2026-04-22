#!/bin/bash

# 乳腺癌超声图像诊断系统启动脚本 (React + Flask)
# 用法: cd src/app && ./run.sh  或  bash src/app/run.sh

echo "========================================"
echo "乳腺癌超声图像诊断系统"
echo "========================================"
echo ""

# 定位项目根目录（app 所在的 src/app）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# 检查 Node.js 环境（前端构建需要）
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装 Node.js 18+"
    exit 1
fi

echo "Node.js版本:"
node --version
echo ""

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.11+"
    exit 1
fi

echo "Python版本:"
python --version
echo ""

# 安装前端依赖并构建
echo "构建前端..."
cd "$FRONTEND_DIR"
npm install > /dev/null 2>&1 && npm run build > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "错误: 前端构建失败"
    exit 1
fi
echo "✓ 前端构建完成"
echo ""

# 安装 Python 依赖
cd "$BACKEND_DIR"
echo "检查Python依赖..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ 依赖已安装"
echo ""

# 检查模型文件
MODEL_PATH="../../experiment/stage4/outputs/exp1_seed2024/best_model.pth"
if [ ! -f "$MODEL_PATH" ]; then
    echo "警告: 未找到模型文件: $MODEL_PATH"
    echo "请确保模型文件存在，否则预测功能不可用"
    echo ""
else
    echo "✓ 模型文件已找到"
    echo ""
fi

# 启动应用
echo "启动Web应用..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python app.py
