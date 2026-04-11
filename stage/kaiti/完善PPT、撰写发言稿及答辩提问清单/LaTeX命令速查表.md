# LaTeX开题报告模板命令速查手册

本文档汇总了华中科技大学本科生毕业设计开题报告LaTeX模板中涉及的所有命令，按功能分类整理，帮助深度学习零基础的同学快速上手LaTeX写作。

## 1. 文档结构命令

这类命令定义了整个文档的框架和基本设置。

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\documentclass[选项]{类名}`|声明文档类型，是每个LaTeX文档的第一行|`\documentclass[supercite]{Hust-undergraduate-kaiti}`|
|`\begin{document}`|标记文档正文开始|`\begin{document}` ... `\end{document}`|
|`\end{document}`|标记文档正文结束|放在文档最后一行|
|`\maketitle`|生成标题页（包含题目、作者等信息）|在`\begin{document}`后使用|
|`\clearpage`|强制换页，确保之前内容输出完毕|`\maketitle \clearpage`|
|`\newpage`|开始新的一页|`\newpage \section{下一章}`|
|`\pagenumbering{格式}`|设置页码格式|`\pagenumbering{Roman}` 罗马数字，`\pagenumbering{arabic}` 阿拉伯数字|

## 2. 宏包引用命令

宏包相当于LaTeX的"插件"，提供额外功能。使用`\usepackage{包名}`引入。

|宏包名|作用说明|使用示例|
|:--|:--|:--|
|`zhnumber`|将数字转换为中文格式|章节编号显示为"一、二、三"|
|`tikz`|强大的绘图工具|绘制流程图、思维导图|
|`algorithm`|算法环境支持|创建算法伪代码框|
|`algpseudocode`|算法伪代码语法支持|编写If、For等伪代码|
|`amsmath`|数学公式增强|支持多行公式对齐|
|`amsthm`|定理环境支持|定义定理、引理样式|
|`amssymb`|数学符号扩展|更多数学符号如∀、∃|
|`graphicx`|图片插入支持|`\includegraphics`命令|
|`subcaption`|子图支持|一个figure中放多个子图|
|`longtable`|跨页长表格|表格太长自动分页|
|`xcolor`|颜色支持|文字着色、背景色|
|`listings`|代码高亮显示|插入程序代码|
|`hyperref`|超链接支持|创建可点击的链接|
|`pdfpages`|PDF页面嵌入|`\includepdf`插入外部PDF|
|`multirow`|表格单元格合并|跨多行的表格单元|
|`tcolorbox`|彩色文本框|创建带边框的提示框|
|`bm`|粗体数学符号|`\bm{x}`加粗向量x|

## 3. 标题与章节命令

这些命令用于设置文档标题信息和组织章节结构。

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\title{标题}`|设置论文标题|`\title{基于深度学习的乳腺癌超声图像自动诊断系统}`|
|`\author{作者}`|设置作者姓名|`\author{张三}`|
|`\school{学院}`|设置学院名称（自定义命令）|`\school{计算机科学与技术学院}`|
|`\classnum{班级}`|设置班级（自定义命令）|`\classnum{CS2101}`|
|`\stunum{学号}`|设置学号（自定义命令）|`\stunum{U202112345}`|
|`\instructor{导师}`|设置指导教师（自定义命令）|`\instructor{李教授}`|
|`\section{标题}`|一级章节标题|`\section{课题来源、目的及意义}`|
|`\subsection{标题}`|二级章节标题|`\subsection{课题来源}`|
|`\subsubsection{标题}`|三级章节标题|`\subsubsection{实验目的与要求}`|

## 4. 图表命令

用于插入图片和创建表格的命令。

### 4.1 图片相关

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\begin{figure}[位置]`|开始图片浮动体环境|`\begin{figure}[htb]` h当前位置,t页顶,b页底|
|`\centering`|图片居中|放在figure环境内|
|`\includegraphics[选项]{文件名}`|插入图片|`\includegraphics[scale=0.5]{image.png}`|
|`\caption{说明}`|图片标题说明|`\caption{系统架构图}`|
|`\label{标签}`|设置引用标签|`\label{fig:architecture}`|
|`\end{figure}`|结束图片环境|与`\begin{figure}`配对|

**图片插入完整示例：**
```latex
\begin{figure}[ht]
\centering
\includegraphics[scale=0.4]{system_architecture.png}
\caption{乳腺癌超声诊断系统架构}
\label{fig:system}
\end{figure}
```

### 4.2 表格相关

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\begin{table}[位置]`|开始表格浮动体|`\begin{table}[htbp]`|
|`\begin{tabular}{列格式}`|开始表格内容|`\begin{tabular}{|c|c|c|}` c居中,l左对齐,r右对齐|
|`\hline`|画水平线|表格行之间的分隔线|
|`&`|列分隔符|`列1 & 列2 & 列3`|
|`\\`|行结束符|每行末尾使用|
|`\multirow{行数}{宽度}{内容}`|合并多行|`\multirow{2}{*}{内容}`|
|`\multicolumn{列数}{格式}{内容}`|合并多列|`\multicolumn{3}{|c|}{标题}`|

**表格完整示例：**
```latex
\begin{table}[htbp]
\centering
\caption{模型性能对比}
\begin{tabular}{|c|c|c|c|}
\hline
模型 & 准确率 & AUC & F1-Score \\
\hline
ResNet18 & 92.3\% & 0.956 & 0.891 \\
\hline
VGG16 & 89.7\% & 0.932 & 0.867 \\
\hline
\end{tabular}
\end{table}
```

## 5. 数学公式命令

LaTeX最强大的功能之一，用于排版专业数学公式。

### 5.1 公式环境

|命令|作用说明|使用示例|
|:--|:--|:--|
|`$公式$`|行内公式|准确率为$A=\frac{TP+TN}{Total}$|
|`$$公式$$`|独立行公式（居中）|`$$E=mc^2$$`|
|`\begin{equation}`|带编号的公式环境|自动生成公式编号|
|`\begin{equation*}`|不带编号的公式|需要`amsmath`宏包|
|`\begin{split}`|多行公式对齐|用`&`标记对齐点，`\\`换行|

### 5.2 常用数学符号

|命令|显示效果|说明|
|:--|:--|:--|
|`\frac{分子}{分母}`|$\frac{a}{b}$|分数|
|`\sum_{下标}^{上标}`|$\sum_{i=1}^{n}$|求和符号|
|`\int_{下限}^{上限}`|$\int_0^1$|积分符号|
|`\sqrt{内容}`|$\sqrt{x}$|平方根|
|`\sqrt[n]{内容}`|$\sqrt[3]{x}$|n次根|
|`x^{上标}`|$x^2$|上标/幂|
|`x_{下标}`|$x_i$|下标|
|`\le` / `\ge`|$\le$ / $\ge$|小于等于/大于等于|
|`\times`|$\times$|乘号|
|`\cdot`|$\cdot$|点乘|
|`\infty`|$\infty$|无穷大|
|`\partial`|$\partial$|偏导数符号|
|`\nabla`|$\nabla$|梯度符号|
|`\bm{x}`|**x**|粗体向量（需bm宏包）|

**多行公式对齐示例：**
```latex
\begin{equation*}
\begin{split}
Loss &= -\frac{1}{N}\sum_{i=1}^{N}[y_i\log(\hat{y}_i) + (1-y_i)\log(1-\hat{y}_i)] \\
     &= CrossEntropy(y, \hat{y})
\end{split}
\end{equation*}
```

## 6. 算法伪代码命令

用于编写算法描述，需要`algorithm`和`algpseudocode`宏包。

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\begin{algorithm}[位置]`|开始算法环境|`\begin{algorithm}[htb]`|
|`\caption{标题}`|算法标题|`\caption{ResNet18分类算法}`|
|`\label{标签}`|算法引用标签|`\label{alg:resnet}`|
|`\begin{algorithmic}[行号]`|开始伪代码|`\begin{algorithmic}[1]` 显示行号|
|`\State`|普通语句|`\State 初始化参数`|
|`\If{条件}`|条件判断开始|`\If{epoch < max\_epoch}`|
|`\ElsIf{条件}`|否则如果|`\ElsIf{loss < threshold}`|
|`\Else`|否则|`\Else`|
|`\EndIf`|条件判断结束|与`\If`配对|
|`\For{条件}`|For循环开始|`\For{i = 1 to N}`|
|`\EndFor`|For循环结束|与`\For`配对|
|`\While{条件}`|While循环开始|`\While{not converged}`|
|`\EndWhile`|While循环结束|与`\While`配对|
|`\Return`|返回语句|`\Return model`|
|`\Input`|输入说明（自定义）|`\Input 训练数据集D`|
|`\Output`|输出说明（自定义）|`\Output 训练好的模型`|

**算法完整示例：**
```latex
\begin{algorithm}[htb]
\caption{ResNet18乳腺癌分类训练}
\label{alg:train}
\hspace*{0.02in} {\bf Input:} 训练集D，学习率lr，轮数epochs \\
\hspace*{0.02in} {\bf Output:} 训练好的模型M
\begin{algorithmic}[1]
\State 加载预训练ResNet18模型
\State 修改最后全连接层为3分类
\For{epoch = 1 to epochs}
    \For{每个batch (X, y) in D}
        \State 前向传播：$\hat{y} = M(X)$
        \State 计算损失：$L = CrossEntropy(y, \hat{y})$
        \State 反向传播：计算梯度$\nabla L$
        \State 更新参数：$\theta = \theta - lr \cdot \nabla L$
    \EndFor
\EndFor
\Return M
\end{algorithmic}
\end{algorithm}
```

## 7. 引用与参考文献命令

用于交叉引用和管理参考文献。

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\label{标签名}`|定义引用标签|`\label{fig:unet}`在图片后定义|
|`\ref{标签名}`|引用标签编号|`如图\ref{fig:unet}所示`|
|`\autoref{标签名}`|自动添加类型前缀的引用|`\autoref{fig:unet}`显示"图1"|
|`\cite{文献标识}`|引用参考文献|`深度学习已广泛应用\cite{ref1}`|
|`\href{URL}{显示文本}`|创建超链接|`\href{https://example.com}{点击这里}`|
|`\begin{thebibliography}{宽度}`|开始参考文献列表|`\begin{thebibliography}{99}`|
|`\bibitem{标识}`|定义一条参考文献|`\bibitem{ref1} He K, et al...`|
|`\end{thebibliography}`|结束参考文献列表|与`\begin`配对|

**参考文献示例：**
```latex
\begin{thebibliography}{99}
\bibitem{ref1} He K, Zhang X, Ren S, et al. Deep residual learning 
for image recognition[C]. CVPR, 2016: 770-778.
\bibitem{ref2} Ronneberger O, Fischer P, Brox T. U-Net: Convolutional 
networks for biomedical image segmentation[C]. MICCAI, 2015: 234-241.
\end{thebibliography}
```

## 8. 格式控制命令

控制文本外观、颜色和排版的命令。

### 8.1 字体样式

|命令|效果|使用示例|
|:--|:--|:--|
|`\textbf{文本}`|**粗体**|`\textbf{重要结论}`|
|`\textit{文本}`|*斜体*|`\textit{emphasis}`|
|`\underline{文本}`|下划线|`\underline{关键词}`|
|`\texttt{文本}`|`等宽字体`|`\texttt{代码变量}`|
|`\heiti`|黑体（中文）|`{\heiti 标题}`|
|`\kaishu`|楷书（中文）|`{\kaishu 正文}`|
|`\zihao{号}`|字号设置|`{\zihao{4} 四号字}`|

### 8.2 颜色设置

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\color{颜色名}`|设置文字颜色|`{\color{red} 红色文字}`|
|`\color[rgb]{r,g,b}`|RGB颜色|`{\color[rgb]{1,0,0} 红色}`|
|`\textcolor{颜色}{文本}`|着色文本|`\textcolor{blue}{蓝色文字}`|
|`\colorlet{新名}{定义}`|定义新颜色|`\colorlet{mycolor}{blue!50}`|

### 8.3 空间控制

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\quad`|1em宽度空格|`公式1 \quad 公式2`|
|`\qquad`|2em宽度空格|更大的空格|
|`\hspace{长度}`|水平空间|`\hspace{2cm}`|
|`\vspace{长度}`|垂直空间|`\vspace{1cm}`|
|`\\`|换行|段内强制换行|
|`\par`|分段|开始新段落|
|`\noindent`|取消段首缩进|`\noindent 本段不缩进`|

## 9. 模板自定义命令

模板中预定义的快捷命令，简化常用操作。

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\cfig{文件名}{宽度}{标题}`|快速插入居中图片|`\cfig{architecture}{0.8}{系统架构}`|
|`\sfig{文件名}{宽度}{标题}`|插入子图|用于subfigure环境|
|`\rfig{标签}`|引用图片|`如\rfig{architecture}所示`|
|`\ralg{标签}`|引用算法|`\ralg{train}展示了训练流程`|
|`\rthm{标签}`|引用定理|`根据\rthm{theorem1}`|
|`\reqn{标签}`|引用公式|`由\reqn{loss}可知`|
|`\rtbl{标签}`|引用表格|`\rtbl{comparison}对比了结果`|
|`\Input`|算法输入标注|`\Input 训练数据`|
|`\Output`|算法输出标注|`\Output 模型参数`|
|`\Break`|算法中断语句|`\Break` 显示break|
|`\Continue`|算法继续语句|`\Continue` 显示continue|
|`\LeftCom{注释}`|算法左侧注释|`\LeftCom{初始化阶段}`|

## 10. 特殊环境命令

用于创建定理、引理和彩色文本框等特殊内容块。

|命令|作用说明|使用示例|
|:--|:--|:--|
|`\newtheorem{环境名}{显示名}`|定义新定理环境|`\newtheorem{thm}{定理}[section]`|
|`\begin{thm}`|使用定理环境|`\begin{thm} 定理内容 \end{thm}`|
|`\begin{lem}`|引理环境|`\begin{lem} 引理内容 \end{lem}`|
|`\begin{abox}[标题]`|彩色文本框（模板自定义）|`\begin{abox}[注意] 内容 \end{abox}`|
|`\begin{comment}`|注释块（不输出）|`\begin{comment} 被注释内容 \end{comment}`|
|`\includepdf[pages=-]{文件}`|嵌入PDF页面|`\includepdf[pages=-]{评审表.pdf}`|

## 11. 常见问题速查

|问题|解决方案|
|:--|:--|
|中文显示乱码|确保使用XeLaTeX编译，而非PDFLaTeX|
|图片找不到|检查图片路径，建议放在tex文件同目录|
|公式编号不连续|检查是否混用`equation`和`equation*`|
|表格超出页面|使用`\resizebox{\textwidth}{!}{表格}`缩放|
|参考文献不显示|需要运行`bibtex`，然后再编译两次|
|超链接无法点击|添加`\usepackage{hyperref}`宏包|

## 12. 编译命令速查

在Mac M系列芯片终端中执行：

|步骤|命令|说明|
|:--|:--|:--|
|1|`xelatex 文件名.tex`|第一次编译，生成辅助文件|
|2|`bibtex 文件名.aux`|处理参考文献|
|3|`xelatex 文件名.tex`|第二次编译，生成引用|
|4|`xelatex 文件名.tex`|第三次编译，完成交叉引用|