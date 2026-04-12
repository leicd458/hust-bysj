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

使用 **ResNet-50** (论文配置):

| 阶段 | 方法 | 目标准确率 |
|------|------|-----------|
| 阶段1 | ResNet-50 (无增强) | 79% |
| 阶段2 | + 传统增强 | 82% |
| 阶段3 | + DAGAN | 89% |
| 阶段4 | + 传统 + DAGAN | **93%** |

### 阶段1: 基础复现（目标 79%）

**方法**: ResNet-50 无数据增强

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

### 阶段2: 传统增强（目标 82%）

**方法**: ResNet-50 + 传统数据增强

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

**方法**: ResNet-50 + DAGAN 合成数据

**DAGAN 实现**:
- 训练 GAN 生成器
- 合成少数类样本 (malignant)
- 平衡训练集类别分布

**数据配比**:
- 原始数据 + 合成数据
- 类别平衡到 437 张/类

### 阶段4: 混合增强（目标 93%）

**方法**: ResNet-50 + 传统增强 + DAGAN

**实现要点**:
- 传统增强在线应用
- DAGAN 数据离线生成
- 超参数优化
- 最终调优

## 关键挑战

1. **类别不平衡**
   - malignant 样本最少 (210张)
   - 需要数据增强平衡
   
2. **实现差异**
   - 论文使用 ResNet-50
   - 你使用 ResNet-18
   - 参数量: 25.6M vs 11.7M

3. **DAGAN 复杂度**
   - 需要额外训练 GAN
   - 生成图像质量控制

## 参考资料

- 论文 PDF: `docs/papers/Al-Dhabyani_2019.pdf`
- 模型介绍: `docs/analysis/模型介绍.md` (旧项目)
- 数据下载: `src/data/download.py`
