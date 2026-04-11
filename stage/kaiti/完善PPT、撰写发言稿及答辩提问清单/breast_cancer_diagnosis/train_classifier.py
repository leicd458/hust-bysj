"""
分类模型训练脚本
适合深度学习零基础的同学：这个脚本就像"教练"，负责训练ResNet18模型识别乳腺癌类型

训练流程：
1. 加载数据集
2. 创建模型
3. 定义损失函数和优化器
4. 训练循环（多个epoch）
5. 验证和保存最佳模型
6. 可视化训练结果
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

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from config import config
from dataset import load_busi_dataset, get_transforms
from models.resnet_classifier import ResNetClassifier
from utils.metrics import calculate_metrics
from utils.visualization import plot_training_history, plot_confusion_matrix, plot_roc_curve

class ClassifierTrainer:
    """
    分类器训练类
    
    什么是训练？
    - 就像教小孩认图片，不断给它看图片和答案
    - 模型通过调整参数，逐渐学会正确分类
    - 训练过程：前向传播 -> 计算损失 -> 反向传播 -> 更新参数
    """
    
    def __init__(self, config):
        """初始化训练器"""
        self.config = config
        self.device = config.device
        
        # 创建保存目录
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        os.makedirs(config.results_dir, exist_ok=True)
        os.makedirs(config.log_dir, exist_ok=True)
        
        print(f"使用设备: {self.device}")
        
        # 训练历史记录
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        # 最佳模型指标
        self.best_val_acc = 0.0
        self.patience_counter = 0
    
    def prepare_data(self):
        """准备数据集"""
        print("
" + "=" * 60)
        print("准备数据集...")
        print("=" * 60)
        
        # 获取数据变换
        train_transform = get_transforms(
            image_size=self.config.image_size,
            augmentation=self.config.use_augmentation
        )
        val_transform = get_transforms(
            image_size=self.config.image_size,
            augmentation=False
        )
        
        # 加载数据集
        train_dataset, val_dataset, test_dataset = load_busi_dataset(
            data_root=self.config.data_root,
            train_transform=train_transform,
            val_transform=val_transform,
            test_transform=val_transform,
            train_ratio=self.config.train_ratio,
            val_ratio=self.config.val_ratio,
            test_ratio=self.config.test_ratio,
            mode='classification'
        )
        
        # 创建数据加载器
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=self.config.num_workers,
            pin_memory=True
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=True
        )
        
        self.test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=True
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
        
        # 创建ResNet18分类器
        self.model = ResNetClassifier(
            num_classes=self.config.num_classes,
            pretrained=self.config.use_pretrained
        ).to(self.device)
        
        # 定义损失函数
        # 交叉熵损失：用于多分类任务
        self.criterion = nn.CrossEntropyLoss()
        
        # 定义优化器
        # Adam优化器：自适应学习率，训练效果好
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate
        )
        
        # 学习率调度器
        # 当验证损失不再下降时，降低学习率
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True
        )
        
        print(f"模型已创建并移至 {self.device}")
    
    def train_epoch(self, epoch):
        """
        训练一个epoch
        
        什么是epoch？
        - 一个epoch = 把整个训练集过一遍
        - 例如：训练集有1000张图，batch_size=10，则一个epoch需要100个batch
        """
        self.model.train()  # 设置为训练模式
        
        running_loss = 0.0
        correct = 0
        total = 0
        
        # 使用tqdm显示进度条
        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch+1}/{self.config.num_epochs} [Train]')
        
        for batch_idx, (images, labels) in enumerate(pbar):
            # 1. 数据移至设备
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # 2. 前向传播
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            # 3. 反向传播
            self.optimizer.zero_grad()  # 清空梯度
            loss.backward()  # 计算梯度
            self.optimizer.step()  # 更新参数
            
            # 4. 统计指标
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # 5. 更新进度条
            pbar.set_postfix({
                'loss': f'{running_loss/(batch_idx+1):.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
        
        # 计算平均损失和准确率
        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = correct / total
        
        return epoch_loss, epoch_acc
    
    def validate_epoch(self, epoch):
        """验证一个epoch"""
        self.model.eval()  # 设置为评估模式
        
        running_loss = 0.0
        correct = 0
        total = 0
        
        all_labels = []
        all_preds = []
        all_probs = []
        
        pbar = tqdm(self.val_loader, desc=f'Epoch {epoch+1}/{self.config.num_epochs} [Val]')
        
        with torch.no_grad():  # 不计算梯度，节省内存
            for batch_idx, (images, labels) in enumerate(pbar):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                # 前向传播
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                # 统计指标
                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
                # 保存预测结果
                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(predicted.cpu().numpy())
                all_probs.extend(torch.softmax(outputs, dim=1).cpu().numpy())
                
                # 更新进度条
                pbar.set_postfix({
                    'loss': f'{running_loss/(batch_idx+1):.4f}',
                    'acc': f'{100.*correct/total:.2f}%'
                })
        
        # 计算平均损失和准确率
        epoch_loss = running_loss / len(self.val_loader)
        epoch_acc = correct / total
        
        return epoch_loss, epoch_acc, all_labels, all_preds, all_probs
    
    def train(self):
        """完整训练流程"""
        print("
" + "=" * 60)
        print("开始训练...")
        print("=" * 60)
        
        for epoch in range(self.config.num_epochs):
            # 训练
            train_loss, train_acc = self.train_epoch(epoch)
            
            # 验证
            val_loss, val_acc, val_labels, val_preds, val_probs = self.validate_epoch(epoch)
            
            # 更新学习率
            self.scheduler.step(val_loss)
            
            # 记录历史
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            # 打印epoch总结
            print(f"
Epoch {epoch+1}/{self.config.num_epochs} 总结:")
            print(f"  训练损失: {train_loss:.4f}, 训练准确率: {train_acc:.4f}")
            print(f"  验证损失: {val_loss:.4f}, 验证准确率: {val_acc:.4f}")
            
            # 保存最佳模型
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                self.patience_counter = 0
                
                checkpoint_path = os.path.join(
                    self.config.checkpoint_dir,
                    'best_classifier.pth'
                )
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_acc': val_acc,
                    'val_loss': val_loss
                }, checkpoint_path)
                
                print(f"  ✓ 保存最佳模型 (验证准确率: {val_acc:.4f})")
            else:
                self.patience_counter += 1
                print(f"  验证准确率未提升 ({self.patience_counter}/{self.config.patience})")
            
            # 早停
            if self.patience_counter >= self.config.patience:
                print(f"
早停触发！验证准确率已 {self.config.patience} 轮未提升。")
                break
        
        print("
训练完成！")
        
        # 保存训练历史
        history_path = os.path.join(self.config.results_dir, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=4)
        print(f"训练历史已保存到: {history_path}")
    
    def evaluate(self):
        """在测试集上评估模型"""
        print("
" + "=" * 60)
        print("在测试集上评估模型...")
        print("=" * 60)
        
        # 加载最佳模型
        checkpoint_path = os.path.join(self.config.checkpoint_dir, 'best_classifier.pth')
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        self.model.eval()
        
        all_labels = []
        all_preds = []
        all_probs = []
        
        with torch.no_grad():
            for images, labels in tqdm(self.test_loader, desc='Testing'):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                _, predicted = outputs.max(1)
                
                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(predicted.cpu().numpy())
                all_probs.extend(torch.softmax(outputs, dim=1).cpu().numpy())
        
        # 计算评估指标
        all_labels = np.array(all_labels)
        all_preds = np.array(all_preds)
        all_probs = np.array(all_probs)
        
        metrics = calculate_metrics(all_labels, all_preds, all_probs, self.config.num_classes)
        
        print("
测试集评估结果:")
        print(f"  准确率: {metrics['accuracy']:.4f}")
        print(f"  精确率: {metrics['precision']:.4f}")
        print(f"  召回率: {metrics['recall']:.4f}")
        print(f"  F1分数: {metrics['f1']:.4f}")
        
        # 保存评估结果
        results_path = os.path.join(self.config.results_dir, 'test_results.json')
        with open(results_path, 'w') as f:
            json.dump(metrics, f, indent=4)
        print(f"
评估结果已保存到: {results_path}")
        
        return all_labels, all_preds, all_probs
    
    def visualize_results(self, labels, preds, probs):
        """可视化训练结果"""
        print("
" + "=" * 60)
        print("生成可视化结果...")
        print("=" * 60)
        
        # 1. 训练历史曲线
        history_plot_path = os.path.join(self.config.results_dir, 'training_history.png')
        plot_training_history(self.history, save_path=history_plot_path)
        
        # 2. 混淆矩阵
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(labels, preds)
        cm_plot_path = os.path.join(self.config.results_dir, 'confusion_matrix.png')
        plot_confusion_matrix(cm, self.config.class_names, save_path=cm_plot_path)
        
        # 3. ROC曲线
        roc_plot_path = os.path.join(self.config.results_dir, 'roc_curve.png')
        plot_roc_curve(labels, probs, self.config.class_names, save_path=roc_plot_path)
        
        print("可视化结果已生成！")


def main():
    """主函数"""
    print("=" * 80)
    print("乳腺癌超声图像分类模型训练")
    print("=" * 80)
    
    # 设置随机种子（保证实验可复现）
    torch.manual_seed(config.random_seed)
    np.random.seed(config.random_seed)
    
    # 创建训练器
    trainer = ClassifierTrainer(config)
    
    # 准备数据
    trainer.prepare_data()
    
    # 构建模型
    trainer.build_model()
    
    # 训练模型
    trainer.train()
    
    # 评估模型
    labels, preds, probs = trainer.evaluate()
    
    # 可视化结果
    trainer.visualize_results(labels, preds, probs)
    
    print("
" + "=" * 80)
    print("训练流程全部完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
