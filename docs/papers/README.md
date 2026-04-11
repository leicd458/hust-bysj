# 乳腺癌超声分类相关论文

本目录包含乳腺癌超声分类领域的核心论文，用于文献综述和研究参考。

---

## 📚 论文清单

### 1. BUSI 数据集原始论文

**Al-Dhabyani et al. (2020) - Dataset of breast ultrasound images**

- **文件**：`Al-Dhabyani_2020_Dataset_of_Breast_Ultrasound_Images.pdf` (756 KB)
- **期刊**：Data in Brief, 2020, Vol. 28, Article 104863
- **DOI**：10.1016/j.dib.2019.104863

**概要**：
- 首次公开发布 BUSI (Breast Ultrasound Images) 数据集
- 包含 780 张乳腺超声图像（133 正常 + 437 良性 + 210 恶性）
- 提供完整的 Ground Truth 标注（mask 图像）
- 成为乳腺超声分类研究的标准数据集



---

### 2. 数据增强与分类方法

**Al-Dhabyani et al. (2019) - Deep Learning Approaches for Data Augmentation and Classification of Breast Masses using Ultrasound Images**

- **文件**：`Al-Dhabyani_2019.pdf` (994 KB)
- **期刊**：International Journal of Advanced Computer Science and Applications (IJACSA), 2019, Vol. 10, Issue 5
- **DOI**：10.14569/ijacsa.2019.0100579

**概要**：
- 数据增强方法：传统数据增强 + DAGAN（生成对抗网络）
- 模型：自定义 CNN + 迁移学习
- 最高准确率：**99%**（合并数据集 + 传统增强 + GAN 增强）
- 证明数据增强对乳腺超声分类的显著效果

---

### 3. EfficientNet 应用与可解释性

**Latha et al. (2024) - Revolutionizing breast ultrasound diagnostics with EfficientNet-B7 and Explainable AI**

- **文件**：`EfficientNet_B7_BUSI_2024.pdf` (5.0 MB)
- **期刊**：BMC Medical Imaging, 2024, Vol. 24, Article 143
- **DOI**：10.1186/s12880-024-01404-3

**概要**：
- 将 EfficientNet-B7 应用于 BUSI 数据集
- 结合可解释性 AI (Explainable AI) 增强模型可信度
- 展示 EfficientNet 在医学图像分类中的应用潜力
- 提供可解释性分析方法

---

### 4. ResNet-18 直接对比研究

**arXiv (2025) - Interpretable Deep Transfer Learning for Breast Ultrasound Image Analysis**

- **文件**：`arXiv_2025_Interpretable_Deep_Transfer_Learning.pdf` (359 KB)
- **来源**：arXiv:2509.05004, 2025 (预印本)

**概要**：
- 系统评估多种深度学习模型在 BUSI 上的性能
- 包含 **ResNet-18** 的详细评估结果
- 对比 ResNet-18、ResNet-50、EfficientNet-B0/B7、VGG-16、DenseNet-121
- 提供可解释性分析（与 Grad-CAM 方法呼应）



---

### 5. ResNet 与 EfficientNet 融合

**Jabeen et al. (2024) - An EfficientNet integrated ResNet deep network and explainable AI for breast lesion classification from ultrasound images**

- **文件**：`Jabeen_2024_EfficientNet_ResNet.pdf` (3.0 MB)
- **期刊**：CAAI Transactions on Intelligence Technology, 2024, Vol. 10, Issue 1, Pages 150-164
- **DOI**：10.1049/cit2.12385

**概要**：
- 提出 EfficientNet-B0 与 ResNet 的融合网络
- 引入特征融合机制提升分类性能
- 结合可解释性 AI 增强临床可信度
- 展示 ResNet 应用和改进思路

---

## 📁 文件列表

```
docs/papers/
├── README.md                                              # 本文档
├── Al-Dhabyani_2019.pdf                                  # 数据增强论文 (994 KB)
├── Al-Dhabyani_2020_Dataset_of_Breast_Ultrasound_Images.pdf  # 数据集论文 (756 KB)
├── EfficientNet_B7_BUSI_2024.pdf                         # EfficientNet论文 (5.0 MB)
├── Jabeen_2024_EfficientNet_ResNet.pdf                  # 融合网络论文 (3.0 MB)
└── arXiv_2025_Interpretable_Deep_Transfer_Learning.pdf # ResNet-18论文 (359 KB)
```

**总计**：5 篇 PDF 论文，约 10 MB
