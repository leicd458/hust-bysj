"""
评估模块

包含:
- metrics: 评估指标计算
- visualization: 可视化工具
- gradcam: Grad-CAM热力图
- report: 报告生成
- evaluate: 主评估脚本
"""

from .metrics import MetricsCalculator, calculate_metrics_from_predictions
from .visualization import VisualizationManager
from .gradcam import GradCAM, visualize_gradcam_samples
from .report import ReportGenerator

__all__ = [
    'MetricsCalculator',
    'calculate_metrics_from_predictions',
    'VisualizationManager',
    'GradCAM',
    'visualize_gradcam_samples',
    'ReportGenerator'
]
