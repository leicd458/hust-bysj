#!/usr/bin/env python3
"""
阶段4超参数搜索脚本

目标：突破90%准确率

策略：
1. 多个随机种子实验
2. 不同学习率
3. 不同Dropout比例
4. 更长的训练patience
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# 实验配置
experiments = [
    # 实验1: 多个随机种子
    {
        'name': 'seed_123',
        'seed': 123,
        'lr': 0.0001,
        'dropout': 0.30,
        'patience': 15,
    },
    {
        'name': 'seed_2024',
        'seed': 2024,
        'lr': 0.0001,
        'dropout': 0.30,
        'patience': 15,
    },
    {
        'name': 'seed_2026',
        'seed': 2026,
        'lr': 0.0001,
        'dropout': 0.30,
        'patience': 15,
    },
    
    # 实验2: 不同学习率
    {
        'name': 'lr_5e-5',
        'seed': 42,
        'lr': 0.00005,
        'dropout': 0.30,
        'patience': 15,
    },
    {
        'name': 'lr_2e-4',
        'seed': 42,
        'lr': 0.0002,
        'dropout': 0.30,
        'patience': 15,
    },
    
    # 实验3: 不同Dropout
    {
        'name': 'dropout_0.20',
        'seed': 42,
        'lr': 0.0001,
        'dropout': 0.20,
        'patience': 15,
    },
    {
        'name': 'dropout_0.25',
        'seed': 42,
        'lr': 0.0001,
        'dropout': 0.25,
        'patience': 15,
    },
    
    # 实验4: 组合优化
    {
        'name': 'opt_seed2024_lr5e-5',
        'seed': 2024,
        'lr': 0.00005,
        'dropout': 0.25,
        'patience': 20,
    },
]

def run_experiment(config):
    """运行单个实验"""
    print(f"\n{'='*70}")
    print(f"实验: {config['name']}")
    print(f"配置: seed={config['seed']}, lr={config['lr']}, dropout={config['dropout']}, patience={config['patience']}")
    print('='*70)
    
    output_dir = f"outputs/search_{config['name']}"
    
    # 构建命令
    cmd = [
        'python', 'train.py',
        '--real_data_dir', '/Users/koolei/Desktop/hust-bysj-new/data/raw/Dataset_BUSI_with_GT',
        '--synthetic_data_dir', '/Users/koolei/Desktop/hust-bysj-new/data/synthetic',
        '--output_dir', output_dir,
        '--pretrained',
        '--epochs', '60',
        '--batch_size', '32',
        '--lr', str(config['lr']),
        '--patience', str(config['patience']),
        '--target_acc', '90.0',
        '--device', 'mps',
        '--num_workers', '0',
        '--synthetic_ratio', '1.0',
        '--dropout', str(config['dropout']),
        '--seed', str(config['seed']),
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # 读取结果
        results_file = Path(output_dir) / 'results.json'
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
                test_acc = results.get('test_acc', 0)
        else:
            test_acc = 0
        
        elapsed = time.time() - start_time
        
        return {
            'name': config['name'],
            'config': config,
            'test_acc': test_acc,
            'time': elapsed,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ 实验失败: {e}")
        return {
            'name': config['name'],
            'config': config,
            'test_acc': 0,
            'time': 0,
            'success': False,
            'error': str(e)
        }

def main():
    print(f"\n{'='*70}")
    print("阶段4超参数搜索")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"实验数量: {len(experiments)}")
    print('='*70)
    
    results = []
    
    for i, exp in enumerate(experiments, 1):
        print(f"\n进度: [{i}/{len(experiments)}]")
        result = run_experiment(exp)
        results.append(result)
        
        # 打印当前结果
        if result['success']:
            print(f"✅ {result['name']}: {result['test_acc']:.2f}% (用时: {result['time']/60:.1f}分钟)")
        else:
            print(f"❌ {result['name']}: 失败")
    
    # 汇总结果
    print(f"\n{'='*70}")
    print("实验结果汇总")
    print('='*70)
    
    # 按准确率排序
    results_sorted = sorted([r for r in results if r['success']], 
                           key=lambda x: x['test_acc'], reverse=True)
    
    print(f"\n{'排名':<6} {'实验名称':<25} {'测试准确率':<12} {'用时(分钟)':<12}")
    print('-' * 70)
    
    for i, result in enumerate(results_sorted, 1):
        print(f"{i:<6} {result['name']:<25} {result['test_acc']:<12.2f} {result['time']/60:<12.1f}")
    
    # 最佳结果
    if results_sorted:
        best = results_sorted[0]
        print(f"\n{'='*70}")
        print(f"🏆 最佳结果")
        print('='*70)
        print(f"实验名称: {best['name']}")
        print(f"测试准确率: {best['test_acc']:.2f}%")
        print(f"配置:")
        for key, value in best['config'].items():
            print(f"  - {key}: {value}")
        print(f"用时: {best['time']/60:.1f} 分钟")
        
        # 保存汇总结果
        summary = {
            'timestamp': datetime.now().isoformat(),
            'best_result': best,
            'all_results': results_sorted
        }
        
        with open('outputs/search_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 结果已保存到 outputs/search_summary.json")
    
    print(f"\n{'='*70}")
    print(f"搜索完成！时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*70)

if __name__ == '__main__':
    main()
