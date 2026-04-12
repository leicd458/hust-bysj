# 阶段1: ResNet-18 基线复现

**目标准确率**: 79%

## 实验配置

| 参数 | 值 |
|------|-----|
| 模型 | ResNet-18 (ImageNet 预训练) |
| 数据增强 | 无 |
| Batch Size | 32 |
| Optimizer | Adam |
| Learning Rate | 0.001 |
| Epochs | 10 |
| 数据划分 | 70% train, 15% val, 15% test |

## 文件说明

- `model.py` - ResNet-18 模型定义
- `dataset.py` - BUSI 数据集加载
- `train.py` - 训练脚本

## 运行方式

```bash
# 确保数据已下载
ls data/raw/Dataset_BUSI_with_GT/

# 开始训练
cd src/experiment/stage1
python train.py --pretrained --epochs 10 --target_acc 79.0
```

## 预期结果

根据论文 Table，ResNet 无数据增强应达到 **79%** 准确率。

## 输出文件

训练完成后会在 `outputs/stage1/` 生成:
- `best_model.pth` - 最佳模型权重
- `final_model.pth` - 最终模型权重
- `results.json` - 训练结果
- `config.json` - 训练配置
