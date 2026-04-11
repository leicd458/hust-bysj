"""
评估指标模块
适合深度学习零基础的同学：这个模块就像"考试评分系统"，用各种指标评估模型的好坏

常用评估指标解释：
1. 准确率（Accuracy）：预测正确的比例
   - 公式：正确预测数 / 总样本数
   - 例如：100个样本预测对90个，准确率=90%

2. 精确率（Precision）：预测为正的样本中，真正为正的比例
   - 公式：真阳性 / (真阳性 + 假阳性)
   - 例如：预测10个恶性肿瘤，实际8个是恶性，精确率=80%

3. 召回率（Recall）：实际为正的样本中，被正确预测的比例
   - 公式：真阳性 / (真阳性 + 假阴性)
   - 例如：实际有10个恶性肿瘤，预测出8个，召回率=80%

4. F1分数：精确率和召回率的调和平均
   - 公式：2 * (精确率 * 召回率) / (精确率 + 召回率)
   - 综合考虑精确率和召回率

5. AUC（Area Under Curve）：ROC曲线下面积
   - 值范围：0-1，越接近1越好
   - 衡量模型区分正负样本的能力

6. Dice系数：用于分割任务，衡量预测区域和真实区域的重叠度
   - 公式：2 * |预测∩真实| / (|预测| + |真实|)
   - 值范围：0-1，1表示完全重叠
"""
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix
)

def calculate_metrics(y_true, y_pred, y_prob=None, average='macro'):
    """
    计算分类任务的各项指标
    
    参数说明：
        y_true: 真实标签，形状 [N]
        y_pred: 预测标签，形状 [N]
        y_prob: 预测概率，形状 [N, num_classes]（可选，用于计算AUC）
        average: 多分类平均方式
                'macro': 每个类别权重相同
                'weighted': 按类别样本数加权
    
    返回：
        metrics: 字典，包含各项指标
    """
    metrics = {}
    
    # 1. 准确率
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    
    # 2. 精确率
    metrics['precision'] = precision_score(y_true, y_pred, average=average, zero_division=0)
    
    # 3. 召回率
    metrics['recall'] = recall_score(y_true, y_pred, average=average, zero_division=0)
    
    # 4. F1分数
    metrics['f1'] = f1_score(y_true, y_pred, average=average, zero_division=0)
    
    # 5. AUC（如果提供了概率）
    if y_prob is not None:
        try:
            # 多分类AUC：使用one-vs-rest策略
            if y_prob.shape[1] > 2:
                metrics['auc'] = roc_auc_score(
                    y_true, y_prob, 
                    multi_class='ovr', 
                    average=average
                )
            else:
                # 二分类AUC
                metrics['auc'] = roc_auc_score(y_true, y_prob[:, 1])
        except:
            metrics['auc'] = 0.0
    
    # 6. 混淆矩阵
    metrics['confusion_matrix'] = confusion_matrix(y_true, y_pred)
    
    return metrics


def dice_coefficient(pred, target, smooth=1e-6):
    """
    计算Dice系数（用于分割任务）
    
    什么是Dice系数？
    - 衡量两个集合的相似度
    - 医学图像分割中最常用的指标
    - 值越接近1，分割效果越好
    
    参数说明：
        pred: 预测掩码，形状 [B, 1, H, W] 或 [B, H, W]
        target: 真实掩码，形状 [B, 1, H, W] 或 [B, H, W]
        smooth: 平滑项（避免除零）
    
    返回：
        dice: Dice系数，标量
    
    计算过程示例：
        预测区域：100个像素
        真实区域：120个像素
        重叠区域：80个像素
        Dice = 2 * 80 / (100 + 120) = 0.727
    """
    # 确保输入是tensor
    if not isinstance(pred, torch.Tensor):
        pred = torch.tensor(pred)
    if not isinstance(target, torch.Tensor):
        target = torch.tensor(target)
    
    # 展平为一维
    pred = pred.contiguous().view(-1)
    target = target.contiguous().view(-1)
    
    # 计算交集
    intersection = (pred * target).sum()
    
    # 计算Dice系数
    dice = (2. * intersection + smooth) / (pred.sum() + target.sum() + smooth)
    
    return dice.item()


def iou_score(pred, target, smooth=1e-6):
    """
    计算IoU分数（Intersection over Union）
    
    什么是IoU？
    - 交并比，衡量两个区域的重叠程度
    - 也叫Jaccard指数
    - 值范围：0-1，1表示完全重叠
    
    参数说明：
        pred: 预测掩码
        target: 真实掩码
        smooth: 平滑项
    
    返回：
        iou: IoU分数
    
    与Dice的关系：
        Dice = 2 * IoU / (1 + IoU)
        IoU = Dice / (2 - Dice)
    """
    # 确保输入是tensor
    if not isinstance(pred, torch.Tensor):
        pred = torch.tensor(pred)
    if not isinstance(target, torch.Tensor):
        target = torch.tensor(target)
    
    # 展平为一维
    pred = pred.contiguous().view(-1)
    target = target.contiguous().view(-1)
    
    # 计算交集和并集
    intersection = (pred * target).sum()
    union = pred.sum() + target.sum() - intersection
    
    # 计算IoU
    iou = (intersection + smooth) / (union + smooth)
    
    return iou.item()


def pixel_accuracy(pred, target):
    """
    计算像素准确率
    
    参数说明：
        pred: 预测掩码
        target: 真实掩码
    
    返回：
        accuracy: 像素准确率
    """
    if not isinstance(pred, torch.Tensor):
        pred = torch.tensor(pred)
    if not isinstance(target, torch.Tensor):
        target = torch.tensor(target)
    
    correct = (pred == target).sum()
    total = target.numel()
    
    return (correct / total).item()


# 测试代码
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("评估指标模块测试")
    print("=" * 60)
    
    # 测试分类指标
    print("\n1. 测试分类指标:")
    y_true = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
    y_pred = np.array([0, 1, 2, 0, 2, 1, 0, 1, 2])
    y_prob = np.random.rand(9, 3)
    
    metrics = calculate_metrics(y_true, y_pred, y_prob)
    print(f"准确率: {metrics['accuracy']:.4f}")
    print(f"精确率: {metrics['precision']:.4f}")
    print(f"召回率: {metrics['recall']:.4f}")
    print(f"F1分数: {metrics['f1']:.4f}")
    print(f"AUC: {metrics['auc']:.4f}")
    print(f"混淆矩阵:\n{metrics['confusion_matrix']}")
    
    # 测试分割指标
    print("\n2. 测试分割指标:")
    pred = torch.randint(0, 2, (2, 1, 64, 64)).float()
    target = torch.randint(0, 2, (2, 1, 64, 64)).float()
    
    dice = dice_coefficient(pred, target)
    iou = iou_score(pred, target)
    pixel_acc = pixel_accuracy(pred, target)
    
    print(f"Dice系数: {dice:.4f}")
    print(f"IoU分数: {iou:.4f}")
    print(f"像素准确率: {pixel_acc:.4f}")
    
    print("\n评估指标模块测试完成！")
