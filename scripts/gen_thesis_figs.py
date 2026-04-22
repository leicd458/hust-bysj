#!/usr/bin/env python3
"""生成论文所需的图片：系统架构图 + Grad-CAM三类示例。"""

from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "stage/final/images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Arial Unicode MS", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ---------------------------------------------------------------------------
# 1) 系统架构图
# ---------------------------------------------------------------------------
def draw_system_architecture(save_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    def box(x, y, w, h, text, face="#E8F0FE", edge="#1A73E8", fs=11, lw=1.6):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.04,rounding_size=0.12",
            linewidth=lw,
            edgecolor=edge,
            facecolor=face,
        )
        ax.add_patch(patch)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=fs,
            wrap=True,
        )

    def arrow(x1, y1, x2, y2, color="#5F6368"):
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=14,
                linewidth=1.4,
                color=color,
            )
        )

    # 顶层：数据层
    box(0.3, 6.0, 2.8, 0.9, "BUSI 数据集\n(780 张超声图)", face="#FFF4E5", edge="#F29900")
    box(3.4, 6.0, 2.8, 0.9, "DAGAN 合成增强\n(训练阶段)", face="#FFF4E5", edge="#F29900")

    # 预处理
    box(0.3, 4.6, 5.9, 0.9, "数据预处理：Resize / ToTensor / ImageNet 标准化 / 在线增强", face="#E6F4EA", edge="#188038")

    # 数据划分
    box(0.3, 3.2, 1.9, 0.9, "训练集 (70%)", face="#E8EAED", edge="#5F6368", fs=10)
    box(2.3, 3.2, 1.9, 0.9, "验证集 (15%)", face="#E8EAED", edge="#5F6368", fs=10)
    box(4.3, 3.2, 1.9, 0.9, "测试集 (15%)", face="#E8EAED", edge="#5F6368", fs=10)

    # 核心：分类模型（训练）
    box(
        0.3,
        1.6,
        5.9,
        1.1,
        "EfficientNet-B0 迁移学习\nLabel Smoothing + WeightedSampler\nReduceLROnPlateau + 早停",
        face="#E8F0FE",
        edge="#1A73E8",
        fs=10,
    )

    # 推理旁路
    box(6.6, 6.0, 5.1, 0.9, "用户界面 (React + TypeScript)", face="#FCE8E6", edge="#D93025")
    box(6.6, 4.6, 5.1, 0.9, "REST API 服务 (Flask)", face="#FCE8E6", edge="#D93025")

    # 推理流程
    box(6.6, 3.2, 2.4, 1.0, "分类推理\n(TTA 4 视角融合)", face="#F3E8FD", edge="#8430CE", fs=10)
    box(9.2, 3.2, 2.5, 1.0, "Grad-CAM\n可解释性热力图", face="#F3E8FD", edge="#8430CE", fs=10)

    box(6.6, 1.6, 5.1, 1.0, "诊断结果输出：类别 + 置信度 + 热力图 + 历史记录", face="#FFF4E5", edge="#F29900", fs=10)

    # 底部：持久化
    box(0.3, 0.2, 11.4, 0.9, "部署与数据持久化：Docker 镜像  |  SQLite 历史记录  |  上传图像文件系统", face="#E8EAED", edge="#5F6368", fs=10)

    # 箭头：数据 → 预处理 → 划分 → 训练
    arrow(1.7, 6.0, 1.7, 5.5)
    arrow(4.8, 6.0, 4.8, 5.5)
    arrow(3.25, 4.6, 3.25, 4.1)
    arrow(1.25, 3.2, 1.25, 2.7)
    arrow(3.25, 3.2, 3.25, 2.7)
    arrow(5.25, 3.2, 5.25, 2.7)

    # 训练模型 → 推理
    arrow(6.2, 2.15, 6.9, 3.4)
    arrow(6.2, 2.15, 9.5, 3.4)

    # 推理 → 输出
    arrow(7.8, 3.2, 7.8, 2.6)
    arrow(10.4, 3.2, 10.4, 2.6)

    # UI ↔ API ↔ 推理
    arrow(9.15, 6.0, 9.15, 5.5)
    arrow(9.15, 4.6, 7.8, 4.2)
    arrow(9.15, 4.6, 10.4, 4.2)

    # 图例
    ax.text(0.3, 7.05, "数据层", fontsize=11, weight="bold", color="#F29900")
    ax.text(6.6, 7.05, "应用层", fontsize=11, weight="bold", color="#D93025")
    ax.text(0.3, 2.75, "模型训练", fontsize=11, weight="bold", color="#1A73E8")
    ax.text(6.6, 2.75, "在线推理", fontsize=11, weight="bold", color="#8430CE")

    plt.tight_layout()
    plt.savefig(save_path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✓ 已保存系统架构图: {save_path}")


# ---------------------------------------------------------------------------
# 2) Grad-CAM 三类紧凑示例
# ---------------------------------------------------------------------------
def generate_gradcam_examples(save_path: Path) -> None:
    """对良/恶/正常各取一张代表图，生成 3 行示例（原图/热力图/叠加）。"""
    import cv2
    import torch
    from PIL import Image
    from torchvision import transforms, models

    sys.path.insert(0, str(ROOT / "src"))
    from evaluation.gradcam import GradCAM  # type: ignore

    # 加载 Stage 5 EfficientNet-B0 模型
    ckpt_path = ROOT / "src/experiment/stage5/outputs/best_model.pth"
    if not ckpt_path.exists():
        print(f"[WARN] 未找到 Stage5 模型 {ckpt_path}，跳过 Grad-CAM 生成")
        return

    device = torch.device("cpu")
    model = models.efficientnet_b0(weights=None)
    # 替换分类头
    in_f = model.classifier[1].in_features
    model.classifier = torch.nn.Sequential(
        torch.nn.Dropout(p=0.5, inplace=True),
        torch.nn.Linear(in_f, 3),
    )
    state = torch.load(ckpt_path, map_location=device, weights_only=False)
    if isinstance(state, dict) and "model_state_dict" in state:
        state = state["model_state_dict"]
    model.load_state_dict(state, strict=False)
    model.to(device).eval()

    # 选择样例
    data_root = ROOT / "data/raw/Dataset_BUSI_with_GT"
    samples = [
        ("benign", "良性 (Benign)", 0),
        ("malignant", "恶性 (Malignant)", 1),
        ("normal", "正常 (Normal)", 2),
    ]
    picks = []
    for sub, cname, cidx in samples:
        # 找第一个不含 mask 的原图
        for p in sorted((data_root / sub).glob("*.png")):
            if "mask" not in p.stem:
                picks.append((p, cname, cidx))
                break

    tf = transforms.Compose(
        [
            transforms.Resize((300, 300)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    # EfficientNet-B0 最后一层为 features (Sequential)，GradCAM 用 features[-1]
    class _Wrapper(torch.nn.Module):
        def __init__(self, m):
            super().__init__()
            self.m = m
            self.layer4 = m.features[-1]  # 别名方便 gradcam 取

        def forward(self, x):
            return self.m(x)

    wrapped = _Wrapper(model)
    cam = GradCAM(wrapped, "layer4")

    fig, axes = plt.subplots(3, 3, figsize=(9, 9))
    for i, (img_path, cname, cidx) in enumerate(picks):
        img = Image.open(img_path).convert("RGB")
        inp = tf(img).unsqueeze(0).to(device)
        original, heat, overlay = cam.visualize(str(img_path), inp, target_class=cidx)

        axes[i, 0].imshow(original)
        axes[i, 0].set_title(f"{cname} — 原图", fontsize=11)
        axes[i, 0].axis("off")
        axes[i, 1].imshow(heat)
        axes[i, 1].set_title("Grad-CAM 热力图", fontsize=11)
        axes[i, 1].axis("off")
        axes[i, 2].imshow(overlay)
        axes[i, 2].set_title("叠加可视化", fontsize=11)
        axes[i, 2].axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✓ 已保存 Grad-CAM 三类示例: {save_path}")


if __name__ == "__main__":
    draw_system_architecture(IMG_DIR / "system_architecture.png")
    try:
        generate_gradcam_examples(IMG_DIR / "gradcam_examples.png")
    except Exception as e:
        print(f"[WARN] Grad-CAM 生成失败（将保留已有 gradcam_examples.png）：{e}")
