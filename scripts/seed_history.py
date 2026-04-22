#!/usr/bin/env python3
"""向本地运行的诊断系统发送若干预测请求，填充历史表用于截图。"""
import random
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/raw/Dataset_BUSI_with_GT"
API = "http://localhost:5000"

random.seed(20260422)


def pick_images(subdir: str, k: int) -> list[Path]:
    pool = [p for p in sorted((DATA / subdir).glob("*.png")) if "mask" not in p.stem]
    return random.sample(pool, k)


def call_predict_tta(image_path: Path) -> dict:
    with open(image_path, "rb") as f:
        r = requests.post(f"{API}/predict_tta", files={"file": (image_path.name, f, "image/png")}, timeout=60)
    r.raise_for_status()
    return r.json()


def main() -> None:
    total = 0
    for sub, k in [("benign", 4), ("malignant", 3), ("normal", 2)]:
        for p in pick_images(sub, k):
            try:
                res = call_predict_tta(p)
                if res.get("success"):
                    total += 1
                    print(f"  ✓ {p.name} -> {res['result']['predicted_class_cn']} ({res['result']['confidence']*100:.1f}%)")
            except Exception as e:
                print(f"  ✗ {p.name}: {e}")
    print(f"已注入 {total} 条历史记录")


if __name__ == "__main__":
    main()
