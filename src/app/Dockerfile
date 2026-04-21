# ============================================================
#  乳腺癌超声图像诊断系统 - Docker 镜像（轻量版）
#  基础镜像: python:3.11-slim-bookworm (Debian Stable)
#  PyTorch: CPU-only (~200MB vs CUDA ~2.5GB)
#  OpenCV: headless 版本 (无 GUI 依赖)
#  预计总大小: ~800MB - ~1GB
# ============================================================

FROM python:3.11-slim-bookworm

WORKDIR /app

# ==================== Python 依赖 ====================
COPY requirements.txt .

# 先装 CPU-only PyTorch（指定 wheel 源，避免下载 2.5GB 的 CUDA 版）
# 再装其余 Python 包
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch torchvision && \
    pip install --no-cache-dir -r requirements.txt

# ==================== 复制应用代码 ====================
COPY app.py .
COPY config.py .
COPY model_handler.py .
COPY db.py .
COPY pdf_report.py .

COPY static/ ./static/
COPY templates/ ./templates/

# ==================== 模型权重 ====================
COPY models/ ./models/

# 运行时目录
RUN mkdir -p uploads data

EXPOSE 5000

ENV FLASK_APP=app.py \
    PYTHONUNBUFFERED=1 \
    APP_BASE_DIR=/app

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "app.py"]
