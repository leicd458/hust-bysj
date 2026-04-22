# ============================================================
#  乳腺癌超声图像诊断系统 - Docker 镜像 (React+TS 前后端分离)
#  构建: Node.js 构建前端 → Python 运行 API + 静态文件
# ============================================================

# ==================== Stage 1: 构建前端 (Node.js) ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端配置
COPY frontend/package.json ./
COPY frontend/tsconfig.json ./
COPY frontend/vite.config.ts ./
COPY frontend/tailwind.config.js ./
COPY frontend/postcss.config.js ./
COPY frontend/index.html ./

# 先复制源码再编译
COPY ./frontend/src ./src

RUN npm install && npx tsc -b && npm run build


# ==================== Stage 2: Python 运行时 + 静态文件服务 ====================
FROM python:3.11-slim-bookworm

WORKDIR /app

# ==================== Python依赖 ====================
COPY backend/requirements.txt .

RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch torchvision && \
    pip install --no-cache-dir -r requirements.txt

# ==================== 复制后端代码 ====================
COPY backend/app.py .
COPY backend/config.py .
COPY backend/model_handler.py .
COPY backend/db.py .
COPY backend/pdf_report.py .

# 复制模型权重
COPY backend/models/ ./models/

# 复制前端构建产物（从 builder stage）
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 运行时目录
RUN mkdir -p uploads data

EXPOSE 5000

ENV FLASK_APP=app.py \
    PYTHONUNBUFFERED=1 \
    APP_BASE_DIR=/app

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health') || exit 1"

CMD ["python", "app.py"]
