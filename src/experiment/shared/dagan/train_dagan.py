#!/usr/bin/env python3
"""
训练 DAGAN 生成器

训练流程:
1. 加载BUSI数据集
2. 划分数据集（只使用训练集训练DAGAN，避免数据泄露）
3. 训练DAGAN生成器
4. 保存训练好的生成器

训练时间: 约 2-4 小时（GPU）或 8-12 小时（CPU）
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
from tqdm import tqdm

# 导入模型
from models import DAGANGenerator, DAGANDiscriminator, GANLoss


class BUSIDataset(Dataset):
    """BUSI数据集加载器（用于DAGAN训练）"""
    
    CLASS_NAMES = ['benign', 'malignant', 'normal']
    CLASS_TO_IDX = {'benign': 0, 'malignant': 1, 'normal': 2}
    
    def __init__(self, data_dir: str, transform=None):
        self.data_dir = Path(data_dir)
        self.transform = transform
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
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = Image.open(sample['image_path']).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, sample['label']


def get_transforms():
    """获取图像变换（DAGAN训练用）"""
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # [-1, 1]
    ])


def get_dataloaders(
    data_dir: str,
    batch_size: int = 16,
    num_workers: int = 4,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """获取数据加载器
    
    注意：只返回训练集用于DAGAN训练
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    
    # 加载完整数据集
    full_dataset = BUSIDataset(data_dir, transform=get_transforms())
    
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
    
    print(f"\n✓ 数据集划分完成 (种子={seed})")
    print(f"  - 训练集: {len(train_dataset)} 张 (用于DAGAN训练)")
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


def train_dagan(
    train_loader: DataLoader,
    num_epochs: int,
    device: torch.device,
    output_dir: Path,
    lr: float = 0.0002,
    beta1: float = 0.5,
    lambda_adv: float = 1.0,
    lambda_rec: float = 100.0,
    save_interval: int = 10
):
    """训练DAGAN
    
    Args:
        train_loader: 训练数据加载器
        num_epochs: 训练轮数
        device: 设备
        output_dir: 输出目录
        lr: 学习率
        beta1: Adam优化器beta1
        lambda_adv: 对抗损失权重
        lambda_rec: 重建损失权重
        save_interval: 保存间隔
    """
    print("\n" + "=" * 70)
    print("开始训练 DAGAN")
    print("=" * 70)
    
    # 创建模型
    generator = DAGANGenerator(in_channels=3, out_channels=3).to(device)
    discriminator = DAGANDiscriminator(in_channels=3).to(device)
    
    # 损失函数
    gan_loss = GANLoss()
    reconstruction_loss = nn.L1Loss()
    
    # 优化器
    g_optimizer = optim.Adam(generator.parameters(), lr=lr, betas=(beta1, 0.999))
    d_optimizer = optim.Adam(discriminator.parameters(), lr=lr, betas=(beta1, 0.999))
    
    # 学习率调度器
    g_scheduler = optim.lr_scheduler.StepLR(g_optimizer, step_size=50, gamma=0.5)
    d_scheduler = optim.lr_scheduler.StepLR(d_optimizer, step_size=50, gamma=0.5)
    
    # 训练历史
    history = {
        'g_loss': [], 'd_loss': [],
        'g_adv_loss': [], 'g_rec_loss': []
    }
    
    start_time = time.time()
    
    for epoch in range(1, num_epochs + 1):
        epoch_start = time.time()
        
        generator.train()
        discriminator.train()
        
        epoch_g_loss = 0.0
        epoch_d_loss = 0.0
        epoch_g_adv_loss = 0.0
        epoch_g_rec_loss = 0.0
        
        pbar = tqdm(train_loader, desc=f"Epoch [{epoch}/{num_epochs}]")
        
        for batch_idx, (real_images, _) in enumerate(pbar):
            real_images = real_images.to(device)
            batch_size = real_images.size(0)
            
            # ==================== 训练判别器 ====================
            d_optimizer.zero_grad()
            
            # 真实图像对
            real_output = discriminator(real_images, real_images)
            d_loss_real = gan_loss(real_output, True)
            
            # 生成图像对
            fake_images = generator(real_images)
            fake_output = discriminator(real_images, fake_images.detach())
            d_loss_fake = gan_loss(fake_output, False)
            
            # 判别器总损失
            d_loss = (d_loss_real + d_loss_fake) * 0.5
            d_loss.backward()
            d_optimizer.step()
            
            # ==================== 训练生成器 ====================
            g_optimizer.zero_grad()
            
            # 对抗损失
            fake_output = discriminator(real_images, fake_images)
            g_loss_adv = gan_loss(fake_output, True)
            
            # 重建损失
            g_loss_rec = reconstruction_loss(fake_images, real_images)
            
            # 生成器总损失
            g_loss = lambda_adv * g_loss_adv + lambda_rec * g_loss_rec
            g_loss.backward()
            g_optimizer.step()
            
            # 累计损失
            epoch_g_loss += g_loss.item()
            epoch_d_loss += d_loss.item()
            epoch_g_adv_loss += g_loss_adv.item()
            epoch_g_rec_loss += g_loss_rec.item()
            
            # 更新进度条
            pbar.set_postfix({
                'G_loss': f'{g_loss.item():.4f}',
                'D_loss': f'{d_loss.item():.4f}',
                'Rec': f'{g_loss_rec.item():.4f}'
            })
        
        # 更新学习率
        g_scheduler.step()
        d_scheduler.step()
        
        # 计算平均损失
        num_batches = len(train_loader)
        avg_g_loss = epoch_g_loss / num_batches
        avg_d_loss = epoch_d_loss / num_batches
        avg_g_adv_loss = epoch_g_adv_loss / num_batches
        avg_g_rec_loss = epoch_g_rec_loss / num_batches
        
        # 记录历史
        history['g_loss'].append(avg_g_loss)
        history['d_loss'].append(avg_d_loss)
        history['g_adv_loss'].append(avg_g_adv_loss)
        history['g_rec_loss'].append(avg_g_rec_loss)
        
        # 打印epoch信息
        epoch_time = time.time() - epoch_start
        total_time = time.time() - start_time
        print(f"Epoch [{epoch:3d}/{num_epochs}] "
              f"G_loss: {avg_g_loss:.4f} (Adv: {avg_g_adv_loss:.4f}, Rec: {avg_g_rec_loss:.4f}) | "
              f"D_loss: {avg_d_loss:.4f} | "
              f"Time: {epoch_time:.1f}s (Total: {total_time/60:.1f}min)")
        
        # 定期保存
        if epoch % save_interval == 0:
            checkpoint = {
                'epoch': epoch,
                'generator_state_dict': generator.state_dict(),
                'discriminator_state_dict': discriminator.state_dict(),
                'g_optimizer_state_dict': g_optimizer.state_dict(),
                'd_optimizer_state_dict': d_optimizer.state_dict(),
                'g_loss': avg_g_loss,
                'd_loss': avg_d_loss,
                'history': history
            }
            save_path = output_dir / f'dagan_epoch_{epoch}.pth'
            torch.save(checkpoint, save_path)
            print(f"  ✅ 保存检查点: {save_path}")
    
    # 保存最终模型
    final_checkpoint = {
        'epoch': num_epochs,
        'generator_state_dict': generator.state_dict(),
        'discriminator_state_dict': discriminator.state_dict(),
        'g_optimizer_state_dict': g_optimizer.state_dict(),
        'd_optimizer_state_dict': d_optimizer.state_dict(),
        'g_loss': avg_g_loss,
        'd_loss': avg_d_loss,
        'history': history
    }
    save_path = output_dir / 'dagan_generator.pth'
    torch.save(final_checkpoint, save_path)
    print(f"\n✅ 最终模型已保存: {save_path}")
    
    # 保存训练历史
    history_path = output_dir / 'training_history.json'
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"✅ 训练历史已保存: {history_path}")
    
    total_time = time.time() - start_time
    print(f"\n训练完成！总耗时: {total_time/60:.1f} 分钟")
    
    return generator, history


def main():
    parser = argparse.ArgumentParser(description='训练DAGAN生成器')
    parser.add_argument('--data_dir', type=str, 
                       default='/Users/koolei/Desktop/hust-bysj/code/data/BUSI',
                       help='BUSI数据集路径')
    parser.add_argument('--output_dir', type=str, 
                       default='outputs/dagan',
                       help='输出目录')
    parser.add_argument('--epochs', type=int, default=100,
                       help='训练轮数 (默认: 100)')
    parser.add_argument('--batch_size', type=int, default=16,
                       help='批次大小 (默认: 16)')
    parser.add_argument('--lr', type=float, default=0.0002,
                       help='学习率 (默认: 0.0002)')
    parser.add_argument('--device', type=str, default='auto',
                       help='设备 (auto/cpu/cuda/mps)')
    parser.add_argument('--num_workers', type=int, default=0,
                       help='数据加载线程数 (默认: 0)')
    parser.add_argument('--save_interval', type=int, default=10,
                       help='保存间隔 (默认: 10)')
    
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
    print("DAGAN 训练配置")
    print('='*70)
    print(f"数据目录: {args.data_dir}")
    print(f"输出目录: {args.output_dir}")
    print(f"设备: {device}")
    print(f"训练轮数: {args.epochs}")
    print(f"批次大小: {args.batch_size}")
    print(f"学习率: {args.lr}")
    print(f"保存间隔: {args.save_interval}")
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取数据加载器
    train_loader, val_loader, test_loader = get_dataloaders(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers
    )
    
    # 训练DAGAN
    generator, history = train_dagan(
        train_loader=train_loader,
        num_epochs=args.epochs,
        device=device,
        output_dir=output_dir,
        lr=args.lr,
        save_interval=args.save_interval
    )
    
    print("\n" + "=" * 70)
    print("✅ DAGAN训练完成！")
    print("=" * 70)
    print(f"\n下一步：运行 generate.py 生成合成图像")
    print(f"命令：python generate.py --generator_path {output_dir}/dagan_generator.pth")


if __name__ == '__main__':
    main()
