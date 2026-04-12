#!/usr/bin/env python3
"""
模型评估主脚本

功能:
- 加载训练好的模型
- 在测试集上评估
- 生成所有评估指标
- 创建可视化图表
- 生成完整评估报告
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import models, transforms
from torchvision.models import ResNet18_Weights
from tqdm import tqdm
from PIL import Image

# 导入评估模块
from metrics import MetricsCalculator
from visualization import VisualizationManager
from gradcam import GradCAM, visualize_gradcam_samples
from report import ReportGenerator

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from experiment.stage4.dataset import BUSIDatasetWithIndices, TransformSubset


class ResNet18Classifier(nn.Module):
    """ResNet-18分类器"""
    
    def __init__(self, num_classes=3, pretrained=True, dropout=0.30):
        super(ResNet18Classifier, self).__init__()
        
        # 加载预训练模型
        if pretrained:
            self.backbone = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        else:
            self.backbone = models.resnet18(weights=None)
        
        # 修改最后的全连接层
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


def load_model(model_path: str, device: torch.device, dropout: float = 0.25):
    """加载训练好的模型
    
    Args:
        model_path: 模型文件路径
        device: 计算设备
        dropout: Dropout比例
    
    Returns:
        加载好的模型
    """
    print(f"\n{'='*70}")
    print("加载模型")
    print(f"{'='*70}")
    
    model = ResNet18Classifier(num_classes=3, pretrained=True, dropout=dropout)
    
    checkpoint = torch.load(model_path, map_location=device)
    
    # 检查checkpoint格式
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        # 完整checkpoint格式（包含optimizer、epoch等）
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"  Checkpoint信息:")
        print(f"    - Epoch: {checkpoint.get('epoch', 'N/A')}")
        print(f"    - Val Acc: {checkpoint.get('val_acc', 'N/A'):.2f}%" if isinstance(checkpoint.get('val_acc'), (int, float)) else f"    - Val Acc: N/A")
    else:
        # 仅模型权重格式
        model.load_state_dict(checkpoint)
    
    model.to(device)
    model.eval()
    
    print(f"✓ 模型加载成功: {model_path}")
    
    return model


def get_test_dataloader(
    data_dir: str,
    test_indices: List[int],
    batch_size: int = 32,
    num_workers: int = 4
) -> Tuple[DataLoader, BUSIDatasetWithIndices]:
    """创建测试数据加载器
    
    Args:
        data_dir: 数据目录
        test_indices: 测试集索引
        batch_size: 批次大小
        num_workers: 工作进程数
    
    Returns:
        (测试数据加载器, 完整数据集)
    """
    # 测试集变换（仅基础预处理）
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    # 加载完整数据集
    full_dataset = BUSIDatasetWithIndices(data_dir)
    
    # 创建测试子集
    test_dataset = TransformSubset(full_dataset, test_indices, test_transform)
    
    # 创建数据加载器
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    print(f"✓ 测试集大小: {len(test_dataset)} 张图像")
    
    return test_loader, full_dataset


def run_inference(
    model: nn.Module,
    test_loader: DataLoader,
    device: torch.device
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
    """运行模型推理
    
    Args:
        model: 模型
        test_loader: 测试数据加载器
        device: 计算设备
    
    Returns:
        (预测标签, 真实标签, 预测概率, 图像路径列表)
    """
    print(f"\n{'='*70}")
    print("运行模型推理")
    print(f"{'='*70}")
    
    model.eval()
    
    all_preds = []
    all_labels = []
    all_probs = []
    all_image_paths = []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="推理中"):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            _, predicted = outputs.max(1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    # 转换为numpy数组
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    print(f"✓ 推理完成: {len(all_preds)} 个样本")
    
    return all_preds, all_labels, all_probs, all_image_paths


def main():
    parser = argparse.ArgumentParser(description='乳腺癌分类模型评估')
    parser.add_argument('--model-path', type=str, required=True, help='模型文件路径')
    parser.add_argument('--data-dir', type=str, required=True, help='数据目录')
    parser.add_argument('--test-indices', type=str, required=True, help='测试集索引文件（JSON）')
    parser.add_argument('--output-dir', type=str, default='outputs/evaluation', help='输出目录')
    parser.add_argument('--batch-size', type=int, default=32, help='批次大小')
    parser.add_argument('--dropout', type=float, default=0.25, help='Dropout比例')
    parser.add_argument('--device', type=str, default='auto', help='计算设备')
    parser.add_argument('--experiment-name', type=str, default='Model Evaluation', help='实验名称')
    parser.add_argument('--gradcam-samples', type=int, default=9, help='Grad-CAM可视化样本数')
    
    args = parser.parse_args()
    
    # 设置设备
    if args.device == 'auto':
        if torch.cuda.is_available():
            device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            device = torch.device('mps')
        else:
            device = torch.device('cpu')
    else:
        device = torch.device(args.device)
    
    print(f"\n使用设备: {device}")
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载模型
    model = load_model(args.model_path, device, args.dropout)
    
    # 加载测试集索引
    with open(args.test_indices, 'r') as f:
        test_indices = json.load(f)
    
    print(f"✓ 加载测试集索引: {len(test_indices)} 张图像")
    
    # 创建测试数据加载器
    test_loader, full_dataset = get_test_dataloader(
        args.data_dir,
        test_indices,
        batch_size=args.batch_size
    )
    
    # 运行推理
    predictions, labels, probabilities, image_paths = run_inference(
        model, test_loader, device
    )
    
    # 收集测试集图像路径
    test_image_paths = [
        full_dataset.get_sample(idx)['image_path']
        for idx in test_indices
    ]
    
    # 计算评估指标
    print(f"\n{'='*70}")
    print("计算评估指标")
    print(f"{'='*70}")
    
    metrics_calculator = MetricsCalculator()
    metrics = metrics_calculator.calculate_all_metrics(labels, predictions, probabilities)
    
    # 打印指标
    metrics_calculator.print_metrics(metrics)
    
    # 创建可视化
    print(f"\n{'='*70}")
    print("生成可视化图表")
    print(f"{'='*70}")
    
    viz_manager = VisualizationManager()
    
    # 1. 混淆矩阵
    cm = np.array(metrics['confusion_matrix'])
    viz_manager.plot_confusion_matrix(
        cm,
        class_names=['benign', 'malignant', 'normal'],
        save_path=str(output_dir / 'confusion_matrix.png'),
        title=f'{args.experiment_name} - Confusion Matrix'
    )
    
    # 2. ROC曲线
    if 'roc_data' in metrics:
        viz_manager.plot_roc_curves(
            metrics['roc_data'],
            class_names=['benign', 'malignant', 'normal'],
            save_path=str(output_dir / 'roc_curves.png'),
            title=f'{args.experiment_name} - ROC Curves'
        )
    
    # 3. 指标对比
    viz_manager.plot_metrics_comparison(
        metrics,
        class_names=['benign', 'malignant', 'normal'],
        save_path=str(output_dir / 'metrics_comparison.png'),
        title=f'{args.experiment_name} - Metrics Comparison'
    )
    
    # 4. Grad-CAM可视化
    if args.gradcam_samples > 0:
        print(f"\n生成Grad-CAM可视化...")
        
        # 随机选择样本
        sample_indices = np.random.choice(
            len(test_indices),
            min(args.gradcam_samples, len(test_indices)),
            replace=False
        )
        
        selected_image_paths = [test_image_paths[i] for i in sample_indices]
        selected_labels = [labels[i] for i in sample_indices]
        selected_preds = [predictions[i] for i in sample_indices]
        
        visualize_gradcam_samples(
            model,
            selected_image_paths,
            selected_labels,
            selected_preds,
            class_names=['benign', 'malignant', 'normal'],
            save_path=str(output_dir / 'gradcam_samples.png'),
            max_samples=args.gradcam_samples
        )
    
    # 生成评估报告
    print(f"\n{'='*70}")
    print("生成评估报告")
    print(f"{'='*70}")
    
    report_generator = ReportGenerator(str(output_dir))
    
    # 模型信息
    model_info = {
        'model_path': args.model_path,
        'architecture': 'ResNet-18',
        'test_size': len(test_indices),
        'config': f'dropout={args.dropout}',
        'gradcam_path': 'gradcam_samples.png' if args.gradcam_samples > 0 else None
    }
    
    # 生成Markdown报告
    report_generator.generate_markdown_report(
        metrics,
        model_info,
        experiment_name=args.experiment_name
    )
    
    # 保存JSON结果
    report_generator.save_json_results(
        metrics,
        model_info,
        predictions.tolist(),
        labels.tolist()
    )
    
    print(f"\n{'='*70}")
    print("✅ 评估完成！")
    print(f"{'='*70}")
    print(f"\n输出目录: {output_dir.absolute()}")
    print(f"\n生成的文件:")
    print(f"  - evaluation_report.md      (Markdown格式报告)")
    print(f"  - evaluation_results.json   (JSON格式完整结果)")
    print(f"  - confusion_matrix.png      (混淆矩阵)")
    print(f"  - roc_curves.png            (ROC曲线)")
    print(f"  - metrics_comparison.png    (指标对比图)")
    
    if args.gradcam_samples > 0:
        print(f"  - gradcam_samples.png       (Grad-CAM可视化)")
    
    print()


if __name__ == '__main__':
    main()
