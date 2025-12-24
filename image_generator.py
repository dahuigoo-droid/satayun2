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


# ============================================
# 십성표 이미지 생성
# ============================================
def create_십성표(사주_data, 기본정보, output_path="십성표.png"):
    """
    십성 분석표 이미지 생성
    - 비겁(비견/겁재), 식상(식신/상관), 재성(편재/정재), 관성(편관/정관), 인성(편인/정인)
    """
    
    일간 = 사주_data['일주'][0]
    일간_오행 = 천간_오행_map[일간]
    
    # 사주에서 십성 개수 세기
    십성_count = {
        '비견': 0, '겁재': 0,
        '식신': 0, '상관': 0,
        '편재': 0, '정재': 0,
        '편관': 0, '정관': 0,
        '편인': 0, '정인': 0,
    }
    
    # 천간 십성 카운트
    for col in ['년', '월', '시']:
        십성 = 사주_data['천간십성'][col]
        if 십성 in 십성_count:
            십성_count[십성] += 1
    
    # 지지 십성 카운트
    for col in ['년', '월', '일', '시']:
        십성 = 사주_data['지지십성'][col]
        if 십성 in 십성_count:
            십성_count[십성] += 1
    
    # 십성별 오행 매핑 (일간 기준)
    오행_순서 = ['목', '화', '토', '금', '수']
    일간_오행_idx = 오행_순서.index(일간_오행)
    
    # 십성별 오행 계산
    십성_오행 = {
        '비견': 일간_오행, '겁재': 일간_오행,
        '식신': 오행_순서[(일간_오행_idx + 1) % 5], 
        '상관': 오행_순서[(일간_오행_idx + 1) % 5],
        '편재': 오행_순서[(일간_오행_idx + 2) % 5], 
        '정재': 오행_순서[(일간_오행_idx + 2) % 5],
        '편관': 오행_순서[(일간_오행_idx + 3) % 5], 
        '정관': 오행_순서[(일간_오행_idx + 3) % 5],
        '편인': 오행_순서[(일간_오행_idx + 4) % 5], 
        '정인': 오행_순서[(일간_오행_idx + 4) % 5],
    }
    
    # 강도 판정
    def get_강도(count):
        if count == 0:
            return '없음'
        elif count == 1:
            return '약함'
        elif count == 2:
            return '보통'
        elif count == 3:
            return '강함'
        else:
            return '매우 강함'
    
    # 십성 분류 데이터
    십성_분류 = [
        {'분류': '비겁', '십성들': [('비견', '양'), ('겁재', '음')], 'color': '#A8D5BA'},
        {'분류': '식상', '십성들': [('식신', '양'), ('상관', '음')], 'color': '#87CEEB'},
        {'분류': '재성', '십성들': [('편재', '양'), ('정재', '음')], 'color': '#90EE90'},
        {'분류': '관성', '십성들': [('편관', '양'), ('정관', '음')], 'color': '#FFB6C1'},
        {'분류': '인성', '십성들': [('편인', '양'), ('정인', '음')], 'color': '#FFFACD'},
    ]
    
    # 이미지 크기
    width = 700
    height = 380
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#2D2D2D')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(16)
    font_header = get_font(12, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    # ========== 상단 제목 ==========
    y_start = 15
    draw.text((width // 2, y_start), f"{기본정보['이름']}님 십성 분석표", 
              font=font_title, fill='#FFFFFF', anchor='mm')
    draw.text((width // 2, y_start + 22), f"(일간: {일간} / {일간_오행})", 
              font=font_small, fill='#AAAAAA', anchor='mm')
    
    # ========== 테이블 ==========
    table_y = 55
    
    # 열 너비
    col_widths = [70, 70, 60, 70, 90, 200]  # 분류, 십성, 음양, 오행, 개수, 강도
    row_height = 28
    
    # 헤더
    headers = ['분류', '십성', '음양', '오행', '개수', '강도']
    x = 20
    for i, header in enumerate(headers):
        draw.rectangle([x, table_y, x + col_widths[i], table_y + 30],
                       fill='#444444', outline='#555555')
        draw.text((x + col_widths[i] // 2, table_y + 15), header,
                  font=font_header, fill='#FFFFFF', anchor='mm')
        x += col_widths[i]
    
    # 데이터 행
    current_y = table_y + 30
    
    for 분류_data in 십성_분류:
        분류명 = 분류_data['분류']
        분류_color = 분류_data['color']
        십성들 = 분류_data['십성들']
        
        # 분류별 2행
        for idx, (십성명, 음양) in enumerate(십성들):
            x = 20
            
            # 분류 (첫 행만)
            if idx == 0:
                draw.rectangle([x, current_y, x + col_widths[0], current_y + row_height * 2],
                               fill='#3D3D3D', outline='#555555')
                draw.text((x + col_widths[0] // 2, current_y + row_height),
                          분류명, font=font_medium, fill='#FFFFFF', anchor='mm')
            x += col_widths[0]
            
            # 십성
            draw.rectangle([x, current_y, x + col_widths[1], current_y + row_height],
                           fill=분류_color, outline='#555555')
            draw.text((x + col_widths[1] // 2, current_y + row_height // 2),
                      십성명, font=font_medium, fill='#333333', anchor='mm')
            x += col_widths[1]
            
            # 음양
            음양_color = '#FFCCCC' if 음양 == '양' else '#CCE5FF'
            draw.rectangle([x, current_y, x + col_widths[2], current_y + row_height],
                           fill=음양_color, outline='#555555')
            draw.text((x + col_widths[2] // 2, current_y + row_height // 2),
                      음양, font=font_medium, fill='#333333', anchor='mm')
            x += col_widths[2]
            
            # 오행
            오행 = 십성_오행[십성명]
            오행_bg = 오행_색상[오행]['천간_bg']
            오행_text = 오행_색상[오행]['text']
            draw.rectangle([x, current_y, x + col_widths[3], current_y + row_height],
                           fill=오행_bg, outline='#555555')
            draw.text((x + col_widths[3] // 2, current_y + row_height // 2),
                      오행, font=font_medium, fill=오행_text, anchor='mm')
            x += col_widths[3]
            
            # 개수
            count = 십성_count[십성명]
            draw.rectangle([x, current_y, x + col_widths[4], current_y + row_height],
                           fill='#3D3D3D', outline='#555555')
            count_color = '#FF6B6B' if count >= 3 else '#FFFFFF' if count > 0 else '#666666'
            draw.text((x + col_widths[4] // 2, current_y + row_height // 2),
                      f"{count}개", font=font_medium, fill=count_color, anchor='mm')
            x += col_widths[4]
            
            # 강도
            강도 = get_강도(count)
            강도_color = '#3D3D3D'
            if 강도 == '매우 강함':
                강도_color = '#5C3D3D'
            elif 강도 == '강함':
                강도_color = '#4D4D3D'
            elif 강도 == '없음':
                강도_color = '#3D3D4D'
            
            draw.rectangle([x, current_y, x + col_widths[5], current_y + row_height],
                           fill=강도_color, outline='#555555')
            강도_text_color = '#FF6B6B' if 강도 in ['강함', '매우 강함'] else '#AAAAAA' if 강도 == '없음' else '#FFFFFF'
            draw.text((x + col_widths[5] // 2, current_y + row_height // 2),
                      강도, font=font_medium, fill=강도_text_color, anchor='mm')
            
            current_y += row_height
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 오행 상생상극 다이어그램
# ============================================
import math

def create_오행도(사주_data, 기본정보, output_path="오행도.png"):
    """
    오행 상생상극 원형 다이어그램
    - 오행별 비율 표시
    - 상생(파란색), 상극(빨간색) 화살표
    - 일간 오행 강조
    """
    
    일간 = 사주_data['일주'][0]
    일간_오행 = 천간_오행_map[일간]
    오행 = 사주_data['오행']
    
    # 총 개수 및 비율 계산
    total = sum(오행.values())
    if total == 0:
        total = 1
    
    비율 = {k: round(v / total * 100, 1) for k, v in 오행.items()}
    
    # 십성 매핑 (일간 기준)
    오행_순서 = ['목', '화', '토', '금', '수']
    일간_idx = 오행_순서.index(일간_오행)
    
    십성_매핑 = {
        오행_순서[(일간_idx + 0) % 5]: '비겁',
        오행_순서[(일간_idx + 1) % 5]: '식상',
        오행_순서[(일간_idx + 2) % 5]: '재성',
        오행_순서[(일간_idx + 3) % 5]: '관성',
        오행_순서[(일간_idx + 4) % 5]: '인성',
    }
    
    # 이미지 크기
    width = 550
    height = 550
    
    # 이미지 생성 (다크 테마)
    img = Image.new('RGB', (width, height), '#1E1E1E')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(18)
    font_large = get_font(16, bold=True)
    font_medium = get_font(13)
    font_small = get_font(11)
    
    # ========== 상단 제목 ==========
    draw.text((width // 2, 25), f"나의 오행: {일간}({일간_오행})", 
              font=font_title, fill='#FFFFFF', anchor='mm')
    
    # 범례
    draw.text((50, 55), "→ 상생(生)", font=font_small, fill='#4A90D9', anchor='lm')
    draw.text((150, 55), "→ 상극(剋)", font=font_small, fill='#D94A4A', anchor='lm')
    
    # ========== 오행 원형 배치 ==========
    center_x, center_y = width // 2, height // 2 + 20
    radius = 160  # 중심에서 각 오행 원까지 거리
    circle_radius = 52  # 각 오행 원의 반지름
    
    # 오행 위치 (상단부터 시계방향: 화 -> 토 -> 금 -> 수 -> 목)
    # 전통적 오행 배치와 다르게 변형
    오행_배치 = ['화', '토', '금', '수', '목']  # 상생 순서
    
    positions = {}
    for i, 오행명 in enumerate(오행_배치):
        angle = math.radians(-90 + i * 72)  # 72도씩 (360/5)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions[오행명] = (x, y)
    
    # ========== 상극 화살표 (별 모양 - 먼저 그림) ==========
    상극_관계 = [('목', '토'), ('토', '수'), ('수', '화'), ('화', '금'), ('금', '목')]
    
    for 공격, 피해 in 상극_관계:
        x1, y1 = positions[공격]
        x2, y2 = positions[피해]
        
        # 원 가장자리에서 시작/끝
        angle = math.atan2(y2 - y1, x2 - x1)
        start_x = x1 + (circle_radius + 5) * math.cos(angle)
        start_y = y1 + (circle_radius + 5) * math.sin(angle)
        end_x = x2 - (circle_radius + 15) * math.cos(angle)
        end_y = y2 - (circle_radius + 15) * math.sin(angle)
        
        # 화살표 선
        draw.line([(start_x, start_y), (end_x, end_y)], fill='#D94A4A', width=2)
        
        # 화살표 머리
        arrow_size = 8
        angle1 = angle + math.radians(150)
        angle2 = angle - math.radians(150)
        draw.polygon([
            (end_x, end_y),
            (end_x + arrow_size * math.cos(angle1), end_y + arrow_size * math.sin(angle1)),
            (end_x + arrow_size * math.cos(angle2), end_y + arrow_size * math.sin(angle2))
        ], fill='#D94A4A')
    
    # ========== 상생 화살표 (외곽 곡선) ==========
    상생_관계 = [('목', '화'), ('화', '토'), ('토', '금'), ('금', '수'), ('수', '목')]
    
    for 생, 받 in 상생_관계:
        x1, y1 = positions[생]
        x2, y2 = positions[받]
        
        # 외곽으로 휘어진 곡선 대신 직선 화살표 (외곽쪽으로)
        # 중심점에서 바깥쪽으로 오프셋
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # 중심에서 중간점 방향으로 오프셋
        offset_angle = math.atan2(mid_y - center_y, mid_x - center_x)
        offset_dist = 35
        ctrl_x = mid_x + offset_dist * math.cos(offset_angle)
        ctrl_y = mid_y + offset_dist * math.sin(offset_angle)
        
        # 시작점, 끝점 계산
        angle_start = math.atan2(ctrl_y - y1, ctrl_x - x1)
        angle_end = math.atan2(y2 - ctrl_y, x2 - ctrl_x)
        
        start_x = x1 + (circle_radius + 5) * math.cos(angle_start)
        start_y = y1 + (circle_radius + 5) * math.sin(angle_start)
        end_x = x2 - (circle_radius + 15) * math.cos(angle_end)
        end_y = y2 - (circle_radius + 15) * math.sin(angle_end)
        
        # 곡선 그리기 (여러 점으로 근사)
        points = []
        for t in range(11):
            t = t / 10
            # 2차 베지어 곡선
            px = (1-t)**2 * start_x + 2*(1-t)*t * ctrl_x + t**2 * end_x
            py = (1-t)**2 * start_y + 2*(1-t)*t * ctrl_y + t**2 * end_y
            points.append((px, py))
        
        for j in range(len(points) - 1):
            draw.line([points[j], points[j+1]], fill='#4A90D9', width=2)
        
        # 화살표 머리
        arrow_size = 8
        final_angle = math.atan2(end_y - points[-2][1], end_x - points[-2][0])
        angle1 = final_angle + math.radians(150)
        angle2 = final_angle - math.radians(150)
        draw.polygon([
            (end_x, end_y),
            (end_x + arrow_size * math.cos(angle1), end_y + arrow_size * math.sin(angle1)),
            (end_x + arrow_size * math.cos(angle2), end_y + arrow_size * math.sin(angle2))
        ], fill='#4A90D9')
    
    # ========== 오행 원 그리기 ==========
    오행_원색 = {
        '목': ('#2E7D32', '#4CAF50'),  # 진한/연한 초록
        '화': ('#C62828', '#EF5350'),  # 진한/연한 빨강
        '토': ('#6D4C41', '#A1887F'),  # 진한/연한 갈색
        '금': ('#F9A825', '#FFEB3B'),  # 진한/연한 노랑
        '수': ('#1565C0', '#42A5F5'),  # 진한/연한 파랑
    }
    
    for 오행명, (x, y) in positions.items():
        percent = 비율[오행명]
        십성 = 십성_매핑[오행명]
        진한색, 연한색 = 오행_원색[오행명]
        
        # 일간 오행 강조
        is_일간 = (오행명 == 일간_오행)
        
        # 외곽 원
        outline_color = '#FFFFFF' if is_일간 else '#555555'
        outline_width = 3 if is_일간 else 1
        
        # 원 배경 (연한색)
        draw.ellipse([x - circle_radius, y - circle_radius, 
                      x + circle_radius, y + circle_radius],
                     fill='#2D2D2D', outline=outline_color, width=outline_width)
        
        # 채우기 효과 (아래에서 위로 퍼센트만큼)
        fill_height = int(circle_radius * 2 * percent / 100)
        if fill_height > 0:
            # 채우기 영역 (원 아래쪽부터)
            fill_top = y + circle_radius - fill_height
            
            # 마스크를 사용한 채우기 (간단히 반원으로 근사)
            for dy in range(fill_height):
                cy = y + circle_radius - dy
                # 해당 y에서 원의 x 범위 계산
                if abs(cy - y) <= circle_radius:
                    dx = math.sqrt(circle_radius**2 - (cy - y)**2)
                    draw.line([(x - dx + 2, cy), (x + dx - 2, cy)], fill=연한색, width=1)
        
        # 오행명 + 십성
        draw.text((x, y - 12), f"{오행명}({십성})", 
                  font=font_medium, fill='#FFFFFF', anchor='mm')
        
        # 퍼센트
        percent_color = '#FFFFFF' if percent > 0 else '#666666'
        draw.text((x, y + 12), f"{percent}%", 
                  font=font_large, fill=percent_color, anchor='mm')
    
    # ========== 하단 음양 비율 ==========
    # 천간 음양 카운트
    양_count = 0
    음_count = 0
    
    천간_음양 = {'갑': '양', '을': '음', '병': '양', '정': '음', '무': '양', 
                '기': '음', '경': '양', '신': '음', '임': '양', '계': '음'}
    지지_음양 = {'자': '양', '축': '음', '인': '양', '묘': '음', '진': '양', '사': '음',
                '오': '양', '미': '음', '신': '양', '유': '음', '술': '양', '해': '음'}
    
    for col in ['년', '월', '일', '시']:
        천간 = 사주_data[f'{col}주'][0]
        지지 = 사주_data[f'{col}주'][1]
        if 천간_음양.get(천간) == '양':
            양_count += 1
        else:
            음_count += 1
        if 지지_음양.get(지지) == '양':
            양_count += 1
        else:
            음_count += 1
    
    양_비율 = round(양_count / 8 * 100)
    음_비율 = 100 - 양_비율
    
    # 음양 바
    bar_y = height - 45
    bar_width = 300
    bar_height = 25
    bar_x = (width - bar_width) // 2
    
    # 배경
    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                   fill='#3D3D3D', outline='#555555')
    
    # 양 (왼쪽, 밝은색)
    양_width = int(bar_width * 양_비율 / 100)
    if 양_width > 0:
        draw.rectangle([bar_x, bar_y, bar_x + 양_width, bar_y + bar_height],
                       fill='#F5F5F5')
    
    # 텍스트
    draw.text((bar_x - 10, bar_y + bar_height // 2), f"양 {양_비율}%", 
              font=font_small, fill='#F5F5F5', anchor='rm')
    draw.text((bar_x + bar_width + 10, bar_y + bar_height // 2), f"음 {음_비율}%", 
              font=font_small, fill='#A5D6A7', anchor='lm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path
