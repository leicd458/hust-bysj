"""
分割模型训练脚本
适合深度学习零基础的同学：这个脚本训练U-Net模型，学会标记出肿瘤区域
"""
import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from tqdm import tqdm
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config import config
from dataset import load_busi_dataset, get_transforms
from models.unet_segmentor import UNet
from utils.metrics import dice_coefficient
from utils.visualization import plot_training_history, plot_segmentation_results

class DiceLoss(nn.Module):
    """
    Dice损失函数
    
    什么是Dice损失？
    - 专门用于分割任务的损失函数
    - 衡量预测区域和真实区域的重叠度
    - Dice系数越大越好，Dice损失 = 1 - Dice系数
    """
    
    def __init__(self):
        super(DiceLoss, self).__init__()
    
    def forward(self, pred, target):
        """
        计算Dice损失
        
        参数：
            pred: 预测掩码，形状 [B, 1, H, W]
            target: 真实掩码，形状 [B, 1, H, W]
        """
        smooth = 1e-5  # 平滑项，避免除零
        
        pred = torch.sigmoid(pred)  # 转换为概率
        
        # 展平
        pred_flat = pred.view(-1)
        target_flat = target.view(-1)
        
        # 计算交集和并集
        intersection = (pred_flat * target_flat).sum()
        union = pred_flat.sum() + target_flat.sum()
        
        # Dice系数
        dice = (2. * intersection + smooth) / (union + smooth)
        
        # Dice损失
        return 1 - dice


class SegmentorTrainer:
    """分割器训练类"""
    
    def __init__(self, config):
        """初始化训练器"""
        self.config = config
        self.device = config.device
        
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        os.makedirs(config.results_dir, exist_ok=True)
        
        print(f"使用设备: {self.device}")
        
        self.history = {
            'train_loss': [],
            'train_dice': [],
            'val_loss': [],
            'val_dice': []
        }
        
        self.best_val_dice = 0.0
        self.patience_counter = 0
    
    def prepare_data(self):
        """准备数据集"""
        print("
" + "=" * 60)
        print("准备数据集...")
        print("=" * 60)
        
        train_transform = get_transforms(self.config.image_size, augmentation=True)
        val_transform = get_transforms(self.config.image_size, augmentation=False)
        
        train_dataset, val_dataset, test_dataset = load_busi_dataset(
            data_root=self.config.data_root,
            train_transform=train_transform,
            val_transform=val_transform,
            test_transform=val_transform,
            mode='segmentation'
        )
        
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.seg_batch_size,
            shuffle=True,
            num_workers=self.config.num_workers
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.seg_batch_size,
            shuffle=False,
            num_workers=self.config.num_workers
        )
        
        self.test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.seg_batch_size,
            shuffle=False,
            num_workers=self.config.num_workers
        )
        
        print(f"训练集大小: {len(train_dataset)}")
        print(f"验证集大小: {len(val_dataset)}")
        print(f"测试集大小: {len(test_dataset)}")
    
    def build_model(self):
        """构建模型"""
        print("
" + "=" * 60)
        print("构建模型...")
        print("=" * 60)
        
        self.model = UNet(
            in_channels=3,
            out_channels=1,
            features=self.config.unet_features
        ).to(self.device)
        
        self.criterion = DiceLoss()
        
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config.seg_learning_rate
        )
        
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='max',
            factor=0.5,
            patience=5,
            verbose=True
        )
        
        print(f"模型已创建并移至 {self.device}")
    
    def train_epoch(self, epoch):
        """训练一个epoch"""
        self.model.train()
        
        running_loss = 0.0
        running_dice = 0.0
        
        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch+1}/{self.config.seg_num_epochs} [Train]')
        
        for batch_idx, (images, masks, _) in enumerate(pbar):
            images = images.to(self.device)
            masks = masks.to(self.device)
            
            # 前向传播
            outputs = self.model(images)
            loss = self.criterion(outputs, masks)
            
            # 反向传播
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            # 计算Dice系数
            with torch.no_grad():
                pred_masks = torch.sigmoid(outputs) > 0.5
                dice = dice_coefficient(pred_masks, masks)
            
            running_loss += loss.item()
            running_dice += dice
            
            pbar.set_postfix({
                'loss': f'{running_loss/(batch_idx+1):.4f}',
                'dice': f'{running_dice/(batch_idx+1):.4f}'
            })
        
        epoch_loss = running_loss / len(self.train_loader)
        epoch_dice = running_dice / len(self.train_loader)
        
        return epoch_loss, epoch_dice
    
    def validate_epoch(self, epoch):
        """验证一个epoch"""
        self.model.eval()
        
        running_loss = 0.0
        running_dice = 0.0
        
        pbar = tqdm(self.val_loader, desc=f'Epoch {epoch+1}/{self.config.seg_num_epochs} [Val]')
        
        with torch.no_grad():
            for batch_idx, (images, masks, _) in enumerate(pbar):
                images = images.to(self.device)
                masks = masks.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, masks)
                
                pred_masks = torch.sigmoid(outputs) > 0.5
                dice = dice_coefficient(pred_masks, masks)
                
                running_loss += loss.item()
                running_dice += dice
                
                pbar.set_postfix({
                    'loss': f'{running_loss/(batch_idx+1):.4f}',
                    'dice': f'{running_dice/(batch_idx+1):.4f}'
                })
        
        epoch_loss = running_loss / len(self.val_loader)
        epoch_dice = running_dice / len(self.val_loader)
        
        return epoch_loss, epoch_dice
    
    def train(self):
        """完整训练流程"""
        print("
" + "=" * 60)
        print("开始训练...")
        print("=" * 60)
        
        for epoch in range(self.config.seg_num_epochs):
            train_loss, train_dice = self.train_epoch(epoch)
            val_loss, val_dice = self.validate_epoch(epoch)
            
            self.scheduler.step(val_dice)
            
            self.history['train_loss'].append(train_loss)
            self.history['train_dice'].append(train_dice)
            self.history['val_loss'].append(val_loss)
            self.history['val_dice'].append(val_dice)
            
            print(f"
Epoch {epoch+1}/{self.config.seg_num_epochs} 总结:")
            print(f"  训练损失: {train_loss:.4f}, 训练Dice: {train_dice:.4f}")
            print(f"  验证损失: {val_loss:.4f}, 验证Dice: {val_dice:.4f}")
            
            if val_dice > self.best_val_dice:
                self.best_val_dice = val_dice
                self.patience_counter = 0
                
                checkpoint_path = os.path.join(
                    self.config.checkpoint_dir,
                    'best_segmentor.pth'
                )
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_dice': val_dice
                }, checkpoint_path)
                
                print(f"  ✓ 保存最佳模型 (验证Dice: {val_dice:.4f})")
            else:
                self.patience_counter += 1
                print(f"  验证Dice未提升 ({self.patience_counter}/{self.config.patience})")
            
            if self.patience_counter >= self.config.patience:
                print(f"
早停触发！")
                break
        
        print("
训练完成！")


def main():
    """主函数"""
    print("=" * 80)
    print("乳腺癌超声图像分割模型训练")
    print("=" * 80)
    
    torch.manual_seed(config.random_seed)
    np.random.seed(config.random_seed)
    
    trainer = SegmentorTrainer(config)
    trainer.prepare_data()
    trainer.build_model()
    trainer.train()
    
    print("
训练流程完成！")


if __name__ == "__main__":
    main()
