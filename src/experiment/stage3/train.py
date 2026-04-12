#!/usr/bin/env python3
"""
阶段3：使用DAGAN合成图像训练ResNet-18分类器

训练流程:
1. 加载原始训练集 + DAGAN合成图像（来自shared/dagan）
2. 训练ResNet-18分类器
3. 在验证集和测试集上评估
4. 目标准确率: 85% (论文DAGAN)

关键改进:
- 严格按照论文70/15/15划分
- 只使用训练集生成合成图像（避免数据泄露）
- 合成图像+传统数据增强
- DAGAN生成器来自 shared/dagan（一次训练，多次使用）
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from torchvision.models import ResNet18_Weights
from tqdm import tqdm

from dataset import get_dataloaders


class ResNet18Classifier(nn.Module):
    """ResNet-18分类器"""
    
    def __init__(self, num_classes=3, pretrained=True, dropout=0.5):
        super(ResNet18Classifier, self).__init__()
        
        # 加载预训练模型
        if pretrained:
            self.backbone = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        else:
            self.backbone = models.resnet18(weights=None)
        
        # 修改最后的全连接层
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


def train_epoch(
    model: nn.Module,
    train_loader,
    criterion,
    optimizer,
    device,
    epoch: int
):
    """训练一个epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(train_loader, desc=f"Epoch [{epoch}] Training")
    
    for batch_idx, (images, labels) in enumerate(pbar):
        images = images.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'acc': f'{100.*correct/total:.2f}%'
        })
    
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100. * correct / total
    
    return epoch_loss, epoch_acc


def validate(
    model: nn.Module,
    val_loader,
    criterion,
    device
):
    """验证"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        pbar = tqdm(val_loader, desc="Validating")
        for images, labels in pbar:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
    
    epoch_loss = running_loss / len(val_loader)
    epoch_acc = 100. * correct / total
    
    return epoch_loss, epoch_acc, all_preds, all_labels


def test(
    model: nn.Module,
    test_loader,
    criterion,
    device
):
    """测试"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        pbar = tqdm(test_loader, desc="Testing")
        for images, labels in pbar:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
    
    accuracy = 100. * correct / total
    
    # 计算各类别准确率
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    class_names = ['benign', 'malignant', 'normal']
    class_accuracies = {}
    
    for class_idx, class_name in enumerate(class_names):
        mask = all_labels == class_idx
        if mask.sum() > 0:
            class_acc = (all_preds[mask] == all_labels[mask]).mean() * 100
            class_accuracies[class_name] = {
                'accuracy': float(class_acc),
                'correct': int((all_preds[mask] == all_labels[mask]).sum()),
                'total': int(mask.sum())
            }
    
    return running_loss / len(test_loader), accuracy, class_accuracies


def main():
    parser = argparse.ArgumentParser(description='阶段3: 使用DAGAN合成图像训练分类器')
    parser.add_argument('--real_data_dir', type=str, 
                       default='/Users/koolei/Desktop/hust-bysj/code/data/BUSI',
                       help='原始BUSI数据集路径')
    parser.add_argument('--synthetic_data_dir', type=str, 
                       default='outputs/synthetic_images',
                       help='DAGAN合成图像路径')
    parser.add_argument('--output_dir', type=str, 
                       default='outputs/stage3',
                       help='输出目录')
    parser.add_argument('--pretrained', action='store_true', default=True,
                       help='使用预训练权重')
    parser.add_argument('--epochs', type=int, default=50,
                       help='最大训练轮数')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='批次大小')
    parser.add_argument('--lr', type=float, default=0.0001,
                       help='学习率')
    parser.add_argument('--patience', type=int, default=10,
                       help='早停耐心值')
    parser.add_argument('--target_acc', type=float, default=85.0,
                       help='目标准确率')
    parser.add_argument('--device', type=str, default='auto',
                       help='设备 (auto/cpu/cuda/mps)')
    parser.add_argument('--num_workers', type=int, default=0,
                       help='数据加载线程数')
    parser.add_argument('--synthetic_ratio', type=float, default=1.0,
                       help='合成数据采样比例 (0.0-1.0, 默认1.0使用全部)')
    
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
    print("阶段3: 使用DAGAN合成图像训练ResNet-18")
    print('='*70)
    print(f"原始数据目录: {args.real_data_dir}")
    print(f"合成数据目录: {args.synthetic_data_dir}")
    print(f"输出目录: {args.output_dir}")
    print(f"设备: {device}")
    print(f"预训练: {args.pretrained}")
    print(f"训练轮数: {args.epochs}")
    print(f"批次大小: {args.batch_size}")
    print(f"学习率: {args.lr}")
    print(f"早停耐心: {args.patience}")
    print(f"目标准确率: {args.target_acc}%")
    print(f"合成数据比例: {args.synthetic_ratio:.2f}")
    
    # 检查合成数据是否存在
    synthetic_dir = Path(args.synthetic_data_dir)
    if not synthetic_dir.exists():
        print(f"\n❌ 合成数据目录不存在: {synthetic_dir}")
        print(f"请先运行 generate.py 生成合成图像")
        sys.exit(1)
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取数据加载器
    train_loader, val_loader, test_loader = get_dataloaders(
        real_data_dir=args.real_data_dir,
        synthetic_data_dir=args.synthetic_data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        synthetic_ratio=args.synthetic_ratio
    )
    
    # 创建模型
    print(f"\n创建ResNet-18模型...")
    model = ResNet18Classifier(num_classes=3, pretrained=args.pretrained).to(device)
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.1)
    
    # 训练
    print(f"\n{'='*70}")
    print("开始训练")
    print('='*70)
    
    history = {
        'train_loss': [], 'train_acc': [],
        'val_loss': [], 'val_acc': []
    }
    
    best_val_acc = 0.0
    no_improve = 0
    start_time = time.time()
    
    for epoch in range(1, args.epochs + 1):
        epoch_start = time.time()
        
        # 训练
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        
        # 验证
        val_loss, val_acc, _, _ = validate(
            model, val_loader, criterion, device
        )
        
        # 更新学习率
        scheduler.step()
        
        # 记录历史
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        # 打印进度
        epoch_time = time.time() - epoch_start
        total_time = time.time() - start_time
        no_improve_str = f" (无改善: {no_improve}/{args.patience})" if no_improve > 0 else ""
        
        print(f"Epoch [{epoch:3d}/{args.epochs}] "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:5.2f}% | "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:5.2f}% | "
              f"Time: {epoch_time:.1f}s{no_improve_str}")
        
        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            no_improve = 0
            
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'val_loss': val_loss,
                'history': history
            }, output_dir / 'best_model.pth')
            
            print(f"  ✅ 保存最佳模型 (Val Acc={best_val_acc:.2f}%)")
            
            # 检查是否达到目标
            if val_acc >= args.target_acc:
                print(f"\n🎉 达到目标准确率 {args.target_acc}%！")
        else:
            no_improve += 1
        
        # 早停
        if no_improve >= args.patience:
            print(f"\n⏸️ 早停触发！连续 {args.patience} 轮验证准确率无改善")
            break
    
    # 加载最佳模型进行测试
    print(f"\n{'='*70}")
    print("加载最佳模型进行测试")
    print('='*70)
    
    checkpoint = torch.load(output_dir / 'best_model.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    
    test_loss, test_acc, class_accuracies = test(
        model, test_loader, criterion, device
    )
    
    print(f"\n测试集结果:")
    print(f"  测试准确率: {test_acc:.2f}%")
    print(f"\n各类别准确率:")
    for class_name, acc_info in class_accuracies.items():
        print(f"  {class_name}: {acc_info['accuracy']:.2f}% "
              f"({acc_info['correct']}/{acc_info['total']})")
    
    # 保存结果
    results = {
        'experiment': 'DAGAN augmentation',
        'best_val_acc': best_val_acc,
        'test_acc': test_acc,
        'class_accuracies': class_accuracies,
        'history': history,
        'config': {
            'pretrained': args.pretrained,
            'epochs': epoch,
            'batch_size': args.batch_size,
            'learning_rate': args.lr,
            'patience': args.patience,
            'target_acc': args.target_acc
        },
        'data_info': {
            'train_original': len(train_loader.dataset.datasets[0]),
            'synthetic': len(train_loader.dataset.datasets[1]),
            'train_total': len(train_loader.dataset),
            'val': len(val_loader.dataset),
            'test': len(test_loader.dataset)
        }
    }
    
    results_path = output_dir / 'results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ 结果已保存: {results_path}")
    
    # 总结
    total_time = time.time() - start_time
    print(f"\n{'='*70}")
    print("训练完成！")
    print('='*70)
    print(f"\n最终结果:")
    print(f"  最佳验证准确率: {best_val_acc:.2f}%")
    print(f"  测试准确率: {test_acc:.2f}%")
    print(f"  目标准确率: {args.target_acc}%")
    print(f"  状态: {'✅ 超过目标' if test_acc >= args.target_acc else '❌ 未达目标'}")
    print(f"\n总训练时间: {total_time/60:.1f} 分钟")


if __name__ == '__main__':
    main()
