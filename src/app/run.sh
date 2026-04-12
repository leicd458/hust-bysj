#!/bin/bash

# 乳腺癌超声图像诊断系统启动脚本

echo "========================================"
echo "乳腺癌超声图像诊断系统"
echo "========================================"
echo ""

# 检查Python环境
if ! command -v python &> /dev/null
then
    echo "错误: 未找到Python，请先安装Python 3.11+"
    exit 1
fi

echo "Python版本:"
python --version
echo ""

# 检查依赖
echo "检查依赖..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ 依赖已安装"
echo ""

# 检查模型文件
MODEL_PATH="../../experiment/stage4/outputs/exp1_seed2024/best_model.pth"
if [ ! -f "$MODEL_PATH" ]; then
    echo "错误: 未找到模型文件: $MODEL_PATH"
    echo "请确保模型文件存在"
    exit 1
fi
echo "✓ 模型文件已找到"
echo ""

# 启动应用
echo "启动Web应用..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python app.py
