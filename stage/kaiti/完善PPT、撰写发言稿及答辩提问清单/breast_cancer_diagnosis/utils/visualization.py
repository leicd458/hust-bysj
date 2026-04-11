"""
可视化工具模块
适合深度学习零基础的同学：这个模块就像"数据画家"，把训练过程和结果画成图表
"""
import matplotlib.pyplot as plt
import seaborn
import seaborn as sns
sns.set_theme()
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.sans-serif'] = ['SimHei']
import seaborn as sns
import numpy as np
from sklearn.metrics import roc_curve, auc
import torch

# 设置中文字体（Mac系统）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def plot_training_history(history, save_path=None):
    """
    绘制训练历史曲线
    
    什么是训练历史？
    - 记录每个epoch的损失和准确率
    - 通过曲线可以看出模型是否收敛、是否过拟合
    
    参数说明：
        history: 字典，包含训练历史
                {
                    'train_loss': [loss1, loss2, ...],
                    'val_loss': [loss1, loss2, ...],
                    'train_acc': [acc1, acc2, ...],
                    'val_acc': [acc1, acc2, ...]
                }
        save_path: 保存路径（如果为None，则显示图表）
    
    如何看懂训练曲线？
    1. 损失曲线：
       - 训练损失和验证损失都下降：正常训练
       - 训练损失下降，验证损失上升：过拟合
       - 两者都不下降：学习率太大或模型有问题
    
    2. 准确率曲线：
       - 训练准确率和验证准确率都上升：正常训练
       - 训练准确率高，验证准确率低：过拟合
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # 1. 绘制损失曲线
    axes[0].plot(history['train_loss'], label='训练损失', marker='o')
    axes[0].plot(history['val_loss'], label='验证损失', marker='s')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('训练和验证损失曲线')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 2. 绘制准确率曲线
    axes[1].plot(history['train_acc'], label='训练准确率', marker='o')
    axes[1].plot(history['val_acc'], label='验证准确率', marker='s')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('训练和验证准确率曲线')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"训练历史曲线已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_confusion_matrix(cm, class_names, save_path=None):
    """
    绘制混淆矩阵
    
    什么是混淆矩阵？
    - 展示模型预测结果的详细情况
    - 行表示真实类别，列表示预测类别
    - 对角线上的数字越大越好（表示预测正确）
    
    参数说明：
        cm: 混淆矩阵，形状 [num_classes, num_classes]
        class_names: 类别名称列表
        save_path: 保存路径
    
    如何看懂混淆矩阵？
    例如3x3矩阵：
              预测:正常  预测:良性  预测:恶性
    真实:正常    50        3         2
    真实:良性     2       45         3
    真实:恶性     1        4        40
    
    - 对角线(50, 45, 40)：预测正确的数量
    - 非对角线：预测错误的数量
    - 第1行第2列(3)：3个正常样本被误判为良性
    """
    plt.figure(figsize=(10, 8))
    
    # 归一化混淆矩阵（转换为百分比）
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    # 绘制热力图
    sns.heatmap(
        cm_normalized, 
        annot=True,  # 显示数字
        fmt='.2%',   # 百分比格式
        cmap='Blues',  # 蓝色渐变
        xticklabels=class_names,
        yticklabels=class_names,
        cbar_kws={'label': '比例'}
    )
    
    plt.xlabel('预测类别')
    plt.ylabel('真实类别')
    plt.title('混淆矩阵（归一化）')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"混淆矩阵已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_roc_curve(y_true, y_prob, class_names, save_path=None):
    """
    绘制ROC曲线
    
    什么是ROC曲线？
    - Receiver Operating Characteristic（接收者操作特征）曲线
    - 横轴：假阳性率（FPR），纵轴：真阳性率（TPR）
    - 曲线越靠近左上角越好
    - AUC（曲线下面积）越大越好，最大为1
    
    参数说明：
        y_true: 真实标签，形状 [N]
        y_prob: 预测概率，形状 [N, num_classes]
        class_names: 类别名称列表
        save_path: 保存路径
    
    如何看懂ROC曲线？
    - 对角线（虚线）：随机猜测的性能
    - 曲线在对角线上方：模型有效
    - 曲线越凸向左上角，性能越好
    - AUC=0.5：随机猜测
    - AUC=1.0：完美分类器
    """
    plt.figure(figsize=(10, 8))
    
    # 为每个类别绘制ROC曲线
    for i, class_name in enumerate(class_names):
        # 将多分类问题转换为二分类（one-vs-rest）
        y_true_binary = (y_true == i).astype(int)
        y_prob_class = y_prob[:, i]
        
        # 计算ROC曲线
        fpr, tpr, _ = roc_curve(y_true_binary, y_prob_class)
        roc_auc = auc(fpr, tpr)
        
        # 绘制曲线
        plt.plot(
            fpr, tpr, 
            label=f'{class_name} (AUC = {roc_auc:.3f})',
            linewidth=2
        )
    
    # 绘制对角线（随机猜测）
    plt.plot([0, 1], [0, 1], 'k--', label='随机猜测 (AUC = 0.5)')
    
    plt.xlabel('假阳性率 (FPR)')
    plt.ylabel('真阳性率 (TPR)')
    plt.title('ROC曲线')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"ROC曲线已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_segmentation_results(images, masks_true, masks_pred, save_path=None, num_samples=4):
    """
    绘制分割结果对比图
    
    参数说明：
        images: 原始图片，形状 [B, 3, H, W]
        masks_true: 真实掩码，形状 [B, 1, H, W]
        masks_pred: 预测掩码，形状 [B, 1, H, W]
        save_path: 保存路径
        num_samples: 显示样本数量
    """
    num_samples = min(num_samples, images.shape[0])
    
    fig, axes = plt.subplots(num_samples, 3, figsize=(12, 4 * num_samples))
    
    for i in range(num_samples):
        # 原始图片
        img = images[i].cpu().numpy().transpose(1, 2, 0)
        img = (img - img.min()) / (img.max() - img.min())
        axes[i, 0].imshow(img)
        axes[i, 0].set_title('原始图片')
        axes[i, 0].axis('off')
        
        # 真实掩码
        mask_true = masks_true[i, 0].cpu().numpy()
        axes[i, 1].imshow(mask_true, cmap='gray')
        axes[i, 1].set_title('真实掩码')
        axes[i, 1].axis('off')
        
        # 预测掩码
        mask_pred = masks_pred[i, 0].cpu().numpy()
        axes[i, 2].imshow(mask_pred, cmap='gray')
        axes[i, 2].set_title('预测掩码')
        axes[i, 2].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"分割结果已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()


# 测试代码
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("可视化工具模块测试")
    print("=" * 60)
    
    # 测试训练历史曲线
    print("\n1. 测试训练历史曲线")
    history = {
        'train_loss': [0.8, 0.6, 0.4, 0.3, 0.2],
        'val_loss': [0.7, 0.5, 0.4, 0.35, 0.3],
        'train_acc': [0.6, 0.7, 0.8, 0.85, 0.9],
        'val_acc': [0.65, 0.72, 0.78, 0.82, 0.85]
    }
    plot_training_history(history, save_path='/usr/local/app/workspace/test_history.png')
    
    # 测试混淆矩阵
    print("\n2. 测试混淆矩阵")
    cm = np.array([[50, 3, 2], [2, 45, 3], [1, 4, 40]])
    class_names = ['正常', '良性', '恶性']
    plot_confusion_matrix(cm, class_names, save_path='/usr/local/app/workspace/test_cm.png')
    
    # 测试ROC曲线
    print("\n3. 测试ROC曲线")
    y_true = np.random.randint(0, 3, 100)
    y_prob = np.random.rand(100, 3)
    y_prob = y_prob / y_prob.sum(axis=1, keepdims=True)
    plot_roc_curve(y_true, y_prob, class_names, save_path='/usr/local/app/workspace/test_roc.png')
    
    print("\n可视化工具模块测试完成！")
