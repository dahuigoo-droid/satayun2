# -*- coding: utf-8 -*-
"""
📄 PDF 생성 모듈 (최적화 버전)
- 이미지 캐싱
- OpenAI 클라이언트 재사용
- 마크다운 제거
"""

import os
import io
import re
import hashlib
from functools import lru_cache
from datetime import datetime
from typing import Optional, Dict, List, Callable

import requests
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame

# ============================================
# 폰트 등록 (한 번만)
# ============================================

FONT_MAP = {
    'NanumGothic': '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
    'NanumMyeongjo': '/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf',
    'NanumBarunGothic': '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
}

_fonts_registered = False
DEFAULT_FONT = 'Helvetica'

def _register_fonts():
    """폰트 등록 (최초 1회만)"""
    global _fonts_registered, DEFAULT_FONT
    if _fonts_registered:
        return DEFAULT_FONT
    
    for name, path in FONT_MAP.items():
        try:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(name, path))
                DEFAULT_FONT = name
        except:
            pass
    
    _fonts_registered = True
    return DEFAULT_FONT

_register_fonts()


# ============================================
# 이미지 캐싱 (LRU)
# ============================================

@lru_cache(maxsize=50)
def _download_image(url: str) -> Optional[bytes]:
    """URL에서 이미지 다운로드 (캐싱)"""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.content
    except:
        pass
    return None


def load_image_for_pdf(image_path: str) -> Optional[io.BytesIO]:
    """이미지 로드 - URL/로컬 모두 지원, 캐싱 적용"""
    if not image_path:
        return None
    
    # URL인 경우
    if image_path.startswith("http"):
        content = _download_image(image_path)
        if content:
            return io.BytesIO(content)
        return None
    
    # 로컬 파일인 경우
    if os.path.exists(image_path):
        return image_path
    
    return None


# ============================================
# 텍스트 처리
# ============================================

# 정규식 사전 컴파일 (성능 최적화)
_MD_PATTERNS = [
    (re.compile(r'^#{1,6}\s*', re.MULTILINE), ''),
    (re.compile(r'\*\*([^*]+)\*\*'), r'\1'),
    (re.compile(r'\*([^*]+)\*'), r'\1'),
    (re.compile(r'__([^_]+)__'), r'\1'),
    (re.compile(r'_([^_]+)_'), r'\1'),
    (re.compile(r'`([^`]+)`'), r'\1'),
    (re.compile(r'\[([^\]]+)\]\([^)]+\)'), r'\1'),
    (re.compile(r'^\s*[-*+]\s+', re.MULTILINE), '• '),
    (re.compile(r'^\s*\d+\.\s+', re.MULTILINE), ''),
    (re.compile(r'\n{3,}'), '\n\n'),
]

def clean_markdown(text: str) -> str:
    """마크다운 문법 제거 (최적화)"""
    if not text:
        return ""
    for pattern, repl in _MD_PATTERNS:
        text = pattern.sub(repl, text)
    return text.strip()


def wrap_text_korean(text: str, max_chars: int) -> List[str]:
    """한글 텍스트 줄바꿈"""
    lines = []
    for paragraph in text.split('\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append('')
            continue
        
        while len(paragraph) > max_chars:
            cut = max_chars
            for i in range(max_chars, max(0, max_chars - 10), -1):
                if i < len(paragraph) and paragraph[i] in ' .,!?。，！？':
                    cut = i + 1
                    break
            lines.append(paragraph[:cut].strip())
            paragraph = paragraph[cut:].strip()
        
        if paragraph:
            lines.append(paragraph)
    return lines


# ============================================
# OpenAI 클라이언트 캐싱
# ============================================

_openai_clients: Dict[str, OpenAI] = {}

def _get_openai_client(api_key: str) -> OpenAI:
    """OpenAI 클라이언트 재사용"""
    if api_key not in _openai_clients:
        _openai_clients[api_key] = OpenAI(api_key=api_key)
    return _openai_clients[api_key]


# ============================================
# GPT 콘텐츠 생성
# ============================================

def calculate_chars_per_page(font_size: int, line_height: int, margin_top: int, 
                             margin_bottom: int, margin_left: int, margin_right: int) -> int:
    """페이지당 글자 수 계산"""
    # A4: 210mm x 297mm
    page_width_mm = 210
    page_height_mm = 297
    
    usable_width_mm = page_width_mm - margin_left - margin_right
    usable_height_mm = page_height_mm - margin_top - margin_bottom
    
    # 한글 기준: 1pt ≈ 0.35mm
    char_width_mm = font_size * 0.35
    line_height_mm = font_size * 0.35 * (line_height / 100)
    
    chars_per_line = int(usable_width_mm / char_width_mm)
    lines_per_page = int(usable_height_mm / line_height_mm)
    
    # 여유분 고려 (80%)
    chars_per_page = int(chars_per_line * lines_per_page * 0.8)
    return max(chars_per_page, 300)


def generate_chapter_content(
    api_key: str,
    customer_info: dict,
    chapter_title: str,
    guideline: str,
    service_type: str,
    target_chars: int = 1000,  # 목표 글자 수 추가
    model: str = "gpt-4o-mini"
) -> str:
    """단일 챕터 콘텐츠 생성 - 목표 글자 수 반영"""
    try:
        client = _get_openai_client(api_key)
        customer_str = "\n".join([f"- {k}: {v}" for k, v in customer_info.items() if v])
        
        prompt = f"""[서비스 유형]
{service_type}

[고객 정보]
{customer_str}

[작성 지침]
{guideline}

[현재 작성할 챕터]
{chapter_title}

[중요 - 글자 수 요구사항]
이 챕터는 반드시 {target_chars}자 이상 작성해주세요.
충분히 상세하고 풍부한 내용으로 작성해야 합니다.

위 챕터를 상세하게 작성해주세요.
- 전문적이면서도 이해하기 쉽게
- 구체적인 조언과 예시 포함
- 따뜻하고 희망적인 톤 유지
- 마크다운 문법 사용하지 말고 일반 텍스트로 작성
- 챕터 제목은 다시 쓰지 마세요
- 최소 {target_chars}자 이상 필수!"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"당신은 전문적이고 따뜻한 {service_type} 전문가입니다. 마크다운 없이 일반 텍스트로만 답변하세요. 요청된 글자 수를 반드시 충족해야 합니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,  # 더 긴 응답 허용
            temperature=0.7
        )
        
        return clean_markdown(response.choices[0].message.content)
    
    except Exception as e:
        return f"[오류: {str(e)}]"


def generate_full_content(
    api_key: str,
    customer_info: dict,
    chapters: list,
    guideline: str,
    service_type: str,
    target_pages: int = 30,
    font_size: int = 12,
    line_height: int = 180,
    margin_top: int = 25,
    margin_bottom: int = 25,
    margin_left: int = 25,
    margin_right: int = 25,
    model: str = "gpt-4o-mini",
    progress_callback: Callable = None
) -> List[Dict]:
    """전체 콘텐츠 생성 - 목표 페이지 반영"""
    
    # 페이지당 글자 수 계산
    chars_per_page = calculate_chars_per_page(
        font_size, line_height, margin_top, margin_bottom, margin_left, margin_right
    )
    
    # 총 필요 글자 수
    total_chars_needed = target_pages * chars_per_page
    
    # 목차당 필요 글자 수 (표지, 목차, 안내 페이지 제외하고 계산)
    content_pages = max(target_pages - 3, target_pages * 0.9)  # 본문 페이지
    chars_per_chapter = int((content_pages * chars_per_page) / len(chapters))
    
    print(f"[PDF설정] 목표: {target_pages}페이지, 페이지당 {chars_per_page}자")
    print(f"[PDF설정] 목차 {len(chapters)}개, 목차당 {chars_per_chapter}자 목표")
    
    full_content = []
    total = len(chapters)
    
    for i, chapter in enumerate(chapters):
        if progress_callback:
            progress_callback((i + 1) / total, f"'{chapter}' 작성 중...")
        
        content = generate_chapter_content(
            api_key, customer_info, chapter, guideline, service_type,
            target_chars=chars_per_chapter,  # 목표 글자 수 전달
            model=model
        )
        
        actual_chars = len(content)
        print(f"[챕터 {i+1}] '{chapter}': {actual_chars}자 생성 (목표: {chars_per_chapter}자)")
        
        full_content.append({"title": chapter, "content": content})
    
    return full_content


# ============================================
# PDF 생성
# ============================================

class PDFGenerator:
    """PDF 생성기 - 양쪽 정렬"""
    
    def __init__(
        self,
        font_name: str = "NanumGothic",
        font_size_title: int = 24,
        font_size_subtitle: int = 16,
        font_size_body: int = 12,
        line_height: int = 180,
        letter_spacing: int = 0,   # 미사용 (호환성 유지)
        char_width: int = 100,     # 미사용 (호환성 유지)
        margin_top: int = 25,
        margin_bottom: int = 25,
        margin_left: int = 25,
        margin_right: int = 25,
        target_pages: int = 30
    ):
        self.font_name = font_name if font_name in FONT_MAP else DEFAULT_FONT
        self.font_size_title = font_size_title
        self.font_size_subtitle = font_size_subtitle
        self.font_size_body = font_size_body
        
        # 행간 계산
        self.line_height_ratio = line_height / 100.0
        self.line_height = font_size_body * self.line_height_ratio
        
        # 여백 (mm → pt) - 1mm = 2.834645669 pt
        self.margin_top = margin_top * mm
        self.margin_bottom = margin_bottom * mm
        self.margin_left = margin_left * mm
        self.margin_right = margin_right * mm
        
        # 페이지 크기 (A4: 595.27 x 841.89 pt)
        self.width, self.height = A4
        self.usable_width = self.width - self.margin_left - self.margin_right
        self.usable_height = self.height - self.margin_top - self.margin_bottom
        
        # 디버깅 로그
        print(f"[PDF] 페이지: {self.width:.1f} x {self.height:.1f} pt")
        print(f"[PDF] 여백(pt): 상{self.margin_top:.1f} 하{self.margin_bottom:.1f} 좌{self.margin_left:.1f} 우{self.margin_right:.1f}")
        print(f"[PDF] 여백(mm): 상{margin_top} 하{margin_bottom} 좌{margin_left} 우{margin_right}")
        print(f"[PDF] 사용영역: {self.usable_width:.1f} x {self.usable_height:.1f} pt")
        print(f"[PDF] 본문: {font_size_body}pt, 행간: {self.line_height:.1f}pt ({line_height}%)")
    
    def create_pdf(
        self,
        chapters_content: list,
        customer_name: str,
        service_type: str,
        cover_image: str = None,
        intro_image: str = None,
        background_image: str = None,
        info_image: str = None,
        customer_name2: str = None
    ) -> bytes:
        """PDF 생성"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # 이미지 로드 (캐싱됨)
        cover_data = load_image_for_pdf(cover_image)
        intro_data = load_image_for_pdf(intro_image)
        bg_data = load_image_for_pdf(background_image)
        info_data = load_image_for_pdf(info_image)
        
        # 1. 표지
        self._draw_cover(c, cover_data, customer_name, service_type, customer_name2)
        
        # 2. 소개 (있으면)
        if intro_data:
            self._draw_full_image(c, intro_data)
        
        # 3. 목차 (내지 배경 적용)
        self._draw_toc(c, chapters_content, bg_data)
        
        # 4. 본문
        for chapter in chapters_content:
            self._draw_chapter(c, chapter, bg_data)
        
        # 5. 안내 (있으면)
        if info_data:
            self._draw_full_image(c, info_data)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _draw_image(self, c, img_data, x, y, w, h):
        """이미지 그리기 헬퍼"""
        if img_data:
            try:
                if hasattr(img_data, 'seek'):
                    img_data.seek(0)
                c.drawImage(img_data, x, y, width=w, height=h, preserveAspectRatio=False, mask='auto')
            except:
                pass
    
    def _draw_cover(self, c, cover_data, name, service_type, name2=None):
        """표지 페이지"""
        self._draw_image(c, cover_data, 0, 0, self.width, self.height)
        
        c.setFont(self.font_name, self.font_size_title + 4)
        name_text = f"{name}  ♥  {name2}" if name2 else f"{name} 님"
        tw = c.stringWidth(name_text, self.font_name, self.font_size_title + 4)
        c.drawString((self.width - tw) / 2, self.height * 0.25, name_text)
        
        c.setFont(self.font_name, self.font_size_subtitle)
        tw = c.stringWidth(service_type, self.font_name, self.font_size_subtitle)
        c.drawString((self.width - tw) / 2, self.height * 0.20, service_type)
        
        c.setFont(self.font_name, self.font_size_body)
        date_text = datetime.now().strftime("%Y년 %m월 %d일")
        tw = c.stringWidth(date_text, self.font_name, self.font_size_body)
        c.drawString((self.width - tw) / 2, self.height * 0.15, date_text)
        
        c.showPage()
    
    def _draw_full_image(self, c, img_data):
        """전체 이미지 페이지"""
        self._draw_image(c, img_data, 0, 0, self.width, self.height)
        c.showPage()
    
    def _draw_toc(self, c, chapters, bg_data=None):
        """목차 페이지 - 내지 배경 적용"""
        # 내지 배경 이미지
        self._draw_image(c, bg_data, 0, 0, self.width, self.height)
        
        c.setFont(self.font_name, self.font_size_title)
        c.drawString(self.margin_left, self.height - self.margin_top, "목 차")
        
        c.setFont(self.font_name, self.font_size_subtitle)
        y = self.height - self.margin_top - 60
        
        for i, ch in enumerate(chapters):
            c.drawString(self.margin_left + 10, y, f"{i+1}. {ch['title']}")
            y -= 35
            if y < self.margin_bottom:
                c.showPage()
                # 다음 페이지에도 배경
                self._draw_image(c, bg_data, 0, 0, self.width, self.height)
                c.setFont(self.font_name, self.font_size_subtitle)
                y = self.height - self.margin_top
        
        c.showPage()
    
    def _draw_chapter(self, c, chapter, bg_data):
        """챕터 페이지들 - 양쪽 정렬"""
        title = chapter['title']
        content = clean_markdown(chapter['content'])
        
        # 양쪽 정렬 스타일
        body_style = ParagraphStyle(
            'BodyText',
            fontName=self.font_name,
            fontSize=self.font_size_body,
            leading=self.line_height,  # 행간
            alignment=TA_JUSTIFY,      # 양쪽 정렬
            firstLineIndent=0,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=self.line_height * 0.5,
            wordWrap='CJK',            # 한글 줄바꿈
        )
        
        # 첫 페이지 - 배경 + 제목
        self._draw_image(c, bg_data, 0, 0, self.width, self.height)
        c.setFont(self.font_name, self.font_size_subtitle)
        c.drawString(self.margin_left, self.height - self.margin_top, f"■ {title}")
        
        # 본문 영역 계산
        frame_x = self.margin_left
        frame_y = self.margin_bottom
        frame_w = self.usable_width
        frame_h = self.height - self.margin_top - self.margin_bottom - 50  # 제목 공간
        
        # 문단 분리 후 Paragraph 객체 생성
        paragraphs = []
        for para in content.split('\n\n'):
            para = para.strip()
            if para:
                # HTML 특수문자 이스케이프
                para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                paragraphs.append(Paragraph(para, body_style))
        
        # 첫 페이지 Frame
        current_y = self.height - self.margin_top - 50
        frame = Frame(frame_x, frame_y, frame_w, current_y - frame_y, 
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        
        # 남은 문단들
        remaining = frame.addFromList(paragraphs, c)
        
        # 넘치는 문단은 다음 페이지로
        while remaining:
            c.showPage()
            self._draw_image(c, bg_data, 0, 0, self.width, self.height)
            
            # 새 페이지 Frame (제목 없이 전체 영역)
            frame = Frame(frame_x, frame_y, frame_w, 
                         self.height - self.margin_top - self.margin_bottom,
                         leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
            remaining = frame.addFromList(remaining, c)
        
        c.showPage()


# ============================================
# 합본 PDF (호환성)
# ============================================

def generate_combined_pdf(
    api_key: str,
    customer_info: dict,
    services_data: list,
    font_settings: dict,
    progress_callback=None
) -> bytes:
    """여러 서비스 합본 PDF"""
    all_content = []
    total = sum(len(s['chapters']) for s in services_data)
    current = 0
    
    for svc in services_data:
        for ch in svc['chapters']:
            current += 1
            if progress_callback:
                progress_callback(current / total, f"[{svc['service_name']}] '{ch}' 작성 중...")
            
            content = generate_chapter_content(
                api_key, customer_info,
                f"{svc['service_name']} - {ch}",
                svc.get('guideline', ''),
                svc['service_name']
            )
            all_content.append({"title": f"{svc['service_name']} - {ch}", "content": content})
    
    pdf_gen = PDFGenerator(**font_settings)
    first = services_data[0] if services_data else {}
    
    return pdf_gen.create_pdf(
        chapters_content=all_content,
        customer_name=customer_info.get('이름', '고객'),
        service_type=" + ".join([s['service_name'] for s in services_data]),
        cover_image=first.get('cover_image'),
        intro_image=first.get('intro_image'),
        background_image=first.get('background_image'),
        info_image=first.get('info_image'),
        customer_name2=customer_info.get('이름2')
    )
