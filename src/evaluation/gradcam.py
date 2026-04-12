#!/usr/bin/env python3
"""
Grad-CAM可视化模块

功能:
- Grad-CAM热力图生成
- 注意力可视化
- 多样本Grad-CAM对比
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import cv2
from typing import Tuple, Optional, List
from pathlib import Path

# 设置中文字体（macOS系统）
plt.rcParams['font.sans-serif'] = ['PingFang HK', 'Arial Unicode MS', 'STHeiti', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class GradCAM:
    """Grad-CAM实现
    
    参考: Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization
    """
    
    def __init__(self, model: nn.Module, target_layer: str):
        """
        Args:
            model: 模型
            target_layer: 目标层名称（如'layer4'）
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # 注册钩子
        self._register_hooks()
    
    def _register_hooks(self):
        """注册前向和反向传播钩子"""
        # 获取目标层
        target_layer = self._get_target_layer()
        
        # 前向钩子：保存特征图
        def forward_hook(module, input, output):
            self.activations = output.detach()
        
        # 反向钩子：保存梯度
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        
        # 注册钩子
        target_layer.register_forward_hook(forward_hook)
        target_layer.register_backward_hook(backward_hook)
    
    def _get_target_layer(self):
        """获取目标层
        
        对于ResNet，目标层通常是layer4
        """
        if hasattr(self.model, 'backbone'):
            # 如果模型有backbone属性
            return getattr(self.model.backbone, self.target_layer)
        else:
            # 直接在模型上查找
            return getattr(self.model, self.target_layer)
    
    def generate_cam(
        self,
        input_image: torch.Tensor,
        target_class: Optional[int] = None
    ) -> np.ndarray:
        """生成类激活图（CAM）
        
        Args:
            input_image: 输入图像 (1, C, H, W)
            target_class: 目标类别（None表示使用预测类别）
        
        Returns:
            CAM热力图 (H, W)，值范围[0, 1]
        """
        # 前向传播
        self.model.eval()
        output = self.model(input_image)
        
        # 确定目标类别
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # 反向传播
        self.model.zero_grad()
        
        # 创建one-hot向量
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1
        
        # 反向传播
        output.backward(gradient=one_hot, retain_graph=True)
        
        # 计算权重
        # 全局平均池化梯度
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)
        
        # 加权求和特征图
        cam = (weights * self.activations).sum(dim=1, keepdim=True)  # (1, 1, H', W')
        
        # ReLU激活
        cam = F.relu(cam)
        
        # 归一化到[0, 1]
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        
        return cam
    
    def visualize(
        self,
        image_path: str,
        input_tensor: torch.Tensor,
        target_class: Optional[int] = None,
        alpha: float = 0.4
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """可视化Grad-CAM
        
        Args:
            image_path: 原始图像路径
            input_tensor: 输入张量 (1, C, H, W)
            target_class: 目标类别
            alpha: 热力图透明度
        
        Returns:
            (原图, CAM热力图, 叠加图)
        """
        # 生成CAM
        cam = self.generate_cam(input_tensor, target_class)
        
        # 加载原始图像
        original_image = cv2.imread(image_path)
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        
        # 调整CAM大小到原始图像尺寸
        cam_resized = cv2.resize(cam, (original_image.shape[1], original_image.shape[0]))
        
        # 应用颜色映射
        cam_heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        cam_heatmap = cv2.cvtColor(cam_heatmap, cv2.COLOR_BGR2RGB)
        
        # 叠加到原图
        overlay = cv2.addWeighted(original_image, 1 - alpha, cam_heatmap, alpha, 0)
        
        return original_image, cam_heatmap, overlay


def visualize_gradcam_samples(
    model: nn.Module,
    image_paths: List[str],
    labels: List[int],
    predictions: List[int],
    class_names: List[str],
    save_path: str,
    target_layer: str = 'layer4',
    max_samples: int = 9
):
    """可视化多个样本的Grad-CAM
    
    Args:
        model: 模型
        image_paths: 图像路径列表
        labels: 真实标签列表
        predictions: 预测标签列表
        class_names: 类别名称
        save_path: 保存路径
        target_layer: 目标层名称
        max_samples: 最大样本数
    """
    # 创建Grad-CAM实例
    grad_cam = GradCAM(model, target_layer)
    
    # 获取模型所在设备
    device = next(model.parameters()).device
    
    # 图像预处理
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    # 选择样本
    n_samples = min(len(image_paths), max_samples)
    
    # 创建图像网格
    fig, axes = plt.subplots(n_samples, 3, figsize=(12, 4 * n_samples))
    
    if n_samples == 1:
        axes = axes.reshape(1, -1)
    
    for i in range(n_samples):
        # 加载图像
        image_path = image_paths[i]
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0).to(device)  # 移动到模型所在设备
        
        # 生成Grad-CAM
        original, cam_heatmap, overlay = grad_cam.visualize(
            image_path, input_tensor, predictions[i]
        )
        
        # 绘制
        axes[i, 0].imshow(original)
        axes[i, 0].set_title('Original', fontsize=12)
        axes[i, 0].axis('off')
        
        axes[i, 1].imshow(cam_heatmap)
        axes[i, 1].set_title('Grad-CAM', fontsize=12)
        axes[i, 1].axis('off')
        
        axes[i, 2].imshow(overlay)
        
        # 标注真实标签和预测标签
        true_label = class_names[labels[i]]
        pred_label = class_names[predictions[i]]
        color = 'green' if labels[i] == predictions[i] else 'red'
        
        axes[i, 2].set_title(
            f'True: {true_label}, Pred: {pred_label}',
            fontsize=12, color=color
        )
        axes[i, 2].axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Grad-CAM可视化已保存: {save_path}")


if __name__ == '__main__':
    print("Grad-CAM模块测试")
    
    # 测试代码需要实际模型
    print("需要加载实际模型才能测试Grad-CAM功能")
    print("✅ 模块已就绪")
