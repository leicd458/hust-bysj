##1. Mac M系列芯片LaTeX编译指南

本指南旨在帮助Mac M系列芯片用户顺利安装LaTeX环境，并编译华中科技大学的开题报告模板。

### 1.1. MacTeX安装方法

MacTeX是macOS上最完整的TeX发行版，包含了LaTeX所需的所有工具和宏包。

#### 1.1.1. 通过Homebrew安装（推荐）

Homebrew是macOS上优秀的包管理器，安装和管理软件更为便捷。

1.  **安装Homebrew**：
    如果尚未安装Homebrew，请打开终端（Terminal.app）并执行以下命令：
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
    按照提示完成安装，可能需要输入管理员密码。

2.  **安装MacTeX**：
    使用Homebrew Cask安装MacTeX。这个过程会下载并安装完整的MacTeX发行版，文件较大（约5-6GB），请确保网络连接良好。
    ```bash
    brew install --cask mactex
    ```
    安装完成后，你可以在 `/Applications/TeX` 目录下找到TeX相关的应用程序，如TeXShop、BibDesk等。同时，`xelatex`、`pdflatex` 等命令行工具也会被添加到系统路径中。

#### 1.1.2. 通过官网下载安装

1.  **下载安装包**：
    访问[TUG (TeX Users Group) 官网](https://www.tug.org/mactex/)，下载最新版本的MacTeX安装包（`.pkg`文件）。文件通常较大，请耐心等待下载完成。

2.  **运行安装程序**：
    双击下载的 `.pkg` 文件，按照安装向导的指示完成安装。通常选择默认设置即可。

### 1.2. 编译命令（xelatex编译中文文档）

对于包含中文内容的LaTeX文档，推荐使用 `xelatex` 编译器，因为它对Unicode和OpenType字体有更好的支持。

假设你的主LaTeX文件名为 `开题报告_完整版.tex`，并且你的模板文件（如 `Hust-undergraduate-kaiti.cls`）和参考文献文件（如 `Hust-undergraduate-kaiti.bib` 或你自定义的 `.bib` 文件）都在同一个目录下。

打开终端，进入你的LaTeX项目目录（例如，如果你的文件在 `/Users/yourname/Documents/GraduationProject`，则执行 `cd /Users/yourname/Documents/GraduationProject`）。

基本的编译命令如下：

```bash
xelatex 开题报告_完整版.tex
```

### 1.3. 完整编译流程（处理参考文献）

由于LaTeX文档中的交叉引用、目录和参考文献等内容需要多次编译才能正确生成，因此需要执行一个特定的编译序列。

对于包含参考文献的文档，标准的编译流程通常是：

1.  **第一次 `xelatex` 编译**：生成 `.aux` 文件，其中包含了交叉引用和参考文献引用信息。
    ```bash
    xelatex 开题报告_完整版.tex
    ```

2.  **`bibtex` 编译**：根据 `.aux` 文件中的引用信息和 `.bib` 参考文献数据库，生成 `.bbl` 文件，其中包含了格式化后的参考文献列表。
    ```bash
    bibtex 开题报告_完整版.aux
    ```
    **注意**：如果你的参考文献样式文件不是 `plain` 或 `unsrt` 等默认样式，而是学校提供的 `gbt7714-hust.bst` 这样的自定义样式，你需要确保该 `.bst` 文件与你的 `.tex` 文件在同一目录下，或者将其放置在TeX系统能够找到的路径中。

3.  **第二次 `xelatex` 编译**：将 `.bbl` 文件中的参考文献列表插入到文档中，并更新交叉引用。
    ```bash
    xelatex 开题报告_完整版.tex
    ```

4.  **第三次 `xelatex` 编译**：确保所有交叉引用（包括目录、图表目录、参考文献页码等）都已正确更新。
    ```bash
    xelatex 开题报告_完整版.tex
    ```

**总结为一键脚本（可选）**：
你可以在项目根目录下创建一个名为 `compile.sh` 的脚本文件，内容如下：
```bash
#!/bin/bash

FILENAME="开题报告_完整版"

echo "Compiling $FILENAME.tex..."

# 第一次编译
xelatex "$FILENAME.tex"

# 编译参考文献
bibtex "$FILENAME.aux"

# 第二次编译
xelatex "$FILENAME.tex"

# 第三次编译 (确保所有引用都正确)
xelatex "$FILENAME.tex"

echo "Compilation finished. Output: $FILENAME.pdf"
```
然后给脚本添加执行权限并运行：
```bash
chmod +x compile.sh
./compile.sh
```

### 1.4. 常见问题解决方案

1.  **`xelatex` 命令找不到**：
    *   **问题**：`zsh: command not found: xelatex`
    *   **原因**：MacTeX可能没有正确安装，或者其二进制文件路径没有添加到系统的 `PATH` 环境变量中。
    *   **解决方案**：
        *   重新安装MacTeX，确保安装过程没有错误。
        *   检查 `/usr/local/texlive/YYYY/bin/universal-darwin` (YYYY是年份，如2023) 是否存在 `xelatex`。如果存在，尝试手动将其添加到 `~/.zshrc` 或 `~/.bash_profile` 中：
            ```bash
            echo 'export PATH="/usr/local/texlive/2023/bin/universal-darwin:$PATH"' >> ~/.zshrc
            source ~/.zshrc
            ```
            （请根据你的MacTeX版本和shell类型调整路径和配置文件）

2.  **中文乱码或字体问题**：
    *   **问题**：编译后PDF中的中文显示为方块或乱码。
    *   **原因**：通常是字体配置问题，或者没有使用 `xelatex` 编译。
    *   **解决方案**：
        *   确保你的 `.tex` 文件开头使用了 `\usepackage{ctex}` 或 `\usepackage{fontspec}` 并正确配置了中文字体（例如 `\setCJKmainfont{SimSun}`）。
        *   **务必使用 `xelatex` 进行编译**。

3.  **参考文献不显示或显示问号 `[?]`**：
    *   **问题**：PDF中参考文献部分为空，或者引用处显示 `[?]`。
    *   **原因**：`bibtex` 没有正确运行，或者 `.bib` 文件有错误，或者编译次数不足。
    *   **解决方案**：
        *   检查 `.bib` 文件格式是否正确，所有条目是否完整。
        *   确保 `\bibliography{your_bib_file_name}` 中的文件名与你的 `.bib` 文件名一致（不含 `.bib` 后缀）。
        *   **严格按照 1.3 节的完整编译流程执行**，特别是 `bibtex` 步骤不能省略。
        *   检查 `.blg` 文件（BibTeX日志文件），它会报告 `bibtex` 运行时的错误。

4.  **图片无法显示**：
    *   **问题**：PDF中图片位置空白或显示错误。
    *   **原因**：图片路径错误，或者图片格式不支持。
    *   **解决方案**：
        *   确保 `\includegraphics` 中的图片路径正确，推荐使用相对路径或绝对路径。例如，如果图片在 `images` 文件夹下，可以使用 `\includegraphics{images/my_image.png}`。
        *   确保图片格式是 `xelatex` 支持的格式，如 `.png`, `.jpg`, `.pdf`。

### 1.5. VS Code + LaTeX Workshop配置方法

VS Code配合LaTeX Workshop插件是Mac上编写LaTeX文档的强大组合。

1.  **安装VS Code**：
    从[VS Code官网](https://code.visualstudio.com/)下载并安装。

2.  **安装LaTeX Workshop插件**：
    *   打开VS Code。
    *   点击左侧活动栏的“Extensions”（或按 `Cmd+Shift+X`）。
    *   搜索 `LaTeX Workshop` 并安装。

3.  **配置LaTeX Workshop**：
    安装插件后，通常会自动检测到MacTeX的安装。如果需要自定义配置，可以：
    *   打开VS Code设置（`Cmd+,`）。
    *   搜索 `latex-workshop.latex.toolchain`。
    *   确保 `latex-workshop.latex.recipes` 中包含 `xelatex` 的编译链。默认情况下，通常会有类似如下的配置：
        ```json
        "latex-workshop.latex.recipes": [
            {
                "name": "xelatex -> bibtex -> xelatex*2",
                "tools": [
                    "xelatex",
                    "bibtex",
                    "xelatex",
                    "xelatex"
                ]
            },
            // ... 其他编译链
        ],
        "latex-workshop.latex.tools": [
            {
                "name": "xelatex",
                "command": "xelatex",
                "args": [
                    "-synctex=1",
                    "-interaction=nonstopmode",
                    "-file-line-error",
                    "%DOC%"
                ]
            },
            {
                "name": "bibtex",
                "command": "bibtex",
                "args": [
                    "%DOCFILE%"
                ]
            },
            // ... 其他工具
        ]
        ```
    *   你可以在VS Code中打开你的 `.tex` 文件，然后点击左侧活动栏的“TeX”图标，在“Build LaTeX project”下选择 `xelatex -> bibtex -> xelatex*2` 即可一键编译。

### 1.6. 学校模板文件准备说明

为了确保学校的LaTeX模板能够正确编译，你需要将所有模板文件放置在正确的位置。

1.  **获取模板文件**：
    确保你拥有华中科技大学开题报告模板的所有文件，通常包括：
    *   `Hust-undergraduate-kaiti.cls` (类文件)
    *   `gbt7714-hust.bst` (参考文献样式文件)
    *   `开题报告_完整版.tex` (你的主文档)
    *   可能还有 `images` 文件夹（存放图片）或其他辅助文件。

2.  **文件组织**：
    **最简单且推荐的方式**是，将所有这些文件（包括 `.cls`, `.bst`, `.tex` 文件以及 `images` 文件夹等）都放在你的LaTeX项目根目录下。这样，编译器在查找这些文件时就能直接找到。

3.  **填写个人信息**：
    在 `开题报告_完整版.tex` 文件的导言区，务必填写你的个人信息：
    ```latex
    \title{基于深度学习的乳腺癌超声图像自动诊断系统设计与实现}
    \school{计算机科学与技术学院}
    \author{你的姓名}  % 请填写你的姓名
    \classnum{你的班级}  % 请填写你的班级
    \stunum{你的学号}  % 请填写你的学号
    \instructor{指导教师姓名}  % 请填写指导教师姓名
    ```
    请将 `你的姓名`、`你的班级`、`你的学号`、`指导教师姓名` 替换为你的实际信息。

遵循以上步骤，你就可以在Mac M系列芯片上顺利完成LaTeX开题报告的编译工作。