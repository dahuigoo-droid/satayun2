# 사주 원국표 이미지 생성기
from PIL import Image, ImageDraw, ImageFont
import os

# ============================================
# 폰트 설정
# ============================================
def get_font(size, bold=False):
    """한글 폰트 로드"""
    font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    
    if bold:
        font_paths.insert(0, "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf")
    
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    
    return ImageFont.load_default()

# ============================================
# 색상 정의 (오행별)
# ============================================
오행_색상 = {
    '목': {
        '천간_bg': '#C5D86D',      # 연두
        '지지_bg': '#B8CF5C',      # 진한 연두
        'text': '#000000',
    },
    '화': {
        '천간_bg': '#E57373',      # 빨강
        '지지_bg': '#D32F2F',      # 진한 빨강
        'text': '#FFFFFF',
    },
    '토': {
        '천간_bg': '#D4A574',      # 황토
        '지지_bg': '#5D5D5D',      # 어두운 회색
        'text': '#FFFFFF',
    },
    '금': {
        '천간_bg': '#E8E4A0',      # 연한 노랑
        '지지_bg': '#D4D094',      # 진한 노랑
        'text': '#000000',
    },
    '수': {
        '천간_bg': '#4A4A4A',      # 검정
        '지지_bg': '#2D2D2D',      # 진한 검정
        'text': '#FFFFFF',
    },
}

# 천간/지지 오행 매핑
천간_오행_map = {
    '갑': '목', '을': '목',
    '병': '화', '정': '화',
    '무': '토', '기': '토',
    '경': '금', '신': '금',
    '임': '수', '계': '수',
}

지지_오행_map = {
    '자': '수', '축': '토', '인': '목', '묘': '목',
    '진': '토', '사': '화', '오': '화', '미': '토',
    '신': '금', '유': '금', '술': '토', '해': '수',
}

# 천간 한자
천간_한자 = {
    '갑': '甲', '을': '乙', '병': '丙', '정': '丁', '무': '戊',
    '기': '己', '경': '庚', '신': '辛', '임': '壬', '계': '癸',
}

# 지지 한자
지지_한자 = {
    '자': '子', '축': '丑', '인': '寅', '묘': '卯',
    '진': '辰', '사': '巳', '오': '午', '미': '未',
    '신': '申', '유': '酉', '술': '戌', '해': '亥',
}

# 오행 한자
오행_한자 = {'목': '木', '화': '火', '토': '土', '금': '金', '수': '水'}

# ============================================
# 원국표 이미지 생성
# ============================================
def create_원국표(사주_data, 기본정보, output_path="원국표.png"):
    """
    원국표 이미지 생성
    
    사주_data: calc_사주() 결과
    기본정보: {'이름': ..., '성별': ..., '나이': ..., '양력': ..., '음력': ...}
    """
    
    # 이미지 크기
    width = 600
    height = 500
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(14)
    font_large = get_font(36, bold=True)
    font_medium = get_font(14)
    font_small = get_font(12)
    
    # ========== 상단 기본정보 ==========
    y_start = 20
    info_text = f"{기본정보['이름']}, {기본정보['성별']}, {기본정보['나이']}세"
    draw.text((20, y_start), "기본정보", font=font_title, fill='#666666')
    draw.text((100, y_start), info_text, font=font_title, fill='#333333')
    
    draw.text((20, y_start + 25), "양력", font=font_title, fill='#666666')
    draw.text((100, y_start + 25), 기본정보['양력'], font=font_title, fill='#333333')
    
    draw.text((20, y_start + 50), "음력", font=font_title, fill='#666666')
    draw.text((100, y_start + 50), 기본정보['음력'], font=font_title, fill='#333333')
    
    # ========== 원국표 테이블 ==========
    table_y = 100
    cell_width = 130
    cell_height_header = 30
    cell_height_main = 70
    cell_height_sub = 25
    label_width = 70
    
    headers = ['생시', '생일', '생월', '생년']
    columns = ['시', '일', '월', '년']
    
    # 헤더 행
    draw.rectangle([label_width, table_y, width - 20, table_y + cell_height_header], 
                   fill='#F5F5F5', outline='#E0E0E0')
    
    for i, header in enumerate(headers):
        x = label_width + i * cell_width + cell_width // 2
        draw.text((x, table_y + 8), header, font=font_medium, fill='#666666', anchor='mm')
    
    current_y = table_y + cell_height_header
    
    # ========== 천간십성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_sub // 2), "천간십성", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        십성 = 사주_data['천간십성'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  십성, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 천간 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_main // 2), "천간", 
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = label_width + i * cell_width
        천간 = 사주_data[f'{col}주'][0] if col != '시' else 사주_data['시주'][0]
        
        # 주 가져오기
        if col == '시':
            천간 = 사주_data['시주'][0]
        elif col == '일':
            천간 = 사주_data['일주'][0]
        elif col == '월':
            천간 = 사주_data['월주'][0]
        else:
            천간 = 사주_data['년주'][0]
        
        오행 = 천간_오행_map[천간]
        bg_color = 오행_색상[오행]['천간_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                       fill=bg_color, outline='#E0E0E0')
        
        # 천간(한자) + 오행
        한자 = 천간_한자[천간]
        display_text = f"{천간}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2 - 10), 
                  display_text, font=font_large, fill=text_color, anchor='mm')
        
        # 오행 표시
        오행_text = f"{오행}"
        draw.text((x + cell_width - 15, current_y + cell_height_main - 15), 
                  오행_text, font=font_small, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_main // 2), "지지", 
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = label_width + i * cell_width
        
        if col == '시':
            지지 = 사주_data['시주'][1]
        elif col == '일':
            지지 = 사주_data['일주'][1]
        elif col == '월':
            지지 = 사주_data['월주'][1]
        else:
            지지 = 사주_data['년주'][1]
        
        오행 = 지지_오행_map[지지]
        bg_color = 오행_색상[오행]['지지_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                       fill=bg_color, outline='#E0E0E0')
        
        # 지지(한자) + 오행
        한자 = 지지_한자[지지]
        display_text = f"{지지}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2 - 10), 
                  display_text, font=font_large, fill=text_color, anchor='mm')
        
        # 오행 표시
        오행_text = f"{오행}"
        draw.text((x + cell_width - 15, current_y + cell_height_main - 15), 
                  오행_text, font=font_small, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지십성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_sub // 2), "지지십성", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        십성 = 사주_data['지지십성'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  십성, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 지장간 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_sub // 2), "지장간", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        지장간 = 사주_data['지장간'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  지장간, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 12운성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_sub // 2), "12운성", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        운성 = 사주_data['12운성'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  운성, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 12신살 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_sub // 2), "12신살", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        신살 = 사주_data['12신살'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  신살, font=font_small, fill='#888888', anchor='mm')
    
    # ========== 오행 분포 ==========
    current_y += cell_height_sub + 20
    오행_text = f"목 {사주_data['오행']['목']}, 화 {사주_data['오행']['화']}, 토 {사주_data['오행']['토']}, 금 {사주_data['오행']['금']}, 수 {사주_data['오행']['수']}"
    draw.text((width // 2, current_y), 오행_text, font=font_medium, fill='#666666', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 대운표 이미지 생성
# ============================================
def create_대운표(대운_data, 기본정보, output_path="대운표.png"):
    """
    대운표 이미지 생성
    
    대운_data: calc_대운() 결과
    기본정보: {'이름': ..., '성별': ..., ...}
    """
    
    대운_list = 대운_data['대운']
    대운수 = 대운_data['대운수']
    순행 = 대운_data['순행']
    사주 = 대운_data['사주']
    일간 = 사주['일주'][0]
    
    # 이미지 크기
    num_cols = len(대운_list)
    cell_width = 80
    label_width = 70
    width = label_width + (cell_width * num_cols) + 20
    height = 400
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(14)
    font_large = get_font(28, bold=True)
    font_medium = get_font(12)
    font_small = get_font(10)
    
    # ========== 상단 제목 ==========
    y_start = 15
    방향 = "순행" if 순행 else "역행"
    title = f"전통나이(대운수:{대운수}, {방향})"
    draw.text((width // 2, y_start), title, font=font_title, fill='#333333', anchor='mm')
    
    # ========== 대운표 테이블 ==========
    table_y = 40
    cell_height_small = 25
    cell_height_main = 55
    
    current_y = table_y
    
    # ========== 나이 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F0F0F0', outline='#E0E0E0')
    
    for i, 대운 in enumerate(대운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#F0F0F0', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  str(대운['나이']), font=font_medium, fill='#333333', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 십성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  대운['천간_십성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_main // 2), "천간",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = label_width + i * cell_width
        천간 = 대운['천간']
        오행 = 천간_오행_map[천간]
        bg_color = 오행_색상[오행]['천간_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                       fill=bg_color, outline='#E0E0E0')
        
        한자 = 천간_한자[천간]
        display_text = f"{천간}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2 - 8),
                  display_text, font=font_large, fill=text_color, anchor='mm')
        
        # 오행 표시
        draw.text((x + cell_width - 12, current_y + cell_height_main - 12),
                  오행, font=font_small, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_main // 2), "지지",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = label_width + i * cell_width
        지지 = 대운['지지']
        오행 = 지지_오행_map[지지]
        bg_color = 오행_색상[오행]['지지_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                       fill=bg_color, outline='#E0E0E0')
        
        한자 = 지지_한자[지지]
        display_text = f"{지지}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2 - 8),
                  display_text, font=font_large, fill=text_color, anchor='mm')
        
        # 오행 표시
        draw.text((x + cell_width - 12, current_y + cell_height_main - 12),
                  오행, font=font_small, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 십성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "지지십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  대운['지지_십성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12운성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "12운성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  대운['12운성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12신살 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "12신살",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  대운['12신살'], font=font_small, fill='#888888', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 세운표 이미지 생성
# ============================================
def create_세운표(세운_data, 기본정보, output_path="세운표.png"):
    """
    세운표 이미지 생성 (10년)
    """
    
    세운_list = 세운_data['세운']
    사주 = 세운_data['사주']
    일간 = 사주['일주'][0]
    
    # 이미지 크기
    num_cols = len(세운_list)
    cell_width = 75
    label_width = 70
    width = label_width + (cell_width * num_cols) + 20
    height = 380
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(14)
    font_large = get_font(24, bold=True)
    font_medium = get_font(11)
    font_small = get_font(9)
    
    # ========== 상단 제목 ==========
    y_start = 15
    draw.text((width // 2, y_start), "세운표 (10년)", font=font_title, fill='#333333', anchor='mm')
    
    # ========== 테이블 ==========
    table_y = 40
    cell_height_small = 22
    cell_height_main = 50
    
    current_y = table_y
    
    # ========== 년도 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F0F0F0', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "년도",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#F0F0F0', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  str(세운['년도']), font=font_small, fill='#333333', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 나이 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F0F0F0', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "나이",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#F0F0F0', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  str(세운['나이']), font=font_small, fill='#333333', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 십성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  세운['천간_십성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_main // 2), "천간",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = label_width + i * cell_width
        천간 = 세운['천간']
        오행 = 천간_오행_map[천간]
        bg_color = 오행_색상[오행]['천간_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                       fill=bg_color, outline='#E0E0E0')
        
        한자 = 천간_한자[천간]
        display_text = f"{천간}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2),
                  display_text, font=font_large, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_main // 2), "지지",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = label_width + i * cell_width
        지지 = 세운['지지']
        오행 = 지지_오행_map[지지]
        bg_color = 오행_색상[오행]['지지_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                       fill=bg_color, outline='#E0E0E0')
        
        한자 = 지지_한자[지지]
        display_text = f"{지지}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2),
                  display_text, font=font_large, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 십성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "지지십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  세운['지지_십성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12운성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "12운성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  세운['12운성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12신살 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "12신살",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  세운['12신살'], font=font_small, fill='#888888', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 월운표 이미지 생성
# ============================================
def create_월운표(월운_data, 기본정보, output_path="월운표.png"):
    """
    월운표 이미지 생성 (12개월)
    """
    
    월운_list = 월운_data['월운']
    년도 = 월운_data['년도']
    사주 = 월운_data['사주']
    
    # 이미지 크기
    num_cols = 12
    cell_width = 65
    label_width = 70
    width = label_width + (cell_width * num_cols) + 20
    height = 350
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(14)
    font_large = get_font(22, bold=True)
    font_medium = get_font(10)
    font_small = get_font(9)
    
    # ========== 상단 제목 ==========
    y_start = 15
    draw.text((width // 2, y_start), f"{년도}년 월운표", font=font_title, fill='#333333', anchor='mm')
    
    # ========== 테이블 ==========
    table_y = 40
    cell_height_small = 22
    cell_height_main = 45
    
    current_y = table_y
    
    # ========== 월 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F0F0F0', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "월",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#F0F0F0', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  f"{월운['월']}월", font=font_small, fill='#333333', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 십성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  월운['천간_십성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_main // 2), "천간",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = label_width + i * cell_width
        천간 = 월운['천간']
        오행 = 천간_오행_map[천간]
        bg_color = 오행_색상[오행]['천간_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                       fill=bg_color, outline='#E0E0E0')
        
        한자 = 천간_한자[천간]
        display_text = f"{천간}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2),
                  display_text, font=font_large, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_main // 2), "지지",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = label_width + i * cell_width
        지지 = 월운['지지']
        오행 = 지지_오행_map[지지]
        bg_color = 오행_색상[오행]['지지_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                       fill=bg_color, outline='#E0E0E0')
        
        한자 = 지지_한자[지지]
        display_text = f"{지지}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2),
                  display_text, font=font_large, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 십성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "지지십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  월운['지지_십성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12운성 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "12운성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  월운['12운성'], font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12신살 행 ==========
    draw.rectangle([0, current_y, label_width, current_y + cell_height_small],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((label_width // 2, current_y + cell_height_small // 2), "12신살",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                       fill='#FFFFFF', outline='#E0E0E0')
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  월운['12신살'], font=font_small, fill='#888888', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 오행 차트 이미지 생성
# ============================================
def create_오행차트(사주_data, 기본정보, output_path="오행차트.png"):
    """
    오행 분포 막대 차트 이미지 생성
    """
    
    오행 = 사주_data['오행']
    
    # 이미지 크기
    width = 500
    height = 300
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(16)
    font_medium = get_font(14)
    font_small = get_font(12)
    
    # ========== 상단 제목 ==========
    y_start = 20
    draw.text((width // 2, y_start), f"{기본정보['이름']}님 오행 분포", 
              font=font_title, fill='#333333', anchor='mm')
    
    # ========== 막대 차트 ==========
    chart_y = 60
    chart_height = 150
    bar_width = 60
    gap = 25
    start_x = 60
    
    오행_목록 = ['목', '화', '토', '금', '수']
    max_val = max(오행.values()) if max(오행.values()) > 0 else 1
    
    # 오행 색상 (차트용)
    chart_colors = {
        '목': '#4CAF50',  # 초록
        '화': '#F44336',  # 빨강
        '토': '#795548',  # 갈색
        '금': '#FFC107',  # 노랑
        '수': '#2196F3',  # 파랑
    }
    
    for i, 오행명 in enumerate(오행_목록):
        x = start_x + i * (bar_width + gap)
        값 = 오행[오행명]
        
        # 막대 높이 계산
        bar_height = int((값 / max_val) * chart_height) if 값 > 0 else 5
        
        # 막대 그리기
        bar_y = chart_y + chart_height - bar_height
        draw.rectangle([x, bar_y, x + bar_width, chart_y + chart_height],
                       fill=chart_colors[오행명], outline='#333333')
        
        # 값 표시
        draw.text((x + bar_width // 2, bar_y - 15),
                  str(값), font=font_medium, fill='#333333', anchor='mm')
        
        # 오행명 표시
        draw.text((x + bar_width // 2, chart_y + chart_height + 20),
                  오행명, font=font_medium, fill='#333333', anchor='mm')
    
    # ========== 하단 요약 ==========
    summary_y = chart_y + chart_height + 50
    
    # 강한 오행 / 약한 오행
    sorted_오행 = sorted(오행.items(), key=lambda x: x[1], reverse=True)
    강한_오행 = [k for k, v in sorted_오행 if v == sorted_오행[0][1]]
    약한_오행 = [k for k, v in sorted_오행 if v == sorted_오행[-1][1]]
    
    draw.text((width // 2, summary_y),
              f"강한 오행: {', '.join(강한_오행)}  |  약한 오행: {', '.join(약한_오행)}",
              font=font_small, fill='#666666', anchor='mm')
    
    # 총 개수
    total = sum(오행.values())
    draw.text((width // 2, summary_y + 25),
              f"총 {total}개 (목{오행['목']} 화{오행['화']} 토{오행['토']} 금{오행['금']} 수{오행['수']})",
              font=font_small, fill='#888888', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path
