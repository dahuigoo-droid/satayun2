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
# 이미지 캐싱 (세션 + LRU 이중 캐싱)
# ============================================

# 세션 레벨 이미지 캐시
_session_image_cache: Dict[str, bytes] = {}

@lru_cache(maxsize=50)
def _download_image(url: str) -> Optional[bytes]:
    """URL에서 이미지 다운로드 (LRU 캐싱)"""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.content
    except:
        pass
    return None


def load_image_for_pdf(image_path: str) -> Optional[io.BytesIO]:
    """이미지 로드 - 세션 캐싱 + LRU 캐싱 이중 적용"""
    if not image_path:
        return None
    
    # URL인 경우
    if image_path.startswith("http"):
        # 1차: 세션 캐시 확인 (가장 빠름)
        if image_path in _session_image_cache:
            return io.BytesIO(_session_image_cache[image_path])
        
        # 2차: LRU 캐시에서 다운로드
        content = _download_image(image_path)
        if content:
            _session_image_cache[image_path] = content  # 세션 캐시에 저장
            return io.BytesIO(content)
        return None
    
    # 로컬 파일인 경우
    if os.path.exists(image_path):
        return image_path
    
    return None


def clear_image_cache():
    """이미지 캐시 초기화"""
    global _session_image_cache
    _session_image_cache.clear()
    _download_image.cache_clear()


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
        
        # 목표 글자 수가 너무 크면 분할 생성
        if target_chars > 1500:
            return _generate_long_chapter(
                client, customer_str, chapter_title, guideline, 
                service_type, target_chars, model
            )
        
        prompt = f"""[서비스 유형]
{service_type}

[고객 정보]
{customer_str}

[작성 지침]
{guideline}

[현재 작성할 챕터]
{chapter_title}

[필수 요구사항]
- 반드시 {target_chars}자 이상 작성
- 최소 {target_chars}자, 최대 {target_chars + 500}자
- 충분히 상세하고 풍부하게 작성

위 챕터를 전문적이면서도 이해하기 쉽게 작성해주세요.
구체적인 조언과 예시를 포함하고, 따뜻하고 희망적인 톤을 유지하세요.
마크다운 문법 없이 일반 텍스트로 작성하세요.
챕터 제목은 다시 쓰지 마세요."""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"당신은 전문적이고 따뜻한 {service_type} 전문가입니다. 요청된 글자 수를 반드시 충족해야 합니다. 마크다운 없이 일반 텍스트로만 답변하세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=6000,
            temperature=0.7
        )
        
        return clean_markdown(response.choices[0].message.content)
    
    except Exception as e:
        return f"[오류: {str(e)}]"


def _generate_long_chapter(
    client,
    customer_str: str,
    chapter_title: str,
    guideline: str,
    service_type: str,
    target_chars: int,
    model: str
) -> str:
    """긴 챕터를 여러 부분으로 나눠서 생성"""
    parts = []
    chars_per_part = 1200  # 한 번에 생성할 글자 수
    num_parts = max(2, (target_chars // chars_per_part) + 1)
    
    part_names = ["도입부", "본론 1", "본론 2", "본론 3", "결론"][:num_parts]
    
    for i, part_name in enumerate(part_names):
        is_first = (i == 0)
        is_last = (i == len(part_names) - 1)
        
        if is_first:
            context = "챕터의 시작 부분입니다. 주제를 소개하고 전체 내용을 이끌어가세요."
        elif is_last:
            context = "챕터의 마무리 부분입니다. 핵심 내용을 정리하고 따뜻한 조언으로 마무리하세요."
        else:
            context = f"챕터의 중간 부분({part_name})입니다. 구체적인 내용과 예시를 상세히 설명하세요."
        
        prompt = f"""[서비스 유형]
{service_type}

[고객 정보]
{customer_str}

[작성 지침]
{guideline}

[현재 작성할 챕터]
{chapter_title}

[현재 작성할 부분]
{part_name} - {context}

[필수 요구사항]
- 이 부분만 {chars_per_part}자 이상 작성
- 자연스럽게 이어지도록 작성
- 마크다운 없이 일반 텍스트로 작성
- 챕터 제목이나 부분 제목은 쓰지 마세요"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"당신은 {service_type} 전문가입니다. 요청된 글자 수를 반드시 충족하세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        part_content = clean_markdown(response.choices[0].message.content)
        parts.append(part_content)
        print(f"  [{part_name}] {len(part_content)}자 생성")
    
    return "\n\n".join(parts)


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
    progress_callback: Callable = None,
    max_workers: int = 3  # 🚀 병렬 워커 수
) -> List[Dict]:
    """전체 콘텐츠 생성 - 🚀 병렬 처리 + 진행률 표시"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # 페이지당 글자 수 계산
    chars_per_page = calculate_chars_per_page(
        font_size, line_height, margin_top, margin_bottom, margin_left, margin_right
    )
    
    # 목차당 필요 글자 수
    content_pages = max(target_pages - 3, target_pages * 0.9)
    chars_per_chapter = int((content_pages * chars_per_page) / len(chapters))
    
    print(f"[PDF설정] 목표: {target_pages}페이지, 페이지당 {chars_per_page}자")
    print(f"[PDF설정] 목차 {len(chapters)}개, 목차당 {chars_per_chapter}자 목표")
    print(f"[PDF설정] 🚀 병렬 처리: {max_workers}개 동시 실행")
    
    total = len(chapters)
    results = [None] * total  # 순서 유지
    
    def process_chapter(idx: int, chapter: str) -> tuple:
        """개별 챕터 처리 (스레드에서 실행) - UI 업데이트 없음"""
        content = generate_chapter_content(
            api_key, customer_info, chapter, guideline, service_type,
            target_chars=chars_per_chapter,
            model=model
        )
        
        actual_chars = len(content)
        print(f"[챕터 {idx+1}] '{chapter}': {actual_chars}자 생성")
        
        return idx, {"title": chapter, "content": content}
    
    # 🚀 병렬 실행 + 메인 스레드에서 진행률 업데이트
    completed_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_chapter, i, ch): (i, ch)
            for i, ch in enumerate(chapters)
        }
        
        for future in as_completed(futures):
            try:
                idx, result = future.result()
                results[idx] = result
                
                # ✅ 메인 스레드에서 진행률 업데이트
                completed_count += 1
                if progress_callback:
                    chapter_name = futures[future][1]
                    progress_callback(
                        completed_count / total, 
                        f"'{chapter_name}' 완료 ({completed_count}/{total})"
                    )
                    
            except Exception as e:
                idx, chapter_name = futures[future]
                print(f"[오류] 챕터 {idx+1} 생성 실패: {e}")
                results[idx] = {"title": chapter_name, "content": f"[오류: {str(e)}]"}
                
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count / total, f"'{chapter_name}' 오류")
    
    return results


# ============================================
# PDF 생성 (Platypus 기반 - 정확한 페이지 수 보장)
# ============================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.colors import black, white, grey

class PDFGenerator:
    """PDF 생성기 - Platypus 기반, 정확한 페이지 수 보장"""
    
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
        self.target_pages = target_pages
        
        # 행간 계산
        self.line_height_ratio = line_height / 100.0
        self.line_height = font_size_body * self.line_height_ratio
        
        # 여백 (mm → pt)
        self.margin_top = margin_top * mm
        self.margin_bottom = margin_bottom * mm
        self.margin_left = margin_left * mm
        self.margin_right = margin_right * mm
        
        # 페이지 크기 (A4)
        self.width, self.height = A4
        self.usable_width = self.width - self.margin_left - self.margin_right
        self.usable_height = self.height - self.margin_top - self.margin_bottom
        
        # 페이지당 줄 수 계산
        self.lines_per_page = int(self.usable_height / self.line_height)
        self.chars_per_line = int(self.usable_width / (self.font_size_body * 0.5))  # 한글 기준
        self.chars_per_page = self.lines_per_page * self.chars_per_line
        
        print(f"[PDF] 목표: {target_pages}페이지")
        print(f"[PDF] 페이지당: {self.lines_per_page}줄, {self.chars_per_line}자/줄, ~{self.chars_per_page}자")
        
        # 스타일 정의
        self._init_styles()
    
    def _init_styles(self):
        """문단 스타일 초기화"""
        self.title_style = ParagraphStyle(
            'ChapterTitle',
            fontName=self.font_name,
            fontSize=self.font_size_title,
            leading=self.font_size_title * 1.5,
            alignment=TA_CENTER,
            spaceAfter=30,
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            fontName=self.font_name,
            fontSize=self.font_size_subtitle,
            leading=self.font_size_subtitle * 1.5,
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        
        self.body_style = ParagraphStyle(
            'BodyText',
            fontName=self.font_name,
            fontSize=self.font_size_body,
            leading=self.line_height,
            alignment=TA_JUSTIFY,
            firstLineIndent=self.font_size_body * 2,  # 들여쓰기
            wordWrap='CJK',
        )
        
        self.toc_style = ParagraphStyle(
            'TOC',
            fontName=self.font_name,
            fontSize=self.font_size_subtitle,
            leading=self.font_size_subtitle * 2,
            leftIndent=20,
        )
    
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
        """PDF 생성 - 정확한 페이지 수 보장"""
        buffer = io.BytesIO()
        
        # 배경 이미지 로드
        self.bg_data = load_image_for_pdf(background_image)
        self.cover_data = load_image_for_pdf(cover_image)
        self.info_data = load_image_for_pdf(info_image)
        
        # SimpleDocTemplate 생성
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=self.margin_top,
            bottomMargin=self.margin_bottom,
            leftMargin=self.margin_left,
            rightMargin=self.margin_right
        )
        
        elements = []
        
        # 1. 표지 페이지 (Canvas로 직접 그리기)
        # Platypus에서는 커스텀 Flowable로 구현
        elements.append(self._create_cover_flowable(customer_name, service_type, customer_name2))
        elements.append(PageBreak())
        
        # 2. 목차 페이지
        elements.append(Paragraph("목 차", self.title_style))
        elements.append(Spacer(1, 30))
        for i, ch in enumerate(chapters_content):
            toc_text = f"{i+1}. {ch['title']}"
            elements.append(Paragraph(toc_text, self.toc_style))
        elements.append(PageBreak())
        
        # 3. 본문 - 정확한 페이지 수로 분배
        content_pages = self.target_pages - 3  # 표지, 목차, 안내지 제외
        pages_per_chapter = max(1, content_pages // len(chapters_content))
        
        for ch_idx, chapter in enumerate(chapters_content):
            title = chapter['title']
            content = clean_markdown(chapter['content'])
            
            # 챕터 제목
            elements.append(Paragraph(title, self.title_style))
            elements.append(Spacer(1, 20))
            
            # 컨텐츠를 페이지 단위로 분할
            content_chunks = self._split_content_to_pages(content, pages_per_chapter)
            
            for page_idx, chunk in enumerate(content_chunks):
                # 본문 추가
                for para in chunk.split('\n\n'):
                    if para.strip():
                        elements.append(Paragraph(para.strip(), self.body_style))
                        elements.append(Spacer(1, 10))
                
                # 마지막 청크가 아니면 페이지 분리
                if page_idx < len(content_chunks) - 1:
                    elements.append(PageBreak())
            
            # 챕터 끝에 페이지 분리 (마지막 챕터 제외)
            if ch_idx < len(chapters_content) - 1:
                elements.append(PageBreak())
        
        # 4. 안내 페이지 (있으면)
        if self.info_data:
            elements.append(PageBreak())
            elements.append(self._create_image_flowable(self.info_data))
        
        # PDF 빌드 (배경 이미지 콜백)
        doc.build(elements, onFirstPage=self._add_background, onLaterPages=self._add_background)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _split_content_to_pages(self, content: str, target_pages: int) -> list:
        """컨텐츠를 목표 페이지 수에 맞게 분할"""
        if not content:
            return [""]
        
        total_chars = len(content)
        chars_per_page = max(100, total_chars // target_pages)
        
        chunks = []
        paragraphs = content.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > chars_per_page and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 목표 페이지 수에 맞게 조정
        while len(chunks) < target_pages and chunks:
            # 가장 긴 청크를 분할
            longest_idx = max(range(len(chunks)), key=lambda i: len(chunks[i]))
            chunk = chunks[longest_idx]
            mid = len(chunk) // 2
            
            # 문단 경계에서 분할
            split_point = chunk.rfind('\n\n', 0, mid)
            if split_point == -1:
                split_point = chunk.rfind('. ', 0, mid)
            if split_point == -1:
                split_point = mid
            
            part1 = chunk[:split_point].strip()
            part2 = chunk[split_point:].strip()
            
            if part1 and part2:
                chunks[longest_idx] = part1
                chunks.insert(longest_idx + 1, part2)
            else:
                break
        
        return chunks if chunks else [""]
    
    def _add_background(self, canvas, doc):
        """각 페이지에 배경 이미지 추가"""
        if self.bg_data:
            try:
                if hasattr(self.bg_data, 'seek'):
                    self.bg_data.seek(0)
                canvas.drawImage(self.bg_data, 0, 0, width=self.width, height=self.height,
                               preserveAspectRatio=False, mask='auto')
            except:
                pass
    
    def _create_cover_flowable(self, name, service_type, name2=None):
        """표지용 Flowable"""
        from reportlab.platypus import Flowable
        
        class CoverPage(Flowable):
            def __init__(self, generator, name, service_type, name2):
                Flowable.__init__(self)
                self.gen = generator
                self.name = name
                self.service_type = service_type
                self.name2 = name2
                self._width = generator.usable_width
                self._height = generator.usable_height
            
            def wrap(self, availWidth, availHeight):
                """Flowable 크기 반환 - 필수!"""
                return (self._width, self._height)
            
            def draw(self):
                c = self.canv
                
                # 표지 이미지
                if self.gen.cover_data:
                    try:
                        if hasattr(self.gen.cover_data, 'seek'):
                            self.gen.cover_data.seek(0)
                        c.drawImage(self.gen.cover_data, -self.gen.margin_left, 
                                  -self.gen.margin_bottom,
                                  width=self.gen.width, height=self.gen.height,
                                  preserveAspectRatio=False, mask='auto')
                    except:
                        pass
                
                # 고객명
                c.setFont(self.gen.font_name, self.gen.font_size_title + 4)
                name_text = f"{self.name}  ♥  {self.name2}" if self.name2 else f"{self.name} 님"
                tw = c.stringWidth(name_text, self.gen.font_name, self.gen.font_size_title + 4)
                c.drawString((self.gen.width - tw) / 2 - self.gen.margin_left, 
                           self.gen.height * 0.25 - self.gen.margin_bottom, name_text)
                
                # 서비스 유형
                c.setFont(self.gen.font_name, self.gen.font_size_subtitle)
                tw = c.stringWidth(self.service_type, self.gen.font_name, self.gen.font_size_subtitle)
                c.drawString((self.gen.width - tw) / 2 - self.gen.margin_left,
                           self.gen.height * 0.20 - self.gen.margin_bottom, self.service_type)
                
                # 날짜
                c.setFont(self.gen.font_name, self.gen.font_size_body)
                date_text = datetime.now().strftime("%Y년 %m월 %d일")
                tw = c.stringWidth(date_text, self.gen.font_name, self.gen.font_size_body)
                c.drawString((self.gen.width - tw) / 2 - self.gen.margin_left,
                           self.gen.height * 0.15 - self.gen.margin_bottom, date_text)
        
        return CoverPage(self, name, service_type, name2)
    
    def _create_image_flowable(self, img_data):
        """이미지 전체 페이지 Flowable"""
        from reportlab.platypus import Flowable
        
        class FullPageImage(Flowable):
            def __init__(self, generator, img_data):
                Flowable.__init__(self)
                self.gen = generator
                self.img_data = img_data
                self._width = generator.usable_width
                self._height = generator.usable_height
            
            def wrap(self, availWidth, availHeight):
                """Flowable 크기 반환 - 필수!"""
                return (self._width, self._height)
            
            def draw(self):
                if self.img_data:
                    try:
                        if hasattr(self.img_data, 'seek'):
                            self.img_data.seek(0)
                        self.canv.drawImage(self.img_data, -self.gen.margin_left,
                                          -self.gen.margin_bottom,
                                          width=self.gen.width, height=self.gen.height,
                                          preserveAspectRatio=False, mask='auto')
                    except:
                        pass
        
        return FullPageImage(self, img_data)
    
    # ========================================
    # 차트 추가 기능 (확장용)
    # ========================================
    
    def add_chart_to_elements(self, elements: list, chart_path: str, width: int = 400, height: int = 300):
        """Matplotlib 차트를 elements에 추가"""
        if os.path.exists(chart_path):
            img = RLImage(chart_path, width=width, height=height)
            elements.append(img)
            elements.append(Spacer(1, 20))
    
    def create_chart_image(self, fig, filename: str = None) -> str:
        """Matplotlib Figure를 이미지로 저장"""
        import tempfile
        if filename is None:
            fd, filename = tempfile.mkstemp(suffix='.png')
            os.close(fd)
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        return filename


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
