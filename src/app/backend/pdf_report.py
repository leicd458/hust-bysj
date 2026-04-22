#!/usr/bin/env python3
"""
PDF 报告生成模块
生成包含诊断结果、热力图、概率分布的专业 PDF 报告
"""

import os
from io import BytesIO
from datetime import datetime

# 尝试导入 reportlab，如果没有则提示安装
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # 注册中文字体 (macOS)
    _font_paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Songti.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
    ]
    _registered = False
    for _fp in _font_paths:
        if os.path.exists(_fp):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', _fp))
                _registered = True
                break
            except Exception:
                continue

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def generate_pdf_report(result: dict, image_base64: str = '',
                        gradcam_base64: str = '', output_path: str = None) -> bytes:
    """
    生成 PDF 诊断报告

    Args:
        result: 预测结果字典
        image_base64: 原始图像 base64（可选）
        gradcam_base64: Grad-CAM 图像 base64（可选）
        output_path: 输出文件路径（可选，为 None 时返回字节流）

    Returns:
        PDF 字节流或 None（如果 reportlab 未安装）
    """
    if not HAS_REPORTLAB:
        return None

    buffer = BytesIO() if output_path is None else None
    doc = SimpleDocTemplate(
        output_path or buffer,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleCN', parent=styles['Title'],
                                  fontName='ChineseFont' if _registered else 'Helvetica-Bold',
                                  fontSize=20, spaceAfter=10)
    heading_style = ParagraphStyle('HeadingCN', parent=styles['Heading1'],
                                    fontName='ChineseFont' if _registered else 'Helvetica-Bold',
                                    fontSize=14, spaceAfter=8, spaceBefore=15)
    normal_style = ParagraphStyle('NormalCN', parent=styles['Normal'],
                                   fontName='ChineseFont' if _registered else 'Helvetica',
                                   fontSize=11)

    elements = []

    # 标题
    elements.append(Paragraph("乳腺癌超声图像诊断报告", title_style))
    elements.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                               ParagraphStyle('Meta', fontSize=9, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))

    # 诊断结论
    cls_cn = result.get('predicted_class_cn', '-')
    cls_en = result.get('predicted_class', '')
    conf = result.get('confidence', 0) * 100
    tta_info = f" (TTA增强, {result.get('tta_augments', 7)}种增强)" if result.get('tta_augments') else " (标准推理)"
    elapsed = result.get('inference_time_ms', 0)

    elements.append(Paragraph("一、诊断结论", heading_style))

    conclusion_data = [
        ['项目', '结果'],
        ['诊断结论', cls_cn],
        ['英文分类', cls_en.upper()],
        ['置信度', f"{conf:.2f}%"],
        ['推理模式', f"{'TTA增强' if result.get('tta_augments') else '标准'}{tta_info}"],
        ['推理耗时', f"{elapsed:.0f} ms" if elapsed else '-'],
    ]

    tbl = Table(conclusion_data, colWidths=[4*cm, 10*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if _registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')]),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 0.5*cm))

    # 概率分布
    elements.append(Paragraph("二、各类别概率", heading_style))
    probs = result.get('probabilities', {})
    prob_data = [
        ['类别', '概率', '可视化']
    ]
    for name, label in [('benign', '良性'), ('malignant', '恶性'), ('normal', '正常')]:
        p = probs.get(name, 0) * 100
        bar_len = max(int(p / 100 * 6), 0.3)
        bar_str = '█' * int(bar_len) + '░' * (6 - int(bar_len))
        prob_data.append([label, f"{p:.2f}%", bar_str])

    prob_tbl = Table(prob_data, colWidths=[3*cm, 3*cm, 7*cm])
    prob_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if _registered else 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafaff')]),
    ]))
    elements.append(prob_tbl)
    elements.append(Spacer(1, 0.5*cm))

    # 图像对比
    has_images = image_base64 or gradcam_base64
    if has_images:
        elements.append(Paragraph("三、影像分析", heading_style))

        img_rows = []
        headers = []
        if image_base64 and gradcam_base64:
            try:
                orig_img = RLImage(BytesIO(_b64_to_bytes(image_base64)), width=7*cm, height=7*cm)
                cam_img = RLImage(BytesIO(_b64_to_bytes(gradcam_base64)), width=7*cm, height=7*cm)
                img_data = [['原始图像', '注意力热力图'], [orig_img, cam_img]]
                img_tbl = Table(img_data, colWidths=[8*cm, 8*cm])
                img_tbl.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont' if _registered else 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(img_tbl)
            except Exception:
                pass
        elif image_base64:
            try:
                orig_img = RLImage(BytesIO(_b64_to_bytes(image_base64)), width=12*cm, height=12*cm)
                elements.append(orig_img)
            except Exception:
                pass

        elements.append(Spacer(1, 0.5*cm))

    # 免责声明
    elements.append(Paragraph("四、免责声明", heading_style))
    disclaimer_text = """本报告由基于深度学习的乳腺癌超声图像自动诊断系统自动生成。
诊断结果仅供学术研究和辅助参考，不能替代专业医生的诊断。
如有疑问，请咨询专业医疗人员。本系统不对因使用本报告而产生的任何后果负责。"""
    elements.append(Paragraph(disclaimer_text, ParagraphStyle(
        'Disclaimer', parent=normal_style, fontSize=9,
        textColor=colors.HexColor('#888'), borderColor=colors.HexColor('#ffc107'),
        borderWidth=1, borderPadding=8, backColor=colors.HexColor('#fffef0')
    )))

    doc.build(elements)

    if output_path:
        return output_path
    return buffer.getvalue()


def _b64_to_bytes(b64_string: str) -> bytes:
    import base64
    if b64_string.startswith('data:'):
        b64_string = b64_string.split(',', 1)[1]
    return base64.b64decode(b64_string)


def check_dependencies():
    """检查 PDF 依赖是否已安装"""
    if not HAS_REPORTLAB:
        return False, "需要安装依赖: pip install reportlab"
    if not _registered:
        return False, "未找到中文字体（macOS PingFang/STHeiti）"
    return True, "OK"
