# 学习资料收集

本分支用于收集项目相关的学习资料，帮助建立理论基础和技术储备。

---

## 📚 核心学习资料

### 1. 深度学习基础

#### 李宏毅机器学习教程
- **来源**：台湾大学李宏毅教授
- **内容**：深度学习基础理论、CNN、RNN、Transformer等
- **资源**：
  - [课程视频](https://www.youtube.com/c/HungyiLeeNTU)
  - 课程讲义PDF
  - Jupyter Notebook 实践代码

#### 相关主题
- [ ] 卷积神经网络（CNN）原理
- [ ] 图像分类任务基础
- [ ] 数据增强技术
- [ ] 模型评估指标

---

### 2. NLP与Transformer

#### Learn NLP with Transformers
- **来源**：Hugging Face 开源教程
- **内容**：Transformer架构、预训练模型、微调技术
- **重点章节**：
  - [ ] Transformer 架构详解
  - [ ] Vision Transformer (ViT)
  - [ ] 注意力机制原理

#### 在本项目中的应用
- Vision Transformer 在医学图像分类中的应用
- Attention U-Net 分割网络
- TransUNet 混合架构

---

### 3. 医学图像分析

#### 乳腺癌超声诊断
- [ ] BUSI 数据集介绍论文
- [ ] 医学图像预处理方法
- [ ] 类别不平衡处理策略
- [ ] 医学伦理与数据脱敏

#### 可解释性方法
- [ ] Grad-CAM 原理与实现
- [ ] 医学AI诊断的可解释性需求
- [ ] 热力图可视化技术

---

### 4. 数据增强技术

#### 传统数据增强
- 几何变换：旋转、翻转、缩放
- 弹性变形
- 颜色增强

#### 生成式数据增强
- **DAGAN (Data Augmentation GAN)**
  - 论文阅读：DAGAN原理
  - 代码实现参考
  - 在医学图像中的应用案例

---

### 5. 实践框架与工具

#### PyTorch 生态
- [ ] PyTorch 基础语法
- [ ] torchvision 数据增强
- [ ] 模型训练与验证流程
- [ ] Checkpoint 管理

#### 可视化工具
- [ ] Matplotlib 绘图
- [ ] TensorBoard 可视化
- [ ] Grad-CAM 实现

---

## 📂 资料组织结构

```
docs/learning/
├── learn-nlp-with-transformers/    # NLP Transformers 教程
│   ├── chapters/                   # 各章节内容
│   └── notebooks/                  # Jupyter notebooks
├── leedl-tutorial/                 # 李宏毅深度学习教程
│   ├── slides/                     # 课程讲义
│   └── notebooks/                  # 实践代码
└── medical-imaging/                # 医学图像相关资料
    ├── papers/                     # 相关论文
    └── tutorials/                  # 教程文档
```

---

## ✅ 收集进度

### 已收集资料
- [x] 李宏毅深度学习教程PDF
- [x] Learn NLP with Transformers 完整教程
- [ ] 待补充...

### 待收集资料
- [ ] DAGAN 论文精读笔记
- [ ] BUSI 数据集分析文档
- [ ] Grad-CAM 实现教程
- [ ] 医学图像分类综述

---

## 🎯 学习目标

### 短期目标（开题阶段）
1. 掌握深度学习基础理论
2. 理解 CNN 和 Transformer 架构
3. 了解医学图像分析特点

### 中期目标（实现阶段）
1. 精通 PyTorch 框架
2. 掌握数据增强技术
3. 实现可解释性方法

---

## 📝 学习笔记

### 学习方法
1. **主动学习**：边看边敲代码
2. **总结提炼**：每学完一章写笔记
3. **实践验证**：在小数据集上验证理解

### 笔记规范
- 使用 Markdown 格式
- 包含代码示例
- 标注重点和疑问
- 定期复习和更新

---

## 📖 参考链接

### 在线课程
- [李宏毅机器学习课程](https://www.youtube.com/c/HungyiLeeNTU)
- [Hugging Face Transformers 教程](https://huggingface.co/learn)

### 开源项目
- [PyTorch 官方教程](https://pytorch.org/tutorials/)
- [Albumentations 数据增强库](https://albumentations.ai/)

### 论文资源
- [arXiv.org](https://arxiv.org/)
- [Papers With Code](https://paperswithcode.com/)

---
