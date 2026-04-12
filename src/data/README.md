# 数据获取

## BUSI 数据集

### 数据集简介
- **名称**: Breast Ultrasound Images Dataset
- **来源**: [Kaggle](https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset)
- **类别**: normal, benign, malignant
- **总图像数**: 1578张

### 类别分布
| 类别 | 数量 |
|------|------|
| normal | 266张 |
| benign | 891张 |
| malignant | 421张 |

### 下载方式

#### 方式1: Kaggle CLI
```bash
kaggle datasets download -d aryashah2k/breast-ultrasound-images-dataset
unzip breast-ultrasound-images-dataset.zip -d data/raw/
```

#### 方式2: 手动下载
1. 访问 [Kaggle 数据集页面](https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset)
2. 下载并解压到 `data/raw/` 目录

### 目录结构

```
data/
├── raw/                    # 原始数据（不提交到 Git）
│   └── BUSI/               # 解压后的数据
│       ├── normal/
│       ├── benign/
│       └── malignant/
└── processed/              # 处理后数据（不提交到 Git）
```

### 数据划分
- **训练集**: 70%
- **验证集**: 15%
- **测试集**: 15%

使用 stratify 保持类别分布，固定随机种子 seed=42。
