# 乳腺癌超声图像诊断系统 Web应用

基于深度学习的乳腺癌超声图像自动诊断Web系统

## 🎯 功能特性

- ✅ **图像上传**: 支持拖拽上传，支持 PNG/JPG/JPEG/BMP 格式
- ✅ **实时诊断**: 三分类诊断（良性、恶性、正常）
- ✅ **置信度显示**: 显示各类别的预测概率
- ✅ **Grad-CAM可视化**: 模型注意力热力图
- ✅ **响应式设计**: 支持桌面和移动端访问
- ✅ **RESTful API**: 提供标准API接口

## 📦 项目结构

```
src/app/
├── app.py                 # Flask主应用
├── model_handler.py       # 模型加载和推理
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker配置
│
├── templates/            # HTML模板
│   ├── layout.html       # 布局模板
│   └── index.html        # 主页
│
├── static/               # 静态资源
│   ├── css/style.css     # 样式表
│   ├── js/main.js        # 前端交互
│   └── images/           # 图标资源
│
└── uploads/              # 临时上传目录
```

## 🚀 快速开始

### 方式1: 本地运行

```bash
# 1. 进入应用目录
cd src/app

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行应用
python app.py

# 4. 访问 http://localhost:5000
```

### 方式2: Docker部署

```bash
# 1. 构建镜像
docker build -t breast-cancer-diagnosis .

# 2. 运行容器
docker run -p 5000:5000 breast-cancer-diagnosis

# 3. 访问 http://localhost:5000
```

## 📡 API接口

### 1. 健康检查

```
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "model": "loaded"
}
```

### 2. 图像诊断

```
POST /predict
```

**请求参数**:
- `file`: 图像文件 (multipart/form-data)

**响应示例**:
```json
{
  "success": true,
  "result": {
    "predicted_class": "malignant",
    "predicted_class_cn": "恶性",
    "confidence": 0.96,
    "probabilities": {
      "benign": 0.02,
      "malignant": 0.96,
      "normal": 0.02
    },
    "gradcam": "data:image/png;base64,..."
  }
}
```

## ⚙️ 配置说明

编辑 `config.py` 修改配置：

```python
# 模型路径
MODEL_PATH = 'path/to/your/model.pth'

# 上传目录
UPLOAD_FOLDER = 'uploads'

# 最大文件大小 (16MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True
```

## 🔧 部署到生产环境

### 使用Gunicorn (推荐)

```bash
# 安装Gunicorn
pip install gunicorn

# 运行 (4个工作进程)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 性能指标

- **模型准确率**: 90.60%
- **AUC**: 99.63%
- **推理速度**: ~100ms/张 (CPU)
- **支持并发**: 多进程支持

## 🛡️ 安全说明

- ⚠️ 本系统仅供学术研究和辅助参考
- ⚠️ 不能替代专业医生的诊断
- ⚠️ 如有疑问，请咨询专业医疗人员
- ⚠️ 生产环境建议添加身份认证和HTTPS

## 📝 技术栈

- **后端**: Flask 3.0
- **深度学习**: PyTorch 2.1
- **模型**: ResNet-18
- **可视化**: Grad-CAM
- **前端**: HTML5 + CSS3 + JavaScript
- **部署**: Docker + Gunicorn + Nginx

## 📄 许可证

本项目为华中科技大学本科毕业设计作品

## 👨‍💻 作者

华中科技大学 毕业设计

---

如有问题或建议，欢迎联系！
