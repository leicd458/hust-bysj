"""
配置文件 - 存储所有超参数和路径配置
适合深度学习零基础的同学：这个文件就像是项目的"设置面板"，所有可调整的参数都在这里
"""
import torch

class Config:
    """项目配置类"""
    
    # ==================== 设备配置 ====================
    # Mac M系列芯片使用MPS加速，相当于Mac版的GPU加速
    # 如果MPS不可用，会自动降级到CPU
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    
    # ==================== 数据集配置 ====================
    # BUSI数据集路径（需要自己下载并解压到这个位置）
    data_root = "./data/BUSI"  # 数据集根目录
    
    # 数据集划分比例
    train_ratio = 0.7  # 70%用于训练
    val_ratio = 0.15   # 15%用于验证
    test_ratio = 0.15  # 15%用于测试
    
    # 图像尺寸（统一调整到这个大小）
    image_size = 224  # ResNet18的标准输入尺寸
    
    # 类别定义
    num_classes = 3  # 三分类：正常(normal)、良性(benign)、恶性(malignant)
    class_names = ['normal', 'benign', 'malignant']
    
    # ==================== 分类模型配置 ====================
    # 批次大小：一次训练处理多少张图片
    # Mac M系列建议设置较小的batch_size，避免内存不足
    batch_size = 16
    
    # 学习率：控制模型参数更新的步长
    # 太大容易不收敛，太小训练太慢
    learning_rate = 0.001
    
    # 训练轮数：整个数据集训练多少遍
    num_epochs = 50
    
    # 早停耐心值：验证集性能多少轮不提升就停止训练
    patience = 10
    
    # ==================== 分割模型配置 ====================
    # U-Net的特征通道数（越大模型越复杂）
    unet_features = [64, 128, 256, 512]
    
    # 分割模型的批次大小（通常比分类小，因为U-Net更占内存）
    seg_batch_size = 8
    
    # 分割模型学习率
    seg_learning_rate = 0.0001
    
    # 分割模型训练轮数
    seg_num_epochs = 100
    
    # ==================== 数据增强配置 ====================
    # 是否使用数据增强（训练时随机变换图片，增加数据多样性）
    use_augmentation = True
    
    # 随机旋转角度范围
    rotation_degree = 15
    
    # 随机水平翻转概率
    horizontal_flip_prob = 0.5
    
    # ==================== 保存路径配置 ====================
    # 模型保存目录
    checkpoint_dir = "./checkpoints"
    
    # 结果保存目录
    results_dir = "./results"
    
    # 日志保存目录
    log_dir = "./logs"
    
    # ==================== Grad-CAM配置 ====================
    # 目标层名称（ResNet18的最后一个卷积层）
    target_layer_name = "layer4"
    
    # ==================== 其他配置 ====================
    # 随机种子（保证实验可复现）
    random_seed = 42
    
    # 工作线程数（数据加载时的并行度）
    num_workers = 4
    
    # 是否使用预训练权重（迁移学习）
    use_pretrained = True
    
    def __repr__(self):
        """打印配置信息"""
        config_str = "\n" + "=" * 50 + "\n"
        config_str += "项目配置信息\n"
        config_str += "=" * 50 + "\n"
        config_str += f"设备: {self.device}\n"
        config_str += f"图像尺寸: {self.image_size}x{self.image_size}\n"
        config_str += f"批次大小: {self.batch_size}\n"
        config_str += f"学习率: {self.learning_rate}\n"
        config_str += f"训练轮数: {self.num_epochs}\n"
        config_str += f"类别数: {self.num_classes}\n"
        config_str += "=" * 50
        return config_str

# 创建全局配置对象
config = Config()

if __name__ == "__main__":
    print(config)
