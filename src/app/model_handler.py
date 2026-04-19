#!/usr/bin/env python3
"""
模型处理模块
负责模型加载、推理和Grad-CAM生成

支持的模型:
- ResNet-18 (Stage4): 88.89%, 输入224x224, 目标层 layer4
- EfficientNet-B0 (Stage5最优): 94.87%, 输入300x300, 目标层 features[8]
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from torchvision.models import EfficientNet_B0_Weights
from PIL import Image
import numpy as np
import cv2
import base64
from io import BytesIO
from pathlib import Path
import sys

# 添加实验代码路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'experiment/stage5'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'experiment/stage4'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODEL_TYPE


# ==================== 模型定义 ====================

class ResNet18Classifier(nn.Module):
    """ResNet-18 三分类器"""
    def __init__(self, num_classes=3, pretrained=True, dropout=0.25):
        super().__init__()
        self.backbone = models.resnet18(
            weights=models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        )
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


class EfficientNetB0Classifier(nn.Module):
    """EfficientNet-B0 三分类器"""
    def __init__(self, num_classes=3, pretrained=True, dropout=0.5):
        super().__init__()
        if pretrained:
            self.backbone = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            self.backbone = models.efficientnet_b0(weights=None)

        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


# ==================== Grad-CAM (兼容双架构) ====================

class GradCAM:
    """通用 Grad-CAM 实现，兼容 ResNet 和 EfficientNet"""

    def __init__(self, model: nn.Module, target_layer_name: str):
        """
        Args:
            model: 模型实例
            target_layer_name: 目标层名称
                - ResNet: 'layer4'
                - EfficientNet: 'features.[8]' 或直接传模块引用
        """
        self.model = model
        self.gradients = None
        self.activations = None
        self.target_module = self._resolve_target(target_layer_name)
        self._register_hooks()

    def _resolve_target(self, target_name):
        """解析目标层，支持字符串或直接模块"""
        if isinstance(target_name, nn.Module):
            return target_name
        # 支持点分路径如 features.8
        parts = target_name.split('.')
        module = self.model if hasattr(model, 'backbone') else self.model
        base = module.backbone if hasattr(module, 'backbone') else module
        for part in parts:
            if part.isdigit():
                base = base[int(part)]
            else:
                base = getattr(base, part)
        return base

    def _register_hooks(self):
        self.target_module.register_forward_hook(
            lambda m, i, o: setattr(self.__class__, '_activations_tmp', o.detach())
        )
        self.target_module.register_full_backward_hook(
            lambda m, gi, go: setattr(self.__class__, '_gradients_tmp', go[0].detach())
        )

    def generate_cam(self, input_tensor: torch.Tensor, target_class: int = None) -> np.ndarray:
        """生成 CAM 热力图"""
        self.model.eval()
        output = self.model(input_tensor)

        if target_class is None:
            target_class = output.argmax(dim=1).item()

        self.model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1
        output.backward(gradient=one_hot, retain_graph=True)

        # 获取钩子保存的数据
        activations = getattr(self.__class__, '_activations_tmp', None)
        gradients = getattr(self.__class__, '_gradients_tmp', None)

        if activations is None or gradients is None:
            raise RuntimeError("Grad-CAM 钩子未触发，请检查目标层名称")

        weights = gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)
        cam = (weights * activations).sum(dim=1, keepdim=True)   # (1, 1, H', W')
        cam = torch.relu(cam).squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam


# ==================== ModelHandler 主类 ====================

# 各模型的预处理和 Grad-CAM 配置
MODEL_CONFIGS = {
    'resnet18': {
        'model_cls': ResNet18Classifier,
        'model_kwargs': {'num_classes': 3, 'pretrained': True, 'dropout': 0.25},
        'image_size': 224,
        'normalize_mean': [0.485, 0.456, 0.406],
        'normalize_std': [0.229, 0.224, 0.225],
        'gradcam_target': 'layer4',
    },
    'efficientnet_b0': {
        'model_cls': EfficientNetB0Classifier,
        'model_kwargs': {'num_classes': 3, 'pretrained': True, 'dropout': 0.5},
        'image_size': 300,
        'normalize_mean': [0.485, 0.456, 0.406],
        'normalize_std': [0.229, 0.224, 0.225],
        'gradcam_target': 'features.8',  # EfficientNet-B0 最后一个 feature block
    },
}


class ModelHandler:
    """模型处理器 — 统一接口，支持多模型切换"""

    def __init__(self, model_path: str, device: str = 'auto', model_type: str = None):
        self.model_type = model_type or MODEL_TYPE
        self.model_path = model_path
        self.device = self._get_device(device)
        self.cfg = MODEL_CONFIGS[self.model_type]

        # 构建模型
        self.model = self.cfg['model_cls'](**self.cfg['model_kwargs'])
        self._load_weights()

        self.model.to(self.device)
        self.model.eval()

        self.class_names = ['benign', 'malignant', 'normal']
        self.class_names_cn = {
            'benign': '良性',
            'malignant': '恶性',
            'normal': '正常'
        }

        # 预处理流水线
        img_size = self.cfg['image_size']
        self.transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.cfg['normalize_mean'], std=self.cfg['normalize_std'])
        ])

        # Grad-CAM
        try:
            self.grad_cam = GradCAM(self.model, self.cfg['gradcam_target'])
            print(f"  Grad-CAM 目标层: {self.cfg['gradcam_target']}")
        except Exception as e:
            print(f"  ⚠ Grad-CAM 初始化失败: {e}")
            self.grad_cam = None

    def _get_device(self, device: str) -> torch.device:
        if device == 'auto':
            if torch.cuda.is_available():
                return torch.device('cuda')
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return torch.device('mps')
            return torch.device('cpu')
        return torch.device(device)

    def _load_weights(self):
        """加载权重文件"""
        print(f"正在加载模型: {self.model_path}")
        print(f"  模型类型: {self.model_type} | 设备: {self.device}")

        ckpt = torch.load(self.model_path, map_location=self.device, weights_only=False)

        if isinstance(ckpt, dict) and 'model_state_dict' in ckpt:
            self.model.load_state_dict(ckpt['model_state_dict'])
            extra = []
            if 'epoch' in ckpt:
                extra.append(f"Epoch={ckpt['epoch']}")
            if 'val_acc' in ckpt:
                extra.append(f"ValAcc={ckpt['val_acc']:.2f}%")
            print(f"  加载成功 ({', '.join(extra)})")
        elif isinstance(ckpt, dict):
            self.model.load_state_dict(ckpt)
            print(f"  加载成功 (state_dict)")
        else:
            raise ValueError(f"无法识别的权重格式: {type(ckpt)}")

    # ---------- 推理 ----------

    def predict(self, image: Image.Image) -> dict:
        """预测单张图像"""
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            pred_idx = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred_idx].item()

        return {
            'predicted_class': self.class_names[pred_idx],
            'predicted_class_cn': self.class_names_cn[self.class_names[pred_idx]],
            'confidence': round(confidence, 4),
            'probabilities': {
                self.class_names[i]: round(probs[0, i].item(), 4)
                for i in range(len(self.class_names))
            }
        }

    # ---------- TTA 推理 ----------

    def predict_with_tta(self, image: Image.Image, n_augments: int = 7) -> dict:
        """
        TTA 测试时增强推理（Stage5 核心创新点）
        
        使用 7 种增强: 原图 + 水平翻转 + 3种旋转(±10°, ±15°) + 2种缩放(±5%)
        """
        import torchvision.transforms.functional as TF

        img_size = self.cfg['image_size']

        augmentations = [
            ('original', image),
            ('hflip', TF.hflip(image)),
            ('rot+10', TF.rotate(image, 10)),
            ('rot-10', TF.rotate(image, -10)),
            ('rot+15', TF.rotate(image, 15)),
            ('rot-15', TF.rotate(image, -15)),
            ('zoom_in', TF.resized(image, int(img_size * 1.05))),
            ('zoom_out', TF.resized(image, int(img_size * 0.95))),
        ]

        all_probs = []
        for name, aug_img in augmentations[:n_augments]:
            tensor = self.transform(aug_img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                out = self.model(tensor)
                prob = torch.nn.functional.softmax(out, dim=1)
                all_probs.append(prob[0])

        # 平均概率
        avg_prob = torch.stack(all_probs).mean(dim=0)
        pred_idx = torch.argmax(avg_prob).item()
        confidence = avg_prob[pred_idx].item()

        return {
            'predicted_class': self.class_names[pred_idx],
            'predicted_class_cn': self.class_names_cn[self.class_names[pred_idx]],
            'confidence': round(confidence, 4),
            'probabilities': {
                self.class_names[i]: round(avg_prob[i].item(), 4)
                for i in range(len(self.class_names))
            },
            'tta_augments': n_augments,
        }

    # ---------- Grad-CAM ----------

    def generate_gradcam(self, image: Image.Image, target_class: int = None) -> str:
        """生成 Grad-CAM 热力图 (base64)"""
        if self.grad_cam is None:
            return ''

        original_rgb = image.convert('RGB')
        original_size = original_rgb.size
        original_array = np.array(original_rgb)

        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        if target_class is None:
            with torch.no_grad():
                outputs = self.model(input_tensor)
                target_class = torch.argmax(outputs, dim=1).item()

        cam = self.grad_cam.generate_cam(input_tensor, target_class)
        cam_resized = cv2.resize(cam, original_size)

        heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(original_array, 0.6, heatmap, 0.4, 0)

        buffered = BytesIO()
        Image.fromarray(overlay).save(buffered, format='PNG')
        b64 = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{b64}"

    # ---------- 完整分析 ----------

    def analyze(self, image: Image.Image, use_tta: bool = False) -> dict:
        """完整分析：预测 + Grad-CAM"""
        prediction = self.predict_with_tta(image) if use_tta else self.predict(image)

        gradcam_b64 = ''
        if self.grad_cam is not None:
            target_idx = self.class_names.index(prediction['predicted_class'])
            gradcam_b64 = self.generate_gradcam(image, target_idx)

        result = {**prediction}
        if gradcam_b64:
            result['gradcam'] = gradcam_b64
        return result

    @property
    def model_info(self) -> dict:
        """返回当前模型元信息"""
        from config import MODEL_META
        info = MODEL_META.get(self.model_type, {})
        info.setdefault('type', self.model_type)
        return info
