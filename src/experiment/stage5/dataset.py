#!/usr/bin/env python3
"""
阶段5数据集: 按论文标准重构

关键改进 (基于论文实证):
1. StratifiedKFold 分层划分 (保证 train/val/test 类别比例一致)
2. Class-Balanced Sampler (每个 batch 内三类等量采样)
3. 轻量数据增强: 旋转±10° + 翻转 + zoom≤10% (与 arXiv 2025 一致)
4. Test-Time Augmentation (TTA) 推理增强

参考论文:
- Latha et al. 2024: EfficientNet-B7 on BUSI, stratified split, Adam lr=1e-4
- arXiv 2025: Interpretable Deep TL, stratified 80/10/10, rotation±10°+flip+zoom
"""

import sys
from pathlib import Path
from typing import Tuple, Optional, List
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, ConcatDataset, WeightedRandomSampler
from sklearn.model_selection import StratifiedKFold
from torchvision import transforms
from PIL import Image


# ==================== 常量 ====================

CLASS_NAMES = ['benign', 'malignant', 'normal']
CLASS_TO_IDX = {'benign': 0, 'malignant': 1, 'normal': 2}
IMAGE_SIZE = 300  # EfficientNet-B0 输入分辨率


# ==================== 数据集类 ====================

class BUSIDataset(Dataset):
    """BUSI 数据集"""

    def __init__(self, data_dir: str, transform=None):
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.samples = []
        self._load_samples()

    def _load_samples(self):
        for class_name in CLASS_NAMES:
            class_dir = self.data_dir / class_name
            if not class_dir.exists():
                continue
            for img_path in class_dir.glob("*.png"):
                if "_mask" in img_path.name:
                    continue
                self.samples.append({
                    'image_path': str(img_path),
                    'label': CLASS_TO_IDX[class_name],
                })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = Image.open(sample['image_path']).convert('RGB')
        label = sample['label']
        if self.transform:
            image = self.transform(image)
        return image, label

    def get_labels(self):
        return [s['label'] for s in self.samples]


class IndexedDataset(Dataset):
    """带索引的数据集子集 (用于 StratifiedKFold 划分)"""

    def __init__(self, dataset: Dataset, indices: list, transform=None):
        self.dataset = dataset
        self.indices = indices
        self.transform = transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        real_idx = self.indices[idx]
        # 获取原始样本路径和标签，重新应用 transform
        sample = self.dataset.samples[real_idx]
        image = Image.open(sample['image_path']).convert('RGB')
        label = sample['label']
        if self.transform:
            image = self.transform(image)
        return image, label


# ==================== 图像变换 (按论文标准) ====================

def get_train_transforms() -> transforms.Compose:
    """
    训练时增强 - 与 arXiv 2025 论文一致:
    RandomRotation(10°) + HorizontalFlip + Affine(zoom<=10%, translate<=5%)
    
    不使用 ColorJitter (医学超声图像颜色变化不是真实的变化模式)
    不使用 VerticalFlip (超声探头方向固定)
    不使用过度旋转 (>15° 会破坏病灶结构)
    """
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),           # 论文: ±10°
        transforms.RandomAffine(
            degrees=0,
            translate=(0.05, 0.05),              # ±5% 平移
            scale=(0.90, 1.10)                   # ±10% 缩放 (论文: zoom ≤ 10%)
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def get_val_transforms() -> transforms.Compose:
    """验证/测试时变换 - 无增强"""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def get_tta_transforms() -> List[transforms.Compose]:
    """
    Test-Time Augmentation
    
    对同一张图像做多次不同变换后预测取平均.
    策略: 原图 + 水平翻转 + 小角度旋转(±5°) + 组合
    """
    base_norm = [
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ]

    tta_list = [
        # 1. 原图
        transforms.Compose([transforms.Resize((IMAGE_SIZE, IMAGE_SIZE))] + base_norm),
        # 2. 水平翻转
        transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomHorizontalFlip(p=1.0),
        ] + base_norm),
        # 3. 顺时针旋转5°
        transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomRotation(degrees=(-5, -5)),  # 固定 -5°
        ] + base_norm),
        # 4. 逆时针旋转5°
        transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomRotation(degrees=(5, 5)),     # 固定 +5°
        ] + base_norm),
    ]
    return tta_list


# ==================== TTA 推理 ====================

@torch.no_grad()
def tta_predict(model, image, tta_transforms, device):
    """对单张图像执行 TTA 预测"""
    model.eval()
    probs_list = []

    for tfm in tta_transforms:
        img_tensor = tfm(image).unsqueeze(0).to(device)
        output = model(img_tensor)
        probs = torch.softmax(output, dim=1)
        probs_list.append(probs)

    avg_probs = torch.stack(probs_list).mean(dim=0).squeeze(0)
    return avg_probs


def tta_predict_batch(model, images, tta_transforms, device, original_loader):
    """
    对整个测试集执行 TTA 推理
    
    Args:
        model: 训练好的模型
        images: 归一化后的 tensor batch [B, C, H, W]
        tta_transforms: TTA 变换列表
        device: 设备
        original_loader: 原始 dataloader (用于获取原始 PIL 图片)
    Returns:
        all_preds: 预测标签数组
        all_labels: 真实标签数组
    """
    model.eval()
    all_preds = []
    all_labels = []

    # 从原始 loader 获取 PIL 图像
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

    for batch_images, batch_labels in original_loader:
        batch_labels_np = batch_labels.numpy()
        batch_preds = []

        for i in range(batch_images.size(0)):
            img_tensor = batch_images[i].cpu()
            # 反归一化
            img_np = (img_tensor * std + mean).clamp(0, 1).numpy()
            img_np = np.transpose(img_np, (1, 2, 0))
            pil_img = Image.fromarray((img_np * 255).astype(np.uint8))

            avg_probs = tta_predict(model, pil_img, tta_transforms, device)
            pred = avg_probs.argmax(dim=0).item()
            batch_preds.append(pred)

        all_preds.extend(batch_preds)
        all_labels.extend(batch_labels_np.tolist())

    return np.array(all_preds), np.array(all_labels)


# ==================== 核心函数: 分层划分 + 均衡采样 ====================

def get_dataloaders(
    data_dir: str,
    synthetic_data_dir: Optional[str] = None,
    batch_size: int = 16,
    num_workers: int = 0,
    train_ratio: float = 0.80,
    val_ratio: float = 0.10,
    test_ratio: float = 0.10,
    seed: int = 42,
    synthetic_ratio: float = 1.0,
    use_balanced_sampler: bool = True,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    获取数据加载器
    
    核心改进:
    1. StratifiedKFold 分层划分 (保证每类的 train/val/test 比例一致)
    2. WeightedRandomSampler 或 Class-Balanced Sampling (解决类别不平衡)
    3. 合成数据只加入训练集
    
    Args:
        use_balanced_sampler: 是否使用均衡采样 (默认 True)
            True  -> 使用 WeightedRandomSampler (过采样少数类)
            False -> 普通 random shuffle
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6

    print("\n" + "=" * 60)
    print(f"阶段5: 数据加载 (输入尺寸={IMAGE_SIZE})")
    print("=" * 60)

    # ========== 加载原始数据 ==========
    full_dataset = BUSIDataset(data_dir)
    labels = np.array(full_dataset.get_labels())
    n_total = len(full_dataset)

    # 打印原始数据分布
    print(f"\n原始数据集 ({n_total} 张):")
    for cls_idx, cls_name in enumerate(CLASS_NAMES):
        cnt = (labels == cls_idx).sum()
        print(f"  {cls_name}: {cnt} 张 ({100*cnt/n_total:.1f}%)")

    # ========== StratifiedKFold 划分 ==========
    # 策略: 先用 StratifiedKFold 分出 test (test_ratio), 剩余再 stratified split 出 val
    # 这样可以处理任意的 train/val/test 比例
    
    # Step 1: 从全部数据中分层抽样出测试集
    n_test = int(round(n_total * test_ratio))
    if n_test == 0:
        n_test = 1  # 至少1张测试图
    # 用 StratifiedShuffleSplit 来获取指定大小的测试集
    from sklearn.model_selection import StratifiedShuffleSplit
    sss_test = StratifiedShuffleSplit(n_splits=1, test_size=n_test/n_total, random_state=seed)
    train_val_idx, test_idx = next(sss_test.split(np.arange(n_total), labels))
    
    # Step 2: 从剩余数据中分层抽出验证集
    n_train_val = len(train_val_idx)
    n_val = int(round(n_train_val * val_ratio / (train_ratio + val_ratio)))
    if n_val == 0:
        n_val = 1
    train_val_sub_labels = labels[train_val_idx]
    
    sss_val = StratifiedShuffleSplit(n_splits=1, test_size=n_val/n_train_val, random_state=seed+1)
    train_idx_arr, val_idx_arr = next(sss_val.split(train_val_idx, train_val_sub_labels))

    # 最终索引
    train_idx = train_val_idx[train_idx_arr].tolist()
    val_idx = train_val_idx[val_idx_arr].tolist()
    test_idx = test_idx.tolist()

    # 打印划分后的分布
    print(f"\nStratified 划分 (seed={seed}):")
    print(f"  训练集: {len(train_idx)} 张")
    for cls_idx, cls_name in enumerate(CLASS_NAMES):
        cnt = sum(1 for i in train_idx if labels[i] == cls_idx)
        print(f"    {cls_name}: {cnt}")
    print(f"  验证集: {len(val_idx)} 张")
    for cls_idx, cls_name in enumerate(CLASS_NAMES):
        cnt = sum(1 for i in val_idx if labels[i] == cls_idx)
        print(f"    {cls_name}: {cnt}")
    print(f"  测试集: {len(test_idx)} 张")
    for cls_idx, cls_name in enumerate(CLASS_NAMES):
        cnt = sum(1 for i in test_idx if labels[i] == cls_idx)
        print(f"    {cls_name}: {cnt}")

    # ========== 创建带变换的数据集 ==========
    train_real = IndexedDataset(full_dataset, train_idx, transform=get_train_transforms())
    val_ds = IndexedDataset(full_dataset, val_idx, transform=get_val_transforms())
    test_ds = IndexedDataset(full_dataset, test_idx, transform=get_val_transforms())

    # ========== 加载合成数据 (仅加入训练集) ==========
    if synthetic_data_dir and Path(synthetic_data_dir).exists():
        syn_dataset = BUSIDataset(synthetic_data_dir, transform=get_train_transforms())
        
        # 可选: 采样部分合成数据
        if synthetic_ratio < 1.0:
            syn_size = int(len(syn_dataset) * synthetic_ratio)
            rng = np.random.RandomState(seed)
            syn_idx = rng.choice(len(syn_dataset), size=syn_size, replace=False).tolist()
            from torch.utils.data import Subset
            syn_dataset = Subset(syn_dataset, syn_idx)
        
        train_combined = ConcatDataset([train_real, syn_dataset])
        
        # 打印合成数据分布
        print(f"\n合成数据 ({len(syn_dataset)} 张):")
        syn_labels = syn_dataset.dataset.get_labels() if hasattr(syn_dataset, 'dataset') else []
        if hasattr(syn_dataset, 'dataset'):
            for cls_idx, cls_name in enumerate(CLASS_NAMES):
                cnt = sum(1 for l in syn_labels[:len(syn_dataset)] if l == cls_idx)
                print(f"  {cls_name}: {cnt} 张")
    else:
        train_combined = train_real
        syn_dataset = None
        print(f"\n合成数据: 无")

    print(f"\n总训练样本: {len(train_combined)} 张 (原始{len(train_real)} + 合成{len(syn_dataset) if syn_dataset else 0})")

    # ========== 创建 DataLoader ==========
    if use_balanced_sampler and len(train_combined) > 0:
        # 构建权重: 少数类权重更高
        if isinstance(train_combined, ConcatDataset):
            # 合并所有标签
            all_labels = []
            for sub_ds in train_combined.datasets:
                if hasattr(sub_ds, 'get_labels'):
                    all_labels.extend(sub_ds.get_labels())
                elif hasattr(sub_ds, 'dataset'):
                    # Subset
                    all_labels.extend([sub_ds.dataset.samples[sub_ds.indices[i]]['label'] 
                                       for i in range(len(sub_ds))])
                else:
                    # IndexedDataset
                    for i in range(len(sub_ds)):
                        real_idx = sub_ds.indices[i]
                        all_labels.append(sub_ds.dataset.samples[real_idx]['label'])
        else:
            all_labels = [train_combined.dataset.samples[train_combined.indices[i]]['label'] 
                         for i in range(len(train_combined))]

        class_counts = np.bincount(all_labels, minlength=3)
        # 权重 = 1 / 类别频率
        weights = 1.0 / class_counts[all_labels]
        sampler = WeightedRandomSampler(
            weights=weights,
            num_samples=len(train_combined),
            replacement=True
        )
        print(f"使用 Balanced Sampler (权重: benign={1/class_counts[0]:.4f}, "
              f"malignant={1/class_counts[1]:.4f}, normal={1/class_counts[2]:.4f})")
        
        train_loader = DataLoader(
            train_combined, batch_size=batch_size, sampler=sampler,
            num_workers=num_workers, pin_memory=True, drop_last=True
        )
    else:
        train_loader = DataLoader(
            train_combined, batch_size=batch_size, shuffle=True,
            num_workers=num_workers, pin_memory=True, drop_last=True
        )

    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                           num_workers=num_workers, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False,
                            num_workers=num_workers, pin_memory=True)

    print(f"\nDataLoaders 创建完成 (batch_size={batch_size})")
    return train_loader, val_loader, test_loader


if __name__ == '__main__':
    data_dir = '/Users/koolei/Desktop/hust-bysj-new/data/raw/Dataset_BUSI_with_GT'
    synthetic_dir = '/Users/koolei/Desktop/hust-bysj-new/data/synthetic'

    if Path(data_dir).exists():
        tl, vl, tesl = get_dataloaders(
            data_dir=data_dir,
            synthetic_data_dir=synthetic_dir,
            batch_size=8, num_workers=0,
            use_balanced_sampler=True
        )
        imgs, labels = next(iter(tl))
        print(f"\n批次测试:")
        print(f"  shape: {imgs.shape}")
        print(f"  labels: {labels.tolist()}")
        
        # 验证采样是否均衡
        all_labels = []
        for _, lbl in tl:
            all_labels.extend(lbl.tolist())
        from collections import Counter
        c = Counter(all_labels)
        total = len(all_labels)
        print(f"\n一个 epoch 中各类采样数:")
        for cls_idx, cls_name in enumerate(CLASS_NAMES):
            print(f"  {cls_name}: {c.get(cls_idx, 0)} ({100*c.get(cls_idx,0)/total:.1f}%)")
    else:
        print(f"数据目录不存在: {data_dir}")
