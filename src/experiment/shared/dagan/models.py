#!/usr/bin/env python3
"""
DAGAN (Data Augmentation GAN) 模型定义

参考论文: Al-Dhabyani et al. 2019 - IJACSA
基于简化版的 Conditional GAN 架构
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


# ==================== 生成器 (简化版U-Net) ====================

class DAGANGenerator(nn.Module):
    """
    DAGAN生成器 - 简化版U-Net
    
    用于从输入图像生成变体
    输入: (B, 3, 256, 256) RGB图像
    输出: (B, 3, 256, 256) 合成图像
    """
    def __init__(self, in_channels=3, out_channels=3, features=64):
        super(DAGANGenerator, self).__init__()
        
        # 编码器
        self.enc1 = self._down_block(in_channels, features, normalize=False)
        self.enc2 = self._down_block(features, features * 2)
        self.enc3 = self._down_block(features * 2, features * 4)
        self.enc4 = self._down_block(features * 4, features * 8, dropout=0.5)
        
        # 瓶颈
        self.bottleneck = self._down_block(features * 8, features * 8, dropout=0.5)
        
        # 解码器
        self.dec4 = self._up_block(features * 8, features * 8, dropout=0.5)
        self.dec3 = self._up_block(features * 16, features * 4)
        self.dec2 = self._up_block(features * 8, features * 2)
        self.dec1 = self._up_block(features * 4, features)
        
        # 输出层
        self.final = nn.Sequential(
            nn.Conv2d(features * 2, out_channels, kernel_size=1),
            nn.Tanh()
        )
    
    def _down_block(self, in_channels, out_channels, normalize=True, dropout=0.0):
        """下采样块"""
        layers = [
            nn.Conv2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1, bias=False)
        ]
        if normalize:
            layers.append(nn.BatchNorm2d(out_channels))
        layers.append(nn.LeakyReLU(0.2, inplace=True))
        if dropout:
            layers.append(nn.Dropout(dropout))
        return nn.Sequential(*layers)
    
    def _up_block(self, in_channels, out_channels, dropout=0.0):
        """上采样块"""
        layers = [
            nn.ConvTranspose2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        ]
        if dropout:
            layers.append(nn.Dropout(dropout))
        return nn.Sequential(*layers)
    
    def forward(self, x):
        # 编码器
        e1 = self.enc1(x)  # 256->128
        e2 = self.enc2(e1)  # 128->64
        e3 = self.enc3(e2)  # 64->32
        e4 = self.enc4(e3)  # 32->16
        
        # 瓶颈
        b = self.bottleneck(e4)  # 16->8
        
        # 解码器（带skip connection）
        d4 = self.dec4(b)  # 8->16
        d4 = torch.cat([d4, e4], dim=1)
        
        d3 = self.dec3(d4)  # 16->32
        d3 = torch.cat([d3, e3], dim=1)
        
        d2 = self.dec2(d3)  # 32->64
        d2 = torch.cat([d2, e2], dim=1)
        
        d1 = self.dec1(d2)  # 64->128
        d1 = torch.cat([d1, e1], dim=1)
        
        # 输出
        out = self.final(d1)  # 128->256
        
        # 上采样到原始尺寸
        return F.interpolate(out, size=x.shape[2:], mode='bilinear', align_corners=False)


# ==================== 判别器 (PatchGAN) ====================

class DAGANDiscriminator(nn.Module):
    """
    DAGAN判别器 - PatchGAN架构
    
    判断图像是真实的还是生成的
    输入: 两张图像拼接 (B, 6, 256, 256)
    输出: 真实性判断 (B, 1, 30, 30)
    """
    def __init__(self, in_channels=3, features=64):
        super(DAGANDiscriminator, self).__init__()
        
        def discriminator_block(in_filters, out_filters, normalize=True):
            """判别器块"""
            layers = [nn.Conv2d(in_filters, out_filters, kernel_size=4, stride=2, padding=1)]
            if normalize:
                layers.append(nn.BatchNorm2d(out_filters))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers
        
        self.model = nn.Sequential(
            *discriminator_block(in_channels * 2, features, normalize=False),  # 输入: 拼接的两张图
            *discriminator_block(features, features * 2),
            *discriminator_block(features * 2, features * 4),
            *discriminator_block(features * 4, features * 8),
            nn.Conv2d(features * 8, 1, kernel_size=4, stride=1, padding=1)
        )
    
    def forward(self, img_A, img_B):
        # 拼接输入图像
        img_input = torch.cat((img_A, img_B), dim=1)
        return self.model(img_input)


# ==================== 损失函数 ====================

class GANLoss(nn.Module):
    """GAN损失函数 - LSGAN (Least Squares GAN)"""
    def __init__(self):
        super(GANLoss, self).__init__()
        self.loss = nn.MSELoss()
    
    def __call__(self, prediction, target_is_real):
        """计算损失
        
        Args:
            prediction: 判别器输出
            target_is_real: True表示真实图像，False表示生成图像
        """
        if target_is_real:
            target_tensor = torch.ones_like(prediction)
        else:
            target_tensor = torch.zeros_like(prediction)
        return self.loss(prediction, target_tensor)


# ==================== 测试代码 ====================

if __name__ == '__main__':
    print("=" * 70)
    print("测试 DAGAN 模型")
    print("=" * 70)
    
    # 测试生成器
    generator = DAGANGenerator(in_channels=3, out_channels=3)
    g_params = sum(p.numel() for p in generator.parameters())
    print(f"\n生成器参数量: {g_params:,}")
    
    # 测试判别器
    discriminator = DAGANDiscriminator(in_channels=3)
    d_params = sum(p.numel() for p in discriminator.parameters())
    print(f"判别器参数量: {d_params:,}")
    print(f"总参数量: {g_params + d_params:,}")
    
    # 测试前向传播
    print("\n测试前向传播...")
    x = torch.randn(2, 3, 256, 256)
    fake = generator(x)
    pred = discriminator(x, fake)
    
    print(f"输入形状: {x.shape}")
    print(f"生成图像形状: {fake.shape}")
    print(f"判别器输出形状: {pred.shape}")
    
    # 测试损失
    print("\n测试损失函数...")
    loss_fn = GANLoss()
    loss_real = loss_fn(pred, True)
    loss_fake = loss_fn(pred, False)
    print(f"真实损失: {loss_real.item():.4f}")
    print(f"虚假损失: {loss_fake.item():.4f}")
    
    print("\n" + "=" * 70)
    print("✅ DAGAN模型测试通过")
    print("=" * 70)
