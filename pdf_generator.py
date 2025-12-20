# -*- coding: utf-8 -*-
"""
📄 PDF 생성 모듈
- GPT 호출 (목차별 분할)
- PDF 생성 (표지→소개→본문→안내)
- 디자인 설정 완전 반영
"""

import os
import io
import re
from datetime import datetime
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ============================================
# 폰트 등록
# ============================================

FONT_MAP = {
    'NanumGothic': '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
    'NanumGothicBold': '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
    'NanumMyeongjo': '/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf',
    'NanumMyeongjoBold': '/usr/share/fonts/truetype/nanum/NanumMyeongjoBold.ttf',
    'NanumBarunGothic': '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
    'NanumSquareRound': '/usr/share/fonts/truetype/nanum/NanumSquareRoundR.ttf',
}

def register_fonts():
    """한글 폰트 등록"""
    registered = []
    
    for name, path in FONT_MAP.items():
        try:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(name, path))
                registered.append(name)
        except Exception as e:
            print(f"폰트 등록 실패 ({name}): {e}")
    
    return registered[0] if registered else 'Helvetica'

# 시작 시 폰트 등록
DEFAULT_FONT = register_fonts()

# ============================================
# 텍스트 처리 유틸리티
# ============================================

def clean_markdown(text: str) -> str:
    """마크다운 문법 제거"""
    if not text:
        return ""
    
    # ### 헤더 제거 (줄 시작의 # 들)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # **볼드** 제거
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # *이탤릭* 제거
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    
    # __볼드__ 제거
    text = re.sub(r'__([^_]+)__', r'\1', text)
    
    # _이탤릭_ 제거
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # `코드` 제거
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # [링크](url) 제거
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # - 리스트 마커 제거 (줄 시작)
    text = re.sub(r'^\s*[-*+]\s+', '• ', text, flags=re.MULTILINE)
    
    # 숫자 리스트 마커 정리
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 연속 빈 줄 하나로
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def wrap_text_korean(text: str, max_chars: int) -> list:
    """한글 텍스트 줄바꿈 (글자 수 기준)"""
    lines = []
    
    for paragraph in text.split('\n'):
        paragraph = paragraph.strip()
        
        if not paragraph:
            lines.append('')
            continue
        
        while len(paragraph) > max_chars:
            # 최대 글자 수에서 자르되, 단어 중간이면 조정
            cut_point = max_chars
            
            # 공백이나 구두점에서 자르기 시도
            for i in range(max_chars, max(0, max_chars - 10), -1):
                if i < len(paragraph) and paragraph[i] in ' .,!?。，！？':
                    cut_point = i + 1
                    break
            
            lines.append(paragraph[:cut_point].strip())
            paragraph = paragraph[cut_point:].strip()
        
        if paragraph:
            lines.append(paragraph)
    
    return lines


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
    """단일 챕터(목차) 콘텐츠 생성"""
    try:
        client = OpenAI(api_key=api_key)
        
        # 고객 정보 포맷팅
        customer_str = "\n".join([f"- {k}: {v}" for k, v in customer_info.items() if v])
        
        prompt = f"""
[서비스 유형]
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
- 마크다운 문법(###, **, 등) 사용하지 말고 일반 텍스트로 작성
- 챕터 제목은 다시 쓰지 마세요
"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": f"당신은 전문적이고 따뜻한 {service_type} 전문가입니다. 마크다운 없이 일반 텍스트로만 답변하세요."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        # 마크다운 제거
        return clean_markdown(content)
    
    except Exception as e:
        return f"[오류 발생: {str(e)}]"


def generate_full_content(
    api_key: str,
    customer_info: dict,
    chapters: list,
    guideline: str,
    service_type: str,
    model: str = "gpt-4o-mini",
    progress_callback=None
) -> list:
    """전체 콘텐츠 생성 (목차별 분할 요청)"""
    full_content = []
    total = len(chapters)
    
    for i, chapter in enumerate(chapters):
        if progress_callback:
            progress_callback((i + 1) / total, f"'{chapter}' 작성 중... ({i+1}/{total})")
        
        content = generate_chapter_content(
            api_key=api_key,
            customer_info=customer_info,
            chapter_title=chapter,
            guideline=guideline,
            service_type=service_type,
            model=model
        )
        
        full_content.append({
            "title": chapter,
            "content": content
        })
    
    return full_content


# ============================================
# PDF 생성
# ============================================

class PDFGenerator:
    """PDF 생성 클래스 - 디자인 설정 완전 반영"""
    
    def __init__(
        self,
        font_name: str = "NanumGothic",
        font_size_title: int = 24,
        font_size_subtitle: int = 16,
        font_size_body: int = 12,
        line_height: int = 180,      # 퍼센트 (180 = 1.8배)
        letter_spacing: int = 0,     # 퍼센트
        char_width: int = 100,       # 장평 퍼센트
        margin_top: int = 25,        # mm
        margin_bottom: int = 25,     # mm
        margin_left: int = 25,       # mm
        margin_right: int = 25,      # mm
        target_pages: int = 30
    ):
        # 폰트 설정
        self.font_name = font_name if font_name in FONT_MAP else DEFAULT_FONT
        self.font_size_title = font_size_title
        self.font_size_subtitle = font_size_subtitle
        self.font_size_body = font_size_body
        
        # 행간 (퍼센트를 실제 값으로)
        self.line_height_ratio = line_height / 100.0
        self.line_height = font_size_body * self.line_height_ratio
        
        # 자간, 장평
        self.letter_spacing = letter_spacing
        self.char_width = char_width / 100.0  # 1.0 = 100%
        
        # 여백 (mm → 포인트)
        self.margin_top = margin_top * mm
        self.margin_bottom = margin_bottom * mm
        self.margin_left = margin_left * mm
        self.margin_right = margin_right * mm
        
        self.target_pages = target_pages
        
        # 페이지 크기
        self.width, self.height = A4
        
        # 사용 가능 영역
        self.usable_width = self.width - self.margin_left - self.margin_right
        self.usable_height = self.height - self.margin_top - self.margin_bottom
        
        # 한 줄 글자 수 계산 (한글은 full-width이므로 font_size와 거의 동일)
        char_width_pt = self.font_size_body * 1.0 * self.char_width
        self.chars_per_line = int(self.usable_width / char_width_pt)
        
        print(f"[PDF설정] 여백: 상{margin_top}mm 하{margin_bottom}mm 좌{margin_left}mm 우{margin_right}mm")
        print(f"[PDF설정] 글자수/줄: {self.chars_per_line}, 본문크기: {font_size_body}pt")
        
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
        
        # 1. 표지 페이지
        self._draw_cover_page(c, cover_image, customer_name, service_type, customer_name2)
        
        # 2. 소개 페이지
        if intro_image:
            self._draw_image_page(c, intro_image)
        
        # 3. 목차 페이지
        self._draw_toc_page(c, chapters_content)
        
        # 4. 본문 페이지들
        for chapter in chapters_content:
            self._draw_content_pages(c, chapter, background_image)
        
        # 5. 안내 페이지
        if info_image:
            self._draw_image_page(c, info_image)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _apply_text_style(self, c, font_size, is_title=False):
        """텍스트 스타일 적용"""
        c.setFont(self.font_name, font_size)
        # 자간은 reportlab 기본 기능으로 지원 안됨 - 생략
    
    def _draw_text_with_style(self, c, x, y, text, font_size):
        """장평 적용된 텍스트 그리기"""
        self._apply_text_style(c, font_size)
        
        if self.char_width != 1.0:
            # 장평 적용
            c.saveState()
            c.translate(x, y)
            c.scale(self.char_width, 1)
            c.drawString(0, 0, text)
            c.restoreState()
        else:
            c.drawString(x, y, text)
    
    def _draw_cover_page(self, c, cover_image, customer_name, service_type, customer_name2=None):
        """표지 페이지 그리기"""
        # 배경 이미지
        print(f"[표지] 이미지 경로: {cover_image}")
        if cover_image:
            try:
                # 경로 존재 여부와 관계없이 시도
                c.drawImage(cover_image, 0, 0, width=self.width, height=self.height, 
                           preserveAspectRatio=False, mask='auto')
                print(f"[표지] 이미지 적용 성공")
            except Exception as e:
                print(f"[표지] 이미지 오류: {e}")
        
        # 고객 이름
        c.setFont(self.font_name, self.font_size_title + 4)
        
        if customer_name2:
            name_text = f"{customer_name}  ♥  {customer_name2}"
        else:
            name_text = f"{customer_name} 님"
        
        text_width = c.stringWidth(name_text, self.font_name, self.font_size_title + 4)
        c.drawString((self.width - text_width) / 2, self.height * 0.25, name_text)
        
        # 서비스 유형
        c.setFont(self.font_name, self.font_size_subtitle)
        service_text = f"{service_type}"
        text_width = c.stringWidth(service_text, self.font_name, self.font_size_subtitle)
        c.drawString((self.width - text_width) / 2, self.height * 0.20, service_text)
        
        # 날짜
        c.setFont(self.font_name, self.font_size_body)
        date_text = datetime.now().strftime("%Y년 %m월 %d일")
        text_width = c.stringWidth(date_text, self.font_name, self.font_size_body)
        c.drawString((self.width - text_width) / 2, self.height * 0.15, date_text)
        
        c.showPage()
    
    def _draw_image_page(self, c, image_path):
        """이미지 전체 페이지 그리기"""
        print(f"[이미지페이지] 경로: {image_path}")
        if image_path:
            try:
                c.drawImage(image_path, 0, 0, width=self.width, height=self.height, 
                           preserveAspectRatio=False, mask='auto')
                print(f"[이미지페이지] 적용 성공")
            except Exception as e:
                print(f"[이미지페이지] 오류: {e}")
        c.showPage()
    
    def _draw_toc_page(self, c, chapters_content):
        """목차 페이지 그리기"""
        c.setFont(self.font_name, self.font_size_title)
        c.drawString(self.margin_left, self.height - self.margin_top, "목 차")
        
        c.setFont(self.font_name, self.font_size_subtitle)
        y_position = self.height - self.margin_top - 60
        
        for i, chapter in enumerate(chapters_content):
            title = chapter['title']
            c.drawString(self.margin_left + 10, y_position, f"{i+1}. {title}")
            y_position -= 30
            
            if y_position < self.margin_bottom:
                c.showPage()
                c.setFont(self.font_name, self.font_size_subtitle)
                y_position = self.height - self.margin_top
        
        c.showPage()
    
    def _draw_content_pages(self, c, chapter, background_image):
        """본문 페이지들 그리기"""
        title = chapter['title']
        content = chapter['content']
        
        # 마크다운 한번 더 정리
        content = clean_markdown(content)
        
        # 새 페이지 시작
        self._start_new_page(c, background_image)
        
        # 챕터 제목
        self._apply_text_style(c, self.font_size_subtitle, is_title=True)
        c.drawString(self.margin_left, self.height - self.margin_top, f"■ {title}")
        
        # 본문 시작 위치
        y_position = self.height - self.margin_top - 40
        
        # 본문 스타일 적용
        self._apply_text_style(c, self.font_size_body)
        
        # 텍스트 줄바꿈
        lines = wrap_text_korean(content, self.chars_per_line)
        
        for line in lines:
            # 빈 줄은 줄간격만큼 이동
            if not line.strip():
                y_position -= self.line_height * 0.5
                continue
            
            # 페이지 넘김 체크
            if y_position < self.margin_bottom:
                c.showPage()
                self._start_new_page(c, background_image)
                self._apply_text_style(c, self.font_size_body)
                y_position = self.height - self.margin_top
            
            # 텍스트 그리기 (장평 적용)
            self._draw_text_with_style(c, self.margin_left, y_position, line, self.font_size_body)
            
            y_position -= self.line_height
        
        c.showPage()
    
    def _start_new_page(self, c, background_image):
        """새 페이지 시작 (배경 이미지 적용)"""
        if background_image:
            try:
                c.drawImage(background_image, 0, 0, width=self.width, height=self.height, 
                           preserveAspectRatio=False, mask='auto')
            except Exception as e:
                print(f"[배경] 이미지 오류: {e}")


# ============================================
# 합본 PDF 생성
# ============================================

def generate_combined_pdf(
    api_key: str,
    customer_info: dict,
    services_data: list,
    font_settings: dict,
    progress_callback=None
) -> bytes:
    """여러 서비스 합본 PDF 생성"""
    all_chapters_content = []
    
    total_chapters = sum(len(s['chapters']) for s in services_data)
    current_chapter = 0
    
    for service in services_data:
        service_name = service['service_name']
        chapters = service['chapters']
        guideline = service.get('guideline', '')
        
        for chapter in chapters:
            current_chapter += 1
            
            if progress_callback:
                progress_callback(
                    current_chapter / total_chapters,
                    f"[{service_name}] '{chapter}' 작성 중... ({current_chapter}/{total_chapters})"
                )
            
            content = generate_chapter_content(
                api_key=api_key,
                customer_info=customer_info,
                chapter_title=f"{service_name} - {chapter}",
                guideline=guideline,
                service_type=service_name
            )
            
            all_chapters_content.append({
                "title": f"{service_name} - {chapter}",
                "content": content
            })
    
    # PDF 생성
    pdf_gen = PDFGenerator(
        font_name=font_settings.get('font_family', 'NanumGothic'),
        font_size_title=font_settings.get('font_size_title', 24),
        font_size_subtitle=font_settings.get('font_size_subtitle', 16),
        font_size_body=font_settings.get('font_size_body', 12),
        line_height=font_settings.get('line_height', 180),
        letter_spacing=font_settings.get('letter_spacing', 0),
        char_width=font_settings.get('char_width', 100),
        margin_top=font_settings.get('margin_top', 25),
        margin_bottom=font_settings.get('margin_bottom', 25),
        margin_left=font_settings.get('margin_left', 25),
        margin_right=font_settings.get('margin_right', 25),
        target_pages=font_settings.get('target_pages', 30)
    )
    
    first_service = services_data[0] if services_data else {}
    
    customer_name = customer_info.get('이름', customer_info.get('name', '고객'))
    customer_name2 = customer_info.get('이름2', customer_info.get('name2', None))
    
    service_types = " + ".join([s['service_name'] for s in services_data])
    
    pdf_bytes = pdf_gen.create_pdf(
        chapters_content=all_chapters_content,
        customer_name=customer_name,
        service_type=service_types,
        cover_image=first_service.get('cover_image'),
        intro_image=first_service.get('intro_image'),
        background_image=first_service.get('background_image'),
        info_image=first_service.get('info_image'),
        customer_name2=customer_name2
    )
    
    return pdf_bytes
