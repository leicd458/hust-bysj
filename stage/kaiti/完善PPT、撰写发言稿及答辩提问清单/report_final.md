# 🎓 毕业论文一周快速完成指南

> 基于深度学习的乳腺癌超声图像自动诊断系统 | Mac M系列芯片适配版

## 1. 执行概览

### 1.1 背景与约束条件

本指南专为大四实习学生设计，针对精力有限、需要在最短时间内高效完成毕业设计的实际情况，提供一套完整的执行方案。核心策略采用**最小可行产品（MVP）思路**，以"先完成，再完美"为原则，确保在一周内完成所有必要交付物[1]。

|项目|内容说明|
|:--|:--|
|论文主题|基于深度学习的乳腺癌超声图像自动诊断系统|
|数据集|BUSI（Breast Ultrasound Images）公开数据集|
|技术栈|ResNet18分类 + U-Net分割 + Grad-CAM可解释性|
|硬件环境|Mac M系列芯片（M1/M2/M3/M4）|
|时间预算|总计约30小时，分散在7天内完成|

### 1.2 关键时间节点

当前日期为2026年2月25日，距离开题答辩截止日期（3月8日）仅剩**11天**。根据毕业论文时间线，各阶段任务安排如下[1]：

|日期|阶段|任务|状态|紧急程度|
|:--|:--|:--|:--|:--|
|3月8日前|春季第1周|完成翻译、开题报告、开题答辩|⚠️进行中|🔴极高|
|4月8日前|春季第6周|毕设中期检查|待完成|🟡中等|
|5月5日前|春季第10周|完成论文|待完成|🟡中等|
|5月14-16日|春季第11周|毕业答辩|待完成|🟡中等|

### 1.3 核心交付物清单

毕业论文的最终交付物需达到以下标准：模型在BUSI测试集上的表现达到或超过近年公开文献的主流水平（分类AUC>0.85），生成病灶热力图或分割轮廓的可视化输出，以及完整的中文技术报告与摘要[1]。

---

## 2. 一周详细执行时间表

### 2.1 总体时间分配

整体方案将7天工作量控制在约30小时，每天投入4-5小时，确保在实习期间可执行。重点前置开题报告撰写，为后续开发预留充足时间[1]。

|天数|日期|主要任务|预计耗时|核心产出|
|:--|:--|:--|:--|:--|
|Day1|2月25日|开题报告撰写（上半部分）|4-5h|研究背景、文献综述初稿|
|Day2|2月26日|开题报告撰写（下半部分）|4-5h|完整开题报告|
|Day3|2月27日|外文翻译+环境搭建|4h|翻译稿+开发环境|
|Day4|2月28日|核心代码实现（分类模型）|5h|分类模型代码|
|Day5|3月1日|核心代码实现（分割+可解释性）|5h|完整代码框架|
|Day6|3月2日|实验运行+结果可视化|4h|实验结果、图表|
|Day7|3月3日|整理汇总+答辩PPT|3-4h|PPT、材料包|

### 2.2 每日任务详解

#### 📅 Day 1（2月25日）：开题报告上半部分

|时间段|任务项|具体内容|
|:--|:--|:--|
|第1小时|模板准备|下载学校开题报告模板，理解格式要求|
|第2小时|研究背景撰写|乳腺癌流行病学数据、超声诊断现状、AI辅助诊断意义|
|第3小时|文献综述撰写|CNN/Transformer在医学图像中的应用、U-Net系列发展|
|第4小时|研究目标与内容|明确三大目标：分类、分割、可解释性|
|第5小时|初稿审阅修改|检查逻辑连贯性，补充细节|

**预期产出**：开题报告前4个章节初稿（约3000字）

#### 📅 Day 2（2月26日）：开题报告下半部分

|时间段|任务项|具体内容|
|:--|:--|:--|
|第1小时|技术路线撰写|绘制技术路线图，说明各模块关系|
|第2小时|实验设计撰写|数据集介绍、评价指标、实验流程|
|第3小时|进度安排撰写|制定16周工作计划甘特图|
|第4小时|预期成果撰写|量化指标（AUC>0.85等）、交付物清单|
|第5小时|全文统稿润色|格式调整、参考文献整理|

**预期产出**：完整开题报告（约6000-8000字）

#### 📅 Day 3（2月27日）：外文翻译+环境搭建

|时间段|任务项|具体内容|
|:--|:--|:--|
|第1小时|外文翻译|使用AI辅助翻译BUSI数据集论文|
|第2小时|翻译润色|专业术语校对、格式调整|
|第3小时|环境搭建|安装conda、配置PyTorch MPS环境|
|第4小时|数据准备|下载BUSI数据集、编写数据加载代码|

**预期产出**：外文翻译稿（约5000字）、可运行的开发环境

#### 📅 Day 4（2月28日）：分类模型实现

|时间段|任务项|具体内容|
|:--|:--|:--|
|第1小时|数据预处理|图像标准化、数据增强pipeline|
|第2小时|数据集划分|训练/验证/测试集划分（7:1.5:1.5）|
|第2小时|分类模型搭建|ResNet18迁移学习实现|
|第1小时|训练流程编写|损失函数、优化器、训练循环|

**预期产出**：完整的分类模型训练代码

#### 📅 Day 5（3月1日）：分割+可解释性实现

|时间段|任务项|具体内容|
|:--|:--|:--|
|第2小时|U-Net模型|实现基础U-Net分割模型|
|第1小时|分割训练|Dice Loss、分割模型训练|
|第1小时|Grad-CAM实现|集成pytorch-grad-cam库|
|第1小时|可视化代码|热力图叠加、分割轮廓绘制|

**预期产出**：完整的分割模型和可解释性可视化代码

#### 📅 Day 6（3月2日）：实验运行+结果可视化

|时间段|任务项|具体内容|
|:--|:--|:--|
|第2小时|模型训练|运行分类和分割模型训练|
|第1小时|结果评估|计算AUC、Dice、F1等指标|
|第1小时|结果可视化|绘制ROC曲线、混淆矩阵、热力图示例|

**预期产出**：实验结果数据、可视化图表

#### 📅 Day 7（3月3日）：整理汇总+答辩PPT

|时间段|任务项|具体内容|
|:--|:--|:--|
|第1小时|材料整理|汇总所有文档、代码、结果|
|第2小时|PPT制作|按框架制作10页答辩PPT|
|第1小时|答辩准备|梳理可能被问到的问题，准备应答|

**预期产出**：答辩PPT、完整材料包

---

## 3. Mac M系列芯片环境配置指南

### 3.1 环境配置完整步骤

Mac M系列芯片（M1/M2/M3/M4）使用ARM架构，需要特别配置以获得GPU加速支持。PyTorch从1.12版本开始支持MPS（Metal Performance Shaders）后端，可实现接近NVIDIA CUDA的加速效果[1]。

**Step 1：安装Miniforge（ARM原生支持）**

```bash
# 下载Miniforge（ARM原生支持）
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
bash Miniforge3-MacOSX-arm64.sh

# 重新加载shell配置
source ~/.zshrc
```

**Step 2：创建项目虚拟环境**

```bash
# 创建Python 3.10环境
conda create -n busi_project python=3.10 -y
conda activate busi_project
```

**Step 3：安装PyTorch（MPS加速版）**

```bash
# 安装支持MPS的PyTorch
pip install torch torchvision torchaudio

# 验证MPS是否可用
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

**Step 4：安装项目完整依赖**

```bash
# 数据处理和科学计算
pip install numpy pandas scikit-learn matplotlib seaborn

# 图像处理和数据增强
pip install opencv-python pillow albumentations

# 深度学习工具
pip install pytorch-grad-cam tensorboard tqdm

# 可选：Jupyter支持
pip install jupyter notebook ipykernel
```

### 3.2 MPS设备使用代码模板

```python
import torch

def get_device():
    """获取最优计算设备（MPS > CUDA > CPU）"""
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✅ 使用 Apple MPS 加速")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("✅ 使用 NVIDIA CUDA 加速")
    else:
        device = torch.device("cpu")
        print("⚠️ 使用 CPU 计算")
    return device

# 使用示例
device = get_device()
model = model.to(device)
data = data.to(device)
```

### 3.3 推荐模型选择

针对Mac M系列芯片和时间约束，选择轻量级、训练快、效果稳定的模型方案[1]：

|模块|推荐方案|选择理由|
|:--|:--|:--|
|分类模型|ResNet18（预训练）|参数量小（11M）、训练快、迁移学习效果好|
|分割模型|基础U-Net（4层）|结构经典、实现简单、BUSI数据集上效果稳定|
|可解释性|pytorch-grad-cam库|开箱即用、支持多种CAM变体、文档完善|
|数据增强|Albumentations|速度快、医学图像增强支持好|

---

## 4. 完整可运行核心代码

### 4.1 项目目录结构

```
/usr/local/app/workspace/busi_project/
├── data/                          # 数据目录
│   ├── raw/                       # 原始BUSI数据集
│   │   ├── normal/
│   │   ├── benign/
│   │   └── malignant/
│   └── processed/                 # 预处理后的数据
├── src/                           # 源代码
│   ├── data/
│   │   ├── dataset.py             # 数据集类
│   │   └── transforms.py          # 数据增强
│   ├── models/
│   │   ├── classifier.py          # 分类模型
│   │   └── segmentor.py           # 分割模型
│   ├── utils/
│   │   ├── metrics.py             # 评价指标
│   │   └── visualization.py       # 可视化工具
│   └── train.py                   # 训练主脚本
├── outputs/                       # 输出目录
│   ├── models/                    # 模型权重
│   ├── figures/                   # 可视化图表
│   └── logs/                      # 训练日志
├── docs/                          # 文档
│   ├── 开题报告.docx
│   ├── 外文翻译.docx
│   └── 答辩PPT.pptx
├── requirements.txt
└── README.md
```

### 4.2 BUSI数据集加载与预处理

```python
"""
BUSI数据集加载和预处理模块
文件路径：/usr/local/app/workspace/busi_project/src/data/dataset.py
"""

import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
import albumentations as A
from albumentations.pytorch import ToTensorV2


class BUSIDataset(Dataset):
    """BUSI乳腺超声图像数据集"""
    
    def __init__(self, images, masks, labels, transform=None, task='classification'):
        """
        Args:
            images: 图像数组列表
            masks: 分割掩模数组列表
            labels: 标签列表
            transform: 数据增强变换
            task: 'classification' 或 'segmentation'
        """
        self.images = images
        self.masks = masks
        self.labels = labels
        self.transform = transform
        self.task = task
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = self.images[idx]
        mask = self.masks[idx] if self.masks is not None else None
        label = self.labels[idx]
        
        # 转换为3通道（适配预训练模型）
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        if self.transform:
            if self.task == 'segmentation' and mask is not None:
                transformed = self.transform(image=image, mask=mask)
                image = transformed['image']
                mask = transformed['mask']
            else:
                transformed = self.transform(image=image)
                image = transformed['image']
        
        if self.task == 'classification':
            return image, torch.tensor(label, dtype=torch.long)
        else:
            mask = torch.tensor(mask, dtype=torch.float32).unsqueeze(0) / 255.0
            return image, mask, torch.tensor(label, dtype=torch.long)


def load_busi_dataset(data_dir):
    """
    加载BUSI数据集
    
    Args:
        data_dir: 数据集根目录路径
        
    Returns:
        images: 图像数组列表
        masks: 分割掩模数组列表
        labels: 标签列表
    """
    images, masks, labels = [], [], []
    class_map = {'normal': 0, 'benign': 1, 'malignant': 2}
    
    for class_name, label in class_map.items():
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.exists(class_dir):
            print(f"⚠️ 目录不存在: {class_dir}")
            continue
            
        for img_name in os.listdir(class_dir):
            # 跳过mask文件
            if '_mask' in img_name or not img_name.endswith('.png'):
                continue
                
            img_path = os.path.join(class_dir, img_name)
            mask_path = img_path.replace('.png', '_mask.png')
            
            # 读取图像
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, (224, 224))
            images.append(img)
            labels.append(label)
            
            # 读取mask（如果存在）
            if os.path.exists(mask_path):
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                mask = cv2.resize(mask, (224, 224))
                masks.append(mask)
            else:
                masks.append(np.zeros((224, 224), dtype=np.uint8))
    
    print(f"✅ 数据集加载完成: {len(images)} 张图像")
    print(f"   类别分布: Normal={labels.count(0)}, Benign={labels.count(1)}, Malignant={labels.count(2)}")
    
    return np.array(images), np.array(masks), np.array(labels)


def get_transforms(is_train=True):
    """获取数据增强变换"""
    if is_train:
        return A.Compose([
            A.Resize(224, 224),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.Rotate(limit=15, p=0.5),
            A.RandomBrightnessContrast(p=0.3),
            A.GaussNoise(p=0.2),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
    else:
        return A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])


def prepare_dataloaders(data_dir, batch_size=16, task='classification'):
    """
    准备训练、验证、测试数据加载器
    
    Args:
        data_dir: 数据集目录
        batch_size: 批次大小
        task: 'classification' 或 'segmentation'
    
    Returns:
        train_loader, val_loader, test_loader
    """
    # 加载数据
    images, masks, labels = load_busi_dataset(data_dir)
    
    # 划分数据集 (7:1.5:1.5)
    X_train, X_temp, y_train, y_temp, m_train, m_temp = train_test_split(
        images, labels, masks, test_size=0.3, stratify=labels, random_state=42
    )
    X_val, X_test, y_val, y_test, m_val, m_test = train_test_split(
        X_temp, y_temp, m_temp, test_size=0.5, stratify=y_temp, random_state=42
    )
    
    print(f"📊 数据集划分: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    # 创建数据集
    train_dataset = BUSIDataset(X_train, m_train, y_train, get_transforms(True), task)
    val_dataset = BUSIDataset(X_val, m_val, y_val, get_transforms(False), task)
    test_dataset = BUSIDataset(X_test, m_test, y_test, get_transforms(False), task)
    
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    return train_loader, val_loader, test_loader
```

### 4.3 ResNet18分类模型完整实现

```python
"""
ResNet18分类模型
文件路径：/usr/local/app/workspace/busi_project/src/models/classifier.py
"""

import torch
import torch.nn as nn
import torchvision.models as models
from tqdm import tqdm
import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, confusion_matrix


class BUSIClassifier(nn.Module):
    """基于ResNet18的乳腺超声图像分类器"""
    
    def __init__(self, num_classes=3, pretrained=True):
        super(BUSIClassifier, self).__init__()
        
        # 加载预训练ResNet18
        self.backbone = models.resnet18(weights='IMAGENET1K_V1' if pretrained else None)
        
        # 修改最后的全连接层适配三分类
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


def train_classifier(model, train_loader, val_loader, device, epochs=30, lr=1e-4):
    """
    训练分类模型
    
    Args:
        model: 分类模型
        train_loader: 训练数据加载器
        val_loader: 验证数据加载器
        device: 计算设备
        epochs: 训练轮数
        lr: 学习率
    
    Returns:
        model: 训练好的模型
        history: 训练历史
    """
    model = model.to(device)
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5)
    
    history = {'train_loss': [], 'val_loss': [], 'val_acc': []}
    best_val_acc = 0.0
    
    for epoch in range(epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
        for images, labels in pbar:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            pbar.set_postfix({'loss': loss.item()})
        
        train_loss /= len(train_loader)
        
        # 验证阶段
        model.eval()
        val_loss = 0.0
        all_preds, all_labels = [], []
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                preds = torch.argmax(outputs, dim=1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        val_loss /= len(val_loader)
        val_acc = accuracy_score(all_labels, all_preds)
        
        # 学习率调整
        scheduler.step(val_loss)
        
        # 记录历史
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f'Epoch {epoch+1}: Train Loss={train_loss:.4f}, Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}')
        
        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), '/usr/local/app/workspace/busi_project/outputs/models/best_classifier.pth')
            print(f'  ✅ 保存最佳模型 (Acc={val_acc:.4f})')
    
    return model, history


def evaluate_classifier(model, test_loader, device):
    """
    评估分类模型
    
    Args:
        model: 分类模型
        test_loader: 测试数据加载器
        device: 计算设备
    
    Returns:
        metrics: 评估指标字典
    """
    model.eval()
    all_preds, all_labels, all_probs = [], [], []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(outputs, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    # 计算指标
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted')
    
    # 计算多分类AUC（OvR方式）
    try:
        auc = roc_auc_score(all_labels, all_probs, multi_class='ovr')
    except:
        auc = 0.0
    
    cm = confusion_matrix(all_labels, all_preds)
    
    metrics = {
        'accuracy': accuracy,
        'f1_score': f1,
        'auc': auc,
        'confusion_matrix': cm,
        'predictions': all_preds,
        'labels': all_labels,
        'probabilities': all_probs
    }
    
    print(f"\n📊 分类模型评估结果:")
    print(f"   Accuracy: {accuracy:.4f}")
    print(f"   F1-Score: {f1:.4f}")
    print(f"   AUC: {auc:.4f}")
    print(f"   混淆矩阵:\n{cm}")
    
    return metrics
```

### 4.4 U-Net分割模型完整实现

```python
"""
U-Net分割模型
文件路径：/usr/local/app/workspace/busi_project/src/models/segmentor.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm
import numpy as np


class DoubleConv(nn.Module):
    """U-Net双卷积块"""
    
    def __init__(self, in_channels, out_channels):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        return self.conv(x)


class UNet(nn.Module):
    """基础U-Net分割模型（4层编码-解码）"""
    
    def __init__(self, in_channels=3, out_channels=1, features=[64, 128, 256, 512]):
        super(UNet, self).__init__()
        
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # 编码器（下采样）
        for feature in features:
            self.downs.append(DoubleConv(in_channels, feature))
            in_channels = feature
        
        # 瓶颈层
        self.bottleneck = DoubleConv(features[-1], features[-1] * 2)
        
        # 解码器（上采样）
        for feature in reversed(features):
            self.ups.append(nn.ConvTranspose2d(feature * 2, feature, kernel_size=2, stride=2))
            self.ups.append(DoubleConv(feature * 2, feature))
        
        # 输出层
        self.final_conv = nn.Conv2d(features[0], out_channels, kernel_size=1)
    
    def forward(self, x):
        skip_connections = []
        
        # 编码器
        for down in self.downs:
            x = down(x)
            skip_connections.append(x)
            x = self.pool(x)
        
        x = self.bottleneck(x)
        skip_connections = skip_connections[::-1]
        
        # 解码器
        for idx in range(0, len(self.ups), 2):
            x = self.ups[idx](x)
            skip = skip_connections[idx // 2]
            
            # 处理尺寸不匹配
            if x.shape != skip.shape:
                x = F.interpolate(x, size=skip.shape[2:])
            
            x = torch.cat([skip, x], dim=1)
            x = self.ups[idx + 1](x)
        
        return torch.sigmoid(self.final_conv(x))


class DiceLoss(nn.Module):
    """Dice损失函数"""
    
    def __init__(self, smooth=1e-6):
        super(DiceLoss, self).__init__()
        self.smooth = smooth
    
    def forward(self, pred, target):
        pred = pred.view(-1)
        target = target.view(-1)
        
        intersection = (pred * target).sum()
        dice = (2. * intersection + self.smooth) / (pred.sum() + target.sum() + self.smooth)
        
        return 1 - dice


def train_segmentor(model, train_loader, val_loader, device, epochs=30, lr=1e-4):
    """
    训练分割模型
    
    Args:
        model: 分割模型
        train_loader: 训练数据加载器
        val_loader: 验证数据加载器
        device: 计算设备
        epochs: 训练轮数
        lr: 学习率
    
    Returns:
        model: 训练好的模型
        history: 训练历史
    """
    model = model.to(device)
    
    # 损失函数（Dice + BCE组合）
    dice_loss = DiceLoss()
    bce_loss = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5)
    
    history = {'train_loss': [], 'val_loss': [], 'val_dice': []}
    best_dice = 0.0
    
    for epoch in range(epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
        for images, masks, _ in pbar:
            images, masks = images.to(device), masks.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            
            loss = 0.5 * dice_loss(outputs, masks) + 0.5 * bce_loss(outputs, masks)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            pbar.set_postfix({'loss': loss.item()})
        
        train_loss /= len(train_loader)
        
        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_dice = 0.0
        
        with torch.no_grad():
            for images, masks, _ in val_loader:
                images, masks = images.to(device), masks.to(device)
                outputs = model(images)
                
                loss = 0.5 * dice_loss(outputs, masks) + 0.5 * bce_loss(outputs, masks)
                val_loss += loss.item()
                
                # 计算Dice系数
                dice = calculate_dice(outputs, masks)
                val_dice += dice
        
        val_loss /= len(val_loader)
        val_dice /= len(val_loader)
        
        scheduler.step(val_loss)
        
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_dice'].append(val_dice)
        
        print(f'Epoch {epoch+1}: Train Loss={train_loss:.4f}, Val Loss={val_loss:.4f}, Val Dice={val_dice:.4f}')
        
        if val_dice > best_dice:
            best_dice = val_dice
            torch.save(model.state_dict(), '/usr/local/app/workspace/busi_project/outputs/models/best_segmentor.pth')
            print(f'  ✅ 保存最佳模型 (Dice={val_dice:.4f})')
    
    return model, history


def calculate_dice(pred, target, threshold=0.5):
    """计算Dice系数"""
    pred = (pred > threshold).float()
    smooth = 1e-6
    
    intersection = (pred * target).sum()
    dice = (2. * intersection + smooth) / (pred.sum() + target.sum() + smooth)
    
    return dice.item()


def calculate_iou(pred, target, threshold=0.5):
    """计算IoU（交并比）"""
    pred = (pred > threshold).float()
    smooth = 1e-6
    
    intersection = (pred * target).sum()
    union = pred.sum() + target.sum() - intersection
    iou = (intersection + smooth) / (union + smooth)
    
    return iou.item()


def evaluate_segmentor(model, test_loader, device):
    """评估分割模型"""
    model.eval()
    total_dice, total_iou = 0.0, 0.0
    
    with torch.no_grad():
        for images, masks, _ in test_loader:
            images, masks = images.to(device), masks.to(device)
            outputs = model(images)
            
            total_dice += calculate_dice(outputs, masks)
            total_iou += calculate_iou(outputs, masks)
    
    avg_dice = total_dice / len(test_loader)
    avg_iou = total_iou / len(test_loader)
    
    print(f"\n📊 分割模型评估结果:")
    print(f"   Dice: {avg_dice:.4f}")
    print(f"   IoU: {avg_iou:.4f}")
    
    return {'dice': avg_dice, 'iou': avg_iou}
```

### 4.5 Grad-CAM可解释性可视化代码

```python
"""
Grad-CAM可解释性可视化模块
文件路径：/usr/local/app/workspace/busi_project/src/utils/visualization.py
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import torch
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from sklearn.metrics import roc_curve, auc, confusion_matrix
import seaborn as sns


def generate_gradcam(model, image_tensor, target_layer, device):
    """
    生成Grad-CAM热力图
    
    Args:
        model: 分类模型
        image_tensor: 输入图像张量 [1, C, H, W]
        target_layer: 目标层（通常是最后一个卷积层）
        device: 计算设备
    
    Returns:
        cam_image: 带热力图的图像
        grayscale_cam: 灰度热力图
    """
    model = model.to(device)
    model.eval()
    
    # 创建Grad-CAM对象
    cam = GradCAM(model=model, target_layers=[target_layer], use_cuda=False)
    
    # 生成热力图
    grayscale_cam = cam(input_tensor=image_tensor.to(device))
    grayscale_cam = grayscale_cam[0, :]
    
    # 将原始图像转换为numpy格式
    image_np = image_tensor.squeeze().permute(1, 2, 0).numpy()
    image_np = (image_np - image_np.min()) / (image_np.max() - image_np.min())
    
    # 叠加热力图
    cam_image = show_cam_on_image(image_np, grayscale_cam, use_rgb=True)
    
    return cam_image, grayscale_cam


def visualize_gradcam_examples(model, test_loader, device, save_path, num_examples=6):
    """
    可视化多个Grad-CAM示例
    
    Args:
        model: 分类模型
        test_loader: 测试数据加载器
        device: 计算设备
        save_path: 保存路径
        num_examples: 示例数量
    """
    model.eval()
    target_layer = model.backbone.layer4[-1]  # ResNet18的最后一个卷积层
    
    class_names = ['Normal', 'Benign', 'Malignant']
    
    fig, axes = plt.subplots(2, num_examples, figsize=(4*num_examples, 8))
    
    images_shown = 0
    for images, labels in test_loader:
        for i in range(len(images)):
            if images_shown >= num_examples:
                break
            
            image = images[i:i+1]
            label = labels[i].item()
            
            # 生成Grad-CAM
            cam_image, _ = generate_gradcam(model, image, target_layer, device)
            
            # 原始图像
            orig_img = image.squeeze().permute(1, 2, 0).numpy()
            orig_img = (orig_img - orig_img.min()) / (orig_img.max() - orig_img.min())
            
            axes[0, images_shown].imshow(orig_img)
            axes[0, images_shown].set_title(f'Original\n{class_names[label]}')
            axes[0, images_shown].axis('off')
            
            axes[1, images_shown].imshow(cam_image)
            axes[1, images_shown].set_title(f'Grad-CAM')
            axes[1, images_shown].axis('off')
            
            images_shown += 1
        
        if images_shown >= num_examples:
            break
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Grad-CAM可视化已保存: {save_path}")


def plot_roc_curves(labels, probabilities, save_path):
    """
    绘制多分类ROC曲线
    
    Args:
        labels: 真实标签
        probabilities: 预测概率 [N, num_classes]
        save_path: 保存路径
    """
    class_names = ['Normal', 'Benign', 'Malignant']
    colors = ['blue', 'green', 'red']
    
    plt.figure(figsize=(8, 6))
    
    for i, (name, color) in enumerate(zip(class_names, colors)):
        # 二值化标签
        binary_labels = (labels == i).astype(int)
        
        fpr, tpr, _ = roc_curve(binary_labels, probabilities[:, i])
        roc_auc = auc(fpr, tpr)
        
        plt.plot(fpr, tpr, color=color, lw=2, label=f'{name} (AUC = {roc_auc:.3f})')
    
    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curves - BUSI Classification', fontsize=14)
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ ROC曲线已保存: {save_path}")


def plot_confusion_matrix(cm, save_path):
    """
    绘制混淆矩阵
    
    Args:
        cm: 混淆矩阵
        save_path: 保存路径
    """
    class_names = ['Normal', 'Benign', 'Malignant']
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted', fontsize=12)
    plt.ylabel('True', fontsize=12)
    plt.title('Confusion Matrix - BUSI Classification', fontsize=14)
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ 混淆矩阵已保存: {save_path}")


def visualize_segmentation_results(model, test_loader, device, save_path, num_examples=4):
    """
    可视化分割结果
    
    Args:
        model: 分割模型
        test_loader: 测试数据加载器
        device: 计算设备
        save_path: 保存路径
        num_examples: 示例数量
    """
    model.eval()
    
    fig, axes = plt.subplots(3, num_examples, figsize=(4*num_examples, 12))
    
    images_shown = 0
    with torch.no_grad():
        for images, masks, _ in test_loader:
            for i in range(len(images)):
                if images_shown >= num_examples:
                    break
                
                image = images[i:i+1].to(device)
                mask = masks[i].squeeze().numpy()
                
                # 预测
                pred = model(image).squeeze().cpu().numpy()
                pred_binary = (pred > 0.5).astype(np.uint8)
                
                # 原始图像
                orig_img = images[i].permute(1, 2, 0).numpy()
                orig_img = (orig_img - orig_img.min()) / (orig_img.max() - orig_img.min())
                
                axes[0, images_shown].imshow(orig_img)
                axes[0, images_shown].set_title('Original')
                axes[0, images_shown].axis('off')
                
                axes[1, images_shown].imshow(mask, cmap='gray')
                axes[1, images_shown].set_title('Ground Truth')
                axes[1, images_shown].axis('off')
                
                axes[2, images_shown].imshow(pred_binary, cmap='gray')
                axes[2, images_shown].set_title('Prediction')
                axes[2, images_shown].axis('off')
                
                images_shown += 1
            
            if images_shown >= num_examples:
                break
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ 分割结果可视化已保存: {save_path}")


def plot_training_history(history, save_path, task='classification'):
    """
    绘制训练历史曲线
    
    Args:
        history: 训练历史字典
        save_path: 保存路径
        task: 'classification' 或 'segmentation'
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    epochs = range(1, len(history['train_loss']) + 1)
    
    # 损失曲线
    axes[0].plot(epochs, history['train_loss'], 'b-', label='Train Loss')
    axes[0].plot(epochs, history['val_loss'], 'r-', label='Val Loss')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 指标曲线
    if task == 'classification':
        axes[1].plot(epochs, history['val_acc'], 'g-', label='Val Accuracy')
        axes[1].set_ylabel('Accuracy')
        axes[1].set_title('Validation Accuracy')
    else:
        axes[1].plot(epochs, history['val_dice'], 'g-', label='Val Dice')
        axes[1].set_ylabel('Dice Score')
        axes[1].set_title('Validation Dice')
    
    axes[1].set_xlabel('Epoch')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ 训练历史曲线已保存: {save_path}")
```

### 4.6 主训练脚本

```python
"""
主训练脚本
文件路径：/usr/local/app/workspace/busi_project/src/train.py
"""

import os
import torch

# 导入自定义模块
from data.dataset import prepare_dataloaders
from models.classifier import BUSIClassifier, train_classifier, evaluate_classifier
from models.segmentor import UNet, train_segmentor, evaluate_segmentor
from utils.visualization import (
    plot_roc_curves, plot_confusion_matrix, plot_training_history,
    visualize_gradcam_examples, visualize_segmentation_results
)


def main():
    # ==================== 配置参数 ====================
    DATA_DIR = '/usr/local/app/workspace/busi_project/data/raw'
    OUTPUT_DIR = '/usr/local/app/workspace/busi_project/outputs'
    
    BATCH_SIZE = 16
    EPOCHS_CLS = 30
    EPOCHS_SEG = 30
    LEARNING_RATE = 1e-4
    
    # 创建输出目录
    os.makedirs(f'{OUTPUT_DIR}/models', exist_ok=True)
    os.makedirs(f'{OUTPUT_DIR}/figures', exist_ok=True)
    os.makedirs(f'{OUTPUT_DIR}/logs', exist_ok=True)
    
    # ==================== 设备配置 ====================
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✅ 使用 Apple MPS 加速")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("✅ 使用 NVIDIA CUDA 加速")
    else:
        device = torch.device("cpu")
        print("⚠️ 使用 CPU 计算")
    
    # ==================== 分类模型训练 ====================
    print("\n" + "="*50)
    print("🔬 开始训练分类模型")
    print("="*50)
    
    # 准备数据
    train_loader_cls, val_loader_cls, test_loader_cls = prepare_dataloaders(
        DATA_DIR, BATCH_SIZE, task='classification'
    )
    
    # 创建模型
    classifier = BUSIClassifier(num_classes=3, pretrained=True)
    
    # 训练
    classifier, cls_history = train_classifier(
        classifier, train_loader_cls, val_loader_cls, device, EPOCHS_CLS, LEARNING_RATE
    )
    
    # 评估
    cls_metrics = evaluate_classifier(classifier, test_loader_cls, device)
    
    # 可视化
    plot_training_history(cls_history, f'{OUTPUT_DIR}/figures/cls_training_history.png', 'classification')
    plot_roc_curves(cls_metrics['labels'], cls_metrics['probabilities'], f'{OUTPUT_DIR}/figures/roc_curves.png')
    plot_confusion_matrix(cls_metrics['confusion_matrix'], f'{OUTPUT_DIR}/figures/confusion_matrix.png')
    visualize_gradcam_examples(classifier, test_loader_cls, device, f'{OUTPUT_DIR}/figures/gradcam_examples.png')
    
    # ==================== 分割模型训练 ====================
    print("\n" + "="*50)
    print("🔬 开始训练分割模型")
    print("="*50)
    
    # 准备数据
    train_loader_seg, val_loader_seg, test_loader_seg = prepare_dataloaders(
        DATA_DIR, BATCH_SIZE, task='segmentation'
    )
    
    # 创建模型
    segmentor = UNet(in_channels=3, out_channels=1)
    
    # 训练
    segmentor, seg_history = train_segmentor(
        segmentor, train_loader_seg, val_loader_seg, device, EPOCHS_SEG, LEARNING_RATE
    )
    
    # 评估
    seg_metrics = evaluate_segmentor(segmentor, test_loader_seg, device)
    
    # 可视化
    plot_training_history(seg_history, f'{OUTPUT_DIR}/figures/seg_training_history.png', 'segmentation')
    visualize_segmentation_results(segmentor, test_loader_seg, device, f'{OUTPUT_DIR}/figures/segmentation_examples.png')
    
    # ==================== 结果汇总 ====================
    print("\n" + "="*50)
    print("📊 实验结果汇总")
    print("="*50)
    print(f"\n分类模型:")
    print(f"  - Accuracy: {cls_metrics['accuracy']:.4f}")
    print(f"  - F1-Score: {cls_metrics['f1_score']:.4f}")
    print(f"  - AUC: {cls_metrics['auc']:.4f}")
    print(f"\n分割模型:")
    print(f"  - Dice: {seg_metrics['dice']:.4f}")
    print(f"  - IoU: {seg_metrics['iou']:.4f}")
    print(f"\n✅ 所有结果已保存至: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
```

---

## 5. 开题报告撰写模板

### 5.1 标准八章节结构

开题报告是开题答辩的核心材料，需要清晰阐述研究的背景、意义、方法和预期成果[1]。

|章节|标题|字数建议|核心内容|
|:--|:--|:--|:--|
|1|选题背景与意义|800-1000字|乳腺癌流行病学、超声诊断现状、AI辅助诊断价值|
|2|国内外研究现状|1000-1500字|深度学习医学图像分析综述、BUSI相关研究|
|3|研究目标与内容|600-800字|三大目标：分类、分割、可解释性系统|
|4|技术路线与方法|800-1000字|整体框架、模型选择依据、实验设计|
|5|实验设计与评价指标|600-800字|数据集划分、评价指标定义|
|6|进度安排|400-500字|16周工作计划甘特图|
|7|预期成果|300-400字|量化指标、交付物清单|
|8|参考文献|--|10-15篇核心文献|

### 5.2 各章节写作要点

**第1章 选题背景与意义**

本章需要从宏观到微观层层递进。首先引用WHO全球乳腺癌发病率数据（每年约230万新发病例），强调早期筛查的重要性（5年生存率差异：早期>90% vs 晚期<30%）。接着指出超声检查的优势（无辐射、成本低、普及率高）和局限性（依赖医生经验、主观性强）。最后引出AI辅助诊断的价值：提高效率、降低漏诊率、增强诊断一致性。

**第2章 国内外研究现状**

本章需要系统梳理深度学习在医学图像分析领域的发展脉络。从CNN的演进（AlexNet→VGG→ResNet→EfficientNet）到Transformer在医学影像中的应用（ViT、Swin Transformer），再到U-Net系列分割模型的演进（U-Net→Attention U-Net→TransUNet）。重点介绍BUSI数据集上的已有研究成果（准确率约85-90%），并指出现有研究的不足：可解释性欠缺、临床落地困难。

**第3章 研究目标与内容**

明确三大研究目标：（1）在BUSI数据集上实现高精度三分类（正常/良性/恶性），目标AUC>0.85；（2）实现病灶区域精确分割，目标Dice>0.75；（3）构建具有Grad-CAM可解释性的诊断辅助原型系统，可视化模型关注区域[1]。

**第4章 技术路线与方法**

本章需要绘制清晰的技术路线图，展示从数据预处理、模型训练、评估到可视化输出的完整流程。说明模型选择依据：选择ResNet18而非更复杂模型是因为其参数量适中、训练效率高、迁移学习效果好；选择基础U-Net是因为其在医学图像分割任务上表现稳定。详细阐述Grad-CAM原理：通过计算目标类别相对于特征图的梯度，生成热力图标识模型关注区域。

**第5章 实验设计与评价指标**

详细描述BUSI数据集（780张图像，三分类）和数据划分策略（7:1.5:1.5）。定义评价指标体系：分类任务使用Accuracy、AUC、F1-score、Sensitivity、Specificity；分割任务使用Dice系数和IoU。说明采用分层抽样和5折交叉验证确保结果可靠性[1]。

### 5.3 核心参考文献

以下文献可直接用于开题报告引用，均为深度学习医学图像分析领域的经典论文[1]：

|序号|文献信息|引用价值|
|:--|:--|:--|
|1|Al-Dhabyani W, et al. Dataset of Breast Ultrasound Images. Data in Brief, 2020|BUSI数据集原始论文，必引|
|2|He K, et al. Deep Residual Learning for Image Recognition. CVPR 2016|ResNet原始论文|
|3|Ronneberger O, et al. U-Net: Convolutional Networks for Biomedical Image Segmentation. MICCAI 2015|U-Net原始论文|
|4|Selvaraju RR, et al. Grad-CAM: Visual Explanations from Deep Networks. ICCV 2017|Grad-CAM原始论文|
|5|Dosovitskiy A, et al. An Image is Worth 16x16 Words: Transformers for Image Recognition. ICLR 2021|ViT论文|

---

## 6. 外文翻译快速方案

### 6.1 推荐翻译论文

推荐翻译Al-Dhabyani W等人发表在Data in Brief期刊的"Dataset of Breast Ultrasound Images"论文[1]。选择该论文的理由是：与毕业论文主题高度相关（BUSI数据集原始论文），篇幅适中（约5000英文单词），结构清晰，专业术语集中，翻译难度适合本科水平。

### 6.2 高效翻译工作流程

|步骤|工具|操作说明|预计耗时|
|:--|:--|:--|:--|
|1|DeepL/Google翻译|全文初步机器翻译|10分钟|
|2|GPT-4/Claude|专业术语校对和润色|30分钟|
|3|人工审校|检查关键术语一致性|20分钟|
|4|格式调整|按学校模板排版|15分钟|

### 6.3 医学图像领域术语对照表

|英文术语|中文翻译|英文术语|中文翻译|
|:--|:--|:--|:--|
|Breast Ultrasound|乳腺超声|Deep Learning|深度学习|
|Benign|良性|Malignant|恶性|
|Lesion|病灶|Tumor|肿瘤|
|Segmentation Mask|分割掩模|Ground Truth|真值标注|
|Sensitivity|灵敏度|Specificity|特异度|
|Convolutional Neural Network|卷积神经网络|Feature Extraction|特征提取|
|Transfer Learning|迁移学习|Data Augmentation|数据增强|
|ROC Curve|受试者工作特征曲线|AUC|曲线下面积|

---

## 7. 答辩PPT框架

### 7.1 十页PPT结构

答辩PPT需要在有限时间内清晰展示研究的核心内容和成果，建议控制在10分钟以内[1]。

|页码|标题|核心要点|时间分配|
|:--|:--|:--|:--|
|1|封面|论文题目、姓名、导师、日期|15秒|
|2|研究背景|乳腺癌危害、超声诊断现状、AI价值|1分钟|
|3|研究目标|三大目标：分类、分割、可解释性|30秒|
|4|技术路线|整体框架图、数据流程|1分钟|
|5|数据集介绍|BUSI数据集、样本分布、预处理|45秒|
|6|模型设计|ResNet18分类、U-Net分割、Grad-CAM|1.5分钟|
|7|实验结果（分类）|混淆矩阵、ROC曲线、AUC值|1分钟|
|8|实验结果（分割+可解释性）|分割示例、热力图展示|1分钟|
|9|总结与展望|主要贡献、局限性、未来工作|1分钟|
|10|致谢|感谢导师和评委|15秒|

### 7.2 重点页面详细要点

**第2页-研究背景**：使用1个核心数据（全球乳腺癌每年新发病例230万），1个关键对比（人工诊断 vs AI辅助诊断效率），1句话引出问题（现有AI系统缺乏可解释性，难以获得临床信任）。

**第6页-模型设计（重点页）**：左侧展示ResNet18网络结构简图，中间展示U-Net编码-解码结构图，右侧展示Grad-CAM热力图生成流程，底部用箭头说明三者如何协同工作。

**第7页-分类实验结果**：展示混淆矩阵（3×3热力图形式），ROC曲线（三条曲线对应三个类别），核心指标表格（Accuracy、AUC、F1-score），用数字突出实验效果。

**第8页-分割与可解释性结果**：展示2-3个典型分割样例（原图→预测分割→真值对比），2-3个Grad-CAM热力图示例，标注Dice系数和IoU数值。

---

## 8. 风险预案与应急方案

### 8.1 常见问题解决方案

在实际执行过程中可能遇到各种技术和时间问题，以下是针对性的解决方案[1]：

|风险类型|具体问题|解决方案|备选方案|
|:--|:--|:--|:--|
|环境问题|MPS不支持某些操作|降级使用CPU训练|减少batch size，耐心等待|
|数据问题|BUSI数据集下载失败|使用Kaggle镜像源|联系同学拷贝数据|
|训练问题|模型不收敛|检查学习率，使用预训练权重|简化模型结构|
|时间问题|某阶段超时|压缩后续阶段时间|优先保证开题报告质量|
|结果问题|指标未达预期|调整超参数，增加数据增强|据实汇报，强调探索过程|

### 8.2 任务优先级排序

核心原则是开题报告和答辩PPT是刚性任务，代码实现有弹性空间：

|优先级|任务|弹性空间|说明|
|:--|:--|:--|:--|
|P0（必须完成）|开题报告|无弹性|3月8日前必须提交|
|P0（必须完成）|外文翻译|无弹性|开题答辩必备材料|
|P1（高优先级）|分类模型实现|可简化|可用更简单的模型（如VGG16）|
|P2（中优先级）|分割模型实现|可延后|可延后到中期检查前完成|
|P2（中优先级）|可解释性实现|可简化|可使用开源代码直接调用|
|P3（可选）|模型优化调参|可省略|时间充裕时再进行|

### 8.3 时间弹性安排

如果某天任务未完成，可占用周末时间（3月4日-5日）进行补救，确保3月6日前完成所有材料，留2天缓冲期进行最终检查和调整。应急时间表建议在Day 1-2集中精力完成开题报告，这是最紧迫的交付物，后续的代码开发即使进度落后也不影响开题答辩。

---

## 参考文献

[1] README.md, 2026年2月. 基于深度学习的乳腺癌超声图像自动诊断系统-毕业论文课题说明. /usr/local/app/attachment/README.md