# 阶段2: 传统数据增强

## 实验目标

在阶段1基线模型基础上，使用传统数据增强方法提升模型性能。

**目标准确率**: 82%（论文 ResNet + 传统增强）

## 实验配置

### 模型
- **架构**: ResNet-18
- **预训练**: ImageNet
- **Dropout**: 0.5
- **输出类别**: 3 (benign, malignant, normal)

### 训练参数
- **Batch Size**: 64
- **Optimizer**: SGD (lr=0.01, momentum=0.9, weight_decay=5e-4)
- **学习率调度**: StepLR (step_size=30, gamma=0.1)
- **最大训练轮数**: 50
- **早停耐心值**: 10
- **随机种子**: 42

### 数据增强策略

#### 训练集增强
```python
transforms.Compose([
    Resize(256, 256),
    RandomCrop(224),           # 随机裁剪
    RandomHorizontalFlip(0.5), # 水平翻转
    RandomVerticalFlip(0.2),   # 垂直翻转（低概率）
    RandomRotation(10),        # 随机旋转±10度
    RandomAffine(
        translate=(0.1, 0.1),  # 平移±10%
        scale=(0.9, 1.1)       # 缩放±10%
    ),
    ToTensor(),
    Normalize(ImageNet均值和方差)
])
```

#### 验证集/测试集
```python
transforms.Compose([
    Resize(224, 224),
    ToTensor(),
    Normalize(ImageNet均值和方差)
])
```

### 数据划分
- **训练集**: 70% (546张)
- **验证集**: 15% (117张)
- **测试集**: 15% (117张)

## 运行训练

```bash
# 使用默认参数训练
python train.py --pretrained --target_acc 82.0 --device mps --num_workers 0

# 自定义参数
python train.py \
    --data_dir /path/to/Dataset_BUSI_with_GT \
    --batch_size 64 \
    --lr 0.01 \
    --epochs 50 \
    --patience 10 \
    --pretrained \
    --target_acc 82.0 \
    --device mps \
    --num_workers 0
```

## 预期结果

| 指标 | 阶段1 (基线) | 阶段2 (传统增强) | 提升 |
|------|-------------|----------------|------|
| 测试准确率 | 79% | **82%** | +3% |
| 验证准确率 | - | - | - |

## 增强策略说明

### 为什么这些增强有效？

1. **随机裁剪**: 增加空间变换鲁棒性
2. **水平翻转**: 医学超声图像左右对称性
3. **垂直翻转**: 低概率应用，保持解剖结构
4. **随机旋转**: 模拟不同扫描角度
5. **仿射变换**: 模拟不同的成像条件

### 医学图像增强注意事项

- ⚠️ **避免过度增强**: 医学图像包含诊断关键特征，过度增强会破坏语义信息
- ⚠️ **保持解剖结构**: 垂直翻转和旋转需要谨慎
- ⚠️ **颜色增强**: 本阶段不使用颜色抖动，避免改变组织特征

## 与阶段1对比

| 维度 | 阶段1 | 阶段2 |
|------|-------|-------|
| 数据增强 | ❌ 无 | ✅ 传统增强 |
| 训练集增强 | - | 翻转、旋转、裁剪、仿射 |
| 验证集增强 | - | 无 |
| 目标准确率 | 79% | 82% |

## 文件结构

```
stage2/
├── dataset.py       # 数据集 + 传统增强
├── model.py         # ResNet-18 模型
├── train.py         # 训练脚本
├── README.md        # 本文件
├── RESULT.md        # 实验结果 (训练后生成)
└── outputs/
    └── stage2/
        ├── config.json       # 训练配置
        ├── results.json      # 训练结果
        └── best_model.pth    # 最佳模型
```

## 参考文献

论文: 《Deep Learning for Breast Cancer Classification Using Ultrasound Images》
- ResNet + 传统增强: 82% 准确率
- 传统增强方法: flipping, scaling, translating, rotating
