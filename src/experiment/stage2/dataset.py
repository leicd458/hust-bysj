"""
阶段2数据集: BUSI 数据集加载 + 传统数据增强
"""

import os
from pathlib import Path
from typing import Tuple, Optional

import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
import numpy as np


class BUSIDataset(Dataset):
    """BUSI 乳腺超声数据集
    
    数据集结构:
    data/raw/Dataset_BUSI_with_GT/
    ├── benign/
    ├── malignant/
    └── normal/
    """
    
    # 类别映射
    CLASS_NAMES = ['benign', 'malignant', 'normal']
    CLASS_TO_IDX = {'benign': 0, 'malignant': 1, 'normal': 2}
    
    def __init__(self, data_dir: str, transform=None, include_mask=False):
        """
        Args:
            data_dir: 数据目录路径
            transform: 图像变换
            include_mask: 是否包含 mask 图像
        """
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.include_mask = include_mask
        
        # 收集所有图像路径
        self.samples = []
        self._load_samples()
        
        print(f"✓ BUSI 数据集已加载")
        print(f"  - 总样本数: {len(self.samples)}")
        self._print_class_distribution()
    
    def _load_samples(self):
        """加载所有样本"""
        for class_name in self.CLASS_NAMES:
            class_dir = self.data_dir / class_name
            if not class_dir.exists():
                continue
            
            # 遍历目录中的所有图像
            for img_path in class_dir.glob("*.png"):
                # 跳过 mask 图像 (包含 "_mask" 的文件)
                if "_mask" in img_path.name:
                    continue
                
                self.samples.append({
                    'image_path': str(img_path),
                    'label': self.CLASS_TO_IDX[class_name],
                    'class_name': class_name
                })
    
    def _print_class_distribution(self):
        """打印类别分布"""
        class_counts = {name: 0 for name in self.CLASS_NAMES}
        for sample in self.samples:
            class_counts[sample['class_name']] += 1
        
        for name, count in class_counts.items():
            print(f"  - {name}: {count} 张")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # 加载图像
        image = Image.open(sample['image_path']).convert('RGB')
        
        # 应用变换
        if self.transform:
            image = self.transform(image)
        
        return image, sample['label']


def get_transforms(is_train=True):
    """获取阶段2的数据变换 (传统数据增强)
    
    阶段2增强策略 (参考老项目成功配置):
    - 随机裁剪: 模拟平移和缩放
    - 随机水平翻转: 50%概率
    - 随机垂直翻转: 20%概率 (医学图像有固定朝向)
    - 随机旋转: ±5度 (mild augmentation)
    - 随机仿射变换: 轻微平移±5%、缩放±5%
    - 高斯模糊: 模拟医学噪声
    
    注意: 医学图像增强需要谨慎，避免过度增强破坏诊断特征
    """
    if is_train:
        # 训练集: 应用传统数据增强 (mild augmentation)
        transform = transforms.Compose([
            # 先resize到稍大尺寸，再随机裁剪
            transforms.Resize((256, 256)),
            transforms.RandomCrop(224),
            
            # 随机翻转
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.2),
            
            # 随机旋转 (±5度，mild augmentation)
            transforms.RandomRotation(degrees=5),
            
            # 随机仿射变换 (轻微平移和缩放)
            transforms.RandomAffine(
                degrees=0,
                translate=(0.05, 0.05),  # ±5% 平移
                scale=(0.95, 1.05)       # ±5% 缩放
            ),
            
            # 高斯模糊 (模拟医学噪声)
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
            
            # 转换为 Tensor
            transforms.ToTensor(),
            
            # 标准化 (ImageNet 均值和方差)
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    else:
        # 验证集/测试集: 仅基础预处理
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    return transform


class BUSIDatasetWithIndices(Dataset):
    """BUSI 数据集（支持索引访问，用于子集划分）"""
    
    # 类别映射
    CLASS_NAMES = ['benign', 'malignant', 'normal']
    CLASS_TO_IDX = {'benign': 0, 'malignant': 1, 'normal': 2}
    
    def __init__(self, data_dir: str):
        """
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = Path(data_dir)
        
        # 收集所有图像路径
        self.samples = []
        self._load_samples()
        
        print(f"✓ BUSI 数据集已加载")
        print(f"  - 总样本数: {len(self.samples)}")
        self._print_class_distribution()
    
    def _load_samples(self):
        """加载所有样本"""
        for class_name in self.CLASS_NAMES:
            class_dir = self.data_dir / class_name
            if not class_dir.exists():
                continue
            
            # 遍历目录中的所有图像
            for img_path in class_dir.glob("*.png"):
                # 跳过 mask 图像 (包含 "_mask" 的文件)
                if "_mask" in img_path.name:
                    continue
                
                self.samples.append({
                    'image_path': str(img_path),
                    'label': self.CLASS_TO_IDX[class_name],
                    'class_name': class_name
                })
    
    def _print_class_distribution(self):
        """打印类别分布"""
        class_counts = {name: 0 for name in self.CLASS_NAMES}
        for sample in self.samples:
            class_counts[sample['class_name']] += 1
        
        for name, count in class_counts.items():
            print(f"  - {name}: {count} 张")
    
    def __len__(self):
        return len(self.samples)
    
    def get_sample(self, idx):
        """获取样本（图像路径和标签）"""
        return self.samples[idx]


class TransformSubset(Dataset):
    """带变换的数据集子集
    
    确保只对指定子集应用数据增强
    """
    
    def __init__(self, dataset: Dataset, indices: list, transform=None):
        """
        Args:
            dataset: 完整数据集
            indices: 子集索引列表
            transform: 图像变换
        """
        self.dataset = dataset
        self.indices = indices
        self.transform = transform
    
    def __len__(self):
        return len(self.indices)
    
    def __getitem__(self, idx):
        # 获取真实索引
        real_idx = self.indices[idx]
        
        # 获取样本信息
        sample = self.dataset.get_sample(real_idx)
        
        # 加载图像
        image = Image.open(sample['image_path']).convert('RGB')
        label = sample['label']
        
        # 应用变换
        if self.transform:
            image = self.transform(image)
        
        return image, label


def get_dataloaders(
    data_dir: str,
    batch_size: int = 64,
    num_workers: int = 4,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """获取数据加载器
    
    Args:
        data_dir: 数据目录
        batch_size: 批次大小
        num_workers: 工作进程数
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        seed: 随机种子
    
    Returns:
        train_loader, val_loader, test_loader
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    
    # 加载完整数据集（不应用变换）
    full_dataset = BUSIDatasetWithIndices(data_dir)
    
    # 设置随机种子
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # 划分数据集索引
    total_size = len(full_dataset)
    train_size = int(train_ratio * total_size)
    val_size = int(val_ratio * total_size)
    test_size = total_size - train_size - val_size
    
    # 使用 random_split 划分索引
    train_indices, val_indices, test_indices = random_split(
        range(total_size),
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(seed)
    )
    
    # 创建带变换的子集
    # ⚠️ 只对训练集应用数据增强
    train_dataset = TransformSubset(
        full_dataset,
        train_indices.indices,
        transform=get_transforms(is_train=True)
    )
    
    val_dataset = TransformSubset(
        full_dataset,
        val_indices.indices,
        transform=get_transforms(is_train=False)
    )
    
    test_dataset = TransformSubset(
        full_dataset,
        test_indices.indices,
        transform=get_transforms(is_train=False)
    )
    
    print(f"\n✓ 数据集划分完成 (种子={seed})")
    print(f"  - 训练集: {len(train_dataset)} 张 (带传统增强)")
    print(f"  - 验证集: {len(val_dataset)} 张")
    print(f"  - 测试集: {len(test_dataset)} 张")
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
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
    
    return train_loader, val_loader, test_loader


if __name__ == "__main__":
    # 测试数据集
    data_dir = "/Users/koolei/Desktop/hust-bysj-new/data/raw/Dataset_BUSI_with_GT"
    
    if Path(data_dir).exists():
        train_loader, val_loader, test_loader = get_dataloaders(
            data_dir=data_dir,
            batch_size=64,
            num_workers=0,
            seed=42
        )
        
        # 测试加载
        images, labels = next(iter(train_loader))
        print(f"\n批次测试:")
        print(f"  - 图像 shape: {images.shape}")  # [64, 3, 224, 224]
        print(f"  - 标签 shape: {labels.shape}")  # [64]
        print(f"  - 标签: {labels}")
        
        # 测试数据增强效果
        print(f"\n数据增强测试:")
        print(f"  - 训练集使用传统数据增强 (翻转、旋转、裁剪、仿射)")
        print(f"  - 验证集/测试集仅使用基础预处理")
    else:
        print(f"数据目录不存在: {data_dir}")
