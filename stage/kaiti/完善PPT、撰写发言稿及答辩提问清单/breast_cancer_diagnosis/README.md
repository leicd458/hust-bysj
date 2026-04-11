# 基于深度学习的乳腺癌超声图像自动诊断系统

## 📋 项目简介

本项目实现了一个完整的乳腺癌超声图像自动诊断系统，适合**深度学习零基础**的同学学习和使用。系统基于BUSI数据集，实现了以下功能：

1. **图像分类**：使用ResNet18模型进行三分类（正常/良性/恶性）
2. **肿瘤分割**：使用U-Net模型标记肿瘤区域
3. **可解释性**：使用Grad-CAM可视化模型决策依据

## 🎯 项目特点

- ✅ **适配Mac M系列芯片**：支持MPS加速，训练速度快
- ✅ **完整中文注释**：每行代码都有详细解释，零基础也能看懂
- ✅ **模块化设计**：代码结构清晰，易于理解和修改
- ✅ **可视化丰富**：训练曲线、混淆矩阵、ROC曲线、热力图等
- ✅ **开箱即用**：提供完整的训练和推理脚本

## 📁 项目结构


breast_cancer_diagnosis/
├── config.py                 # 配置文件（超参数、路径等）
├── dataset.py                # 数据加载模块
├── models/                   # 模型定义
│   ├── __init__.py
│   ├── resnet_classifier.py  # ResNet18分类器
│   └── unet_segmentor.py     # U-Net分割器
├── utils/                    # 工具模块
│   ├── __init__.py
│   ├── grad_cam.py          # Grad-CAM实现
│   ├── metrics.py           # 评估指标
│   └── visualization.py     # 可视化工具
├── train_classifier.py       # 分类模型训练脚本
├── train_segmentor.py        # 分割模型训练脚本
├── inference.py              # 推理脚本
├── requirements.txt          # 依赖包列表
└── README.md                 # 项目说明（本文件）


## 🚀 快速开始

### 1. 环境配置

**Mac M系列芯片推荐使用Miniforge：**

bash
# 安装Miniforge（如果还没安装）
brew install miniforge

# 创建虚拟环境
conda create -n breast_cancer python=3.10
conda activate breast_cancer

# 安装依赖
pip install -r requirements.txt


### 2. 数据准备

下载BUSI数据集并解压到 `./data/BUSI/` 目录：


data/
└── BUSI/
    ├── normal/
    │   ├── normal (1).png
    │   ├── normal (1)_mask.png
    │   └── ...
    ├── benign/
    │   ├── benign (1).png
    │   ├── benign (1)_mask.png
    │   └── ...
    └── malignant/
        ├── malignant (1).png
        ├── malignant (1)_mask.png
        └── ...


**数据集下载地址：**
- Kaggle: https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset
- 百度网盘: [链接] 提取码: [xxxx]

### 3. 训练分类模型

bash
python train_classifier.py


**训练过程说明：**
- 训练时间：Mac M1约2-3小时（50个epoch）
- 内存占用：约4-6GB
- 输出文件：
  - `checkpoints/best_classifier.pth` - 最佳模型
  - `results/training_history.json` - 训练历史
  - `results/training_history.png` - 训练曲线
  - `results/confusion_matrix.png` - 混淆矩阵
  - `results/roc_curve.png` - ROC曲线

### 4. 训练分割模型（可选）

bash
python train_segmentor.py


**训练过程说明：**
- 训练时间：Mac M1约4-5小时（100个epoch）
- 内存占用：约6-8GB
- 输出文件：
  - `checkpoints/best_segmentor.pth` - 最佳模型

### 5. 推理预测

bash
python inference.py --image path/to/your/image.png


**推理结果：**
- 分类结果：正常/良性/恶性
- 置信度：模型的预测信心
- Grad-CAM热力图：模型关注的区域
- 肿瘤分割掩码（如果训练了分割模型）

## 📊 模型性能

### 分类模型（ResNet18）

| 指标 | 训练集 | 验证集 | 测试集 |
|:--:|:--:|:--:|:--:|
| 准确率 | 95.2% | 92.8% | 91.5% |
| 精确率 | 94.8% | 91.6% | 90.3% |
| 召回率 | 95.1% | 92.3% | 91.2% |
| F1分数 | 94.9% | 91.9% | 90.7% |

### 分割模型（U-Net）

| 指标 | 训练集 | 验证集 | 测试集 |
|:--:|:--:|:--:|:--:|
| Dice系数 | 0.89 | 0.85 | 0.83 |
| IoU | 0.82 | 0.78 | 0.76 |

*注：以上数据为示例，实际性能取决于数据集和训练参数*

## 🔧 配置说明

所有可调整的参数都在 `config.py` 中：


# 关键参数说明
batch_size = 16          # 批次大小（Mac M1建议16）
learning_rate = 0.001    # 学习率
num_epochs = 50          # 训练轮数
image_size = 224         # 图片尺寸
patience = 10            # 早停耐心值


## 📚 核心概念解释

### 1. 什么是深度学习？
- 就像教小孩认图片，给它看很多例子，它逐渐学会识别
- 模型通过调整内部参数，不断提高预测准确率

### 2. 什么是ResNet18？
- 一种卷积神经网络（CNN），专门用于图像分类
- "18"表示有18层，层数越多，模型越复杂
- 使用"残差连接"技术，解决深层网络训练困难的问题

### 3. 什么是U-Net？
- 专门用于图像分割的网络，形状像字母"U"
- 先压缩图片提取特征，再恢复尺寸生成分割掩码
- 使用"跳跃连接"保留细节信息

### 4. 什么是Grad-CAM？
- 可视化技术，显示模型关注图片的哪些区域
- 生成热力图：红色=重要区域，蓝色=不重要区域
- 帮助理解模型的决策依据

### 5. 什么是迁移学习？
- 使用在大数据集（ImageNet）上预训练的模型
- 就像"站在巨人的肩膀上"，训练更快、效果更好
- 特别适合小数据集（BUSI只有780张图）

## 🎓 适合人群

- ✅ 计算机专业本科生（毕业设计）
- ✅ 深度学习初学者
- ✅ 医学图像处理研究者
- ✅ 对AI医疗感兴趣的开发者

## 💡 常见问题

### Q1: 为什么训练很慢？
**A:** 
- 检查是否启用了MPS加速：`print(torch.backends.mps.is_available())`
- 减小batch_size（如改为8）
- 减少训练轮数（如改为30）

### Q2: 内存不足怎么办？
**A:**
- 减小batch_size
- 减小图片尺寸（如改为128）
- 关闭其他占内存的应用

### Q3: 准确率不高怎么办？
**A:**
- 增加训练轮数
- 使用数据增强
- 调整学习率
- 尝试其他模型（如ResNet50）

### Q4: 如何使用自己的数据集？
**A:**
1. 按照BUSI格式组织数据
2. 修改 `config.py` 中的 `data_root` 路径
3. 运行训练脚本

## 📖 参考文献

1. He et al. "Deep Residual Learning for Image Recognition" (ResNet)
2. Ronneberger et al. "U-Net: Convolutional Networks for Biomedical Image Segmentation"
3. Selvaraju et al. "Grad-CAM: Visual Explanations from Deep Networks"
4. Al-Dhabyani et al. "Dataset of breast ultrasound images" (BUSI)

## 📝 许可证

MIT License

## 👨‍💻 作者

- 姓名：[你的姓名]
- 学号：[你的学号]
- 指导教师：[导师姓名]
- 联系方式：[邮箱]

## 🙏 致谢

感谢华中科技大学计算机学院提供的学习平台和指导。

---

**祝你毕业设计顺利！🎓**
