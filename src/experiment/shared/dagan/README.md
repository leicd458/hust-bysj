# DAGAN共享资源

## 概述

DAGAN（Data Augmentation GAN）生成器训练一次，被阶段3和阶段4共同使用。

## 文件结构

```
shared/dagan/
├── models.py          # DAGAN模型定义（生成器、判别器、损失函数）
├── train_dagan.py     # 训练DAGAN生成器
├── generate.py        # 生成合成图像
├── README.md          # 本文档
└── outputs/           # 输出目录（.gitignore）
    ├── dagan_generator.pth      # 训练好的生成器
    ├── training_history.json    # 训练历史
    ├── synthetic_images/        # 合成图像
    │   ├── benign/
    │   ├── malignant/
    │   └── normal/
    └── generated_info.json      # 生成信息
```

## 使用流程

### 步骤1: 训练DAGAN（只需一次）

```bash
cd src/experiment/shared/dagan

python train_dagan.py \
  --data_dir /path/to/BUSI \
  --output_dir outputs \
  --epochs 100 \
  --batch_size 16 \
  --device mps
```

**输出**:
- `outputs/dagan_generator.pth` - 生成器权重
- `outputs/training_history.json` - 训练历史

**训练时间**: 约2-4小时（GPU）或 8-12小时（CPU）

### 步骤2: 生成合成图像（只需一次）

```bash
python generate.py \
  --generator_path outputs/dagan_generator.pth \
  --data_dir /path/to/BUSI \
  --output_dir outputs/synthetic_images \
  --num_variants 5
```

**输出**:
- `outputs/synthetic_images/benign/*.png` - 良性合成图像
- `outputs/synthetic_images/malignant/*.png` - 恶性合成图像
- `outputs/synthetic_images/normal/*.png` - 正常合成图像
- `outputs/generated_info.json` - 生成信息

**生成时间**: 约10-30分钟

### 步骤3: 在阶段3中使用

```bash
cd ../../stage3

python train.py \
  --synthetic_data_dir ../shared/dagan/outputs/synthetic_images \
  --target_acc 85.0
```

### 步骤4: 在阶段4中使用

```bash
cd ../../stage4

python train.py \
  --synthetic_data_dir ../shared/dagan/outputs/synthetic_images \
  --use_focal_loss \
  --target_acc 93.0
```

## 关键特性

✅ **避免数据泄露**:
- DAGAN只使用训练集（70%）训练
- 合成图像只从训练集生成
- 验证集（15%）和测试集（15%）使用原始数据

✅ **数据一致性**:
- 阶段3和阶段4使用完全相同的合成数据
- 便于公平对比不同训练策略

✅ **节省时间**:
- DAGAN训练一次，永久复用
- 无需为每个实验重复训练

## DAGAN架构

### 生成器（U-Net）

- **输入**: (B, 3, 256, 256) RGB图像
- **输出**: (B, 3, 256, 256) 合成图像
- **参数量**: ~54M
- **架构**: 编码器-解码器 + Skip Connections

### 判别器（PatchGAN）

- **输入**: 两张图像拼接 (B, 6, 256, 256)
- **输出**: 真实性判断 (B, 1, 30, 30)
- **参数量**: ~2.8M
- **架构**: 卷积层 + BatchNorm + LeakyReLU

### 损失函数

- **对抗损失**: LSGAN (Least Squares GAN)
- **重建损失**: L1 Loss
- **总损失**: `G_loss = λ_adv * L_adv + λ_rec * L_rec`
  - λ_adv = 1.0
  - λ_rec = 100.0

## 训练配置

```python
config = {
    'epochs': 100,
    'batch_size': 16,
    'learning_rate': 0.0002,
    'optimizer': 'Adam',
    'beta1': 0.5,
    'lambda_adv': 1.0,
    'lambda_rec': 100.0,
    'scheduler': 'StepLR (step=50, gamma=0.5)'
}
```

## 故障排查

### 问题1: DAGAN训练不收敛

```bash
# 降低学习率
python train_dagan.py --lr 0.0001

# 减小batch size
python train_dagan.py --batch_size 8

# 增加训练轮数
python train_dagan.py --epochs 200
```

### 问题2: 合成图像质量差

检查训练历史：
```bash
cat outputs/training_history.json
```

关键指标：
- `g_loss` 应该逐渐下降
- `g_rec_loss` 应该 < 0.1

### 问题3: 内存不足

```bash
# 减小batch size
python train_dagan.py --batch_size 8

# 使用CPU（慢但稳定）
python train_dagan.py --device cpu
```

## 检查清单

训练DAGAN前，请确认：

- [ ] BUSI数据集路径正确
- [ ] 有足够磁盘空间（约2GB用于合成图像）
- [ ] 有足够时间（2-4小时）

生成合成图像前，请确认：

- [ ] DAGAN已训练完成
- [ ] `dagan_generator.pth` 存在

使用合成图像前，请确认：

- [ ] 合成图像已生成
- [ ] `synthetic_images/` 目录存在
- [ ] 三个类别都有图像

## 参考文献

- Al-Dhabyani, W., et al. (2019). "Breast Ultrasound Images Dataset (BUSI)". *IJACSA*.
- Isola, P., et al. (2017). "Image-to-Image Translation with Conditional Adversarial Networks". *CVPR*.
