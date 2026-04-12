#!/usr/bin/env python3
"""
评估报告生成模块

功能:
- Markdown格式报告
- JSON格式完整结果
- 实验对比表格
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ReportGenerator:
    """评估报告生成器"""
    
    def __init__(self, output_dir: str):
        """
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_markdown_report(
        self,
        metrics: Dict,
        model_info: Dict,
        experiment_name: str = "Model Evaluation",
        save_filename: str = "evaluation_report.md"
    ):
        """生成Markdown格式评估报告
        
        Args:
            metrics: 评估指标字典
            model_info: 模型信息字典
            experiment_name: 实验名称
            save_filename: 保存文件名
        """
        report_path = self.output_dir / save_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # 标题
            f.write(f"# {experiment_name}\n\n")
            
            # 生成时间
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"**生成时间**: {timestamp}\n\n")
            
            # 分隔线
            f.write("---\n\n")
            
            # 模型信息
            f.write("## 模型信息\n\n")
            f.write(f"- **模型路径**: {model_info.get('model_path', 'N/A')}\n")
            f.write(f"- **模型架构**: {model_info.get('architecture', 'ResNet-18')}\n")
            f.write(f"- **测试集大小**: {model_info.get('test_size', 'N/A')}\n")
            f.write(f"- **训练配置**: {model_info.get('config', 'N/A')}\n\n")
            
            # 整体性能
            f.write("## 整体性能指标\n\n")
            f.write("| 指标 | 值 |\n")
            f.write("|------|----|\n")
            f.write(f"| **准确率** | {metrics['accuracy']:.2f}% |\n")
            f.write(f"| 精确率（加权） | {metrics['precision_weighted']:.2f}% |\n")
            f.write(f"| 召回率（加权） | {metrics['recall_weighted']:.2f}% |\n")
            f.write(f"| F1分数（加权） | {metrics['f1_weighted']:.2f}% |\n")
            
            if 'auc_macro' in metrics:
                f.write(f"| AUC（宏平均） | {metrics['auc_macro']:.2f}% |\n")
            
            f.write("\n")
            
            # 各类别性能
            f.write("## 各类别性能指标\n\n")
            f.write("| 类别 | 精确率 | 召回率（灵敏度） | 特异度 | F1分数 |")
            
            if 'auc_per_class' in metrics:
                f.write(" AUC |")
            
            f.write("\n")
            f.write("|------|--------|------------------|--------|--------|")
            
            if 'auc_per_class' in metrics:
                f.write("------|")
            
            f.write("\n")
            
            # 类别名称
            class_names = list(metrics['precision_per_class'].keys())
            
            for class_name in class_names:
                precision = metrics['precision_per_class'][class_name]
                recall = metrics['recall_per_class'][class_name]
                specificity = metrics['specificity_per_class'][class_name]
                f1 = metrics['f1_per_class'][class_name]
                
                f.write(f"| **{class_name}** | {precision:.2f}% | {recall:.2f}% | {specificity:.2f}% | {f1:.2f}% |")
                
                if 'auc_per_class' in metrics:
                    auc = metrics['auc_per_class'][class_name]
                    f.write(f" {auc:.2f}% |")
                
                f.write("\n")
            
            f.write("\n")
            
            # 混淆矩阵
            f.write("## 混淆矩阵\n\n")
            f.write("![混淆矩阵](confusion_matrix.png)\n\n")
            
            # ROC曲线
            if 'roc_data' in metrics:
                f.write("## ROC曲线\n\n")
                f.write("![ROC曲线](roc_curves.png)\n\n")
            
            # 指标对比
            f.write("## 指标对比\n\n")
            f.write("![指标对比](metrics_comparison.png)\n\n")
            
            # Grad-CAM可视化（如果有）
            if model_info.get('gradcam_path'):
                f.write("## Grad-CAM可视化\n\n")
                f.write("![Grad-CAM](gradcam_samples.png)\n\n")
            
            # 结论
            f.write("## 结论\n\n")
            f.write(f"- 模型在测试集上达到 **{metrics['accuracy']:.2f}%** 的准确率\n")
            
            # 找出最佳和最差类别
            class_accuracies = {
                c: metrics['recall_per_class'][c]
                for c in class_names
            }
            
            best_class = max(class_accuracies, key=class_accuracies.get)
            worst_class = min(class_accuracies, key=class_accuracies.get)
            
            f.write(f"- **{best_class}** 类别表现最佳（召回率: {class_accuracies[best_class]:.2f}%）\n")
            f.write(f"- **{worst_class}** 类别表现相对较弱（召回率: {class_accuracies[worst_class]:.2f}%）\n")
            
            if 'auc_macro' in metrics:
                f.write(f"- 宏平均AUC为 **{metrics['auc_macro']:.2f}%**，表明模型具有较好的区分能力\n")
            
            f.write("\n---\n\n")
            f.write("*报告由自动化脚本生成*\n")
        
        print(f"✓ Markdown报告已保存: {report_path}")
    
    def save_json_results(
        self,
        metrics: Dict,
        model_info: Dict,
        predictions: List[int],
        labels: List[int],
        save_filename: str = "evaluation_results.json"
    ):
        """保存JSON格式的完整结果
        
        Args:
            metrics: 评估指标
            model_info: 模型信息
            predictions: 预测结果
            labels: 真实标签
            save_filename: 保存文件名
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'model_info': model_info,
            'metrics': metrics,
            'predictions': predictions,
            'labels': labels
        }
        
        results_path = self.output_dir / save_filename
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON结果已保存: {results_path}")
    
    def generate_comparison_table(
        self,
        experiments: List[Dict],
        save_filename: str = "experiments_comparison.md"
    ):
        """生成多个实验的对比表格
        
        Args:
            experiments: 实验列表，每个实验包含name, accuracy, config等字段
            save_filename: 保存文件名
        """
        comparison_path = self.output_dir / save_filename
        
        with open(comparison_path, 'w', encoding='utf-8') as f:
            f.write("# 实验对比\n\n")
            f.write("| 实验名称 | 测试准确率 | 验证准确率 | 配置 |\n")
            f.write("|----------|-----------|-----------|------|\n")
            
            for exp in experiments:
                name = exp.get('name', 'Unknown')
                test_acc = exp.get('test_accuracy', exp.get('accuracy', 0))
                val_acc = exp.get('val_accuracy', 0)
                config = exp.get('config', 'N/A')
                
                f.write(f"| {name} | {test_acc:.2f}% | {val_acc:.2f}% | {config} |\n")
        
        print(f"✓ 实验对比表已保存: {comparison_path}")


if __name__ == '__main__':
    print("测试报告生成器")
    
    # 创建测试数据
    output_dir = 'test_outputs'
    generator = ReportGenerator(output_dir)
    
    # 模拟指标
    metrics = {
        'accuracy': 90.60,
        'precision_weighted': 90.12,
        'recall_weighted': 90.60,
        'f1_weighted': 90.23,
        'auc_macro': 94.56,
        'precision_per_class': {
            'benign': 87.69,
            'malignant': 96.67,
            'normal': 95.24
        },
        'recall_per_class': {
            'benign': 86.36,
            'malignant': 96.67,
            'normal': 95.24
        },
        'specificity_per_class': {
            'benign': 94.44,
            'malignant': 97.67,
            'normal': 98.86
        },
        'f1_per_class': {
            'benign': 87.02,
            'malignant': 96.67,
            'normal': 95.24
        },
        'auc_per_class': {
            'benign': 92.34,
            'malignant': 97.89,
            'normal': 96.45
        }
    }
    
    model_info = {
        'model_path': 'models/best_model.pth',
        'architecture': 'ResNet-18',
        'test_size': 117,
        'config': 'seed=2024, dropout=0.25, lr=0.0001'
    }
    
    # 生成报告
    generator.generate_markdown_report(metrics, model_info, "Stage4 Best Model Evaluation")
    
    print("\n✅ 测试完成")
