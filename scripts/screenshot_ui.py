#!/usr/bin/env python3
"""用 Playwright 截取评测系统界面图，保存到 stage/final/images/。

场景：
1. 首页（单张模式）- 空白状态
2. 首页（单张模式）- 已诊断一张图，含概率条/热力图
3. 首页（批量模式）- 已上传 6 张图的批量结果
4. 历史记录页
"""
import asyncio
import random
import time
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "stage/final/images"
OUT.mkdir(parents=True, exist_ok=True)

APP_URL = "http://localhost:5000"
DATA = ROOT / "data/raw/Dataset_BUSI_with_GT"


def pick(sub: str, n: int, seed: int) -> list[str]:
    r = random.Random(seed)
    pool = [str(p) for p in sorted((DATA / sub).glob("*.png")) if "mask" not in p.stem]
    return r.sample(pool, n)


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = await ctx.new_page()

        # ---- 1) 历史记录页（已有 9 条注入的记录） ----
        await page.goto(f"{APP_URL}/history", wait_until="networkidle")
        await page.wait_for_timeout(900)
        await page.screenshot(path=str(OUT / "ui_history.png"), full_page=True)
        print("✓ ui_history.png")

        # ---- 2) 首页 - 单张空白 ----
        await page.goto(APP_URL, wait_until="networkidle")
        await page.wait_for_timeout(600)
        await page.screenshot(path=str(OUT / "ui_single_empty.png"), full_page=True)
        print("✓ ui_single_empty.png")

        # ---- 3) 首页 - 单张已诊断 ----
        img = pick("malignant", 1, seed=11)[0]
        # 寻找 file input（accept image，非 multiple）
        single_input = page.locator('input[type="file"]:not([multiple])').first
        await single_input.set_input_files(img)
        # 等待上传预览渲染
        await page.wait_for_timeout(800)
        # 点击"开始分析"
        await page.get_by_role("button", name="开始分析").click()
        # 等待分析完成：等待 "诊断结果" 标题出现或 GradCAM 卡片
        try:
            await page.wait_for_selector("text=诊断结果", timeout=30000)
        except Exception:
            pass
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / "ui_single_result.png"), full_page=True)
        print("✓ ui_single_result.png")

        # ---- 4) 批量模式 ----
        # 切到批量 tab：模式切换按钮文本 "批量"
        await page.get_by_role("button", name="批量", exact=True).click()
        await page.wait_for_timeout(400)

        batch_imgs = []
        batch_imgs += pick("benign", 2, seed=21)
        batch_imgs += pick("malignant", 2, seed=22)
        batch_imgs += pick("normal", 2, seed=23)
        batch_input = page.locator('input[type="file"][multiple]').first
        await batch_input.set_input_files(batch_imgs)
        await page.wait_for_timeout(800)
        # 点击"批量分析"按钮
        await page.get_by_role("button", name="批量分析").click()
        try:
            await page.wait_for_selector("text=诊断结果", timeout=60000)
        except Exception:
            pass
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(OUT / "ui_batch_result.png"), full_page=True)
        print("✓ ui_batch_result.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
