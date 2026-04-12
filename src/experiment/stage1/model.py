"""
阶段1模型: ResNet-18 基线 (无数据增强)
目标准确率: 79%
"""

import torch
import torch.nn as nn
from torchvision import models


class ResNet18Baseline(nn.Module):
    """ResNet-18 基线模型
    
    使用 ImageNet 预训练权重，修改最后一层适配三分类任务
    """
    
    def __init__(self, num_classes=3, pretrained=True):
        super().__init__()
        
        # 加载预训练模型
        self.model = models.resnet18(pretrained=pretrained)
        
        # 修改最后一层 (fc)
        # ResNet-18 的 fc 输入维度是 512
        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, num_classes)
        )
        
        print(f"✓ ResNet-18 基线模型已加载")
        print(f"  - 预训练: {pretrained}")
        print(f"  - 类别数: {num_classes}")
        print(f"  - 参数量: {sum(p.numel() for p in self.parameters()):,}")
    
    def forward(self, x):
        return self.model(x)
    
    def freeze_backbone(self):
        """冻结骨干网络，只训练分类头"""
        for param in self.model.parameters():
            param.requires_grad = False
        
        # 解冻最后一层
        for param in self.model.fc.parameters():
            param.requires_grad = True
        
        print("✓ 骨干网络已冻结，只训练分类头")
    
    def unfreeze_all(self):
        """解冻所有层"""
        for param in self.model.parameters():
            param.requires_grad = True
        
        print("✓ 所有层已解冻")


def load_model(num_classes=3, pretrained=True, device='cpu'):
    """加载模型
    
    Args:
        num_classes: 类别数 (默认3: benign, malignant, normal)
        pretrained: 是否使用预训练权重
        device: 设备
    
    Returns:
        model: 加载好的模型
    """
    model = ResNet18Baseline(num_classes=num_classes, pretrained=pretrained)
    model = model.to(device)
    
    return model


if __name__ == "__main__":
    # 测试模型
    model = load_model(num_classes=3, pretrained=False)
    
    # 测试前向传播
    dummy_input = torch.randn(2, 3, 224, 224)
    output = model(dummy_input)
    
    print(f"\n测试输出 shape: {output.shape}")  # [2, 3]
    print(f"输出: {output}")
