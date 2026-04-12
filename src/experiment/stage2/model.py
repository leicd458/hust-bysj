"""
阶段2模型: ResNet-18 (与阶段1相同)
"""

import torch
import torch.nn as nn
from torchvision import models


class ResNetClassifier(nn.Module):
    """ResNet-18 分类器
    
    使用预训练的 ResNet-18 模型，修改最后一层用于 3 分类任务
    """
    
    def __init__(self, num_classes=3, pretrained=True):
        super(ResNetClassifier, self).__init__()
        
        # 加载预训练的 ResNet-18
        if pretrained:
            self.model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        else:
            self.model = models.resnet18(weights=None)
        
        # 修改最后一层 (fc)
        # ResNet-18 的 fc 输入维度是 512
        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)
    
    def get_num_parameters(self):
        """获取模型参数量"""
        return sum(p.numel() for p in self.parameters())


if __name__ == "__main__":
    # 测试模型
    model = ResNetClassifier(num_classes=3, pretrained=True)
    
    print(f"模型: ResNet-18 (预训练)")
    print(f"参数量: {model.get_num_parameters():,}")
    
    # 测试前向传播
    x = torch.randn(2, 3, 224, 224)
    y = model(x)
    print(f"输入 shape: {x.shape}")
    print(f"输出 shape: {y.shape}")  # [2, 3]
