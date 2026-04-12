#!/usr/bin/env python3
"""
阶段4数据集加载器

策略: 传统数据增强 + DAGAN合成数据混合训练

关键改进:
1. 原始训练集 + 传统增强
2. DAGAN合成数据（探索是否应用传统增强）
3. 探索最优合成数据比例
4. 探索不同的训练策略（分阶段训练、混合训练等）
"""

import sys
from pathlib import Path
from typing import Tuple
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split, ConcatDataset
from torchvision import transforms
from PIL import Image


class BUSIDataset(Dataset):
    """BUSI数据集"""
    
    CLASS_NAMES = ['benign', 'malignant', 'normal']
    CLASS_TO_IDX = {'benign': 0, 'malignant': 1, 'normal': 2}
    IDX_TO_CLASS = {0: 'benign', 1: 'malignant', 2: 'normal'}
    
    def __init__(self, data_dir: str, transform=None, class_names=None):
        """
        Args:
            data_dir: 数据目录
            transform: 图像变换
            class_names: 要加载的类别（None表示全部）
        """
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.samples = []
        
        # 确定要加载的类别
        if class_names is None:
            class_names = self.CLASS_NAMES
        
        self._load_samples(class_names)
    
    def _load_samples(self, class_names):
        """加载样本"""
        for class_name in class_names:
            if class_name not in self.CLASS_TO_IDX:
                continue
            
            class_dir = self.data_dir / class_name
            if not class_dir.exists():
                continue
            
            for img_path in class_dir.glob("*.png"):
                # 跳过 mask 图像
                if "_mask" in img_path.name:
                    continue
                
                self.samples.append({
                    'image_path': str(img_path),
                    'label': self.CLASS_TO_IDX[class_name],
                    'class_name': class_name
                })
        
        print(f"  ✓ {Path(self.data_dir).name}: {len(self.samples)} 张图像")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = Image.open(sample['image_path']).convert('RGB')
        label = sample['label']
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class BUSIDatasetWithIndices(Dataset):
    """BUSI数据集（支持索引访问，用于子集划分）"""
    
    CLASS_NAMES = ['benign', 'malignant', 'normal']
    CLASS_TO_IDX = {'benign': 0, 'malignant': 1, 'normal': 2}
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.samples = []
        self._load_samples()
        self._print_stats()
    
    def _load_samples(self):
        """加载所有样本"""
        for class_name in self.CLASS_NAMES:
            class_dir = self.data_dir / class_name
            if not class_dir.exists():
                continue
            
            for img_path in class_dir.glob("*.png"):
                if "_mask" in img_path.name:
                    continue
                self.samples.append({
                    'image_path': str(img_path),
                    'label': self.CLASS_TO_IDX[class_name],
                    'class_name': class_name
                })
    
    def _print_stats(self):
        """打印统计信息"""
        print(f"✓ 加载 BUSI 数据集")
        print(f"  - 总样本数: {len(self.samples)}")
        
        class_counts = {name: 0 for name in self.CLASS_NAMES}
        for sample in self.samples:
            class_counts[sample['class_name']] += 1
        
        for name, count in class_counts.items():
            print(f"  - {name}: {count} 张")
    
    def __len__(self):
        return len(self.samples)
    
    def get_sample(self, idx):
        return self.samples[idx]


class TransformSubset(Dataset):
    """带变换的数据集子集"""
    
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
        real_idx = self.indices[idx]
        sample = self.dataset.get_sample(real_idx)
        
        image = Image.open(sample['image_path']).convert('RGB')
        label = sample['label']
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


def get_transforms(is_train=True):
    """获取图像变换
    
    阶段4增强策略（继承阶段2成功配置）:
    - 随机裁剪: 模拟平移和缩放
    - 随机水平翻转: 50%概率
    - 随机垂直翻转: 20%概率
    - 随机旋转: ±5度
    - 随机仿射变换: 轻微平移±5%、缩放±5%
    - 高斯模糊: 模拟医学噪声
    
    Args:
        is_train: 是否为训练集
    """
    if is_train:
        # 训练集：传统数据增强（mild augmentation）
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.2),
            transforms.RandomRotation(degrees=5),
            transforms.RandomAffine(
                degrees=0,
                translate=(0.05, 0.05),
                scale=(0.95, 1.05)
            ),
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    else:
        # 验证集/测试集：仅基础预处理
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])


def get_dataloaders(
    real_data_dir: str,
    synthetic_data_dir: str,
    batch_size: int = 32,
    num_workers: int = 4,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
    synthetic_ratio: float = 1.0,
    augment_synthetic: bool = True
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """获取数据加载器
    
    Args:
        real_data_dir: 原始数据目录
        synthetic_data_dir: 合成数据目录
        batch_size: 批次大小
        num_workers: 工作进程数
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        seed: 随机种子
        synthetic_ratio: 合成数据采样比例 (0.0-1.0, 默认1.0使用全部)
        augment_synthetic: 是否对合成数据应用传统增强（默认True）
    
    Returns:
        train_loader, val_loader, test_loader
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    
    print("\n" + "=" * 70)
    print("阶段4: 加载数据集（传统增强 + DAGAN合成数据）")
    print("=" * 70)
    
    # 加载原始数据集（不应用变换）
    full_dataset = BUSIDatasetWithIndices(real_data_dir)
    
    # 设置随机种子
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # 划分数据集索引
    total_size = len(full_dataset)
    train_size = int(train_ratio * total_size)
    val_size = int(val_ratio * total_size)
    test_size = total_size - train_size - val_size
    
    # 使用相同的随机种子划分，确保与之前阶段一致
    train_dataset, val_dataset, test_dataset = random_split(
        full_dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(seed)
    )
    
    print(f"\n✓ 数据集划分完成 (种子={seed})")
    print(f"  - 训练集（原始）: {len(train_dataset)} 张")
    print(f"  - 验证集: {len(val_dataset)} 张")
    print(f"  - 测试集: {len(test_dataset)} 张")
    
    # 创建原始训练集子集（带传统增强）
    train_real_dataset = TransformSubset(
        full_dataset,
        train_dataset.indices,
        transform=get_transforms(is_train=True)
    )
    
    # 加载合成数据集
    print(f"\n加载合成数据集...")
    synthetic_dataset_full = BUSIDataset(
        synthetic_data_dir,
        transform=get_transforms(is_train=augment_synthetic)  # 根据参数决定是否增强
    )
    
    # 按比例采样合成数据
    if synthetic_ratio < 1.0:
        synthetic_size = int(len(synthetic_dataset_full) * synthetic_ratio)
        torch.manual_seed(seed)
        indices = torch.randperm(len(synthetic_dataset_full))[:synthetic_size].tolist()
        synthetic_dataset = torch.utils.data.Subset(synthetic_dataset_full, indices)
        print(f"  采样比例: {synthetic_ratio:.2f} ({synthetic_size}/{len(synthetic_dataset_full)} 张)")
    else:
        synthetic_dataset = synthetic_dataset_full
    
    # 合并训练集
    print(f"\n合并训练集:")
    print(f"  - 原始训练集: {len(train_real_dataset)} 张（带传统增强）")
    print(f"  - 合成数据集: {len(synthetic_dataset)} 张（{'带传统增强' if augment_synthetic else '无增强'}）")
    
    train_dataset_combined = ConcatDataset([train_real_dataset, synthetic_dataset])
    print(f"  - 合并后训练集: {len(train_dataset_combined)} 张")
    
    # 创建验证集和测试集（不增强）
    val_dataset_final = TransformSubset(
        full_dataset,
        val_dataset.indices,
        transform=get_transforms(is_train=False)
    )
    
    test_dataset_final = TransformSubset(
        full_dataset,
        test_dataset.indices,
        transform=get_transforms(is_train=False)
    )
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset_combined,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset_final,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset_final,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    print(f"\n✅ 数据加载器创建完成")
    
    return train_loader, val_loader, test_loader


if __name__ == '__main__':
    # 测试数据加载
    print("=" * 70)
    print("测试数据加载器")
    print("=" * 70)
    
    # 假设数据目录
    real_data_dir = '/Users/koolei/Desktop/hust-bysj-new/data/raw/Dataset_BUSI_with_GT'
    synthetic_data_dir = '/Users/koolei/Desktop/hust-bysj-new/data/synthetic'
    
    # 检查目录是否存在
    if not Path(real_data_dir).exists():
        print(f"❌ 原始数据目录不存在: {real_data_dir}")
        sys.exit(1)
    
    if not Path(synthetic_data_dir).exists():
        print(f"⚠️  合成数据目录不存在，将只使用原始训练集")
        synthetic_data_dir = None
    
    # 测试加载
    if synthetic_data_dir:
        train_loader, val_loader, test_loader = get_dataloaders(
            real_data_dir=real_data_dir,
            synthetic_data_dir=synthetic_data_dir,
            batch_size=32,
            num_workers=0,
            augment_synthetic=True  # 测试对合成数据应用增强
        )
        
        # 测试加载一个批次
        images, labels = next(iter(train_loader))
        print(f"\n批次测试:")
        print(f"  - 图像 shape: {images.shape}")
        print(f"  - 标签 shape: {labels.shape}")
        
        print(f"\n✅ 测试完成")
    else:
        # 只加载原始数据
        full_dataset = BUSIDatasetWithIndices(real_data_dir)
        print(f"\n✅ 测试完成")
