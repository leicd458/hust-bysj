# 学习资料

本分支收集了项目相关的学习资料，包括深度学习基础和 Transformer 教程。

---

## 📚 已收集资料

### 1. 李宏毅深度学习教程

#### 教程讲义
- **文件**：`LeeDL_Tutorial_v.1.2.4.pdf`
- **大小**：135 MB
- **内容**：深度学习基础理论、CNN、RNN、Transformer 等
- **作者**：台湾大学李宏毅教授

#### 课程作业与实践代码
- **目录**：`leedl-tutorial/`
- **内容**：15个课程作业 + PyTorch 入门教程

| 作业编号 | 主题 | 涉及技术 |
|---------|------|---------|
| HW1 | PM2.5 预测 | 线性回归 |
| HW2 | 音素分类 | 深度神经网络 |
| HW3 | 图像情感分类 | CNN |
| HW4 | 自注意力机制 | Self-Attention |
| HW5 | 序列到序列 | seq2seq |
| HW6 | 生成对抗网络 | GAN |
| HW7 | BERT 微调 | Transformer |
| HW8 | 异常检测 | Autoencoder |
| HW9 | 可解释性 AI | Explainable AI |
| HW10 | 对抗攻击 | Adversarial Attack |
| HW11 | 域适应 | Domain Adaptation |
| HW12 | 强化学习 | Reinforcement Learning |
| HW13 | 网络压缩 | Network Compression |
| HW14 | 终身学习 | Life-Long Learning |
| HW15 | 元学习 | Meta Learning |
| Warmup | PyTorch 入门 | PyTorch 基础 |

**课程资源**：
- [课程视频](https://www.youtube.com/c/HungyiLeeNTU)
- 课程讲义位于 `leedl-tutorial/docs/`

---

### 2. Learn NLP with Transformers

#### 教程内容
- **目录**：`learn-nlp-with-transformers/`
- **来源**：Hugging Face 开源教程
- **内容**：Transformer 架构、预训练模型、微调技术

#### 章节结构

**章节 1 - 前言**
- 本地阅读和代码运行环境配置
- Transformers 在 NLP 中的兴起

**章节 2 - Transformer 相关原理**
- 图解 Attention 注意力机制
- 图解 Transformer 架构
- PyTorch 编写 Transformer（含 Jupyter Notebook）

**章节 3 - BERT 相关原理**
- BERT 模型介绍
- BERT 应用实践

**相关资源**：
- [Hugging Face 官方教程](https://huggingface.co/learn)
- 依赖包：`requirements.txt`

---

## 📂 目录结构

```
docs/learning/
├── README.md                           # 本文档
├── LeeDL_Tutorial_v.1.2.4.pdf         # 李宏毅教程 PDF (135MB)
├── learn-nlp-with-transformers/        # NLP Transformers 教程
│   ├── docs/                           # 教程文档
│   └── requirements.txt                # Python 依赖
└── leedl-tutorial/                     # 李宏毅课程作业
    ├── docs/                           # 课程讲义
    ├── Homework/                       # 15个作业 + Warmup
    └── assets/                         # 课程资源图片
```

---

## 📊 统计信息

- **总文件数**：218 个文件
- **总代码行数**：393,754 行
- **主要资源**：
  - 1 个 PDF 教程（135MB）
  - 137 个 Transformers 教程文件
  - 74 个李宏毅课程文件

---

*资料收集时间：2026年4月11日*
