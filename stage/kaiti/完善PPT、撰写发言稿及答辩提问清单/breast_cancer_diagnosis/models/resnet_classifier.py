"""
ResNet18分类器模块
适合深度学习零基础的同学：ResNet是一种经典的深度学习模型，就像"搭积木"一样层层堆叠
"""
import torch
import torch.nn as nn
from torchvision import models

class ResNetClassifier(nn.Module):
    """
    基于ResNet18的乳腺癌分类器
    
    什么是ResNet？
    - ResNet（残差网络）是2015年ImageNet冠军模型
    - 核心创新：引入"跳跃连接"（skip connection），解决深层网络训练困难的问题
    - 就像爬楼梯时可以跳过几级台阶，让信息更容易传递
    
    为什么选择ResNet18？
    - 18表示网络有18层（相对较浅，适合小数据集）
    - 在医学图像分类任务中表现优秀
    - 训练速度快，适合Mac M系列芯片
    """
    
    def __init__(self, num_classes=3, pretrained=True):
        """
        初始化分类器
        
        参数说明：
            num_classes: 分类类别数（正常、良性、恶性 = 3类）
            pretrained: 是否使用预训练权重（迁移学习）
        
        什么是迁移学习？
        - 就像"站在巨人的肩膀上"
        - 使用在ImageNet（百万级图片数据集）上训练好的权重
        - 然后在我们的小数据集上微调，效果更好、训练更快
        """
        super(ResNetClassifier, self).__init__()
        
        # 1. 加载预训练的ResNet18模型
        if pretrained:
            print("加载预训练的ResNet18权重（来自ImageNet）...")
            self.resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        else:
            print("从零开始训练ResNet18...")
            self.resnet = models.resnet18(weights=None)
        
        # 2. 获取ResNet18最后一层的输入特征数
        # ResNet18的全连接层输入是512维特征
        num_features = self.resnet.fc.in_features
        
        # 3. 替换最后的全连接层
        # 原始ResNet18是1000类分类（ImageNet），我们改成3类
        self.resnet.fc = nn.Linear(num_features, num_classes)
        
        print(f"ResNet18分类器初始化完成: {num_classes}类分类")
        print(f"  - 使用预训练权重: {pretrained}")
        print(f"  - 最后一层: Linear({num_features} -> {num_classes})")
    
    def forward(self, x):
        """
        前向传播：输入图片 -> 输出类别概率
        
        参数说明：
            x: 输入图片张量，形状为 [batch_size, 3, 224, 224]
               - batch_size: 批次大小
               - 3: RGB三通道
               - 224x224: 图片尺寸
        
        返回：
            输出张量，形状为 [batch_size, num_classes]
            每一行是一张图片属于各个类别的"得分"（未归一化的概率）
        """
        return self.resnet(x)
    
    def get_feature_maps(self, x):
        """
        获取中间层特征图（用于Grad-CAM可视化）
        
        什么是特征图？
        - 就像模型的"思考过程"
        - 每一层都会提取不同层次的特征
        - 浅层：边缘、纹理
        - 深层：语义信息（如"肿瘤"、"正常组织"）
        """
        # 逐层前向传播，保存中间结果
        x = self.resnet.conv1(x)
        x = self.resnet.bn1(x)
        x = self.resnet.relu(x)
        x = self.resnet.maxpool(x)
        
        x = self.resnet.layer1(x)
        x = self.resnet.layer2(x)
        x = self.resnet.layer3(x)
        x = self.resnet.layer4(x)  # 最后一个卷积层，用于Grad-CAM
        
        return x
    
    def freeze_backbone(self):
        """
        冻结骨干网络（除了最后一层）
        
        什么时候用？
        - 数据量很小时，只训练最后一层，防止过拟合
        - 就像"只调整最后的决策部分，前面的特征提取器保持不变"
        """
        for param in self.resnet.parameters():
            param.requires_grad = False
        
        # 只让最后一层可训练
        for param in self.resnet.fc.parameters():
            param.requires_grad = True
        
        print("已冻结ResNet18骨干网络，仅训练最后一层")
    
    def unfreeze_all(self):
        """解冻所有层，允许全部参数更新"""
        for param in self.resnet.parameters():
            param.requires_grad = True
        print("已解冻ResNet18所有层")


# 测试代码
if __name__ == "__main__":
    # 创建模型
    model = ResNetClassifier(num_classes=3, pretrained=True)
    
    # 打印模型结构
    print("\n" + "=" * 60)
    print("模型结构:")
    print("=" * 60)
    print(model)
    
    # 测试前向传播
    print("\n" + "=" * 60)
    print("测试前向传播:")
    print("=" * 60)
    
    # 创建随机输入（模拟一个批次的图片）
    batch_size = 4
    dummy_input = torch.randn(batch_size, 3, 224, 224)
    print(f"输入形状: {dummy_input.shape}")
    
    # 前向传播
    output = model(dummy_input)
    print(f"输出形状: {output.shape}")
    print(f"输出示例:\n{output}")
    
    # 计算参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n总参数量: {total_params:,}")
    print(f"可训练参数量: {trainable_params:,}")
