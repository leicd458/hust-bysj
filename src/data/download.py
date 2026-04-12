"""
BUSI 数据集下载脚本
"""

import subprocess
import zipfile
from pathlib import Path


def main():
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # 下载
    subprocess.run([
        "kaggle", "datasets", "download",
        "-d", "aryashah2k/breast-ultrasound-images-dataset",
        "-p", str(raw_dir)
    ])
    
    # 解压
    zip_path = raw_dir / "breast-ultrasound-images-dataset.zip"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(raw_dir)
        print("✓ 数据集下载完成")


if __name__ == "__main__":
    main()
