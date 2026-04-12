#!/usr/bin/env python3
"""
模型处理模块
负责模型加载、推理和Grad-CAM生成
"""

import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import numpy as np
import cv2
import base64
from io import BytesIO
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'experiment/stage4'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from train import ResNet18Classifier
from evaluation.gradcam import GradCAM


class ModelHandler:
    """模型处理器"""
    
    def __init__(self, model_path: str, device: str = 'auto'):
        """
        初始化模型处理器
        
        Args:
            model_path: 模型文件路径
            device: 计算设备 ('auto', 'cuda', 'mps', 'cpu')
        """
        self.model_path = model_path
        self.device = self._get_device(device)
        self.model = self._load_model()
        self.class_names = ['benign', 'malignant', 'normal']
        self.class_names_cn = {
            'benign': '良性',
            'malignant': '恶性',
            'normal': '正常'
        }
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Grad-CAM
        self.grad_cam = GradCAM(self.model, 'layer4')
    
    def _get_device(self, device: str) -> torch.device:
        """获取计算设备"""
        if device == 'auto':
            if torch.cuda.is_available():
                return torch.device('cuda')
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return torch.device('mps')
            else:
                return torch.device('cpu')
        return torch.device(device)
    
    def _load_model(self) -> nn.Module:
        """加载模型"""
        print(f"正在加载模型: {self.model_path}")
        print(f"使用设备: {self.device}")
        
        # 创建模型
        model = ResNet18Classifier(num_classes=3, pretrained=True, dropout=0.25)
        
        # 加载权重
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
            print(f"模型加载成功 (Epoch: {checkpoint.get('epoch', 'N/A')}, "
                  f"Val Acc: {checkpoint.get('val_acc', 'N/A'):.2f}%)")
        else:
            model.load_state_dict(checkpoint)
        
        model.to(self.device)
        model.eval()
        
        return model
    
    def predict(self, image: Image.Image) -> dict:
        """
        预测图像类别
        
        Args:
            image: PIL图像对象
            
        Returns:
            包含预测结果的字典
        """
        # 预处理
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # 推理
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, predicted_class].item()
        
        # 获取各类别概率
        probs_dict = {
            self.class_names[i]: probabilities[0, i].item()
            for i in range(len(self.class_names))
        }
        
        return {
            'predicted_class': self.class_names[predicted_class],
            'predicted_class_cn': self.class_names_cn[self.class_names[predicted_class]],
            'confidence': confidence,
            'probabilities': probs_dict
        }
    
    def generate_gradcam(self, image: Image.Image, target_class: int = None) -> str:
        """
        生成Grad-CAM热力图
        
        Args:
            image: PIL图像对象
            target_class: 目标类别（默认使用预测类别）
            
        Returns:
            base64编码的图像
        """
        # 保存原始图像尺寸和RGB模式
        original_image_rgb = image.convert('RGB')
        original_size = original_image_rgb.size  # (width, height)
        original_array = np.array(original_image_rgb)
        
        # 预处理
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # 如果未指定目标类别，使用预测类别
        if target_class is None:
            with torch.no_grad():
                outputs = self.model(input_tensor)
                target_class = torch.argmax(outputs, dim=1).item()
        
        # 生成CAM
        cam = self.grad_cam.generate_cam(input_tensor, target_class)
        
        # 调整CAM大小到原始图像尺寸
        cam_resized = cv2.resize(cam, original_size)
        
        # 应用颜色映射
        cam_heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        cam_heatmap = cv2.cvtColor(cam_heatmap, cv2.COLOR_BGR2RGB)
        
        # 叠加到原图
        overlay = cv2.addWeighted(original_array, 0.6, cam_heatmap, 0.4, 0)
        
        # 转换为base64
        buffered = BytesIO()
        overlay_image = Image.fromarray(overlay)
        overlay_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def analyze(self, image: Image.Image) -> dict:
        """
        完整分析：预测 + Grad-CAM
        
        Args:
            image: PIL图像对象
            
        Returns:
            包含预测结果和Grad-CAM的字典
        """
        # 预测
        prediction = self.predict(image)
        
        # 生成Grad-CAM
        target_class_idx = self.class_names.index(prediction['predicted_class'])
        gradcam_base64 = self.generate_gradcam(image, target_class_idx)
        
        return {
            **prediction,
            'gradcam': gradcam_base64
        }
