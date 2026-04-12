# 评估模块使用指南

## 📋 模块概述

本评估模块独立于实验流程，提供完整的模型评估与可视化功能。

### 模块结构

```
src/evaluation/
├── __init__.py           # 模块初始化
├── metrics.py            # 评估指标计算
├── visualization.py      # 可视化工具
├── gradcam.py           # Grad-CAM热力图
├── report.py            # 报告生成
├── evaluate.py          # 主评估脚本
└── README.md            # 本文档
```

## 🎯 功能特性

### 1. 评估指标计算 (`metrics.py`)

支持的指标：
- **整体指标**：准确率、精确率、召回率、F1分数
- **类别指标**：每个类别的精确率、召回率、特异度、F1分数
- **AUC指标**：每个类别的AUC、宏平均AUC
- **混淆矩阵**：详细的混淆矩阵

### 2. 可视化工具 (`visualization.py`)

- **混淆矩阵**：带准确率标注的热力图
- **ROC曲线**：多类别ROC曲线
- **训练曲线**：损失和准确率曲线
- **指标对比**：各类别指标对比柱状图

### 3. Grad-CAM可视化 (`gradcam.py`)

- **热力图生成**：生成类激活图
- **注意力可视化**：叠加到原始图像
- **多样本对比**：批量生成Grad-CAM可视化

### 4. 报告生成 (`report.py`)

- **Markdown报告**：可读性强的格式化报告
- **JSON结果**：完整的结构化数据
- **实验对比**：多实验对比表格

## 🚀 快速开始

### 基本使用

```bash
# 评估训练好的模型
python evaluate.py \
    --model-path src/experiment/stage4/outputs/exp1_seed2024/best_model.pth \
    --data-dir data/raw/Dataset_BUSI_with_GT \
    --test-indices outputs/test_indices.json \
    --output-dir outputs/evaluation \
    --experiment-name "Stage4 Best Model"
```

### 参数说明

| 参数 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| `--model-path` | ✅ | 模型文件路径 | - |
| `--data-dir` | ✅ | 数据目录 | - |
| `--test-indices` | ✅ | 测试集索引JSON文件 | - |
| `--output-dir` | ❌ | 输出目录 | `outputs/evaluation` |
| `--batch-size` | ❌ | 批次大小 | 32 |
| `--dropout` | ❌ | Dropout比例 | 0.25 |
| `--device` | ❌ | 计算设备 | auto |
| `--experiment-name` | ❌ | 实验名称 | Model Evaluation |
| `--gradcam-samples` | ❌ | Grad-CAM样本数 | 9 |

## 📝 准备测试集索引

评估需要测试集索引文件（JSON格式）：

```python
# 生成测试集索引示例
import json
import torch
from torch.utils.data import random_split
from src.experiment.stage4.dataset import BUSIDatasetWithIndices

# 加载数据集
dataset = BUSIDatasetWithIndices('data/raw/Dataset_BUSI_with_GT')

# 划分数据集（与训练时相同的种子）
train_size = int(0.7 * len(dataset))
val_size = int(0.15 * len(dataset))
test_size = len(dataset) - train_size - val_size

train_set, val_set, test_set = random_split(
    dataset,
    [train_size, val_size, test_size],
    generator=torch.Generator().manual_seed(2024)
)

# 保存测试集索引
test_indices = test_set.indices
with open('outputs/test_indices.json', 'w') as f:
    json.dump(test_indices, f)

print(f"测试集大小: {len(test_indices)}")
```

## 📊 输出文件

评估完成后，输出目录包含：

```
outputs/evaluation/
├── evaluation_report.md       # Markdown格式报告
├── evaluation_results.json    # JSON格式完整结果
├── confusion_matrix.png       # 混淆矩阵可视化
├── roc_curves.png            # ROC曲线
├── metrics_comparison.png    # 指标对比图
└── gradcam_samples.png       # Grad-CAM可视化（可选）
```

## 🔧 高级用法

### 1. 单独使用指标计算模块

```python
from metrics import MetricsCalculator
import numpy as np

# 预测结果
y_true = np.array([0, 1, 2, 0, 1, 2])
y_pred = np.array([0, 1, 1, 0, 1, 2])
y_prob = np.random.rand(6, 3)  # 预测概率
y_prob = y_prob / y_prob.sum(axis=1, keepdims=True)

# 计算指标
calculator = MetricsCalculator(class_names=['benign', 'malignant', 'normal'])
metrics = calculator.calculate_all_metrics(y_true, y_pred, y_prob)

# 打印指标
calculator.print_metrics(metrics)
```

### 2. 单独使用可视化模块

```python
from visualization import VisualizationManager
import numpy as np

viz_manager = VisualizationManager()

# 混淆矩阵
cm = np.array([[57, 5, 4], [1, 29, 0], [1, 0, 20]])
viz_manager.plot_confusion_matrix(
    cm,
    class_names=['benign', 'malignant', 'normal'],
    save_path='confusion_matrix.png',
    title='Confusion Matrix'
)

# ROC曲线
roc_data = {
    'benign': {'fpr': [...], 'tpr': [...]},
    'malignant': {'fpr': [...], 'tpr': [...]},
    'normal': {'fpr': [...], 'tpr': [...]}
}
viz_manager.plot_roc_curves(
    roc_data,
    class_names=['benign', 'malignant', 'normal'],
    save_path='roc_curves.png'
)
```

### 3. 单独使用Grad-CAM模块

```python
import torch
from gradcam import GradCAM, visualize_gradcam_samples

# 加载模型
model = load_model('best_model.pth', device)
model.eval()

# 创建Grad-CAM实例
grad_cam = GradCAM(model, target_layer='layer4')

# 生成热力图
input_tensor = preprocess_image('test_image.png')
original, heatmap, overlay = grad_cam.visualize(
    'test_image.png',
    input_tensor,
    target_class=1
)
```

### 4. 单独生成报告

```python
from report import ReportGenerator

generator = ReportGenerator('output_dir')

# 生成Markdown报告
generator.generate_markdown_report(
    metrics=metrics,
    model_info={
        'model_path': 'best_model.pth',
        'architecture': 'ResNet-18',
        'test_size': 117
    },
    experiment_name='My Experiment'
)

# 保存JSON结果
generator.save_json_results(
    metrics=metrics,
    model_info=model_info,
    predictions=predictions,
    labels=labels
)
```

## 📈 评估指标说明

### 整体指标

- **准确率（Accuracy）**：所有预测正确的样本比例
- **精确率（Precision）**：预测为正类的样本中，真正为正类的比例
- **召回率（Recall）**：真实为正类的样本中，被正确预测的比例
- **F1分数**：精确率和召回率的调和平均

### 类别指标

对于每个类别（benign、malignant、normal）：

- **灵敏度（Sensitivity）**：同召回率，衡量对正类的识别能力
- **特异度（Specificity）**：衡量对负类的识别能力
- **AUC**：ROC曲线下面积，衡量分类器整体性能

## 💡 最佳实践

1. **保持数据划分一致**：评估时使用与训练时相同的测试集索引
2. **保存测试集索引**：将测试集索引保存为JSON文件，便于复现
3. **定期评估**：训练完成后立即进行评估
4. **对比实验**：使用实验对比功能追踪不同配置的性能

## 🐛 常见问题

### Q1: 如何确保评估使用正确的测试集？

A: 使用与训练时相同的随机种子生成数据划分，并保存测试集索引到JSON文件。

### Q2: Grad-CAM可视化效果不佳怎么办？

A: 检查目标层设置（通常为`layer4`），并确保模型在评估模式（model.eval()）。

### Q3: 如何对比多个实验的结果？

A: 使用`ReportGenerator.generate_comparison_table()`方法生成对比表格。

## 📚 参考资料

- [Grad-CAM论文](https://arxiv.org/abs/1610.02391)
- [sklearn评估指标](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [PyTorch可视化工具](https://pytorch.org/vision/stable/index.html)

---

**作者**: 毕业设计项目  
**更新时间**: 2026-04-12
