# -*- coding: utf-8 -*-
import os
import io
from datetime import datetime
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image

# 1. 폰트 등록 (한글 깨짐 방지)
def register_fonts():
    font_paths = [
        ('/usr/share/fonts/truetype/nanum/NanumGothic.ttf', 'NanumGothic'),
        ('/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf', 'NanumGothicBold'),
    ]
    for path, name in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
            return name
    return 'Helvetica'

class PDFGenerator:
    def __init__(self, font_name='NanumGothic', font_size=12, line_height=18):
        self.font_name = register_fonts()
        self.styles = getSampleStyleSheet()
        self.normal_style = ParagraphStyle(
            'NormalKo',
            fontName=self.font_name,
            fontSize=font_size,
            leading=line_height,
            alignment=TA_LEFT
        )
        self.title_style = ParagraphStyle(
            'TitleKo',
            fontName=self.font_name,
            fontSize=font_size + 6,
            leading=line_height + 10,
            alignment=TA_CENTER,
            spaceAfter=20
        )

    def create_pdf(self, chapters_content, target_page_count=None):
        """
        내용(chapters_content)을 받아서 PDF를 만듭니다.
        target_page_count가 있으면 그 페이지 수를 무조건 맞춥니다.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # 내용을 한 장씩 추가
        for chapter in chapters_content:
            elements.append(Paragraph(chapter['title'], self.title_style))
            elements.append(Spacer(1, 10*mm))
            text = chapter['content'].replace('\n', '<br/>')
            elements.append(Paragraph(text, self.normal_style))
            elements.append(PageBreak()) # 챕터가 끝나면 다음 장으로!

        # [중요] 페이지 수 맞추기 대작전
        # 일단 지금까지 만든 걸로 몇 페이지인지 계산해봅니다.
        temp_buffer = io.BytesIO()
        temp_doc = SimpleDocTemplate(temp_buffer, pagesize=A4)
        temp_doc.build(elements)
        current_pages = temp_doc.page # 현재 페이지 수 확인

        # 모자란 페이지만큼 빈 종이를 더 넣습니다.
        if target_page_count and current_pages < target_page_count:
            needed = target_page_count - current_pages
            for _ in range(needed):
                elements.append(Paragraph(" ", self.normal_style)) # 투명 글자 하나 넣기
                elements.append(PageBreak()) # 다음 장으로 넘기기

        # 진짜 PDF 만들기
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

# (기본 GPT 호출 함수 등은 기존과 동일하게 유지하거나 필요시 수정)
