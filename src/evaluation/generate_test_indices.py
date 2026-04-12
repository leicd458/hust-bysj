#!/usr/bin/env python3
"""
生成测试集索引文件
使用与训练时相同的随机种子，确保测试集划分一致
"""

import sys
import json
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from experiment.stage4.dataset import BUSIDatasetWithIndices
import torch
from torch.utils.data import random_split


def main():
    # 数据目录
    data_dir = '/Users/koolei/Desktop/hust-bysj-new/data/raw/Dataset_BUSI_with_GT'
    
    # 随机种子（与训练时一致）
    seed = 2024
    
    # 加载数据集
    print("加载数据集...")
    dataset = BUSIDatasetWithIndices(data_dir)
    
    # 划分数据集（与训练时相同的参数）
    train_ratio = 0.7
    val_ratio = 0.15
    test_ratio = 0.15
    
    train_size = int(train_ratio * len(dataset))
    val_size = int(val_ratio * len(dataset))
    test_size = len(dataset) - train_size - val_size
    
    # 使用相同的随机种子划分
    train_set, val_set, test_set = random_split(
        dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(seed)
    )
    
    # 提取索引
    train_indices = train_set.indices
    val_indices = val_set.indices
    test_indices = test_set.indices
    
    # 保存到JSON
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'test_indices.json'
    with open(output_file, 'w') as f:
        json.dump(test_indices, f)
    
    print(f"\n✓ 测试集索引已保存: {output_file}")
    print(f"  - 训练集: {len(train_indices)} 张")
    print(f"  - 验证集: {len(val_indices)} 张")
    print(f"  - 测试集: {len(test_indices)} 张")
    print(f"  - 随机种子: {seed}")


if __name__ == '__main__':
    main()
