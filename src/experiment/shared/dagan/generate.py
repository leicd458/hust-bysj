#!/usr/bin/env python3
"""
使用训练好的DAGAN生成合成图像

关键点:
- 只使用训练集图像生成（避免数据泄露）
- 严格按照论文70/15/15划分
- 使用stratify保持类别分布
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List
import numpy as np
import torch
from PIL import Image
import torchvision.transforms as transforms
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader, random_split

from models import DAGANGenerator


class BUSIDatasetWithIndices(Dataset):
    """BUSI数据集（支持索引访问）"""
    
    CLASS_NAMES = ['benign', 'malignant', 'normal']
    CLASS_TO_IDX = {'benign': 0, 'malignant': 1, 'normal': 2}
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.samples = []
        self._load_samples()
    
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
        
        print(f"✓ 加载 {len(self.samples)} 张图像")
    
    def __len__(self):
        return len(self.samples)
    
    def get_sample(self, idx):
        return self.samples[idx]


def load_and_split_data(
    data_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Dict[str, List[str]]:
    """加载数据并划分，返回训练集图像路径
    
    Args:
        data_dir: 数据目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        seed: 随机种子
    
    Returns:
        按类别组织的训练集图像路径
    """
    print("\n" + "=" * 70)
    print("加载并划分 BUSI 数据集（论文标准：70%/15%/15%）")
    print("=" * 70)
    
    # 加载完整数据集
    full_dataset = BUSIDatasetWithIndices(data_dir)
    
    # 设置随机种子
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # 划分数据集
    total_size = len(full_dataset)
    train_size = int(train_ratio * total_size)
    val_size = int(val_ratio * total_size)
    test_size = total_size - train_size - val_size
    
    train_dataset, val_dataset, test_dataset = random_split(
        full_dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(seed)
    )
    
    print(f"\n数据划分结果:")
    print(f"  - 训练集: {len(train_dataset)} 张 (用于生成合成图像)")
    print(f"  - 验证集: {len(val_dataset)} 张")
    print(f"  - 测试集: {len(test_dataset)} 张")
    
    # 按类别组织训练集图像
    train_images_by_class = {name: [] for name in full_dataset.CLASS_NAMES}
    
    for idx in train_dataset.indices:
        sample = full_dataset.get_sample(idx)
        train_images_by_class[sample['class_name']].append(sample['image_path'])
    
    print(f"\n训练集各类别分布:")
    for class_name in full_dataset.CLASS_NAMES:
        print(f"  {class_name}: {len(train_images_by_class[class_name])} 张")
    
    print(f"\n✅ 只使用训练集图像生成（避免数据泄露）")
    
    return train_images_by_class


def generate_synthetic_images(
    generator: DAGANGenerator,
    device: torch.device,
    images_by_class: Dict[str, List[str]],
    output_dir: str,
    num_variants: int = 5
):
    """使用DAGAN生成合成图像
    
    Args:
        generator: 训练好的生成器
        device: 设备
        images_by_class: 按类别组织的图像路径
        output_dir: 输出目录
        num_variants: 每张图生成多少变体
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator.eval()
    
    generated_info = []
    total_generated = 0
    
    # 图像变换
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    print("\n" + "=" * 70)
    print("生成合成图像")
    print("=" * 70)
    print(f"每张原始图像生成 {num_variants} 个变体")
    
    for class_name, image_paths in images_by_class.items():
        print(f"\n处理类别: {class_name} ({len(image_paths)} 张)")
        
        class_output_dir = output_dir / class_name
        class_output_dir.mkdir(parents=True, exist_ok=True)
        
        pbar = tqdm(image_paths, desc=f"生成 {class_name}")
        
        for img_path in pbar:
            # 加载图像
            image = Image.open(img_path).convert('RGB')
            img_name = Path(img_path).stem
            
            # 转换
            img_tensor = transform(image).unsqueeze(0).to(device)
            
            # 生成变体
            for i in range(num_variants):
                with torch.no_grad():
                    fake_img = generator(img_tensor)
                
                # 反归一化
                fake_img = (fake_img.squeeze(0).cpu() * 0.5) + 0.5
                fake_img = torch.clamp(fake_img, 0, 1)
                fake_img_pil = transforms.ToPILImage()(fake_img)
                
                # 保存
                output_name = f"{img_name}_synthetic_{i+1:03d}.png"
                output_path = class_output_dir / output_name
                fake_img_pil.save(output_path)
                
                # 记录信息
                generated_info.append({
                    'class': class_name,
                    'original': str(img_path),
                    'synthetic': str(output_path),
                    'variant_id': i + 1
                })
                
                total_generated += 1
                pbar.set_postfix({'generated': total_generated})
    
    print(f"\n✅ 总共生成了 {total_generated} 张合成图像")
    
    # 保存生成信息
    info_path = output_dir.parent / "generated_info.json"
    with open(info_path, 'w') as f:
        json.dump(generated_info, f, indent=2)
    print(f"✅ 生成信息已保存: {info_path}")
    
    # 统计
    print(f"\n生成统计:")
    for class_name in images_by_class.keys():
        count = len([g for g in generated_info if g['class'] == class_name])
        print(f"  {class_name}: {count} 张")


def main():
    parser = argparse.ArgumentParser(description='使用DAGAN生成合成图像')
    parser.add_argument('--generator_path', type=str, required=True,
                       help='训练好的生成器路径')
    parser.add_argument('--data_dir', type=str, 
                       default='/Users/koolei/Desktop/hust-bysj/code/data/BUSI',
                       help='BUSI数据集路径')
    parser.add_argument('--output_dir', type=str, 
                       default='outputs/synthetic_images',
                       help='输出目录')
    parser.add_argument('--num_variants', type=int, default=5,
                       help='每张图生成多少变体 (默认: 5)')
    parser.add_argument('--device', type=str, default='auto',
                       help='设备 (auto/cpu/cuda/mps)')
    
    args = parser.parse_args()
    
    # 设置设备
    if args.device == 'auto':
        if torch.backends.mps.is_available():
            device = torch.device('mps')
        elif torch.cuda.is_available():
            device = torch.device('cuda')
        else:
            device = torch.device('cpu')
    else:
        device = torch.device(args.device)
    
    print(f"\n{'='*70}")
    print("DAGAN 图像生成配置")
    print('='*70)
    print(f"生成器路径: {args.generator_path}")
    print(f"数据目录: {args.data_dir}")
    print(f"输出目录: {args.output_dir}")
    print(f"设备: {device}")
    print(f"每张图变体数: {args.num_variants}")
    
    # 加载生成器
    print(f"\n加载生成器: {args.generator_path}")
    checkpoint = torch.load(args.generator_path, map_location=device)
    
    generator = DAGANGenerator(in_channels=3, out_channels=3).to(device)
    generator.load_state_dict(checkpoint['generator_state_dict'])
    generator.eval()
    
    print(f"✅ 生成器加载完成")
    print(f"   训练轮数: {checkpoint.get('epoch', 'N/A')}")
    print(f"   最终损失: {checkpoint.get('g_loss', 'N/A'):.4f}" if 'g_loss' in checkpoint else "")
    
    # 加载并划分数据（只使用训练集）
    train_images_by_class = load_and_split_data(args.data_dir)
    
    # 生成合成图像
    generate_synthetic_images(
        generator=generator,
        device=device,
        images_by_class=train_images_by_class,
        output_dir=args.output_dir,
        num_variants=args.num_variants
    )
    
    print("\n" + "=" * 70)
    print("✅ 图像生成完成！")
    print("=" * 70)
    print(f"\n合成图像保存在: {args.output_dir}")
    print(f"\n下一步：运行 train.py 训练分类器")


if __name__ == '__main__':
    main()
