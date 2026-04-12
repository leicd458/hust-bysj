"""
阶段1训练脚本: ResNet-18 基线模型
目标准确率: 79%

配置 (参考老项目成功经验):
- Batch size: 64
- Optimizer: SGD (lr=0.01, momentum=0.9, weight_decay=5e-4)
- Epochs: 50 (早停 patience=10)
- 数据划分: 70% train, 15% val, 15% test
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR
from tqdm import tqdm
import numpy as np


def train_one_epoch(model, train_loader, criterion, optimizer, device, epoch):
    """训练一个 epoch"""
    model.train()
    
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(train_loader, desc=f"Epoch {epoch}")
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)
        
        # 前向传播
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # 反向传播
        loss.backward()
        optimizer.step()
        
        # 统计
        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        # 更新进度条
        pbar.set_postfix({
            'loss': running_loss / total,
            'acc': 100. * correct / total
        })
    
    epoch_loss = running_loss / total
    epoch_acc = 100. * correct / total
    
    return epoch_loss, epoch_acc


def validate(model, val_loader, criterion, device):
    """验证"""
    model.eval()
    
    running_loss = 0.0
    correct = 0
    total = 0
    
    # 每个类别的准确率
    class_correct = [0, 0, 0]
    class_total = [0, 0, 0]
    class_names = ['benign', 'malignant', 'normal']
    
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # 每个类别的统计
            for i in range(len(labels)):
                label = labels[i].item()
                class_total[label] += 1
                if predicted[i] == label:
                    class_correct[label] += 1
    
    val_loss = running_loss / total
    val_acc = 100. * correct / total
    
    # 每个类别的准确率
    class_accs = {}
    for i, name in enumerate(class_names):
        if class_total[i] > 0:
            class_accs[name] = 100. * class_correct[i] / class_total[i]
        else:
            class_accs[name] = 0.0
    
    return val_loss, val_acc, class_accs


def train(args):
    """完整训练流程"""
    # 设置设备
    device = torch.device(args.device if torch.cuda.is_available() or args.device == 'cpu' else 'cpu')
    print(f"\n使用设备: {device}")
    
    # 设置随机种子
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(args.seed)
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存配置
    config = vars(args)
    with open(output_dir / 'config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # 加载数据
    sys.path.insert(0, str(Path(__file__).parent))
    from dataset import get_dataloaders
    
    train_loader, val_loader, test_loader = get_dataloaders(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        seed=args.seed
    )
    
    # 加载模型
    from model import load_model
    
    model = load_model(num_classes=3, pretrained=args.pretrained, device=device)
    
    # 损失函数
    criterion = nn.CrossEntropyLoss()
    
    # 优化器 (SGD + momentum + weight decay)
    optimizer = optim.SGD(
        model.parameters(),
        lr=args.lr,
        momentum=0.9,
        weight_decay=5e-4
    )
    
    # 学习率调度器
    scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
    
    # 训练循环
    best_acc = 0.0
    patience = args.patience
    no_improve = 0
    history = {
        'train_loss': [], 'train_acc': [],
        'val_loss': [], 'val_acc': [],
        'class_accs': []
    }
    
    print(f"\n开始训练 (目标: {args.target_acc}%)")
    print(f"早停设置: patience={patience}")
    print("=" * 60)
    
    for epoch in range(1, args.epochs + 1):
        # 训练
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        
        # 验证
        val_loss, val_acc, class_accs = validate(
            model, val_loader, criterion, device
        )
        
        # 更新学习率
        scheduler.step()
        
        # 记录历史
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['class_accs'].append(class_accs)
        
        # 打印结果
        print(f"\nEpoch {epoch}/{args.epochs}")
        print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        print(f"  Class Accs: benign={class_accs['benign']:.2f}%, "
              f"malignant={class_accs['malignant']:.2f}%, "
              f"normal={class_accs['normal']:.2f}%")
        
        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            no_improve = 0
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'class_accs': class_accs
            }, output_dir / 'best_model.pth')
            
            print(f"  ✓ 保存最佳模型 (Val Acc: {val_acc:.2f}%)")
        else:
            no_improve += 1
        
        # 早停检查
        if no_improve >= patience:
            print(f"\n⏸️ 早停触发！连续 {patience} 轮验证准确率无改善")
            break
    
    # 最终测试 (加载最佳模型)
    print("\n" + "=" * 60)
    print("测试集评估 (使用最佳模型):")
    
    # 加载最佳模型
    checkpoint = torch.load(output_dir / 'best_model.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    
    test_loss, test_acc, test_class_accs = validate(
        model, test_loader, criterion, device
    )
    
    print(f"  Test Loss: {test_loss:.4f}")
    print(f"  Test Acc: {test_acc:.2f}%")
    print(f"  Class Accs: benign={test_class_accs['benign']:.2f}%, "
          f"malignant={test_class_accs['malignant']:.2f}%, "
          f"normal={test_class_accs['normal']:.2f}%")
    
    # 保存结果
    results = {
        'best_val_acc': best_acc,
        'test_acc': test_acc,
        'test_class_accs': test_class_accs,
        'history': history
    }
    
    with open(output_dir / 'results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # 保存最终模型
    torch.save(model.state_dict(), output_dir / 'final_model.pth')
    
    print(f"\n✓ 训练完成!")
    print(f"  - 最佳验证准确率: {best_acc:.2f}%")
    print(f"  - 测试准确率: {test_acc:.2f}%")
    print(f"  - 结果保存在: {output_dir}")
    
    return test_acc


def main():
    parser = argparse.ArgumentParser(description='阶段1训练: ResNet-18 基线')
    
    # 数据参数
    parser.add_argument('--data_dir', type=str, 
                        default='data/raw/Dataset_BUSI_with_GT',
                        help='数据目录')
    
    # 模型参数
    parser.add_argument('--pretrained', action='store_true', default=True,
                        help='使用预训练权重')
    
    # 训练参数
    parser.add_argument('--batch_size', type=int, default=64,
                        help='批次大小')
    parser.add_argument('--lr', type=float, default=0.01,
                        help='学习率')
    parser.add_argument('--epochs', type=int, default=50,
                        help='训练轮数')
    parser.add_argument('--patience', type=int, default=10,
                        help='早停耐心值')
    parser.add_argument('--seed', type=int, default=42,
                        help='随机种子')
    
    # 目标
    parser.add_argument('--target_acc', type=float, default=79.0,
                        help='目标准确率 (%)')
    
    # 其他
    parser.add_argument('--device', type=str, default='mps',
                        help='设备 (cuda/mps/cpu)')
    parser.add_argument('--num_workers', type=int, default=4,
                        help='数据加载进程数')
    parser.add_argument('--output_dir', type=str, 
                        default='outputs/stage1',
                        help='输出目录')
    
    args = parser.parse_args()
    
    train(args)


if __name__ == "__main__":
    main()
