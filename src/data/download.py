"""
BUSI 数据集下载脚本

使用 Kaggle API 下载 Breast Ultrasound Images Dataset
"""

import os
import subprocess
import zipfile
from pathlib import Path


def download_busi_dataset():
    """下载 BUSI 数据集"""
    
    # 设置路径
    project_root = Path(__file__).parent.parent.parent
    raw_data_dir = project_root / "data" / "raw"
    zip_path = raw_data_dir / "breast-ultrasound-images-dataset.zip"
    
    # 创建目录
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("BUSI 数据集下载")
    print("=" * 60)
    
    # 检查 Kaggle API
    print("\n[1/4] 检查 Kaggle API...")
    try:
        result = subprocess.run(
            ["kaggle", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise FileNotFoundError
        print("✓ Kaggle API 已安装")
    except FileNotFoundError:
        print("✗ 未安装 Kaggle API")
        print("\n请先安装 Kaggle API:")
        print("  pip install kaggle")
        print("\n并配置 API Token:")
        print("  1. 访问 https://www.kaggle.com/settings/account")
        print("  2. 点击 'Create New API Token'")
        print("  3. 将 kaggle.json 放到 ~/.kaggle/")
        return False
    
    # 下载数据集
    print("\n[2/4] 下载数据集...")
    if (raw_data_dir / "Dataset").exists():
        print("✓ 数据集已存在，跳过下载")
    else:
        try:
            subprocess.run([
                "kaggle", "datasets", "download",
                "-d", "aryashah2k/breast-ultrasound-images-dataset",
                "-p", str(raw_data_dir)
            ], check=True)
            print(f"✓ 下载完成: {zip_path}")
        except subprocess.CalledProcessError as e:
            print(f"✗ 下载失败: {e}")
            return False
    
    # 解压数据集
    print("\n[3/4] 解压数据集...")
    if (raw_data_dir / "Dataset").exists():
        print("✓ 数据集已解压，跳过")
    else:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(raw_data_dir)
            print("✓ 解压完成")
        except zipfile.BadZipFile as e:
            print(f"✗ 解压失败: {e}")
            return False
    
    # 统计数据
    print("\n[4/4] 统计数据...")
    dataset_path = raw_data_dir / "Dataset" / "BUSI"
    
    if not dataset_path.exists():
        # 尝试其他可能的路径
        for possible_path in [
            raw_data_dir / "BUSI",
            raw_data_dir / "breast-ultrasound-images-dataset",
        ]:
            if possible_path.exists():
                dataset_path = possible_path
                break
    
    if dataset_path.exists():
        categories = ["normal", "benign", "malignant"]
        total = 0
        
        print(f"\n数据集路径: {dataset_path}")
        print("\n类别统计:")
        for category in categories:
            category_path = dataset_path / category
            if category_path.exists():
                # 统计图像文件（排除mask）
                images = [f for f in os.listdir(category_path) 
                         if f.endswith(('.png', '.jpg', '.jpeg')) 
                         and 'mask' not in f.lower()]
                count = len(images)
                total += count
                print(f"  {category:12s}: {count:4d} 张")
        
        print(f"  {'总计':12s}: {total:4d} 张")
        print("\n✓ 数据集下载完成!")
        return True
    else:
        print(f"✗ 未找到数据集目录: {dataset_path}")
        print("\n目录内容:")
        for item in raw_data_dir.iterdir():
            print(f"  {item.name}")
        return False


def main():
    success = download_busi_dataset()
    
    if not success:
        print("\n" + "=" * 60)
        print("手动下载方式:")
        print("=" * 60)
        print("1. 访问 https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset")
        print("2. 下载数据集")
        print(f"3. 解压到: data/raw/")
        print("=" * 60)
    
    return success


if __name__ == "__main__":
    main()
