# 毕业答辩 PPT 资料包

> **课题**：基于深度学习的乳腺癌超声图像自动诊断系统
> **答辩人**：雷传栋 | CS2202 | U202211999
> **指导教师**：陆枫
> **拟定答辩日期**：2026年6月（最终答辩）

本文件夹为交付给「PPT 生产专家」的完整资料集。**不包含最终 .pptx 文件**，只提供结构化的内容说明、演讲稿、素材与视觉规范，供专家据此生成答辩 PPT。

---

## 目录结构

```
ppt/
├── README.md                      # 本文件：资料包导览 + 交付说明
├── PPT_BRIEF.md                   # 给 PPT 专家的总体简报（风格/规范/边界）
├── SLIDE_DECK_SPEC.md             # 逐页 PPT 内容说明（核心文档）
├── SPEECH_SCRIPT.md               # 答辩发言稿（配合 SLIDE_DECK_SPEC 使用）
├── QA_PREP.md                     # 预测答辩问题清单与参考回答
├── KEY_FACTS.md                   # 关键数据/结论速查卡（答辩兜底）
└── assets/
    └── images/                    # 可直接嵌入 PPT 的高清图片
        ├── system_architecture.png    # 系统总体架构图
        ├── confusion_matrix.png       # Stage 5 混淆矩阵
        ├── roc_curves.png             # Stage 5 ROC 曲线
        ├── metrics_comparison.png     # 五阶段指标对比
        ├── gradcam_examples.png       # Grad-CAM 热力图示例
        ├── ui_single_empty.png        # Web 单张分析（空态）
        ├── ui_single_result.png       # Web 单张分析（结果态）
        ├── ui_batch_result.png        # Web 批量分析
        ├── ui_history.png             # Web 历史记录
        └── fig1.png                   # BUSI 数据集样例
```

---

## 给 PPT 专家的交付清单

请按以下顺序阅读与使用：

1. **`PPT_BRIEF.md`**：一页看懂「要做什么」——总体定位、风格、约束、交付物。
2. **`SLIDE_DECK_SPEC.md`**：**最重要**。每一页 PPT 的标题、布局建议、核心内容、需要插入的图片文件名、给答辩人提示的备注都在这里。
3. **`SPEECH_SCRIPT.md`**：每页对应的口头讲稿，用于判断每页的信息密度是否合适。
4. **`QA_PREP.md`** 和 **`KEY_FACTS.md`**：答辩辅助材料，PPT 专家可忽略内容本身，但可据此判断核心卖点。
5. **`assets/images/`**：全部图片素材已备好，PPT 中直接按文件名嵌入即可，**无需再自行生成图表**。

---

## 硬性约束

- **总页数**：正文 20--24 页（含封面与致谢），答辩汇报时长控制在 **12--15 分钟**。
- **语言**：简体中文。
- **不允许**加入任何政治人物、政治机构、敏感政治话题相关内容。
- **图片版权**：`assets/images/` 中的图全部来自本课题实验，可放心使用。
- **严禁**在 PPT 中出现「AI 生成」「本项目由 AI 协助完成」等字样。

---

## 快速开始（供 PPT 专家）

1. 选用一套简洁的学术风模板（推荐冷色调：深蓝/墨绿 + 白灰）。
2. 按 `SLIDE_DECK_SPEC.md` 逐页落稿，插入 `assets/images/` 中的图片。
3. 将页码对齐 `SPEECH_SCRIPT.md` 的段落，保证「讲到哪页就能看到什么」。
4. 封底使用致谢页，标明指导教师陆枫老师。
