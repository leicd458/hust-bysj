"""
数据加载模块 - 负责读取和预处理BUSI数据集
适合深度学习零基础的同学：这个模块就像是"数据管家"，负责把图片整理好送给模型训练
"""
import os
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.model_selection import train_test_split
from pathlib import Path

class BUSIDataset(Dataset):
    """
    BUSI乳腺超声图像数据集类
    
    什么是Dataset？
    - 就像一个"图片仓库"，PyTorch通过它来获取训练数据
    - 必须实现三个方法：__init__（初始化）、__len__（返回数据量）、__getitem__（获取单个数据）
    """
    
    def __init__(self, image_paths, labels, mask_paths=None, transform=None, mode='classification'):
        """
        初始化数据集
        
        参数说明：
            image_paths: 图片路径列表，例如 ['img1.png', 'img2.png', ...]
            labels: 标签列表，例如 [0, 1, 2, ...] 对应 [正常, 良性, 恶性]
            mask_paths: 分割掩码路径列表（可选，仅分割任务需要）
            transform: 数据变换操作（如调整大小、归一化等）
            mode: 'classification'（分类）或 'segmentation'（分割）
        """
        self.image_paths = image_paths
        self.labels = labels
        self.mask_paths = mask_paths
        self.transform = transform
        self.mode = mode
        
    def __len__(self):
        """返回数据集大小"""
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        """
        获取第idx个数据样本
        
        这个方法会被DataLoader自动调用，每次返回一个样本
        """
        # 1. 读取图片
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')  # 转换为RGB格式
        
        # 2. 获取标签
        label = self.labels[idx]
        
        # 3. 应用数据变换（如果有）
        if self.transform:
            image = self.transform(image)
        
        # 4. 根据任务类型返回不同的数据
        if self.mode == 'classification':
            # 分类任务：返回图片和类别标签
            return image, torch.tensor(label, dtype=torch.long)
        
        elif self.mode == 'segmentation':
            # 分割任务：还需要返回分割掩码
            if self.mask_paths is not None and idx < len(self.mask_paths):
                mask_path = self.mask_paths[idx]
                if os.path.exists(mask_path):
                    mask = Image.open(mask_path).convert('L')  # 转换为灰度图
                    if self.transform:
                        mask = self.transform(mask)
                    return image, mask, torch.tensor(label, dtype=torch.long)
            
            # 如果没有掩码，返回空掩码
            empty_mask = torch.zeros((1, image.shape[1], image.shape[2]))
            return image, empty_mask, torch.tensor(label, dtype=torch.long)


def get_transforms(image_size=224, augmentation=True):
    """
    获取数据变换操作
    
    什么是数据变换？
    - 就像给图片做"标准化处理"，让所有图片格式统一
    - 训练时可以加入随机变换（数据增强），增加数据多样性
    
    参数说明：
        image_size: 目标图片尺寸
        augmentation: 是否使用数据增强
    """
    if augmentation:
        # 训练集变换：包含数据增强
        transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),  # 调整大小
            transforms.RandomHorizontalFlip(p=0.5),       # 随机水平翻转
            transforms.RandomRotation(15),                 # 随机旋转±15度
            transforms.ColorJitter(brightness=0.2, contrast=0.2),  # 随机调整亮度和对比度
            transforms.ToTensor(),                         # 转换为张量（Tensor）
            transforms.Normalize(mean=[0.485, 0.456, 0.406],  # 归一化（使用ImageNet统计值）
                               std=[0.229, 0.224, 0.225])
        ])
    else:
        # 验证集/测试集变换：不使用数据增强
        transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
    
    return transform


def load_busi_data(data_root, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, random_seed=42):
    """
    加载BUSI数据集并划分训练集、验证集、测试集
    
    BUSI数据集结构：
    data_root/
    ├── normal/          # 正常图片
    │   ├── normal (1).png
    │   ├── normal (2).png
    │   └── ...
    ├── benign/          # 良性肿瘤图片
    │   ├── benign (1).png
    │   ├── benign (1)_mask.png  # 对应的分割掩码
    │   └── ...
    └── malignant/       # 恶性肿瘤图片
        ├── malignant (1).png
        ├── malignant (1)_mask.png
        └── ...
    
    参数说明：
        data_root: 数据集根目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        random_seed: 随机种子（保证每次划分结果一致）
    
    返回：
        字典，包含训练集、验证集、测试集的图片路径、标签、掩码路径
    """
    print("\n" + "=" * 60)
    print("开始加载BUSI数据集...")
    print("=" * 60)
    
    # 类别映射：文件夹名 -> 数字标签
    class_to_idx = {'normal': 0, 'benign': 1, 'malignant': 2}
    
    all_image_paths = []
    all_labels = []
    all_mask_paths = []
    
    # 遍历每个类别文件夹
    for class_name, class_idx in class_to_idx.items():
        class_dir = Path(data_root) / class_name
        
        if not class_dir.exists():
            print(f"警告: 未找到类别文件夹 {class_dir}")
            continue
        
        # 获取该类别下的所有图片（排除掩码文件）
        image_files = [f for f in class_dir.glob("*.png") if "_mask" not in f.name]
        
        print(f"\n类别: {class_name} (标签={class_idx})")
        print(f"  找到 {len(image_files)} 张图片")
        
        for img_path in image_files:
            all_image_paths.append(str(img_path))
            all_labels.append(class_idx)
            
            # 查找对应的掩码文件
            mask_path = img_path.parent / f"{img_path.stem}_mask.png"
            if mask_path.exists():
                all_mask_paths.append(str(mask_path))
            else:
                all_mask_paths.append(None)  # 正常类别通常没有掩码
    
    print(f"\n总计加载 {len(all_image_paths)} 张图片")
    
    # 划分数据集
    # 第一步：先分出测试集
    train_val_images, test_images, train_val_labels, test_labels, train_val_masks, test_masks = \
        train_test_split(all_image_paths, all_labels, all_mask_paths, 
                        test_size=test_ratio, random_state=random_seed, stratify=all_labels)
    
    # 第二步：从剩余数据中分出验证集
    val_ratio_adjusted = val_ratio / (train_ratio + val_ratio)  # 调整验证集比例
    train_images, val_images, train_labels, val_labels, train_masks, val_masks = \
        train_test_split(train_val_images, train_val_labels, train_val_masks,
                        test_size=val_ratio_adjusted, random_state=random_seed, stratify=train_val_labels)
    
    print(f"\n数据集划分完成:")
    print(f"  训练集: {len(train_images)} 张")
    print(f"  验证集: {len(val_images)} 张")
    print(f"  测试集: {len(test_images)} 张")
    print("=" * 60)
    
    return {
        'train': {'images': train_images, 'labels': train_labels, 'masks': train_masks},
        'val': {'images': val_images, 'labels': val_labels, 'masks': val_masks},
        'test': {'images': test_images, 'labels': test_labels, 'masks': test_masks}
    }


def create_dataloaders(data_dict, batch_size=16, image_size=224, num_workers=4, mode='classification'):
    """
    创建数据加载器（DataLoader）
    
    什么是DataLoader？
    - 就像是"传送带"，自动把数据分批次送给模型
    - 支持多线程加载，提高效率
    
    参数说明：
        data_dict: load_busi_data返回的数据字典
        batch_size: 批次大小（一次训练多少张图）
        image_size: 图片尺寸
        num_workers: 数据加载线程数
        mode: 'classification' 或 'segmentation'
    
    返回：
        train_loader, val_loader, test_loader
    """
    # 获取数据变换
    train_transform = get_transforms(image_size, augmentation=True)   # 训练集使用数据增强
    val_transform = get_transforms(image_size, augmentation=False)    # 验证集不使用数据增强
    
    # 创建数据集对象
    train_dataset = BUSIDataset(
        data_dict['train']['images'],
        data_dict['train']['labels'],
        data_dict['train']['masks'],
        transform=train_transform,
        mode=mode
    )
    
    val_dataset = BUSIDataset(
        data_dict['val']['images'],
        data_dict['val']['labels'],
        data_dict['val']['masks'],
        transform=val_transform,
        mode=mode
    )
    
    test_dataset = BUSIDataset(
        data_dict['test']['images'],
        data_dict['test']['labels'],
        data_dict['test']['masks'],
        transform=val_transform,
        mode=mode
    )
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,        # 训练时打乱数据
        num_workers=num_workers,
        pin_memory=True      # 加速数据传输到GPU/MPS
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,       # 验证时不打乱
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    print(f"\n数据加载器创建完成:")
    print(f"  训练批次数: {len(train_loader)}")
    print(f"  验证批次数: {len(val_loader)}")
    print(f"  测试批次数: {len(test_loader)}")
    
    return train_loader, val_loader, test_loader


# 测试代码
if __name__ == "__main__":
    from config import config
    
    # 加载数据
    data_dict = load_busi_data(
        config.data_root,
        config.train_ratio,
        config.val_ratio,
        config.test_ratio,
        config.random_seed
    )
    
    # 创建数据加载器
    train_loader, val_loader, test_loader = create_dataloaders(
        data_dict,
        config.batch_size,
        config.image_size,
        config.num_workers
    )
    
    # 查看一个批次的数据
    images, labels = next(iter(train_loader))
    print(f"\n批次数据形状:")
    print(f"  图片: {images.shape}")  # 应该是 [batch_size, 3, 224, 224]
    print(f"  标签: {labels.shape}")  # 应该是 [batch_size]
