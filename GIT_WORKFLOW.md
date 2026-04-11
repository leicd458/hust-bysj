# Git 工作流管理指南

## 📋 分支命名规范

```
阶段编号-阶段名称/具体任务
```

示例：
- `01-kaiti/task-description` - 开题阶段的任务描述
- `02-zhongqi/reproduction-phase1` - 中期阶段的复现实验第一阶段

---

## 🔄 工作流程

### 阶段一：开题 (01-kaiti)

#### 任务 1: 任务描述
```bash
# 切换到该分支
git checkout 01-kaiti/task-description

# 进行工作...
git add .
git commit -m "描述提交内容"

# 完成后合并回 main
git checkout main
git merge --no-ff 01-kaiti/task-description
```

#### 任务 2: 学习资料收集
```bash
# 从 main 创建新分支
git checkout main
git checkout -b 01-kaiti/learning-materials

# 进行工作...
git add .
git commit -m "添加学习资料"

# 完成后合并
git checkout main
git merge --no-ff 01-kaiti/learning-materials
```

#### 任务 3: 任务相关资料收集
```bash
git checkout main
git checkout -b 01-kaiti/task-materials

# 进行工作...
git add .
git commit -m "添加任务资料"

# 完成后合并
git checkout main
git merge --no-ff 01-kaiti/task-materials
```

#### 任务 4: 开题报告撰写
```bash
git checkout main
git checkout -b 01-kaiti/report

# 进行工作...
git add .
git commit -m "完成开题报告"

# 完成后合并
git checkout main
git merge --no-ff 01-kaiti/report
```

---

### 阶段二：中期 (02-zhongqi)

#### 复现实验阶段
```bash
# Phase 1
git checkout main
git checkout -b 02-zhongqi/reproduction-phase1
# 工作完成后合并...

# Phase 2
git checkout main
git checkout -b 02-zhongqi/reproduction-phase2
# 工作完成后合并...

# Phase 3
git checkout main
git checkout -b 02-zhongqi/reproduction-phase3
# 工作完成后合并...

# Phase 4
git checkout main
git checkout -b 02-zhongqi/reproduction-phase4
# 工作完成后合并...
```

#### 正式实现代码
```bash
git checkout main
git checkout -b 02-zhongqi/implementation

# 进行工作...
git add .
git commit -m "实现核心功能"

# 完成后合并
git checkout main
git merge --no-ff 02-zhongqi/implementation
```

#### 中期报告
```bash
git checkout main
git checkout -b 02-zhongqi/report

# 进行工作...
git add .
git commit -m "完成中期报告"

# 完成后合并
git checkout main
git merge --no-ff 02-zhongqi/report
```

---

### 阶段三：答辩 (03-dabi)

#### 毕业论文撰写
```bash
git checkout main
git checkout -b 03-dabi/thesis

# 进行工作...
git add .
git commit -m "完成论文初稿"

# 完成后合并
git checkout main
git merge --no-ff 03-dabi/thesis
```

---

## 📝 提交信息规范

```
<类型>: <简短描述>

[可选的详细描述]
```

**类型说明：**
- `feat`: 新功能
- `docs`: 文档更新
- `experiment`: 实验相关
- `fix`: 修复问题
- `refactor`: 重构代码
- `test`: 测试相关

**示例：**
```
docs: 添加开题报告初稿

feat: 实现数据预处理模块

experiment: 完成 Phase 1 基线实验
```

---

## 🎯 工作原则

1. **一个任务一个分支** - 保持分支功能单一
2. **从 main 创建分支** - 确保基于最新稳定版本
3. **完成后及时合并** - 避免长期游离分支
4. **使用 --no-ff 合并** - 保留分支历史信息
5. **及时推送远程** - 防止本地代码丢失

---

## 🔧 常用命令

```bash
# 查看当前分支
git branch

# 查看所有分支（包括已合并）
git branch -a

# 查看分支历史图
git log --oneline --graph --all

# 删除已合并的本地分支
git branch -d <branch-name>

# 强制删除未合并的分支（谨慎使用）
git branch -D <branch-name>
```

---

## 📊 当前分支状态

```bash
# 查看当前分支
git branch
```

当前已有分支：
- `main` - 主分支
- `01-kaiti/task-description` - 开题-任务描述

---

*最后更新：2026年4月11日*
