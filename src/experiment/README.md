# 论文复现要求

## 目标论文

**Al-Dhabyani et al. (2019)** - "Dataset of Breast Ultrasound Images"

发表期刊: IJACSA Vol. 10, No. 5

## 数据集信息

- **名称**: BUSI (Breast Ultrasound Images Dataset)
- **规模**: 780张乳腺超声图像
- **类别**: 
  - benign (良性): 437张
  - malignant (恶性): 210张
  - normal (正常): 133张
- **任务**: 三分类

## 实验阶段（论文 Table 结果）

使用 **TL-ResNet**（迁移学习 ResNet）：

| 阶段 | 方法 | 目标准确率 |
|------|------|-----------|
| 阶段1 | ResNet (无增强) | 79% |
| 阶段2 | + 传统增强 | 82% |
| 阶段3 | + DAGAN | 89% |
| 阶段4 | + 传统 + DAGAN | **93%** |

### 阶段1: 基础复现（目标 79%）

**方法**: ResNet-18 无数据增强

**实现要点**:
- 使用 ImageNet 预训练权重
- 数据预处理: resize 224x224, normalize
- 无数据增强
- 基础训练流程

**论文配置**:
- Batch size: 32
- Optimizer: Adam
- Learning rate: 0.001
- Epochs: 10
- 数据划分: 70% train, 15% val, 15% test

### 阶段2: 传统增强（目标 82%）

**方法**: ResNet-18 + 传统数据增强

**增强方法**:
- 随机水平翻转
- 随机旋转 (±15°)
- 随机裁剪 (scale 0.8-1.0)
- 亮度/对比度调整

**实现要点**:
- 在线增强 (训练时实时应用)
- 验证集不增强
- 保持数据分布一致

### 阶段3: DAGAN 增强（目标 89%）

**方法**: ResNet-18 + DAGAN 合成数据

**DAGAN 实现**:
- 训练 GAN 生成器
- 合成少数类样本 (malignant)
- 平衡训练集类别分布

**数据配比**:
- 原始数据 + 合成数据
- 类别平衡到 437 张/类

### 阶段4: 混合增强（目标 93%）

**方法**: ResNet-18 + 传统增强 + DAGAN

**实现要点**:
- 传统增强在线应用
- DAGAN 数据离线生成
- 超参数优化
- 最终调优

## 模型选择说明

### 为什么选择 ResNet-18？

| 维度 | ResNet-18 | ResNet-50 | NASNet |
|------|-----------|-----------|--------|
| 参数量 | 11.7M | 25.6M | 5.3M |
| PyTorch 支持 | ✅ 内置 | ✅ 内置 | ❌ 需第三方 |
| 实现难度 | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 困难 |
| 训练速度 | ⚡ 快 | ⚡⚡ 中等 | ⚡⚡⚡ 慢 |
| 适合 Mac M 系列 | ✅ 是 | ⚠️ 一般 | ❌ 不推荐 |

## 参考资料

- 论文 PDF: `docs/papers/Al-Dhabyani_2019.pdf`
- 论文数据: Dataset BUSI+B, Table in Section V
- 数据下载: `src/data/download.py`
