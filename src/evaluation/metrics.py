#!/usr/bin/env python3
"""
评估指标计算模块

功能:
- 准确率、精确率、召回率、F1分数
- 灵敏度、特异度
- AUC、ROC曲线数据
- 各类别详细指标
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    roc_curve
)
from sklearn.preprocessing import label_binarize
from typing import Dict, List, Tuple, Optional


class MetricsCalculator:
    """评估指标计算器"""
    
    CLASS_NAMES = ['benign', 'malignant', 'normal']
    
    def __init__(self, class_names: Optional[List[str]] = None):
        """
        Args:
            class_names: 类别名称列表
        """
        if class_names is None:
            class_names = self.CLASS_NAMES
        self.class_names = class_names
        self.n_classes = len(class_names)
    
    def calculate_all_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None
    ) -> Dict:
        """计算所有评估指标
        
        Args:
            y_true: 真实标签 (N,)
            y_pred: 预测标签 (N,)
            y_prob: 预测概率 (N, n_classes)，用于计算AUC
        
        Returns:
            包含所有指标的字典
        """
        metrics = {}
        
        # 1. 整体指标
        metrics['accuracy'] = accuracy_score(y_true, y_pred) * 100
        
        # 2. 加权平均指标
        metrics['precision_weighted'] = precision_score(
            y_true, y_pred, average='weighted', zero_division=0
        ) * 100
        
        metrics['recall_weighted'] = recall_score(
            y_true, y_pred, average='weighted', zero_division=0
        ) * 100
        
        metrics['f1_weighted'] = f1_score(
            y_true, y_pred, average='weighted', zero_division=0
        ) * 100
        
        # 3. 每个类别的指标
        precision_per_class = precision_score(
            y_true, y_pred, average=None, zero_division=0
        ) * 100
        
        recall_per_class = recall_score(
            y_true, y_pred, average=None, zero_division=0
        ) * 100
        
        f1_per_class = f1_score(
            y_true, y_pred, average=None, zero_division=0
        ) * 100
        
        metrics['precision_per_class'] = {
            self.class_names[i]: float(precision_per_class[i])
            for i in range(self.n_classes)
        }
        
        metrics['recall_per_class'] = {
            self.class_names[i]: float(recall_per_class[i])
            for i in range(self.n_classes)
        }
        
        metrics['f1_per_class'] = {
            self.class_names[i]: float(f1_per_class[i])
            for i in range(self.n_classes)
        }
        
        # 4. 混淆矩阵
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # 5. 特异度（每个类别）
        specificity_per_class = self._calculate_specificity(cm)
        metrics['specificity_per_class'] = {
            self.class_names[i]: float(specificity_per_class[i])
            for i in range(self.n_classes)
        }
        
        # 6. AUC和ROC曲线（如果提供了概率）
        if y_prob is not None:
            auc_metrics = self._calculate_auc(y_true, y_prob)
            metrics.update(auc_metrics)
        
        return metrics
    
    def _calculate_specificity(self, cm: np.ndarray) -> np.ndarray:
        """计算每个类别的特异度
        
        特异度 = TN / (TN + FP)
        
        Args:
            cm: 混淆矩阵 (n_classes, n_classes)
        
        Returns:
            每个类别的特异度
        """
        specificity = np.zeros(self.n_classes)
        
        for i in range(self.n_classes):
            # TN: 所有不是类别i的样本中，正确预测为不是类别i的数量
            tn = cm.sum() - cm[i, :].sum() - cm[:, i].sum() + cm[i, i]
            
            # FP: 实际不是类别i，但预测为类别i的数量
            fp = cm[:, i].sum() - cm[i, i]
            
            # 特异度
            if (tn + fp) > 0:
                specificity[i] = (tn / (tn + fp)) * 100
            else:
                specificity[i] = 0.0
        
        return specificity
    
    def _calculate_auc(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray
    ) -> Dict:
        """计算AUC和ROC曲线数据
        
        Args:
            y_true: 真实标签 (N,)
            y_prob: 预测概率 (N, n_classes)
        
        Returns:
            AUC相关指标
        """
        metrics = {}
        
        # 二值化标签
        y_true_bin = label_binarize(y_true, classes=range(self.n_classes))
        
        # 每个类别的AUC
        auc_per_class = {}
        for i, class_name in enumerate(self.class_names):
            try:
                auc = roc_auc_score(y_true_bin[:, i], y_prob[:, i])
                auc_per_class[class_name] = float(auc * 100)
            except ValueError:
                auc_per_class[class_name] = 0.0
        
        metrics['auc_per_class'] = auc_per_class
        
        # 宏平均AUC
        try:
            auc_macro = roc_auc_score(
                y_true_bin, y_prob,
                multi_class='ovr',
                average='macro'
            )
            metrics['auc_macro'] = float(auc_macro * 100)
        except ValueError:
            metrics['auc_macro'] = 0.0
        
        # ROC曲线数据
        roc_data = {}
        for i, class_name in enumerate(self.class_names):
            fpr, tpr, thresholds = roc_curve(y_true_bin[:, i], y_prob[:, i])
            roc_data[class_name] = {
                'fpr': fpr.tolist(),
                'tpr': tpr.tolist(),
                'thresholds': thresholds.tolist()
            }
        
        metrics['roc_data'] = roc_data
        
        return metrics
    
    def calculate_class_accuracy(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """计算每个类别的准确率
        
        Args:
            y_true: 真实标签
            y_pred: 预测标签
        
        Returns:
            每个类别的准确率
        """
        class_accuracy = {}
        
        for i, class_name in enumerate(self.class_names):
            mask = y_true == i
            if mask.sum() > 0:
                acc = (y_pred[mask] == y_true[mask]).mean() * 100
                class_accuracy[class_name] = float(acc)
            else:
                class_accuracy[class_name] = 0.0
        
        return class_accuracy
    
    def print_metrics(self, metrics: Dict):
        """打印评估指标
        
        Args:
            metrics: 指标字典
        """
        print("\n" + "="*70)
        print("评估指标")
        print("="*70)
        
        # 整体性能
        print("\n【整体性能】")
        print(f"  准确率: {metrics['accuracy']:.2f}%")
        print(f"  精确率（加权）: {metrics['precision_weighted']:.2f}%")
        print(f"  召回率（加权）: {metrics['recall_weighted']:.2f}%")
        print(f"  F1分数（加权）: {metrics['f1_weighted']:.2f}%")
        
        if 'auc_macro' in metrics:
            print(f"  AUC（宏平均）: {metrics['auc_macro']:.2f}%")
        
        # 各类别性能
        print("\n【各类别性能】")
        print(f"{'类别':<12} {'精确率':>8} {'召回率':>8} {'特异度':>8} {'F1分数':>8} {'AUC':>8}")
        print("-" * 70)
        
        for class_name in self.class_names:
            precision = metrics['precision_per_class'][class_name]
            recall = metrics['recall_per_class'][class_name]
            specificity = metrics['specificity_per_class'][class_name]
            f1 = metrics['f1_per_class'][class_name]
            
            line = f"{class_name:<12} {precision:>7.2f}% {recall:>7.2f}% {specificity:>7.2f}% {f1:>7.2f}%"
            
            if 'auc_per_class' in metrics:
                auc = metrics['auc_per_class'][class_name]
                line += f" {auc:>7.2f}%"
            
            print(line)
        
        print("="*70)


def calculate_metrics_from_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    class_names: Optional[List[str]] = None
) -> Dict:
    """便捷函数：从预测结果计算所有指标
    
    Args:
        y_true: 真实标签
        y_pred: 预测标签
        y_prob: 预测概率（可选）
        class_names: 类别名称（可选）
    
    Returns:
        指标字典
    """
    calculator = MetricsCalculator(class_names)
    return calculator.calculate_all_metrics(y_true, y_pred, y_prob)


if __name__ == '__main__':
    # 测试代码
    print("测试评估指标计算器")
    
    # 模拟数据
    np.random.seed(42)
    n_samples = 117
    n_classes = 3
    
    y_true = np.random.randint(0, n_classes, n_samples)
    y_pred = np.random.randint(0, n_classes, n_samples)
    y_prob = np.random.rand(n_samples, n_classes)
    y_prob = y_prob / y_prob.sum(axis=1, keepdims=True)  # 归一化
    
    # 计算指标
    calculator = MetricsCalculator()
    metrics = calculator.calculate_all_metrics(y_true, y_pred, y_prob)
    
    # 打印指标
    calculator.print_metrics(metrics)
    
    print("\n✅ 测试完成")
