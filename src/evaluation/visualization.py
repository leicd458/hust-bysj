#!/usr/bin/env python3
"""
可视化工具模块

功能:
- 混淆矩阵可视化
- ROC曲线绘制
- 训练曲线绘制
- 各类别准确率对比
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from typing import Dict, List, Optional
from pathlib import Path


def get_chinese_font():
    """获取中文字体"""
    font_names = ['PingFang HK', 'Arial Unicode MS', 'STHeiti']
    for font_name in font_names:
        try:
            font_path = fm.findfont(font_name)
            if 'PingFang' in font_path or 'Arial Unicode' in font_path or 'STHeiti' in font_path:
                return fm.FontProperties(fname=font_path)
        except:
            continue
    # 如果找不到，返回None，使用默认字体
    return None


class VisualizationManager:
    """可视化工具管理器"""
    
    # 配色方案
    COLORS = {
        'benign': '#3498db',      # 蓝色
        'malignant': '#e74c3c',   # 红色
        'normal': '#2ecc71',      # 绿色
    }
    
    def __init__(self, style: str = 'whitegrid'):
        """
        Args:
            style: seaborn样式 ('whitegrid', 'darkgrid', 'white', 'dark', 'ticks')
        """
        sns.set_style(style)
        
        # 在 seaborn 设置之后重新配置字体（避免被覆盖）
        plt.rcParams['font.sans-serif'] = ['PingFang HK', 'Arial Unicode MS', 'STHeiti', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        self.figsize = (10, 8)
        self.dpi = 300
    
    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        class_names: List[str],
        save_path: str,
        title: str = 'Confusion Matrix',
        normalize: bool = False,
        show_accuracy: bool = True
    ):
        """绘制混淆矩阵
        
        Args:
            cm: 混淆矩阵 (n_classes, n_classes)
            class_names: 类别名称
            save_path: 保存路径
            title: 标题
            normalize: 是否归一化
            show_accuracy: 是否显示每个类别的准确率
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 归一化混淆矩阵
        if normalize:
            cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
            fmt = '.1f'
            cmap = 'YlGnBu'
        else:
            cm_normalized = cm
            fmt = 'd'
            cmap = 'Blues'
        
        # 绘制热力图
        sns.heatmap(
            cm_normalized,
            annot=True,
            fmt=fmt,
            cmap=cmap,
            xticklabels=class_names,
            yticklabels=class_names,
            cbar_kws={'label': '样本数量' if not normalize else '百分比 (%)'},
            ax=ax
        )
        
        # 获取中文字体
        chinese_font = get_chinese_font()
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20, 
                    fontproperties=chinese_font if chinese_font else None)
        ax.set_xlabel('预测类别', fontsize=14, 
                     fontproperties=chinese_font if chinese_font else None)
        ax.set_ylabel('真实类别', fontsize=14,
                     fontproperties=chinese_font if chinese_font else None)
        
        # 在右侧添加准确率标注
        if show_accuracy and not normalize:
            for i in range(len(class_names)):
                total = cm[i, :].sum()
                correct = cm[i, i]
                accuracy = correct / total * 100 if total > 0 else 0
                
                ax.text(
                    len(class_names) + 0.5, i + 0.5,
                    f'{accuracy:.1f}%',
                    ha='left', va='center',
                    fontsize=11, color='green', fontweight='bold'
                )
            
            # 添加列标题
            ax.text(
                len(class_names) + 0.5, -0.7,
                '准确率',
                ha='center', va='bottom',
                fontsize=11, fontweight='bold'
            )
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 混淆矩阵已保存: {save_path}")
    
    def plot_roc_curves(
        self,
        roc_data: Dict,
        class_names: List[str],
        save_path: str,
        title: str = 'ROC Curves'
    ):
        """绘制ROC曲线
        
        Args:
            roc_data: ROC数据字典，格式为 {class_name: {'fpr': [], 'tpr': []}}
            class_names: 类别名称
            save_path: 保存路径
            title: 标题
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 为每个类别绘制ROC曲线
        for class_name in class_names:
            if class_name in roc_data:
                fpr = np.array(roc_data[class_name]['fpr'])
                tpr = np.array(roc_data[class_name]['tpr'])
                
                # 计算AUC（使用numpy的trapezoid函数，兼容新旧版本）
                try:
                    auc = np.trapezoid(tpr, fpr)  # numpy新版本
                except AttributeError:
                    auc = np.trapz(tpr, fpr)  # numpy旧版本
                
                color = self.COLORS.get(class_name, 'blue')
                
                ax.plot(
                    fpr, tpr,
                    color=color, linewidth=2.5,
                    label=f'{class_name} (AUC = {auc:.3f})'
                )
        
        # 绘制对角线（随机分类器）
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1.5, label='Random Classifier')
        
        ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=14)
        ax.set_ylabel('True Positive Rate (Sensitivity)', fontsize=14)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20,
                    fontproperties=get_chinese_font() if get_chinese_font() else None)
        ax.legend(loc='lower right', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([-0.02, 1.02])
        ax.set_ylim([-0.02, 1.02])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"✓ ROC曲线已保存: {save_path}")
    
    def plot_training_history(
        self,
        history: Dict,
        save_path: str,
        title: str = 'Training History'
    ):
        """绘制训练历史曲线
        
        Args:
            history: 包含train_loss, train_acc, val_loss, val_acc的字典
            save_path: 保存路径
            title: 标题
        """
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        epochs = range(1, len(history['train_loss']) + 1)
        
        # 损失曲线
        axes[0].plot(epochs, history['train_loss'], 'b-', linewidth=2, label='Training Loss')
        axes[0].plot(epochs, history['val_loss'], 'r-', linewidth=2, label='Validation Loss')
        axes[0].set_xlabel('Epoch', fontsize=14)
        axes[0].set_ylabel('Loss', fontsize=14)
        axes[0].set_title('Loss Curves', fontsize=16, fontweight='bold')
        axes[0].legend(fontsize=12)
        axes[0].grid(True, alpha=0.3)
        
        # 准确率曲线
        axes[1].plot(epochs, history['train_acc'], 'b-', linewidth=2, label='Training Accuracy')
        axes[1].plot(epochs, history['val_acc'], 'r-', linewidth=2, label='Validation Accuracy')
        axes[1].set_xlabel('Epoch', fontsize=14)
        axes[1].set_ylabel('Accuracy (%)', fontsize=14)
        axes[1].set_title('Accuracy Curves', fontsize=16, fontweight='bold')
        axes[1].legend(fontsize=12)
        axes[1].grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=18, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 训练曲线已保存: {save_path}")
    
    def plot_metrics_comparison(
        self,
        metrics: Dict,
        class_names: List[str],
        save_path: str,
        title: str = 'Metrics Comparison'
    ):
        """绘制各指标对比柱状图
        
        Args:
            metrics: 指标字典
            class_names: 类别名称
            save_path: 保存路径
            title: 标题
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 准备数据
        metric_names = ['Precision', 'Recall', 'Specificity', 'F1-score']
        x = np.arange(len(class_names))
        width = 0.2
        
        # 提取各类别的指标
        precision = [metrics['precision_per_class'][c] for c in class_names]
        recall = [metrics['recall_per_class'][c] for c in class_names]
        specificity = [metrics['specificity_per_class'][c] for c in class_names]
        f1 = [metrics['f1_per_class'][c] for c in class_names]
        
        # 绘制柱状图
        ax.bar(x - 1.5*width, precision, width, label='Precision', color='#3498db')
        ax.bar(x - 0.5*width, recall, width, label='Recall', color='#e74c3c')
        ax.bar(x + 0.5*width, specificity, width, label='Specificity', color='#2ecc71')
        ax.bar(x + 1.5*width, f1, width, label='F1-score', color='#f39c12')
        
        ax.set_xlabel('Class', fontsize=14)
        ax.set_ylabel('Score (%)', fontsize=14)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20,
                    fontproperties=get_chinese_font() if get_chinese_font() else None)
        ax.set_xticks(x)
        ax.set_xticklabels(class_names, fontsize=12)
        ax.legend(fontsize=11)
        ax.set_ylim([0, 105])
        ax.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for i, class_name in enumerate(class_names):
            for j, values in enumerate([precision, recall, specificity, f1]):
                ax.text(
                    i + (j - 1.5) * width, values[i] + 1,
                    f'{values[i]:.1f}',
                    ha='center', va='bottom',
                    fontsize=9
                )
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 指标对比图已保存: {save_path}")


if __name__ == '__main__':
    # 测试代码
    print("测试可视化工具")
    
    viz_manager = VisualizationManager()
    
    # 测试混淆矩阵
    cm = np.array([[57, 5, 4], [1, 29, 0], [1, 0, 20]])
    class_names = ['benign', 'malignant', 'normal']
    
    output_dir = Path('test_outputs')
    output_dir.mkdir(exist_ok=True)
    
    viz_manager.plot_confusion_matrix(
        cm, class_names,
        save_path=str(output_dir / 'test_cm.png'),
        title='Test Confusion Matrix'
    )
    
    # 测试ROC曲线
    np.random.seed(42)
    roc_data = {
        'benign': {
            'fpr': np.linspace(0, 1, 100),
            'tpr': np.linspace(0, 1, 100) ** 0.5
        },
        'malignant': {
            'fpr': np.linspace(0, 1, 100),
            'tpr': np.linspace(0, 1, 100) ** 0.3
        },
        'normal': {
            'fpr': np.linspace(0, 1, 100),
            'tpr': np.linspace(0, 1, 100) ** 0.4
        }
    }
    
    viz_manager.plot_roc_curves(
        roc_data, class_names,
        save_path=str(output_dir / 'test_roc.png')
    )
    
    print("\n✅ 测试完成")
