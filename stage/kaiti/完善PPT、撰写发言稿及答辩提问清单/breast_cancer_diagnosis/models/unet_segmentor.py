"""
U-Net分割器模块
适合深度学习零基础的同学：U-Net是专门用于图像分割的模型，形状像字母"U"
"""
import torch
import torch.nn as nn

class DoubleConv(nn.Module):
    """
    双卷积块：U-Net的基本构建单元
    
    结构：Conv -> BatchNorm -> ReLU -> Conv -> BatchNorm -> ReLU
    
    什么是卷积（Convolution）？
    - 就像用"滤镜"扫描图片，提取特征
    - 例如：边缘检测滤镜可以找到图片中的轮廓
    
    什么是BatchNorm？
    - 批归一化，让训练更稳定
    - 就像"标准化考试成绩"，让不同批次的数据分布一致
    
    什么是ReLU？
    - 激活函数，引入非线性
    - 公式：ReLU(x) = max(0, x)
    - 就像"过滤负能量"，只保留正值
    """
    
    def __init__(self, in_channels, out_channels):
        """
        参数说明：
            in_channels: 输入通道数
            out_channels: 输出通道数
        """
        super(DoubleConv, self).__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        return self.double_conv(x)


class UNet(nn.Module):
    """
    U-Net分割网络
    
    什么是U-Net？
    - 2015年提出，专门用于医学图像分割
    - 结构像字母"U"：先下采样（压缩），再上采样（恢复）
    - 核心创新：跳跃连接（skip connection），保留细节信息
    
    为什么叫"分割"？
    - 不是简单的分类（整张图是什么），而是像素级分类
    - 对每个像素判断：这个像素是肿瘤还是正常组织？
    - 输出是一张"掩码图"，标记出肿瘤区域
    
    U-Net结构：
    
    输入图片 (224x224)
         ↓
    [编码器 Encoder - 下采样路径]
    DoubleConv(3->64)   ──┐
         ↓ MaxPool         │ 跳跃连接
    DoubleConv(64->128) ──┤
         ↓ MaxPool         │
    DoubleConv(128->256)──┤
         ↓ MaxPool         │
    DoubleConv(256->512)──┘
         ↓
    [瓶颈层 Bottleneck]
    DoubleConv(512->1024)
         ↓
    [解码器 Decoder - 上采样路径]
    UpConv + Concat + DoubleConv
         ↓
    UpConv + Concat + DoubleConv
         ↓
    UpConv + Concat + DoubleConv
         ↓
    UpConv + Concat + DoubleConv
         ↓
    输出掩码 (224x224)
    """
    
    def __init__(self, in_channels=3, out_channels=1, features=[64, 128, 256, 512]):
        """
        初始化U-Net
        
        参数说明：
            in_channels: 输入通道数（RGB图片=3）
            out_channels: 输出通道数（二分类分割=1，多分类分割=类别数）
            features: 每层的特征通道数列表
        """
        super(UNet, self).__init__()
        
        self.encoder_blocks = nn.ModuleList()  # 编码器（下采样）
        self.decoder_blocks = nn.ModuleList()  # 解码器（上采样）
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)  # 池化层（缩小尺寸）
        
        # ==================== 编码器（下采样路径）====================
        # 逐层提取特征，同时缩小图片尺寸
        for feature in features:
            self.encoder_blocks.append(DoubleConv(in_channels, feature))
            in_channels = feature
        
        # ==================== 瓶颈层 ====================
        # 最深层，特征最抽象
        self.bottleneck = DoubleConv(features[-1], features[-1] * 2)
        
        # ==================== 解码器（上采样路径）====================
        # 逐层恢复图片尺寸，同时融合编码器的特征
        for feature in reversed(features):
            # 上采样：放大图片尺寸
            self.decoder_blocks.append(
                nn.ConvTranspose2d(feature * 2, feature, kernel_size=2, stride=2)
            )
            # 双卷积：处理拼接后的特征
            self.decoder_blocks.append(
                DoubleConv(feature * 2, feature)
            )
        
        # ==================== 最后的输出层 ====================
        # 1x1卷积，将特征图转换为分割掩码
        self.final_conv = nn.Conv2d(features[0], out_channels, kernel_size=1)
        
        print(f"U-Net初始化完成:")
        print(f"  - 输入通道: {3}")
        print(f"  - 输出通道: {out_channels}")
        print(f"  - 特征层级: {features}")
    
    def forward(self, x):
        """
        前向传播
        
        参数说明：
            x: 输入图片，形状 [batch_size, 3, 224, 224]
        
        返回：
            分割掩码，形状 [batch_size, 1, 224, 224]
            每个像素的值表示该像素属于肿瘤的概率
        """
        # 保存编码器每层的输出（用于跳跃连接）
        skip_connections = []
        
        # ==================== 编码器前向传播 ====================
        for encoder_block in self.encoder_blocks:
            x = encoder_block(x)
            skip_connections.append(x)  # 保存当前层输出
            x = self.pool(x)  # 下采样（缩小尺寸）
        
        # ==================== 瓶颈层 ====================
        x = self.bottleneck(x)
        
        # 反转跳跃连接列表（从深到浅）
        skip_connections = skip_connections[::-1]
        
        # ==================== 解码器前向传播 ====================
        for idx in range(0, len(self.decoder_blocks), 2):
            # 上采样
            x = self.decoder_blocks[idx](x)
            
            # 获取对应的跳跃连接
            skip_connection = skip_connections[idx // 2]
            
            # 如果尺寸不匹配，进行调整（处理奇数尺寸的情况）
            if x.shape != skip_connection.shape:
                x = nn.functional.interpolate(x, size=skip_connection.shape[2:])
            
            # 拼接跳跃连接（在通道维度）
            # 例如：[B, 256, 56, 56] + [B, 256, 56, 56] -> [B, 512, 56, 56]
            x = torch.cat([skip_connection, x], dim=1)
            
            # 双卷积处理
            x = self.decoder_blocks[idx + 1](x)
        
        # ==================== 输出层 ====================
        x = self.final_conv(x)
        
        return x


# 测试代码
if __name__ == "__main__":
    # 创建U-Net模型
    model = UNet(in_channels=3, out_channels=1, features=[64, 128, 256, 512])
    
    # 打印模型结构
    print("\n" + "=" * 60)
    print("模型结构:")
    print("=" * 60)
    print(model)
    
    # 测试前向传播
    print("\n" + "=" * 60)
    print("测试前向传播:")
    print("=" * 60)
    
    # 创建随机输入
    batch_size = 2
    dummy_input = torch.randn(batch_size, 3, 224, 224)
    print(f"输入形状: {dummy_input.shape}")
    
    # 前向传播
    output = model(dummy_input)
    print(f"输出形状: {output.shape}")
    
    # 计算参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n总参数量: {total_params:,}")
    print(f"可训练参数量: {trainable_params:,}")
