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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

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

def generate_chapter_content(
    api_key: str,
    customer_info: dict,
    chapter_title: str,
    guideline: str,
    service_type: str,
    model: str = "gpt-4o-mini"
) -> str:
    """단일 챕터 콘텐츠 생성"""
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

위 챕터를 상세하게 작성해주세요.
- 전문적이면서도 이해하기 쉽게
- 구체적인 조언과 예시 포함
- 따뜻하고 희망적인 톤 유지
- 최소 500자 이상 작성
- 마크다운 문법 사용하지 말고 일반 텍스트로 작성
- 챕터 제목은 다시 쓰지 마세요"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"당신은 전문적이고 따뜻한 {service_type} 전문가입니다. 마크다운 없이 일반 텍스트로만 답변하세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
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
    model: str = "gpt-4o-mini",
    progress_callback: Callable = None
) -> List[Dict]:
    """전체 콘텐츠 생성"""
    full_content = []
    total = len(chapters)
    
    for i, chapter in enumerate(chapters):
        if progress_callback:
            progress_callback((i + 1) / total, f"'{chapter}' 작성 중...")
        
        content = generate_chapter_content(
            api_key, customer_info, chapter, guideline, service_type, model
        )
        full_content.append({"title": chapter, "content": content})
    
    return full_content


# ============================================
# PDF 생성
# ============================================

class PDFGenerator:
    """PDF 생성기"""
    
    def __init__(
        self,
        font_name: str = "NanumGothic",
        font_size_title: int = 24,
        font_size_subtitle: int = 16,
        font_size_body: int = 12,
        line_height: int = 180,
        letter_spacing: int = 0,
        char_width: int = 100,
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
        
        self.line_height_ratio = line_height / 100.0
        self.line_height = font_size_body * self.line_height_ratio
        self.char_width = char_width / 100.0
        
        self.margin_top = margin_top * mm
        self.margin_bottom = margin_bottom * mm
        self.margin_left = margin_left * mm
        self.margin_right = margin_right * mm
        
        self.width, self.height = A4
        self.usable_width = self.width - self.margin_left - self.margin_right
        self.usable_height = self.height - self.margin_top - self.margin_bottom
        
        char_width_pt = font_size_body * 1.0 * self.char_width
        self.chars_per_line = int(self.usable_width / char_width_pt)
    
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
        
        # 3. 목차
        self._draw_toc(c, chapters_content)
        
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
    
    def _draw_toc(self, c, chapters):
        """목차 페이지"""
        c.setFont(self.font_name, self.font_size_title)
        c.drawString(self.margin_left, self.height - self.margin_top, "목 차")
        
        c.setFont(self.font_name, self.font_size_subtitle)
        y = self.height - self.margin_top - 60
        
        for i, ch in enumerate(chapters):
            c.drawString(self.margin_left + 10, y, f"{i+1}. {ch['title']}")
            y -= 30
            if y < self.margin_bottom:
                c.showPage()
                c.setFont(self.font_name, self.font_size_subtitle)
                y = self.height - self.margin_top
        
        c.showPage()
    
    def _draw_chapter(self, c, chapter, bg_data):
        """챕터 페이지들"""
        title = chapter['title']
        content = clean_markdown(chapter['content'])
        
        # 첫 페이지
        self._draw_image(c, bg_data, 0, 0, self.width, self.height)
        c.setFont(self.font_name, self.font_size_subtitle)
        c.drawString(self.margin_left, self.height - self.margin_top, f"■ {title}")
        
        y = self.height - self.margin_top - 40
        c.setFont(self.font_name, self.font_size_body)
        
        for line in wrap_text_korean(content, self.chars_per_line):
            if not line.strip():
                y -= self.line_height * 0.5
                continue
            
            if y < self.margin_bottom:
                c.showPage()
                self._draw_image(c, bg_data, 0, 0, self.width, self.height)
                c.setFont(self.font_name, self.font_size_body)
                y = self.height - self.margin_top
            
            if self.char_width != 1.0:
                c.saveState()
                c.translate(self.margin_left, y)
                c.scale(self.char_width, 1)
                c.drawString(0, 0, line)
                c.restoreState()
            else:
                c.drawString(self.margin_left, y, line)
            
            y -= self.line_height
        
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
