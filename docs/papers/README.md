# 乳腺癌超声分类相关论文

本目录包含与乳腺癌超声分类相关的4篇核心论文，用于毕业论文的文献综述和研究背景阐述。

---

## 📚 论文清单

### 1. [Al-Dhabyani 2020] - BUSI数据集原始论文 🔴 **必引**

**文件名**: `Al-Dhabyani_2020_Dataset_of_Breast_Ultrasound_Images.pdf` (756 KB, 11页)

**论文标题**: Dataset of breast ultrasound images

**作者**: Walid Al-Dhabyani, Mohammed Gomaa, Hussien Khaled, Aly Fahmy

**期刊**: Data in Brief, 2020, Volume 28, Article 104863

**DOI**: 10.1016/j.dib.2019.104863

**数据集**: BUSI (Breast Ultrasound Images)
- 正常样本: 133张
- 良性样本: 437张
- 恶性样本: 210张
- **总计: 780张**

**论文作用**:
- 🔴 **必须引用**: 这是BUSI数据集的原始出处
- 提供数据集的收集、标注、统计信息
- 为后续研究提供了统一的数据集

**核心贡献**:
- 首次公开发布BUSI数据集，成为乳腺超声分类研究的标准数据集
- 提供了完整的Ground Truth标注（mask图像）
- 包含780张图像（133正常 + 437良性 + 210恶性）

**在本论文中的引用位置**:
- 引言：介绍BUSI数据集
- 数据集描述部分：数据来源、样本分布、收集方法
- 参考文献：作为数据集出处必须引用

⚠️ **重要说明**:
- 这篇论文**不包含**任何实验结果或准确率数据
- 这是一篇**数据集论文**（Data Article），仅描述数据集本身
- 性能基准准确率来自同一作者的另一篇论文（IJACSA 2019，见下方）

---

### 1.5. [Al-Dhabyani 2019] - BUSI数据集的深度学习方法研究 🔴 **必引（性能基准）**

**文件名**: `Al-Dhabyani_2019.pdf` (994 KB, 6页)

**论文标题**: Deep Learning Approaches for Data Augmentation and Classification of Breast Masses using Ultrasound Images

**作者**: Walid Al-Dhabyani, Mohammed Gomaa, Hussien Khaled, Aly Fahmy

**期刊**: International Journal of Advanced Computer Science and Applications (IJACSA), 2019, Volume 10, Issue 5, Paper No. 79

**DOI**: 10.14569/ijacsa.2019.0100579

**数据集**: 
- BUSI (780张图像)
- Dataset B (163张图像)
- 合并数据集 (943张图像)

**模型**: 
- CNN (自定义卷积神经网络)
- Transfer Learning (迁移学习)

**数据增强方法**:
- 传统数据增强：旋转、翻转等
- GAN数据增强：使用DAGAN架构生成新图像
- 每个类别生成5,000张合成图像

**实验结果**: 
- **最高准确率: 99%** (合并数据集 + 传统增强 + GAN增强 + 迁移学习)
- BUSI数据集单独：准确率约92%（迁移学习 + 数据增强）
- 使用数据增强显著提升性能

**论文作用**:
- 🔴 **必须引用**: 提供了BUSI数据集的**性能基准**
- 展示了数据增强（尤其是GAN）对乳腺超声分类的显著效果
- 证明了迁移学习在医学图像分类中的优势

**与你的工作对比**:
- **数据增强方法**: 你使用离线数据增强（旋转、翻转、缩放），与论文中的传统增强类似
- **模型选择**: 你使用ResNet-18（预训练），与论文中的迁移学习思路一致
- **性能对比**: 你的85.47%准确率合理（未使用GAN增强，且未合并多个数据集）

**在本论文中的引用位置**:
- 引言：介绍数据增强在乳腺超声分类中的应用
- 相关工作：总结BUSI数据集的基准性能
- 实验对比：与99%最高准确率对比，说明你的方法在更严格的条件下的合理性
- 讨论：解释为什么你的准确率低于99%（未使用GAN、仅用单一数据集）

**引用格式（GB/T 7714）**:
```
[1a] AL-DHABYANI W, GOMAA M, KHALED H, et al. Deep learning approaches for data 
    augmentation and classification of breast masses using ultrasound images[J]. 
    International Journal of Advanced Computer Science and Applications, 2019, 10(5): 79.
```

---

### 2. [EfficientNet-B7 2024] - EfficientNet在BUSI上的应用 🟡 **强烈推荐**

**文件名**: `EfficientNet_B7_BUSI_2024.pdf` (5.0 MB)

**论文标题**: Revolutionizing breast ultrasound diagnostics with EfficientNet-B7 and Explainable AI

**作者**: M. Latha, P. S. Kumar, R. R. Chandrika, et al.

**期刊**: BMC Medical Imaging, 2024, Volume 24, Article 143

**DOI**: 10.1186/s12880-024-01404-3

**数据集**: BUSI (Breast Ultrasound Images)

**模型**: 
- EfficientNet-B7
- 结合可解释性AI (XAI)

**论文作用**:
- 展示EfficientNet-B7在BUSI数据集上的性能
- 提供可解释性分析（与你的Grad-CAM方法呼应）
- 用于解释"为什么选ResNet18而不是EfficientNet"

**核心贡献**:
- 将最新的EfficientNet-B7模型应用于BUSI数据集
- 结合可解释性AI增强模型可信度
- 展示了EfficientNet在医学图像分类中的应用潜力

**在本论文中的引用位置**:
- 相关工作：EfficientNet在医学图像中的应用
- 方法对比：说明为什么选择ResNet18而非EfficientNet
- 讨论：对比不同模型架构的性能和可解释性

---

### 3. [arXiv 2025] - ResNet-18在BUSI上的直接对比 🟡 **强烈推荐**

**文件名**: `arXiv_2025_Interpretable_Deep_Transfer_Learning.pdf` (359 KB)

**论文标题**: Interpretable Deep Transfer Learning for Breast Ultrasound Image Analysis

**来源**: arXiv:2509.05004, 2025 (预印本)

**作者**: 未列出具体作者（预印本）

**数据集**: 
- BUSI (Breast Ultrasound Images)
- BUS-BRA (Breast Ultrasound for Breast Abnormality Recognition)
- BrEaST-Lesions USG

**模型**: 
- **ResNet-18**（与你的模型完全相同！）
- ResNet-50
- EfficientNet-B0/B7
- VGG-16
- DenseNet-121

**论文作用**:
- ✅ **最重要的参考论文**：直接评估了ResNet-18在BUSI上的性能
- 提供了ResNet-18与其他模型的对比结果
- 包含可解释性分析（与你的Grad-CAM呼应）

**核心贡献**:
- 系统评估了多种深度学习模型在BUSI数据集上的性能
- 特别评估了ResNet-18的准确率、召回率等指标
- 提供了模型可解释性的对比分析

**在本论文中的引用位置**:
- 相关工作：ResNet在医学图像分类中的应用
- 实验对比：与ResNet-18的性能直接对比
- 讨论：验证你的85.47%准确率在合理范围内

---

### 4. [Jabeen 2024] - ResNet + EfficientNet融合 🟢 **可选**

**文件名**: `Jabeen_2024_EfficientNet_ResNet.pdf` (3.0 MB)

**论文标题**: An EfficientNet integrated ResNet deep network and explainable AI for breast lesion classification from ultrasound images

**作者**: Kiran Jabeen, M. A. Khan, A. Hamza, et al.

**期刊**: CAAI Transactions on Intelligence Technology, 2024, Volume 10, Issue 1, Pages 150-164

**DOI**: 10.1049/cit2.12385

**模型**:
- EfficientNet-B0 + ResNet
- 特征融合
- 可解释性AI (XAI)

**数据集**: 未明确（可能是私有数据集或多个数据集的混合）

**论文作用**:
- 展示ResNet与EfficientNet的融合方法
- 提供特征融合的创新思路
- 结合可解释性AI

**核心贡献**:
- 提出EfficientNet-B0与ResNet的融合网络
- 引入特征融合机制提升分类性能
- 结合可解释性AI增强临床可信度

**在本论文中的引用位置**:
- 相关工作：ResNet的应用和改进
- 方法对比：说明你的创新点（离线数据增强而非模型融合）
- 讨论：对比不同方法的优劣

---

## 🎯 在你的论文中的应用建议

### **文献综述结构（第2章）**

```
2.1 BUSI数据集概述
   → 引用 Al-Dhabyani 2020 [1]（数据集出处）
   → 引用 Al-Dhabyani 2019 [1a]（性能基准：99%）

2.2 深度学习在乳腺超声分类中的应用
   2.2.1 ResNet系列模型
       → 引用 Jabeen 2024 [3], arXiv 2025 [4]
   2.2.2 EfficientNet系列模型
       → 引用 EfficientNet-B7 2024 [5]
   2.2.3 数据增强方法
       → 引用 Al-Dhabyani 2019 [1a]（传统增强 + GAN增强）

2.3 可解释性AI在医学图像中的应用
   → 引用 arXiv 2025 [4], Jabeen 2024 [3], EfficientNet-B7 2024 [5]
```

---

## 📊 五篇论文对比表

| 论文 | 年份 | 数据集 | 模型 | 准确率 | 可解释性 | 是否必引 | 作用 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| **Al-Dhabyani 2020** | 2020 | BUSI | - | - | ❌ | 🔴 **必须** | 数据集出处 |
| **Al-Dhabyani 2019** | 2019 | BUSI等 | CNN/TL | **99%** | ❌ | 🔴 **必须** | 性能基准、数据增强 |
| **EfficientNet-B7 2024** | 2024 | BUSI | EfficientNet-B7 | - | ✅ | 🟡 推荐 | EfficientNet参考 |
| **arXiv 2025** | 2025 | BUSI等 | **ResNet-18** | - | ✅ | 🟡 **推荐** | **ResNet-18直接对比** |
| **Jabeen 2024** | 2024 | 未明确 | ResNet+EfficientNet | - | ✅ | 🟢 可选 | ResNet应用、特征融合 |

---

## 💡 引用建议

### **必引论文（1篇）**
- ✅ **Al-Dhabyani 2020**: 数据集出处，学术规范要求

### **强烈推荐引用（2篇）**
- ✅ **arXiv 2025**: ResNet-18直接对比，与你的模型相同
- ✅ **EfficientNet-B7 2024**: EfficientNet参考，解释为什么选ResNet18

### **可选引用（1篇）**
- 🟢 **Jabeen 2024**: 展示ResNet的应用和改进，但已有arXiv 2025作为ResNet参考

---

## 📝 GB/T 7714 参考文献格式

```markdown
[1] AL-DHABYANI W, GOMAA M, KHALED H, et al. Dataset of breast ultrasound images[J].
    Data in Brief, 2020, 28: 104863.

[1a] AL-DHABYANI W, GOMAA M, KHALED H, et al. Deep learning approaches for data
    augmentation and classification of breast masses using ultrasound images[J].
    International Journal of Advanced Computer Science and Applications, 2019, 10(5): 79.

[2] LATHA M, KUMAR P S, CHANDRIKA R R, et al. Revolutionizing breast ultrasound diagnostics with
    EfficientNet-B7 and Explainable AI[J]. BMC Medical Imaging, 2024, 24(1): 143.

[3] Interpretable Deep Transfer Learning for Breast Ultrasound Image Analysis[J/OL].
    arXiv:2509.05004, 2025.

[4] JABEEN K, KHAN M A, HAMZA A, et al. An EfficientNet integrated ResNet deep network and
    explainable AI for breast lesion classification from ultrasound images[J].
    CAAI Transactions on Intelligence Technology, 2024, 10(1): 150-164.
```

---

## 🚀 下一步行动

1. ✅ **阅读Al-Dhabyani 2020**（15分钟）
   - 重点：数据集描述、样本分布、数据收集方法

2. ✅ **阅读Al-Dhabyani 2019 (IJACSA)**（30分钟）
   - 重点：数据增强方法（传统 + GAN）、迁移学习性能、99%准确率

3. ✅ **阅读arXiv 2025**（30分钟）
   - 重点：ResNet-18在BUSI上的性能、可解释性方法

4. ✅ **阅读EfficientNet-B7 2024**（30分钟）
   - 重点：EfficientNet性能、可解释性分析

5. 🟢 **阅读Jabeen 2024**（可选，20分钟）
   - 重点：ResNet与EfficientNet融合方法

6. 📝 **开始写文献综述**（2-3小时）
   - 基于这5篇论文
   - 按照上述结构组织

---

**重要说明**:
- **Al-Dhabyani 2020**: 数据集论文，无实验结果
- **Al-Dhabyani 2019**: 性能基准论文，包含99%最高准确率
- 你的85.47%准确率在合理范围内（未使用GAN增强、仅用单一数据集）

---

**更新时间**: 2026-03-29

**文件总数**: 5篇PDF文件

**总大小**: 约10.1 MB
