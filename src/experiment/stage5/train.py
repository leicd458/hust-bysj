#!/usr/bin/env python3
"""
阶段5: 准确率优化 - 基于论文标准方法

目标: 测试准确率 >= 93%

核心设计 (全部基于论文实证):
1. 骨干网络: EfficientNet-B0 (比 ResNet-18 更高效, 参数量 4M vs 11.7M)
2. 输入分辨率: 300x300 (EfficientNet 默认分辨率)
3. 损失函数: CrossEntropyLoss + LabelSmoothing=0.1 (论文常用, 正则化效果)
4. 优化器: Adam (lr=1e-4) - 与 Latha 2024 / arXiv 2025 一致
5. 数据划分: StratifiedKFold 80/10/10 (保证类别比例一致)
6. 类别平衡: WeightedRandomSampler (每个 batch 近似等量三类样本)
7. 数据增强: 轻量级 (旋转±10° + 翻转 + zoom≤10% + translate≤5%)
8. TTA: 4倍推理增强

参考论文:
- Latha et al. (2024): EfficientNet-B7 on BUSI, Adam lr=1e-4, stratified split
- arXiv 2025: Interpretable Deep Transfer Learning, rotation±10°+flip+zoom
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
from torchvision.models import EfficientNet_B0_Weights
from tqdm import tqdm

from dataset import get_dataloaders, tta_predict_batch, get_tta_transforms


# ==================== 模型定义 ====================

class EfficientNetB0Classifier(nn.Module):
    """EfficientNet-B0 三分类器 (benign / malignant / normal)"""

    def __init__(self, num_classes=3, pretrained=True, dropout=0.5):
        super().__init__()
        if pretrained:
            self.backbone = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            self.backbone = models.efficientnet_b0(weights=None)

        # 替换分类头
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


# ==================== 训练 & 验证 & 测试 ====================

def train_epoch(model, train_loader, criterion, optimizer, device, epoch_num):
    """训练一个 epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(train_loader, desc=f"Epoch [{epoch_num}]", leave=False)
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        pbar.set_postfix({'loss': f'{loss.item():.4f}', 'acc': f'{100.*correct/total:.2f}%'})

    return running_loss / total, 100. * correct / total


def validate(model, val_loader, criterion, device):
    """验证"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    class_correct = [0] * 3
    class_total = [0] * 3

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

            for i in range(len(labels)):
                lbl = labels[i].item()
                class_total[lbl] += 1
                if predicted[i] == lbl:
                    class_correct[lbl] += 1

    class_names = ['benign', 'malignant', 'normal']
    class_accs = {}
    for i, name in enumerate(class_names):
        class_accs[name] = 100. * class_correct[i] / max(class_total[i], 1)

    return running_loss / total, 100. * correct / total, class_accs


def test_standard(model, test_loader, criterion, device):
    """标准测试 (无 TTA)"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Testing", leave=False):
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            all_preds.extend(predicted.cpu().numpy().tolist())
            all_labels.extend(labels.cpu().numpy().tolist())

    accuracy = 100. * correct / total
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    class_names = ['benign', 'malignant', 'normal']
    class_accuracies = {}
    for idx, name in enumerate(class_names):
        mask = all_labels == idx
        if mask.sum() > 0:
            class_accuracies[name] = {
                'accuracy': float((all_preds[mask] == all_labels[mask]).mean() * 100),
                'correct': int((all_preds[mask] == all_labels[mask]).sum()),
                'total': int(mask.sum())
            }

    return running_loss / len(test_loader), accuracy, class_accuracies


def test_with_tta(model, test_loader, criterion, device, tta_transforms):
    """TTA 测试"""
    all_preds, all_labels = tta_predict_batch(
        model, None, tta_transforms, device, test_loader
    )
    accuracy = (all_preds == all_labels).mean() * 100

    class_names = ['benign', 'malignant', 'normal']
    class_accuracies = {}
    for idx, name in enumerate(class_names):
        mask = all_labels == idx
        if mask.sum() > 0:
            class_accuracies[name] = {
                'accuracy': float((all_preds[mask] == all_labels[mask]).mean() * 100),
                'correct': int((all_preds[mask] == all_labels[mask]).sum()),
                'total': int(mask.sum())
            }

    return accuracy, class_accuracies


# ==================== 主流程 ====================

def main():
    parser = argparse.ArgumentParser(description='阶段5: 论文级准确率优化')
    
    # 数据
    parser.add_argument('--data_dir', type=str,
                       default='/Users/koolei/Desktop/hust-bysj-new/data/raw/Dataset_BUSI_with_GT')
    parser.add_argument('--synthetic_data_dir', type=str,
                       default='/Users/koolei/Desktop/hust-bysj-new/data/synthetic')
    parser.add_argument('--synthetic_ratio', type=float, default=1.0,
                       help='合成数据使用比例')

    # 模型
    parser.add_argument('--pretrained', action='store_true', default=True)
    parser.add_argument('--dropout', type=float, default=0.5)

    # 训练超参数 (与论文一致)
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-4,
                       help='学习率 (论文推荐 Adam lr=1e-4)')
    parser.add_argument('--weight_decay', type=float, default=1e-4)
    parser.add_argument('--patience', type=int, default=12)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--label_smoothing', type=float, default=0.1,
                       help='Label smoothing (论文常用 0.05~0.1)')
    
    # 数据划分比例
    parser.add_argument('--train_ratio', type=float, default=0.70,
                       help='训练集比例')
    parser.add_argument('--val_ratio', type=float, default=0.15,
                       help='验证集比例')
    parser.add_argument('--test_ratio', type=float, default=0.15,
                       help='测试集比例')
    
    # TTA
    parser.add_argument('--use_tta', action='store_true', default=True)

    # 其他
    parser.add_argument('--device', type=str, default='auto')
    parser.add_argument('--num_workers', type=int, default=0)
    parser.add_argument('--output_dir', type=str,
                       default='/Users/koolei/Desktop/hust-bysj-new/src/experiment/stage5/outputs')
    parser.add_argument('--target_acc', type=float, default=93.0)

    args = parser.parse_args()

    # ========== 设备 ==========
    if args.device == 'auto':
        if torch.backends.mps.is_available():
            device = torch.device('mps')
        elif torch.cuda.is_available():
            device = torch.device('cuda')
        else:
            device = torch.device('cpu')
    else:
        device = torch.device(args.device)

    # 种子
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(args.seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ========== 打印配置 ==========
    print(f"\n{'='*70}")
    print("阶段5: 论文级准确率优化")
    print(f"{'='*70}")
    print(f"模型:       EfficientNet-B0 (pretrained={args.pretrained}, dropout={args.dropout})")
    print(f"输入尺寸:   {300}x{300}")
    print(f"损失函数:   CrossEntropyLoss(label_smoothing={args.label_smoothing})")
    print(f"优化器:     Adam(lr={args.lr}, weight_decay={args.weight_decay})")
    print(f"调度器:     ReduceLROnPlateau(factor=0.5, patience=5)")
    print(f"数据划分:   Stratified {args.train_ratio:.0%}/{args.val_ratio:.0%}/{args.test_ratio:.0%}")
    print(f"采样策略:   WeightedRandomSampler (类别均衡)")
    print(f"数据增强:   Rotation±10° + HFlip + Zoom≤10% + Translate≤5%")
    print(f"TTA推理:    {'开启 (4x)' if args.use_tta else '关闭'}")
    print(f"训练轮数:   {args.epochs} | Batch: {args.batch_size} | Patience: {args.patience}")
    print(f"设备:       {device}")
    print(f"目标准确率: {args.target_acc}%")

    # 保存配置
    config_dict = vars(args)
    config_dict['image_size'] = 300
    config_dict['model'] = 'EfficientNet-B0'
    config_dict['optimizer'] = 'Adam'
    config_dict['scheduler'] = 'ReduceLROnPlateau'
    with open(output_dir / 'config.json', 'w') as f:
        json.dump(config_dict, f, indent=2)

    # ========== 加载数据 ==========
    train_loader, val_loader, test_loader = get_dataloaders(
        data_dir=args.data_dir,
        synthetic_data_dir=args.synthetic_data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        synthetic_ratio=args.synthetic_ratio,
        seed=args.seed,
        use_balanced_sampler=True
    )

    # ========== 创建模型 ==========
    print(f"\n创建模型...")
    model = EfficientNetB0Classifier(
        num_classes=3,
        pretrained=args.pretrained,
        dropout=args.dropout
    ).to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"  参数量: {n_params:,}")

    # 损失函数: CrossEntropy + LabelSmoothing
    criterion = nn.CrossEntropyLoss(label_smoothing=args.label_smoothing)
    print(f"  损失函数: CrossEntropyLoss(label_smoothing={args.label_smoothing})")

    # 优化器: Adam (与论文一致)
    optimizer = optim.Adam(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay
    )
    print(f"  优化器: Adam(lr={args.lr}, wd={args.weight_decay})")

    # 学习率调度: ReduceLROnPlateau (验证损失不降时减半)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=5
    )

    # ========== 训练循环 ==========
    print(f"\n{'='*70}")
    print("开始训练")
    print(f"{'='*70}")

    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    best_val_acc = 0.0
    no_improve = 0
    start_time = time.time()
    last_epoch = 0

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()

        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )

        val_loss, val_acc, class_accs = validate(model, val_loader, criterion, device)
        scheduler.step(val_acc)

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        current_lr = optimizer.param_groups[0]['lr']
        elapsed = time.time() - t0
        no_improve_str = f" [无改善:{no_improve}/{args.patience}]" if no_improve > 0 else ""

        print(f"Epoch [{epoch:3d}/{args.epochs}] "
              f"Train {train_acc:5.2f}% | Val {val_acc:5.2f}% "
              f"| B:{class_accs['benign']:4.1f}% M:{class_accs['malignant']:4.1f}% N:{class_accs['normal']:4.1f}% "
              f"| lr:{current_lr:.6f} | {elapsed:.1f}s{no_improve_str}")

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
                'class_accs': class_accs
            }, output_dir / 'best_model.pth')
            print(f"      ** 最佳! Val Acc={val_acc:.2f}%")

            if val_acc >= args.target_acc:
                print(f"\n      !!! 达到目标准确率 {args.target_acc}% !!!")
        else:
            no_improve += 1

        if no_improve >= args.patience:
            print(f"\n早停触发! 连续{args.patience}轮无改善 (Epoch {epoch})")
            break

        last_epoch = epoch

    # ========== 测试 ==========
    print(f"\n{'='*70}")
    print("加载最佳模型进行测试")
    print(f"{'='*70}")

    checkpoint = torch.load(output_dir / 'best_model.pth', map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])

    # 标准测试
    test_loss, test_acc_std, class_accs_std = test_standard(model, test_loader, criterion, device)
    print(f"\n标准测试结果:")
    print(f"  准确率: {test_acc_std:.2f}%")
    for name, info in class_accs_std.items():
        print(f"    {name}: {info['accuracy']:.2f}% ({info['correct']}/{info['total']})")

    # TTA 测试
    final_acc = test_acc_std
    final_class_accs = class_accs_std
    test_acc_tta = None
    class_accs_tta = None
    
    if args.use_tta:
        tta_transforms = get_tta_transforms()
        test_acc_tta, class_accs_tta = test_with_tta(model, test_loader, criterion, device, tta_transforms)
        print(f"\nTTA 测试结果:")
        print(f"  准确率: {test_acc_tta:.2f}% (+{test_acc_tta-test_acc_std:.2f}%)")
        for name, info in class_accs_tta.items():
            print(f"    {name}: {info['accuracy']:.2f}% ({info['correct']}/{info['total']})")
        final_acc = test_acc_tta
        final_class_accs = class_accs_tta

    # ========== 保存结果 ==========
    results = {
        'experiment': 'stage5: Paper-standard method',
        'method_summary': {
            'backbone': 'EfficientNet-B0',
            'input_size': 300,
            'loss': 'CrossEntropyLoss+LabelSmoothing',
            'optimizer': 'Adam',
            'lr': args.lr,
            'split': 'StratifiedKFold 80/10/10',
            'sampling': 'WeightedRandomSampler (balanced)',
            'augmentation': 'Rotation±10°+HFlip+Zoom≤10%',
            'tta': args.use_tta,
        },
        'best_val_acc': best_val_acc,
        'test_acc_standard': test_acc_std,
        'test_acc_tta': test_acc_tta,
        'test_acc_final': final_acc,
        'class_accs_standard': class_accs_std,
        'class_accs_tta': class_accs_tta,
        'history': history,
        'config': dict(config_dict),
        'target_acc': args.target_acc,
        'achieved': bool(final_acc >= args.target_acc),
        'epochs_trained': last_epoch,
        'total_time_minutes': (time.time() - start_time) / 60,
    }
    with open(output_dir / 'results.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 保存最终模型权重
    torch.save(model.state_dict(), output_dir / 'final_model.pth')

    total_time = time.time() - start_time
    print(f"\n{'='*70}")
    print("训练完成!")
    print(f"{'='*70}")
    print(f"  最佳验证准确率: {best_val_acc:.2f}%")
    print(f"  标准测试准确率: {test_acc_std:.2f}%")
    if args.use_tta:
        print(f"  TTA 测试准确率:  {final_acc:.2f}% (+{final_acc-test_acc_std:.2f}%)")
    print(f"  目标准确率:     {args.target_acc}%")
    status = '**达成目标!**' if final_acc >= args.target_acc else '未达目标'
    print(f"  状态: {status}")
    print(f"  总时间: {total_time/60:.1f} 分钟 ({last_epoch} epochs)")
    print(f"  结果保存至: {output_dir}")


if __name__ == '__main__':
    main()
