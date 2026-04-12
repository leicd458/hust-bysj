# 阶段3: DAGAN数据增强

## 实验目标

使用DAGAN（Data Augmentation GAN）生成合成图像，扩充训练集，目标准确率 **85%**

## 实验流程

```
┌─────────────────────┐
│  原始BUSI数据集      │
│  (780张)            │
└──────┬──────────────┘
       │
       ├─ 划分数据集 (70%/15%/15%)
       │  ├─ 训练集: 546张
       │  ├─ 验证集: 117张
       │  └─ 测试集: 117张
       │
       ▼
┌─────────────────────┐
│  训练DAGAN生成器     │  ← 步骤1
│  (只使用训练集)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  生成合成图像        │  ← 步骤2
│  (每张图5个变体)     │
│  = 546 × 5 = 2730张  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  合并训练集          │
│  ├─ 原始训练集: 546张│
│  └─ 合成图像: 2730张 │
│  = 3276张 (带增强)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  训练ResNet-18分类器 │  ← 步骤3
│  目标准确率: 85%     │
└─────────────────────┘
```

## 文件结构

```
stage3/
├── models.py          # DAGAN模型定义（生成器、判别器）
├── train_dagan.py     # 训练DAGAN生成器
├── generate.py        # 生成合成图像
├── dataset.py         # 数据加载器
├── train.py           # 训练分类器
├── README.md          # 本文档
└── .gitignore         # 忽略文件
```

## 使用方法

### 前置条件

**确保DAGAN已训练并生成合成图像**：

```bash
# 步骤1: 训练DAGAN（只需一次）
cd ../shared/dagan
python train_dagan.py --epochs 100 --device mps

# 步骤2: 生成合成图像（只需一次）
python generate.py --num_variants 5 --device mps
```

详细说明请参考：[../shared/dagan/README.md](../shared/dagan/README.md)

### 阶段3训练

```bash
cd src/experiment/stage3

python train.py \
  --real_data_dir /path/to/BUSI \
  --synthetic_data_dir ../shared/dagan/outputs/synthetic_images \
  --output_dir outputs/stage3 \
  --pretrained \
  --epochs 50 \
  --patience 10 \
  --target_acc 85.0 \
  --device mps
```

## 关键改进

### 1. 避免数据泄露

- ✅ **只使用训练集训练DAGAN**
- ✅ **只使用训练集生成合成图像**
- ✅ **验证集和测试集使用原始数据**

### 2. DAGAN架构

**生成器（U-Net）**:
- 输入: (B, 3, 256, 256)
- 输出: (B, 3, 256, 256)
- 参数量: ~54M

**判别器（PatchGAN）**:
- 输入: 两张图像拼接 (B, 6, 256, 256)
- 输出: 真实性判断 (B, 1, 30, 30)
- 参数量: ~2.8M

### 3. 损失函数

- **对抗损失**: LSGAN (Least Squares GAN)
- **重建损失**: L1 Loss
- **总损失**: `G_loss = λ_adv * L_adv + λ_rec * L_rec`
  - λ_adv = 1.0
  - λ_rec = 100.0

### 4. 数据增强策略

**训练集（原始 + 合成）**:
- RandomCrop (224×224)
- RandomHorizontalFlip (p=0.5)
- RandomVerticalFlip (p=0.2)
- RandomRotation (±5°)
- RandomAffine (平移±5%, 缩放±5%)
- GaussianBlur (kernel=3, σ=0.1~2.0)

**验证集/测试集**:
- Resize (224×224)
- Normalize (ImageNet)

## 训练配置

### DAGAN训练

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

### 分类器训练

```python
config = {
    'model': 'ResNet-18 (ImageNet预训练)',
    'epochs': 50,
    'batch_size': 32,
    'learning_rate': 0.0001,
    'optimizer': 'Adam',
    'weight_decay': 1e-4,
    'dropout': 0.5,
    'patience': 10,
    'scheduler': 'StepLR (step=20, gamma=0.1)'
}
```

## 预期结果

根据论文（Al-Dhabyani et al. 2019）:

| 阶段 | 方法 | 目标准确率 | 论文结果 |
|------|------|-----------|---------|
| 阶段1 | 无增强 | 79% | 79% |
| 阶段2 | 传统增强 | 82% | 82% |
| **阶段3** | **DAGAN** | **85%** | **89%** |

## 注意事项

1. **训练时间**:
   - DAGAN训练: 约 2-4 小时（GPU）或 8-12 小时（CPU）
   - 生成图像: 约 10-30 分钟
   - 分类器训练: 约 20-40 分钟

2. **内存需求**:
   - DAGAN训练: ~4GB GPU内存
   - 合成图像存储: ~2GB磁盘空间

3. **数据泄露检查**:
   - 确保DAGAN只使用训练集
   - 确保验证集和测试集不包含合成图像

## 故障排查

### 问题1: DAGAN训练不收敛

```bash
# 降低学习率
python train_dagan.py --lr 0.0001

# 减小batch size
python train_dagan.py --batch_size 8
```

### 问题2: 合成图像质量差

```bash
# 增加训练轮数
python train_dagan.py --epochs 200

# 检查训练历史
cat outputs/dagan/training_history.json
```

### 问题3: 分类器过拟合

```bash
# 增加dropout
# 修改 train.py 中的 dropout=0.6

# 减少训练轮数
python train.py --epochs 30

# 增加早停耐心
python train.py --patience 15
```

## 参考文献

- Al-Dhabyani, W., et al. (2019). "Breast Ultrasound Images Dataset (BUSI)". *International Journal of Advanced Computer Science and Applications (IJACSA)*.
- DAGAN架构参考: Isola, P., et al. (2017). "Image-to-Image Translation with Conditional Adversarial Networks". *CVPR*.
