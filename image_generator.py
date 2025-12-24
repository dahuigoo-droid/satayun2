# 사주 원국표 이미지 생성기
from PIL import Image, ImageDraw, ImageFont
import os

# ============================================
# 지지 이모지 및 동물 이름 매핑
# ============================================
지지_이모지 = {
    '자': '🐀', '축': '🐂', '인': '🐅', '묘': '🐇',
    '진': '🐉', '사': '🐍', '오': '🐴', '미': '🐏',
    '신': '🐒', '유': '🐓', '술': '🐕', '해': '🐖',
}

지지_동물 = {
    '자': '쥐', '축': '소', '인': '호랑이', '묘': '토끼',
    '진': '용', '사': '뱀', '오': '말', '미': '양',
    '신': '원숭이', '유': '닭', '술': '개', '해': '돼지',
}

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

def get_emoji_font(size):
    """이모지 폰트 로드"""
    emoji_paths = [
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    
    for path in emoji_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    
    return None

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
def create_원국표(사주_data, 기본정보, output_path="원국표.png", 신살_data=None):
    """
    원국표 이미지 생성
    
    사주_data: calc_사주() 결과
    기본정보: {'이름': ..., '성별': ..., '나이': ..., '양력': ..., '음력': ...}
    신살_data: calc_신살() 결과 (optional)
    """
    
    # 이미지 크기 (신살 있으면 높이 증가)
    width = 600
    height = 505 if 신살_data else 445
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(14)
    font_large = get_font(36, bold=True)
    font_medium = get_font(14)
    font_small = get_font(12)
    font_tiny = get_font(9)
    
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
    cell_width = 120
    cell_height_header = 30
    cell_height_main = 70
    cell_height_sub = 25
    label_width = 65
    
    # 테이블 중앙 정렬
    table_width = label_width + (cell_width * 4)
    margin_x = (width - table_width) // 2
    
    headers = ['생시', '생일', '생월', '생년']
    columns = ['시', '일', '월', '년']
    
    # 헤더 행
    draw.rectangle([margin_x + label_width, table_y, margin_x + table_width, table_y + cell_height_header], 
                   fill='#F5F5F5', outline='#E0E0E0')
    
    for i, header in enumerate(headers):
        x = margin_x + label_width + i * cell_width + cell_width // 2
        draw.text((x, table_y + 8), header, font=font_medium, fill='#666666', anchor='mm')
    
    current_y = table_y + cell_height_header
    
    # ========== 천간십성 행 ==========
    draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((margin_x + label_width // 2, current_y + cell_height_sub // 2), "천간십성", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = margin_x + label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        십성 = 사주_data['천간십성'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  십성, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 천간 행 ==========
    draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((margin_x + label_width // 2, current_y + cell_height_main // 2), "천간", 
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = margin_x + label_width + i * cell_width
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
    draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_main],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((margin_x + label_width // 2, current_y + cell_height_main // 2), "지지", 
              font=font_medium, fill='#666666', anchor='mm')
    
    # 이모지 폰트 로드 시도
    emoji_font = get_emoji_font(20)
    
    for i, col in enumerate(columns):
        x = margin_x + label_width + i * cell_width
        
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
        
        # 지지(한자)
        한자 = 지지_한자[지지]
        display_text = f"{지지}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2 - 15), 
                  display_text, font=font_large, fill=text_color, anchor='mm')
        
        # 동물 이름 표시 (이모지 대신)
        동물 = 지지_동물[지지]
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2 + 15), 
                  동물, font=font_small, fill=text_color, anchor='mm')
        
        # 오행 표시
        오행_text = f"{오행}"
        draw.text((x + cell_width - 15, current_y + cell_height_main - 15), 
                  오행_text, font=font_small, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지십성 행 ==========
    draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((margin_x + label_width // 2, current_y + cell_height_sub // 2), "지지십성", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = margin_x + label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        십성 = 사주_data['지지십성'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  십성, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 지장간 행 ==========
    draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((margin_x + label_width // 2, current_y + cell_height_sub // 2), "지장간", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = margin_x + label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        지장간 = 사주_data['지장간'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  지장간, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 12운성 행 ==========
    draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((margin_x + label_width // 2, current_y + cell_height_sub // 2), "12운성", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = margin_x + label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        운성 = 사주_data['12운성'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  운성, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 12신살 행 ==========
    draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_sub],
                   fill='#F9F9F9', outline='#E0E0E0')
    draw.text((margin_x + label_width // 2, current_y + cell_height_sub // 2), "12신살", 
              font=font_small, fill='#666666', anchor='mm')
    
    for i, col in enumerate(columns):
        x = margin_x + label_width + i * cell_width
        draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                       fill='#FFFFFF', outline='#E0E0E0')
        신살 = 사주_data['12신살'][col]
        draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                  신살, font=font_small, fill='#888888', anchor='mm')
    
    current_y += cell_height_sub
    
    # ========== 신살 행 (옵션) ==========
    if 신살_data:
        cell_height_sinsal = 45
        
        # 천간 신살 행
        draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_sub],
                       fill='#FFF9E6', outline='#E0E0E0')
        draw.text((margin_x + label_width // 2, current_y + cell_height_sub // 2), "천간신살", 
                  font=font_small, fill='#666666', anchor='mm')
        
        for i, col in enumerate(columns):
            x = margin_x + label_width + i * cell_width
            draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sub],
                           fill='#FFFDF5', outline='#E0E0E0')
            신살_list = 신살_data['천간신살'][col]
            if 신살_list:
                신살_text = '\n'.join(신살_list[:2])  # 최대 2개만
                draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                          신살_text, font=font_tiny, fill='#996600', anchor='mm')
            else:
                draw.text((x + cell_width // 2, current_y + cell_height_sub // 2), 
                          '×', font=font_small, fill='#CCCCCC', anchor='mm')
        
        current_y += cell_height_sub
        
        # 지지 신살 행
        draw.rectangle([margin_x, current_y, margin_x + label_width, current_y + cell_height_sinsal],
                       fill='#F0F9FF', outline='#E0E0E0')
        draw.text((margin_x + label_width // 2, current_y + cell_height_sinsal // 2), "지지신살", 
                  font=font_small, fill='#666666', anchor='mm')
        
        for i, col in enumerate(columns):
            x = margin_x + label_width + i * cell_width
            draw.rectangle([x, current_y, x + cell_width, current_y + cell_height_sinsal],
                           fill='#F8FCFF', outline='#E0E0E0')
            신살_list = 신살_data['지지신살'][col]
            if 신살_list:
                신살_text = '\n'.join(신살_list[:3])  # 최대 3개만
                draw.text((x + cell_width // 2, current_y + cell_height_sinsal // 2), 
                          신살_text, font=font_tiny, fill='#006699', anchor='mm')
            else:
                draw.text((x + cell_width // 2, current_y + cell_height_sinsal // 2), 
                          '×', font=font_small, fill='#CCCCCC', anchor='mm')
        
        current_y += cell_height_sinsal
    
    # ========== 오행 분포 ==========
    current_y += 20
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
    대운표 이미지 생성 (100세+ 지원)
    """
    
    대운_list = 대운_data['대운']
    대운수 = 대운_data['대운수']
    순행 = 대운_data['순행']
    사주 = 대운_data['사주']
    일간 = 사주['일주'][0]
    
    # 이미지 크기 (좌우 여백 추가)
    margin = 25
    num_cols = len(대운_list)
    cell_width = 75
    label_width = 60
    content_width = label_width + (cell_width * num_cols)
    width = content_width + (margin * 2)
    height = 320
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트 (가독성 개선)
    font_title = get_font(15)
    font_large = get_font(22, bold=True)
    font_medium = get_font(12)
    font_small = get_font(11)
    
    # ========== 상단 제목 ==========
    y_start = 18
    방향 = "순행" if 순행 else "역행"
    title = f"{기본정보['이름']}님 대운표 (대운수:{대운수}, {방향})"
    draw.text((width // 2, y_start), title, font=font_title, fill='#333333', anchor='mm')
    
    # ========== 대운표 테이블 ==========
    table_y = 45
    cell_height_small = 28
    cell_height_main = 50
    border_color = '#CCCCCC'
    border_width = 2
    
    current_y = table_y
    start_x = margin
    
    # ========== 나이 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#E8E8E8', outline=border_color, width=border_width)
    
    for i, 대운 in enumerate(대운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#F5F5F5', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  str(대운['나이']), font=font_medium, fill='#333333', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 십성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  대운['천간_십성'], font=font_small, fill='#666666', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_main],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_main // 2), "천간",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = start_x + label_width + i * cell_width
        천간 = 대운['천간']
        오행 = 천간_오행_map[천간]
        bg_color = 오행_색상[오행]['천간_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                               radius=3, fill=bg_color, outline=border_color, width=border_width)
        
        한자 = 천간_한자[천간]
        display_text = f"{천간}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2 - 5),
                  display_text, font=font_large, fill=text_color, anchor='mm')
        draw.text((x + cell_width - 12, current_y + cell_height_main - 10),
                  오행, font=font_small, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_main],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_main // 2), "지지",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = start_x + label_width + i * cell_width
        지지 = 대운['지지']
        오행 = 지지_오행_map[지지]
        bg_color = 오행_색상[오행]['지지_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                               radius=3, fill=bg_color, outline=border_color, width=border_width)
        
        한자 = 지지_한자[지지]
        display_text = f"{지지}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2 - 5),
                  display_text, font=font_large, fill=text_color, anchor='mm')
        draw.text((x + cell_width - 12, current_y + cell_height_main - 10),
                  오행, font=font_small, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 십성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "지지십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  대운['지지_십성'], font=font_small, fill='#666666', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12운성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "12운성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  대운['12운성'], font=font_small, fill='#666666', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12신살 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "12신살",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 대운 in enumerate(대운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  대운['12신살'], font=font_small, fill='#666666', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 세운표 이미지 생성
# ============================================
def create_세운표(세운_data, 기본정보, output_path="세운표.png"):
    """
    세운표 이미지 생성 (당해년부터 10년)
    """
    
    세운_list = 세운_data['세운']
    사주 = 세운_data['사주']
    일간 = 사주['일주'][0]
    
    # 이미지 크기 (좌우 여백 추가)
    margin = 25
    num_cols = len(세운_list)
    cell_width = 70
    label_width = 60
    content_width = label_width + (cell_width * num_cols)
    width = content_width + (margin * 2)
    height = 310
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트 (가독성 개선)
    font_title = get_font(15)
    font_large = get_font(20, bold=True)
    font_medium = get_font(12)
    font_small = get_font(11)
    
    # ========== 상단 제목 ==========
    y_start = 18
    draw.text((width // 2, y_start), f"{기본정보['이름']}님 세운표 (10년)", font=font_title, fill='#333333', anchor='mm')
    
    # ========== 테이블 ==========
    table_y = 45
    cell_height_small = 26
    cell_height_main = 48
    border_color = '#CCCCCC'
    border_width = 2
    start_x = margin
    
    current_y = table_y
    
    # ========== 년도 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#E8E8E8', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "년도",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#F5F5F5', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  str(세운['년도']), font=font_small, fill='#333333', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 나이 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#E8E8E8', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "나이",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#F5F5F5', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  str(세운['나이']), font=font_small, fill='#333333', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 십성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  세운['천간_십성'], font=font_small, fill='#666666', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_main],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_main // 2), "천간",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = start_x + label_width + i * cell_width
        천간 = 세운['천간']
        오행 = 천간_오행_map[천간]
        bg_color = 오행_색상[오행]['천간_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                               radius=3, fill=bg_color, outline=border_color, width=border_width)
        
        한자 = 천간_한자[천간]
        display_text = f"{천간}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2),
                  display_text, font=font_large, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_main],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_main // 2), "지지",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = start_x + label_width + i * cell_width
        지지 = 세운['지지']
        오행 = 지지_오행_map[지지]
        bg_color = 오행_색상[오행]['지지_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                               radius=3, fill=bg_color, outline=border_color, width=border_width)
        
        한자 = 지지_한자[지지]
        display_text = f"{지지}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2),
                  display_text, font=font_large, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 십성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "지지십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  세운['지지_십성'], font=font_small, fill='#666666', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12운성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "12운성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 세운 in enumerate(세운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  세운['12운성'], font=font_small, fill='#666666', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 월운표 이미지 생성
# ============================================
def create_월운표(월운_data, 기본정보, output_path="월운표.png"):
    """
    월운표 이미지 생성 (당해월부터 12개월)
    """
    
    월운_list = 월운_data['월운']
    시작년 = 월운_data.get('시작년', 월운_data.get('년도', 2025))
    시작월 = 월운_data.get('시작월', 1)
    사주 = 월운_data['사주']
    
    # 이미지 크기 (좌우 여백 추가)
    margin = 25
    num_cols = 12
    cell_width = 68
    label_width = 55
    content_width = label_width + (cell_width * num_cols)
    width = content_width + (margin * 2)
    height = 290
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트 (가독성 개선)
    font_title = get_font(15)
    font_large = get_font(18, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    # ========== 상단 제목 ==========
    y_start = 18
    draw.text((width // 2, y_start), f"{기본정보['이름']}님 월운표 ({시작년}.{시작월}월~)", 
              font=font_title, fill='#333333', anchor='mm')
    
    # ========== 테이블 ==========
    table_y = 45
    cell_height_small = 26
    cell_height_main = 44
    border_color = '#CCCCCC'
    border_width = 2
    start_x = margin
    
    current_y = table_y
    
    # ========== 년월 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#E8E8E8', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "년월",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#F5F5F5', outline=border_color, width=border_width)
        년도 = 월운.get('년도', 시작년)
        월 = 월운['월']
        # 년도 축약 (2025 → 25)
        년도_short = str(년도)[-2:]
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  f"{년도_short}.{월}월", font=font_small, fill='#333333', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 십성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  월운['천간_십성'], font=font_small, fill='#666666', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 천간 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_main],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_main // 2), "천간",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = start_x + label_width + i * cell_width
        천간 = 월운['천간']
        오행 = 천간_오행_map[천간]
        bg_color = 오행_색상[오행]['천간_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                               radius=3, fill=bg_color, outline=border_color, width=border_width)
        
        한자 = 천간_한자[천간]
        display_text = f"{천간}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2),
                  display_text, font=font_large, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_main],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_main // 2), "지지",
              font=font_medium, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = start_x + label_width + i * cell_width
        지지 = 월운['지지']
        오행 = 지지_오행_map[지지]
        bg_color = 오행_색상[오행]['지지_bg']
        text_color = 오행_색상[오행]['text']
        
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_main],
                               radius=3, fill=bg_color, outline=border_color, width=border_width)
        
        한자 = 지지_한자[지지]
        display_text = f"{지지}({한자})"
        draw.text((x + cell_width // 2, current_y + cell_height_main // 2),
                  display_text, font=font_large, fill=text_color, anchor='mm')
    
    current_y += cell_height_main
    
    # ========== 지지 십성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "지지십성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  월운['지지_십성'], font=font_small, fill='#666666', anchor='mm')
    
    current_y += cell_height_small
    
    # ========== 12운성 행 ==========
    draw.rounded_rectangle([start_x, current_y, start_x + label_width, current_y + cell_height_small],
                           radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
    draw.text((start_x + label_width // 2, current_y + cell_height_small // 2), "12운성",
              font=font_small, fill='#666666', anchor='mm')
    
    for i, 월운 in enumerate(월운_list):
        x = start_x + label_width + i * cell_width
        draw.rounded_rectangle([x, current_y, x + cell_width, current_y + cell_height_small],
                               radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
        draw.text((x + cell_width // 2, current_y + cell_height_small // 2),
                  월운['12운성'], font=font_small, fill='#666666', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 오행 차트 이미지 생성
# ============================================
def create_오행차트(사주_data, 기본정보, output_path="오행차트.png"):
    """
    오행 분포 + 상생상극 통합 이미지
    - 좌측: 막대 그래프
    - 우측: 상생상극 다이어그램
    """
    import math
    
    일간 = 사주_data['일주'][0]
    일간_오행 = 천간_오행_map[일간]
    오행 = 사주_data['오행']
    
    # 이미지 크기
    width = 850
    height = 420
    margin = 25
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(16)
    font_large = get_font(14, bold=True)
    font_medium = get_font(12)
    font_small = get_font(11)
    
    # 오행 색상
    chart_colors = {
        '목': '#4CAF50', '화': '#F44336', '토': '#795548', 
        '금': '#FFC107', '수': '#2196F3',
    }
    
    # ========== 상단 제목 ==========
    draw.text((width // 2, 22), f"{기본정보['이름']}님 오행 분석", 
              font=font_title, fill='#333333', anchor='mm')
    
    # ========== 좌측: 막대 그래프 ==========
    left_section_width = 380
    chart_x = margin + 30
    chart_y = 70
    chart_height = 180
    bar_width = 50
    gap = 15
    
    # 섹션 제목
    draw.text((chart_x + 130, 50), "[ 오행 분포 ]", font=font_medium, fill='#666666', anchor='mm')
    
    오행_목록 = ['목', '화', '토', '금', '수']
    max_val = max(오행.values()) if max(오행.values()) > 0 else 1
    
    for i, 오행명 in enumerate(오행_목록):
        x = chart_x + i * (bar_width + gap)
        값 = 오행[오행명]
        
        # 막대 높이 계산
        bar_height = int((값 / max_val) * chart_height) if 값 > 0 else 8
        
        # 막대 그리기 (라운드)
        bar_y = chart_y + chart_height - bar_height
        draw.rounded_rectangle([x, bar_y, x + bar_width, chart_y + chart_height],
                               radius=5, fill=chart_colors[오행명], outline='#666666', width=2)
        
        # 값 표시
        draw.text((x + bar_width // 2, bar_y - 15),
                  str(값), font=font_large, fill='#333333', anchor='mm')
        
        # 오행명 표시
        draw.text((x + bar_width // 2, chart_y + chart_height + 20),
                  오행명, font=font_medium, fill='#333333', anchor='mm')
    
    # 요약 정보
    total = sum(오행.values())
    draw.text((chart_x + 130, chart_y + chart_height + 55),
              f"총 {total}개 | 일간: {일간}({일간_오행})",
              font=font_small, fill='#666666', anchor='mm')
    
    # 강한/약한 오행
    sorted_오행 = sorted(오행.items(), key=lambda x: x[1], reverse=True)
    강한 = sorted_오행[0][0] if sorted_오행[0][1] > 0 else "-"
    약한 = sorted_오행[-1][0]
    draw.text((chart_x + 130, chart_y + chart_height + 78),
              f"강: {강한} | 약: {약한}",
              font=font_small, fill='#888888', anchor='mm')
    
    # ========== 우측: 상생상극도 ==========
    right_x = left_section_width + 60
    center_x = right_x + 190
    center_y = height // 2 + 15
    radius = 120
    circle_radius = 38
    
    # 섹션 제목
    draw.text((center_x, 50), "[ 상생상극 관계 ]", font=font_medium, fill='#666666', anchor='mm')
    
    # 범례
    draw.text((center_x - 55, height - 35), "→ 상생", font=font_small, fill='#1565C0', anchor='mm')
    draw.text((center_x + 55, height - 35), "→ 상극", font=font_small, fill='#C62828', anchor='mm')
    
    # 오행 위치 계산
    오행_배치 = ['화', '토', '금', '수', '목']
    positions = {}
    for i, 오행명 in enumerate(오행_배치):
        angle = math.radians(-90 + i * 72)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions[오행명] = (x, y)
    
    # 상극 화살표 (빨간색)
    상극_관계 = [('목', '토'), ('토', '수'), ('수', '화'), ('화', '금'), ('금', '목')]
    for 공격, 피해 in 상극_관계:
        x1, y1 = positions[공격]
        x2, y2 = positions[피해]
        angle = math.atan2(y2 - y1, x2 - x1)
        start_x = x1 + (circle_radius + 5) * math.cos(angle)
        start_y = y1 + (circle_radius + 5) * math.sin(angle)
        end_x = x2 - (circle_radius + 12) * math.cos(angle)
        end_y = y2 - (circle_radius + 12) * math.sin(angle)
        draw.line([(start_x, start_y), (end_x, end_y)], fill='#C62828', width=2)
        # 화살표 머리
        arrow_size = 7
        angle1 = angle + math.radians(150)
        angle2 = angle - math.radians(150)
        draw.polygon([
            (end_x, end_y),
            (end_x + arrow_size * math.cos(angle1), end_y + arrow_size * math.sin(angle1)),
            (end_x + arrow_size * math.cos(angle2), end_y + arrow_size * math.sin(angle2))
        ], fill='#C62828')
    
    # 상생 화살표 (파란색)
    상생_관계 = [('목', '화'), ('화', '토'), ('토', '금'), ('금', '수'), ('수', '목')]
    for 생, 받 in 상생_관계:
        x1, y1 = positions[생]
        x2, y2 = positions[받]
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        offset_angle = math.atan2(mid_y - center_y, mid_x - center_x)
        offset_dist = 25
        ctrl_x = mid_x + offset_dist * math.cos(offset_angle)
        ctrl_y = mid_y + offset_dist * math.sin(offset_angle)
        
        angle_start = math.atan2(ctrl_y - y1, ctrl_x - x1)
        angle_end = math.atan2(y2 - ctrl_y, x2 - ctrl_x)
        sx = x1 + (circle_radius + 3) * math.cos(angle_start)
        sy = y1 + (circle_radius + 3) * math.sin(angle_start)
        ex = x2 - (circle_radius + 10) * math.cos(angle_end)
        ey = y2 - (circle_radius + 10) * math.sin(angle_end)
        draw.line([(sx, sy), (ctrl_x, ctrl_y), (ex, ey)], fill='#1565C0', width=2)
        # 화살표 머리
        arrow_size = 7
        angle1 = angle_end + math.radians(150)
        angle2 = angle_end - math.radians(150)
        draw.polygon([
            (ex, ey),
            (ex + arrow_size * math.cos(angle1), ey + arrow_size * math.sin(angle1)),
            (ex + arrow_size * math.cos(angle2), ey + arrow_size * math.sin(angle2))
        ], fill='#1565C0')
    
    # 오행 원 그리기
    for 오행명, (x, y) in positions.items():
        값 = 오행[오행명]
        is_일간 = (오행명 == 일간_오행)
        
        # 원 테두리
        outline_color = '#333333' if is_일간 else '#AAAAAA'
        outline_width = 3 if is_일간 else 2
        
        draw.ellipse([x - circle_radius, y - circle_radius, 
                      x + circle_radius, y + circle_radius],
                     fill=chart_colors[오행명], outline=outline_color, width=outline_width)
        
        # 오행명
        draw.text((x, y - 8), 오행명, font=font_large, fill='#FFFFFF', anchor='mm')
        # 개수
        draw.text((x, y + 12), f"{값}개", font=font_small, fill='#FFFFFF', anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 십성표 이미지 생성
# ============================================
def create_십성표(사주_data, 기본정보, output_path="십성표.png"):
    """
    십성 분석표 이미지 생성 (유무+보조+키워드 구조)
    """
    
    일간 = 사주_data['일주'][0]
    일간_오행 = 천간_오행_map[일간]
    
    # 천간/지지 십성 위치 확인
    십성_위치 = {
        '비견': [], '겁재': [],
        '식신': [], '상관': [],
        '편재': [], '정재': [],
        '편관': [], '정관': [],
        '편인': [], '정인': [],
    }
    
    # 천간 십성 위치
    for col in ['년', '월', '시']:
        십성 = 사주_data['천간십성'][col]
        if 십성 in 십성_위치:
            십성_위치[십성].append(f"{col}간")
    
    # 지지 십성 위치 (본원 기준)
    for col in ['년', '월', '일', '시']:
        십성 = 사주_data['지지십성'][col]
        if 십성 in 십성_위치:
            십성_위치[십성].append(f"{col}지")
    
    # 십성별 오행 매핑 (일간 기준)
    오행_순서 = ['목', '화', '토', '금', '수']
    일간_오행_idx = 오행_순서.index(일간_오행)
    
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
    
    # 키워드 정의
    키워드_표 = {
        '비견': '자아확장, 협업/대립, 자존',
        '겁재': '돌파, 확보, 생존경쟁',
        '식신': '생산, 실행, 결과 창출',
        '상관': '창의력, 재구성, 영향력',
        '편재': '사업, 거래, 기회포착',
        '정재': '안정자산, 관리, 현실주의',
        '편관': '도전, 경쟁적 압력, 시험',
        '정관': '규율, 명예, 직업/제도',
        '편인': '특수지식, 독립적 학습',
        '정인': '지지, 보호, 정서 기반',
    }
    
    # 십성 분류 데이터
    십성_분류 = [
        {'분류': '비겁', '십성들': [('비견', '양'), ('겁재', '음')], 'color': '#A8D5BA'},
        {'분류': '식상', '십성들': [('식신', '양'), ('상관', '음')], 'color': '#87CEEB'},
        {'분류': '재성', '십성들': [('편재', '양'), ('정재', '음')], 'color': '#90EE90'},
        {'분류': '관성', '십성들': [('편관', '양'), ('정관', '음')], 'color': '#FFB6C1'},
        {'분류': '인성', '십성들': [('편인', '양'), ('정인', '음')], 'color': '#FFFACD'},
    ]
    
    # 이미지 크기 (여백 최소화)
    width = 520
    height = 400
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(16)
    font_header = get_font(12, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    # ========== 상단 제목 ==========
    draw.text((width // 2, 20), f"{기본정보['이름']}님 십성 분석표", 
              font=font_title, fill='#333333', anchor='mm')
    draw.text((width // 2, 42), f"(일간: {일간} / {일간_오행})", 
              font=font_small, fill='#666666', anchor='mm')
    
    # ========== 테이블 ==========
    table_y = 62
    col_widths = [50, 50, 40, 45, 45, 55, 175]  # 분류, 십성, 음양, 오행, 유무, 보조, 키워드
    total_width = sum(col_widths)
    start_x = (width - total_width) // 2
    row_height = 30
    border_color = '#CCCCCC'
    border_width = 2
    
    # 헤더
    headers = ['분류', '십성', '음양', '오행', '유무', '보조', '키워드']
    x = start_x
    for i, header in enumerate(headers):
        draw.rounded_rectangle([x, table_y, x + col_widths[i], table_y + 30],
                               radius=3, fill='#E0E0E0', outline=border_color, width=border_width)
        draw.text((x + col_widths[i] // 2, table_y + 15), header,
                  font=font_header, fill='#333333', anchor='mm')
        x += col_widths[i]
    
    # 데이터 행
    current_y = table_y + 30
    
    for 분류_data in 십성_분류:
        분류명 = 분류_data['분류']
        분류_color = 분류_data['color']
        십성들 = 분류_data['십성들']
        
        for idx, (십성명, 음양) in enumerate(십성들):
            x = start_x
            
            # 분류 (첫 행만 병합)
            if idx == 0:
                draw.rounded_rectangle([x, current_y, x + col_widths[0], current_y + row_height * 2],
                                       radius=3, fill='#F5F5F5', outline=border_color, width=border_width)
                draw.text((x + col_widths[0] // 2, current_y + row_height),
                          분류명, font=font_medium, fill='#333333', anchor='mm')
            x += col_widths[0]
            
            # 십성
            draw.rounded_rectangle([x, current_y, x + col_widths[1], current_y + row_height],
                                   radius=3, fill=분류_color, outline=border_color, width=border_width)
            draw.text((x + col_widths[1] // 2, current_y + row_height // 2),
                      십성명, font=font_medium, fill='#333333', anchor='mm')
            x += col_widths[1]
            
            # 음양
            음양_color = '#FFEBEE' if 음양 == '양' else '#E3F2FD'
            draw.rounded_rectangle([x, current_y, x + col_widths[2], current_y + row_height],
                                   radius=3, fill=음양_color, outline=border_color, width=border_width)
            draw.text((x + col_widths[2] // 2, current_y + row_height // 2),
                      음양, font=font_medium, fill='#333333', anchor='mm')
            x += col_widths[2]
            
            # 오행
            오행 = 십성_오행[십성명]
            오행_bg = 오행_색상[오행]['천간_bg']
            오행_text = 오행_색상[오행]['text']
            draw.rounded_rectangle([x, current_y, x + col_widths[3], current_y + row_height],
                                   radius=3, fill=오행_bg, outline=border_color, width=border_width)
            draw.text((x + col_widths[3] // 2, current_y + row_height // 2),
                      오행, font=font_medium, fill=오행_text, anchor='mm')
            x += col_widths[3]
            
            # 유무 (천간+지지 본원에 있는지)
            위치들 = 십성_위치[십성명]
            if len(위치들) > 0:
                유무 = "O"
                유무_color = '#E8F5E9'
                유무_text_color = '#2E7D32'
            else:
                유무 = "X"
                유무_color = '#FFEBEE'
                유무_text_color = '#C62828'
            
            draw.rounded_rectangle([x, current_y, x + col_widths[4], current_y + row_height],
                                   radius=3, fill=유무_color, outline=border_color, width=border_width)
            draw.text((x + col_widths[4] // 2, current_y + row_height // 2),
                      유무, font=font_header, fill=유무_text_color, anchor='mm')
            x += col_widths[4]
            
            # 보조 (지장간에만 있는 경우 표시)
            보조 = ""
            if len(위치들) > 0:
                보조 = ", ".join(위치들[:2])  # 최대 2개만 표시
            draw.rounded_rectangle([x, current_y, x + col_widths[5], current_y + row_height],
                                   radius=3, fill='#FAFAFA', outline=border_color, width=border_width)
            draw.text((x + col_widths[5] // 2, current_y + row_height // 2),
                      보조, font=font_small, fill='#666666', anchor='mm')
            x += col_widths[5]
            
            # 키워드
            키워드 = 키워드_표.get(십성명, "")
            draw.rounded_rectangle([x, current_y, x + col_widths[6], current_y + row_height],
                                   radius=3, fill='#FFFFFF', outline=border_color, width=border_width)
            draw.text((x + col_widths[6] // 2, current_y + row_height // 2),
                      키워드, font=font_small, fill='#555555', anchor='mm')
            
            current_y += row_height
    
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
    
    # 이미지 생성 (라이트 테마)
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(18)
    font_large = get_font(16, bold=True)
    font_medium = get_font(13)
    font_small = get_font(11)
    
    # ========== 상단 제목 ==========
    draw.text((width // 2, 25), f"나의 오행: {일간}({일간_오행})", 
              font=font_title, fill='#333333', anchor='mm')
    
    # 범례 (중앙 정렬)
    draw.text((width // 2 - 60, 55), "→ 상생(生)", font=font_small, fill='#1565C0', anchor='lm')
    draw.text((width // 2 + 30, 55), "→ 상극(剋)", font=font_small, fill='#C62828', anchor='lm')
    
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
        draw.line([(start_x, start_y), (end_x, end_y)], fill='#C62828', width=2)
        
        # 화살표 머리
        arrow_size = 8
        angle1 = angle + math.radians(150)
        angle2 = angle - math.radians(150)
        draw.polygon([
            (end_x, end_y),
            (end_x + arrow_size * math.cos(angle1), end_y + arrow_size * math.sin(angle1)),
            (end_x + arrow_size * math.cos(angle2), end_y + arrow_size * math.sin(angle2))
        ], fill='#C62828')
    
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
            draw.line([points[j], points[j+1]], fill='#1565C0', width=2)
        
        # 화살표 머리
        arrow_size = 8
        final_angle = math.atan2(end_y - points[-2][1], end_x - points[-2][0])
        angle1 = final_angle + math.radians(150)
        angle2 = final_angle - math.radians(150)
        draw.polygon([
            (end_x, end_y),
            (end_x + arrow_size * math.cos(angle1), end_y + arrow_size * math.sin(angle1)),
            (end_x + arrow_size * math.cos(angle2), end_y + arrow_size * math.sin(angle2))
        ], fill='#1565C0')
    
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
        outline_color = '#333333' if is_일간 else '#CCCCCC'
        outline_width = 3 if is_일간 else 1
        
        # 원 배경 (라이트 테마)
        draw.ellipse([x - circle_radius, y - circle_radius, 
                      x + circle_radius, y + circle_radius],
                     fill='#F5F5F5', outline=outline_color, width=outline_width)
        
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
                  font=font_medium, fill='#333333', anchor='mm')
        
        # 퍼센트
        percent_color = '#333333' if percent > 0 else '#BDBDBD'
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
    
    # 배경 (라이트 테마)
    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                   fill='#E0E0E0', outline='#CCCCCC')
    
    # 양 (왼쪽, 밝은색)
    양_width = int(bar_width * 양_비율 / 100)
    if 양_width > 0:
        draw.rectangle([bar_x, bar_y, bar_x + 양_width, bar_y + bar_height],
                       fill='#FFCCCC')
    
    # 텍스트
    draw.text((bar_x - 10, bar_y + bar_height // 2), f"양 {양_비율}%", 
              font=font_small, fill='#C62828', anchor='rm')
    draw.text((bar_x + bar_width + 10, bar_y + bar_height // 2), f"음 {음_비율}%", 
              font=font_small, fill='#1565C0', anchor='lm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 신살표 이미지 생성
# ============================================
def create_신살표(신살_data, 기본정보, output_path="신살표.png"):
    """
    신살 분석표 이미지 생성 (길신/흉신 분리) - 라이트 테마
    """
    
    길신 = 신살_data['길신']
    흉신 = 신살_data['흉신']
    특수신살 = 신살_data['특수신살']
    
    # 최대 행 수 계산
    max_rows = max(len(길신), len(흉신), len(특수신살), 1)
    
    # 이미지 크기 (동적 높이)
    width = 650
    row_height = 30
    table_y = 55
    header_height = 35
    table_height = header_height + (max_rows * row_height) + 30
    summary_height = 55
    height = table_y + table_height + summary_height + 10
    
    # 이미지 생성 (라이트 테마)
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 폰트
    font_title = get_font(18)
    font_header = get_font(14, bold=True)
    font_medium = get_font(12)
    font_small = get_font(11)
    
    # ========== 상단 제목 ==========
    y_start = 18
    draw.text((width // 2, y_start), f"{기본정보['이름']}님 신살 분석표", 
              font=font_title, fill='#333333', anchor='mm')
    
    # ========== 3열 레이아웃 ==========
    col_width = 200
    col_gap = 12
    start_x = (width - (col_width * 3 + col_gap * 2)) // 2
    
    # ========== 길신 열 ==========
    col1_x = start_x
    
    # 헤더 (파스텔 블루)
    draw.rectangle([col1_x, table_y, col1_x + col_width, table_y + header_height],
                   fill='#E3F2FD', outline='#90CAF9')
    draw.text((col1_x + col_width // 2, table_y + header_height // 2), 
              "[길신]", font=font_header, fill='#1565C0', anchor='mm')
    
    # 길신 목록
    current_y = table_y + header_height
    
    if 길신:
        for 신살명, 위치 in 길신:
            draw.rectangle([col1_x, current_y, col1_x + col_width, current_y + row_height],
                           fill='#F5F5F5', outline='#E0E0E0')
            draw.text((col1_x + 10, current_y + row_height // 2), 
                      f"{신살명}", font=font_medium, fill='#1565C0', anchor='lm')
            draw.text((col1_x + col_width - 10, current_y + row_height // 2), 
                      f"({위치})", font=font_small, fill='#42A5F5', anchor='rm')
            current_y += row_height
    else:
        draw.rectangle([col1_x, current_y, col1_x + col_width, current_y + row_height],
                       fill='#F5F5F5', outline='#E0E0E0')
        draw.text((col1_x + col_width // 2, current_y + row_height // 2), 
                  "-", font=font_medium, fill='#BDBDBD', anchor='mm')
        current_y += row_height
    
    # 길신 개수
    count_y = table_y + header_height + (max_rows * row_height) + 8
    draw.text((col1_x + col_width // 2, count_y), 
              f"총 {len(길신)}개", font=font_small, fill='#1565C0', anchor='mm')
    
    # ========== 흉신 열 ==========
    col2_x = start_x + col_width + col_gap
    
    # 헤더 (파스텔 핑크)
    draw.rectangle([col2_x, table_y, col2_x + col_width, table_y + header_height],
                   fill='#FFEBEE', outline='#FFCDD2')
    draw.text((col2_x + col_width // 2, table_y + header_height // 2), 
              "[흉신]", font=font_header, fill='#C62828', anchor='mm')
    
    # 흉신 목록
    current_y = table_y + header_height
    
    if 흉신:
        for 신살명, 위치 in 흉신:
            draw.rectangle([col2_x, current_y, col2_x + col_width, current_y + row_height],
                           fill='#F5F5F5', outline='#E0E0E0')
            draw.text((col2_x + 10, current_y + row_height // 2), 
                      f"{신살명}", font=font_medium, fill='#C62828', anchor='lm')
            draw.text((col2_x + col_width - 10, current_y + row_height // 2), 
                      f"({위치})", font=font_small, fill='#E57373', anchor='rm')
            current_y += row_height
    else:
        draw.rectangle([col2_x, current_y, col2_x + col_width, current_y + row_height],
                       fill='#F5F5F5', outline='#E0E0E0')
        draw.text((col2_x + col_width // 2, current_y + row_height // 2), 
                  "-", font=font_medium, fill='#BDBDBD', anchor='mm')
        current_y += row_height
    
    # 흉신 개수
    draw.text((col2_x + col_width // 2, count_y), 
              f"총 {len(흉신)}개", font=font_small, fill='#C62828', anchor='mm')
    
    # ========== 특수신살 열 ==========
    col3_x = start_x + (col_width + col_gap) * 2
    
    # 헤더 (파스텔 퍼플)
    draw.rectangle([col3_x, table_y, col3_x + col_width, table_y + header_height],
                   fill='#F3E5F5', outline='#E1BEE7')
    draw.text((col3_x + col_width // 2, table_y + header_height // 2), 
              "[특수신살]", font=font_header, fill='#7B1FA2', anchor='mm')
    
    # 특수신살 목록
    current_y = table_y + header_height
    
    if 특수신살:
        for 신살명, 위치 in 특수신살:
            draw.rectangle([col3_x, current_y, col3_x + col_width, current_y + row_height],
                           fill='#F5F5F5', outline='#E0E0E0')
            draw.text((col3_x + 10, current_y + row_height // 2), 
                      f"{신살명}", font=font_medium, fill='#7B1FA2', anchor='lm')
            draw.text((col3_x + col_width - 10, current_y + row_height // 2), 
                      f"({위치})", font=font_small, fill='#AB47BC', anchor='rm')
            current_y += row_height
    else:
        draw.rectangle([col3_x, current_y, col3_x + col_width, current_y + row_height],
                       fill='#F5F5F5', outline='#E0E0E0')
        draw.text((col3_x + col_width // 2, current_y + row_height // 2), 
                  "-", font=font_medium, fill='#BDBDBD', anchor='mm')
        current_y += row_height
    
    # 특수신살 개수
    draw.text((col3_x + col_width // 2, count_y), 
              f"총 {len(특수신살)}개", font=font_small, fill='#7B1FA2', anchor='mm')
    
    # ========== 하단 요약 ==========
    summary_y = count_y + 25
    
    # 총평 배경 (연한 회색)
    draw.rectangle([start_x, summary_y, start_x + col_width * 3 + col_gap * 2, summary_y + 50],
                   fill='#FAFAFA', outline='#E0E0E0')
    
    total_길 = len(길신)
    total_흉 = len(흉신)
    
    # 조건형 문구로 수정
    if total_길 > total_흉:
        총평 = f"길신 {total_길}개는 보호·완충 역할을 합니다."
        총평_color = '#1565C0'
    elif total_흉 > total_길:
        총평 = f"흉신 {total_흉}개는 조건 충족 시 작동하는 변수입니다."
        총평_color = '#666666'
    else:
        총평 = "길신과 흉신이 균형을 이루고 있습니다."
        총평_color = '#F57C00'
    
    draw.text((width // 2, summary_y + 17), 
              f"길신 {total_길}개 vs 흉신 {total_흉}개", 
              font=font_medium, fill='#333333', anchor='mm')
    draw.text((width // 2, summary_y + 36), 
              총평, font=font_small, fill=총평_color, anchor='mm')
    
    # 저장
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 12운성표 이미지 생성
# ============================================
def create_12운성표(사주_data, 기본정보, output_path="12운성표.png"):
    """12운성 전체 테이블 이미지 생성"""
    
    from saju_calculator import calc_12운성_전체, 지지, 운성_순서
    
    일간 = 사주_data['일주'][0]
    운성_전체 = calc_12운성_전체(일간)
    
    # 원국 지지들
    원국_지지 = {
        '년': 사주_data['년주'][1],
        '월': 사주_data['월주'][1],
        '일': 사주_data['일주'][1],
        '시': 사주_data['시주'][1],
    }
    
    # 이미지 크기
    width = 700
    height = 265
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(16)
    font_header = get_font(12, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    # 제목
    draw.text((width // 2, 20), f"{기본정보['이름']}님 12운성표 (일간: {일간})", 
              font=font_title, fill='#333333', anchor='mm')
    
    # 운성별 에너지 레벨
    에너지 = {
        '장생': ('상승', '#4CAF50'), '목욕': ('불안', '#FFC107'), '관대': ('성장', '#8BC34A'),
        '건록': ('최강', '#2196F3'), '제왕': ('정점', '#1565C0'), '쇠': ('하강', '#FF9800'),
        '병': ('약함', '#F44336'), '사': ('최약', '#B71C1C'), '묘': ('잠복', '#795548'),
        '절': ('단절', '#9E9E9E'), '태': ('잉태', '#E1BEE7'), '양': ('양육', '#CE93D8'),
    }
    
    # 테이블
    table_y = 55
    col_width = 50
    row_height = 26
    label_width = 50
    table_width = label_width + 12 * col_width  # 50 + 600 = 650
    start_x = (width - table_width) // 2  # 중앙 정렬
    
    # 헤더 (지지)
    draw.rectangle([start_x, table_y, start_x + label_width, table_y + 28],
                   fill='#E8E8E8', outline='#CCCCCC')
    draw.text((start_x + label_width // 2, table_y + 14), "지지", 
              font=font_header, fill='#333333', anchor='mm')
    
    for i, 지지명 in enumerate(지지):
        x = start_x + label_width + i * col_width
        # 원국에 있는 지지 강조
        is_원국 = 지지명 in 원국_지지.values()
        bg_color = '#E3F2FD' if is_원국 else '#F5F5F5'
        draw.rectangle([x, table_y, x + col_width, table_y + 28],
                       fill=bg_color, outline='#CCCCCC')
        draw.text((x + col_width // 2, table_y + 14), 지지명, 
                  font=font_header, fill='#333333', anchor='mm')
    
    # 운성 행
    current_y = table_y + 28
    draw.rectangle([start_x, current_y, start_x + label_width, current_y + row_height],
                   fill='#E8E8E8', outline='#CCCCCC')
    draw.text((start_x + label_width // 2, current_y + row_height // 2), "운성", 
              font=font_header, fill='#333333', anchor='mm')
    
    for i, 지지명 in enumerate(지지):
        x = start_x + label_width + i * col_width
        운성 = 운성_전체[지지명]
        에너지_상태, 색상 = 에너지[운성]
        
        is_원국 = 지지명 in 원국_지지.values()
        bg_color = '#E3F2FD' if is_원국 else '#FFFFFF'
        draw.rectangle([x, current_y, x + col_width, current_y + row_height],
                       fill=bg_color, outline='#CCCCCC')
        draw.text((x + col_width // 2, current_y + row_height // 2), 운성, 
                  font=font_medium, fill=색상, anchor='mm')
    
    # 에너지 행
    current_y += row_height
    draw.rectangle([start_x, current_y, start_x + label_width, current_y + row_height],
                   fill='#E8E8E8', outline='#CCCCCC')
    draw.text((start_x + label_width // 2, current_y + row_height // 2), "에너지", 
              font=font_header, fill='#333333', anchor='mm')
    
    for i, 지지명 in enumerate(지지):
        x = start_x + label_width + i * col_width
        운성 = 운성_전체[지지명]
        에너지_상태, 색상 = 에너지[운성]
        
        is_원국 = 지지명 in 원국_지지.values()
        bg_color = '#E3F2FD' if is_원국 else '#FFFFFF'
        draw.rectangle([x, current_y, x + col_width, current_y + row_height],
                       fill=bg_color, outline='#CCCCCC')
        draw.text((x + col_width // 2, current_y + row_height // 2), 에너지_상태, 
                  font=font_small, fill='#666666', anchor='mm')
    
    # 내 사주 운성 요약
    summary_y = current_y + 35
    draw.rectangle([20, summary_y, width - 20, summary_y + 95],
                   fill='#FAFAFA', outline='#E0E0E0')
    draw.text((width // 2, summary_y + 12), "[ 내 사주 12운성 ]", 
              font=font_header, fill='#333333', anchor='mm')
    
    col_positions = [100, 250, 400, 550]
    labels = ['년주', '월주', '일주', '시주']
    cols = ['년', '월', '일', '시']
    
    for i, (label, col) in enumerate(zip(labels, cols)):
        x = col_positions[i]
        지지명 = 원국_지지[col]
        운성 = 운성_전체[지지명]
        에너지_상태, 색상 = 에너지[운성]
        
        draw.text((x, summary_y + 35), label, font=font_medium, fill='#666666', anchor='mm')
        draw.text((x, summary_y + 55), f"{지지명} -> {운성}", font=font_medium, fill=색상, anchor='mm')
        draw.text((x, summary_y + 73), f"({에너지_상태})", font=font_small, fill='#999999', anchor='mm')
    
    # 범례
    legend_y = summary_y + 105
    draw.text((20, legend_y), "강한 운성: 건록, 제왕, 관대", font=font_small, fill='#1565C0', anchor='lm')
    draw.text((250, legend_y), "약한 운성: 병, 사, 묘, 절", font=font_small, fill='#C62828', anchor='lm')
    draw.text((450, legend_y), "시작 운성: 장생, 태, 양", font=font_small, fill='#7B1FA2', anchor='lm')
    
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 지장간표 이미지 생성
# ============================================
def create_지장간표(사주_data, 기본정보, output_path="지장간표.png"):
    """지장간 테이블 이미지 생성"""
    
    from saju_calculator import calc_지장간_전체, 지지
    
    지장간_전체 = calc_지장간_전체()
    
    원국_지지 = {
        '년': 사주_data['년주'][1],
        '월': 사주_data['월주'][1],
        '일': 사주_data['일주'][1],
        '시': 사주_data['시주'][1],
    }
    
    width = 700
    height = 290
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(16)
    font_header = get_font(12, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    draw.text((width // 2, 20), f"{기본정보['이름']}님 지장간표", 
              font=font_title, fill='#333333', anchor='mm')
    
    table_y = 55
    col_width = 50
    row_height = 28
    label_width = 50
    table_width = label_width + 12 * col_width
    start_x = (width - table_width) // 2  # 중앙 정렬
    
    # 헤더
    draw.rectangle([start_x, table_y, start_x + label_width, table_y + 28],
                   fill='#E8E8E8', outline='#CCCCCC')
    draw.text((start_x + label_width // 2, table_y + 14), "구분", 
              font=font_header, fill='#333333', anchor='mm')
    
    for i, 지지명 in enumerate(지지):
        x = start_x + label_width + i * col_width
        is_원국 = 지지명 in 원국_지지.values()
        bg_color = '#E3F2FD' if is_원국 else '#E8E8E8'
        draw.rectangle([x, table_y, x + col_width, table_y + 28],
                       fill=bg_color, outline='#CCCCCC')
        draw.text((x + col_width // 2, table_y + 14), 지지명, 
                  font=font_header, fill='#333333', anchor='mm')
    
    # 여기, 중기, 본기 행
    행_이름 = ['여기', '중기', '본기']
    
    for row_idx, 행 in enumerate(행_이름):
        current_y = table_y + 28 + row_idx * row_height
        
        draw.rectangle([start_x, current_y, start_x + label_width, current_y + row_height],
                       fill='#F5F5F5', outline='#CCCCCC')
        draw.text((start_x + label_width // 2, current_y + row_height // 2), 행, 
                  font=font_medium, fill='#333333', anchor='mm')
        
        for i, 지지명 in enumerate(지지):
            x = start_x + label_width + i * col_width
            지장간 = 지장간_전체[지지명][행]
            
            is_원국 = 지지명 in 원국_지지.values()
            bg_color = '#E3F2FD' if is_원국 else '#FFFFFF'
            
            draw.rectangle([x, current_y, x + col_width, current_y + row_height],
                           fill=bg_color, outline='#CCCCCC')
            text = 지장간 if 지장간 else '-'
            color = '#333333' if 지장간 else '#CCCCCC'
            draw.text((x + col_width // 2, current_y + row_height // 2), text, 
                      font=font_medium, fill=color, anchor='mm')
    
    # 내 사주 지장간 요약
    summary_y = table_y + 28 + len(행_이름) * row_height + 20
    draw.rectangle([20, summary_y, width - 20, summary_y + 80],
                   fill='#FAFAFA', outline='#E0E0E0')
    draw.text((width // 2, summary_y + 12), "[ 내 사주 지장간 ]", 
              font=font_header, fill='#333333', anchor='mm')
    
    col_positions = [100, 250, 400, 550]
    labels = ['년지', '월지', '일지', '시지']
    cols = ['년', '월', '일', '시']
    
    for i, (label, col) in enumerate(zip(labels, cols)):
        x = col_positions[i]
        지지명 = 원국_지지[col]
        지장간 = 지장간_전체[지지명]
        
        draw.text((x, summary_y + 35), f"{label}: {지지명}", font=font_medium, fill='#666666', anchor='mm')
        
        지장간_str = []
        if 지장간['여기']:
            지장간_str.append(지장간['여기'])
        if 지장간['중기']:
            지장간_str.append(지장간['중기'])
        if 지장간['본기']:
            지장간_str.append(지장간['본기'])
        
        draw.text((x, summary_y + 58), ' '.join(지장간_str), font=font_medium, fill='#1565C0', anchor='mm')
    
    desc_y = summary_y + 88
    draw.text((width // 2, desc_y), "* 지장간: 지지 속에 숨어있는 천간 (본기가 가장 강함)", 
              font=font_small, fill='#666666', anchor='mm')
    
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 합충형파해표 이미지 생성
# ============================================
def create_합충형파해표(사주_data, 기본정보, output_path="합충형파해표.png"):
    """합충형파해 관계 분석 이미지"""
    
    from saju_calculator import calc_합충형파해, calc_천간합
    
    합충형파해 = calc_합충형파해(사주_data)
    천간합_결과 = calc_천간합(사주_data)
    
    width = 650
    height = 520
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(16)
    font_header = get_font(13, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    draw.text((width // 2, 20), f"{기본정보['이름']}님 합충형파해 분석", 
              font=font_title, fill='#333333', anchor='mm')
    
    # 원국 표시
    원국_y = 50
    draw.rectangle([20, 원국_y, width - 20, 원국_y + 50],
                   fill='#FAFAFA', outline='#E0E0E0')
    
    labels = ['시주', '일주', '월주', '년주']
    cols = ['시', '일', '월', '년']
    col_positions = [100, 220, 380, 520]
    
    for i, (label, col) in enumerate(zip(labels, cols)):
        x = col_positions[i]
        천간 = 사주_data[f'{col}주'][0]
        지지 = 사주_data[f'{col}주'][1]
        draw.text((x, 원국_y + 18), label, font=font_small, fill='#666666', anchor='mm')
        draw.text((x, 원국_y + 38), f"{천간}{지지}", font=font_header, fill='#333333', anchor='mm')
    
    # 분석 결과
    current_y = 원국_y + 70
    
    관계_목록 = [
        ('천간합', 천간합_결과, '#1565C0', '합하여 새로운 오행'),
        ('육합', 합충형파해['육합'], '#2196F3', '두 지지가 합'),
        ('삼합', 합충형파해['삼합'], '#4CAF50', '세 지지가 합'),
        ('방합', 합충형파해['방합'], '#8BC34A', '계절 합'),
        ('충', 합충형파해['충'], '#F44336', '대립/변동'),
        ('형', 합충형파해['형'], '#E91E63', '형벌/시련'),
        ('파', 합충형파해['파'], '#FF9800', '깨짐'),
        ('해', 합충형파해['해'], '#9C27B0', '해침'),
    ]
    
    row_height = 42
    
    for 관계명, 결과, 색상, 설명 in 관계_목록:
        has_result = len(결과) > 0
        bg_color = '#FFF3E0' if has_result and 관계명 in ['충', '형', '파', '해'] else '#E8F5E9' if has_result else '#F5F5F5'
        
        draw.rectangle([20, current_y, width - 20, current_y + row_height],
                       fill=bg_color, outline='#E0E0E0')
        
        draw.text((80, current_y + row_height // 2), 관계명, 
                  font=font_header, fill=색상, anchor='mm')
        
        if has_result:
            if 관계명 == '천간합':
                result_str = ', '.join([f"{r['천간']}->{r['합화']}" for r in 결과])
            elif 관계명 in ['삼합', '방합']:
                result_str = ', '.join([f"{r['오행']}({'-'.join(r['지지'])})" for r in 결과])
            elif 관계명 == '육합':
                result_str = ', '.join([f"{r['지지']}->{r['합화']}" for r in 결과])
            else:
                result_str = ', '.join([f"{r['지지']}({r['위치']})" for r in 결과])
            
            draw.text((350, current_y + 13), result_str, font=font_medium, fill='#333333', anchor='mm')
            draw.text((350, current_y + 30), 설명, font=font_small, fill='#666666', anchor='mm')
        else:
            draw.text((350, current_y + row_height // 2), "해당 없음", font=font_medium, fill='#BDBDBD', anchor='mm')
        
        current_y += row_height
    
    # 요약
    summary_y = current_y + 10
    합_count = len(천간합_결과) + len(합충형파해['육합']) + len(합충형파해['삼합']) + len(합충형파해['방합'])
    충돌_count = len(합충형파해['충']) + len(합충형파해['형']) + len(합충형파해['파']) + len(합충형파해['해'])
    
    draw.rectangle([20, summary_y, width - 20, summary_y + 40],
                   fill='#FAFAFA', outline='#E0E0E0')
    
    총평 = "합이 많아 조화로움" if 합_count > 충돌_count else "충돌이 있어 변동 있음" if 충돌_count > 합_count else "균형"
    총평_color = '#4CAF50' if 합_count > 충돌_count else '#F44336' if 충돌_count > 합_count else '#FF9800'
    
    draw.text((width // 2, summary_y + 20), f"합: {합_count}개 | 충돌: {충돌_count}개 -> {총평}", 
              font=font_medium, fill=총평_color, anchor='mm')
    
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 궁성표 이미지 생성  
# ============================================
def create_궁성표(사주_data, 기본정보, output_path="궁성표.png"):
    """사주 궁성 분석 이미지"""
    
    from saju_calculator import calc_궁성
    
    궁성 = calc_궁성(사주_data)
    
    width = 700
    height = 250
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(16)
    font_header = get_font(13, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    draw.text((width // 2, 20), f"{기본정보['이름']}님 사주 궁성표", 
              font=font_title, fill='#333333', anchor='mm')
    
    box_width = 155
    box_height = 110
    start_x = 30
    box_y = 55
    gap = 10
    
    궁_색상 = {'년주': '#E3F2FD', '월주': '#E8F5E9', '일주': '#FFF3E0', '시주': '#F3E5F5'}
    헤더_색상 = {'년주': '#1565C0', '월주': '#2E7D32', '일주': '#E65100', '시주': '#7B1FA2'}
    
    for i, (주, 정보) in enumerate(궁성.items()):
        x = start_x + i * (box_width + gap)
        
        draw.rectangle([x, box_y, x + box_width, box_y + box_height],
                       fill=궁_색상[주], outline='#CCCCCC')
        
        draw.rectangle([x, box_y, x + box_width, box_y + 28],
                       fill=헤더_색상[주], outline=헤더_색상[주])
        draw.text((x + box_width // 2, box_y + 14), 주, 
                  font=font_header, fill='#FFFFFF', anchor='mm')
        
        draw.text((x + box_width // 2, box_y + 48), f"{정보['천간']}{정보['지지']}", 
                  font=get_font(16, bold=True), fill='#333333', anchor='mm')
        
        draw.text((x + box_width // 2, box_y + 72), 정보['궁'], 
                  font=font_small, fill=헤더_색상[주], anchor='mm')
        
        의미_short = 정보['의미'][:20]
        draw.text((x + box_width // 2, box_y + 92), 의미_short, 
                  font=font_small, fill='#666666', anchor='mm')
    
    # 시간대 설명
    time_y = box_y + box_height + 20
    draw.rectangle([20, time_y, width - 20, time_y + 50],
                   fill='#FAFAFA', outline='#E0E0E0')
    
    draw.text((width // 2, time_y + 15), "[ 운세 적용 시기 ]", font=font_header, fill='#333333', anchor='mm')
    draw.text((width // 2, time_y + 35), "년주:1~15세 | 월주:15~30세 | 일주:30~45세 | 시주:45세~", 
              font=font_medium, fill='#666666', anchor='mm')
    
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 육친표 이미지 생성
# ============================================
def create_육친표(사주_data, 기본정보, gender='남', output_path="육친표.png"):
    """육친 관계 분석 이미지"""
    
    from saju_calculator import calc_육친
    
    육친 = calc_육친(사주_data, gender)
    
    width = 650
    height = 295
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(16)
    font_header = get_font(12, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    성별_텍스트 = '남성' if gender == '남' else '여성'
    draw.text((width // 2, 20), f"{기본정보['이름']}님 육친표 ({성별_텍스트})", 
              font=font_title, fill='#333333', anchor='mm')
    
    table_y = 55
    label_width = 55
    col_width = 140
    row_height = 32
    table_width = label_width + col_width * 4
    start_x = (width - table_width) // 2  # 중앙 정렬
    
    headers = ['구분', '년주', '월주', '일주', '시주']
    for i, h in enumerate(headers):
        if i == 0:
            x, w = start_x, label_width
        else:
            x, w = start_x + label_width + (i-1) * col_width, col_width
        draw.rectangle([x, table_y, x + w, table_y + 28], fill='#E8E8E8', outline='#CCCCCC')
        draw.text((x + w // 2, table_y + 14), h, font=font_header, fill='#333333', anchor='mm')
    
    rows = [('천간십성', '천간'), ('천간육친', '천간'), ('지지십성', '지지'), ('지지육친', '지지')]
    
    for row_idx, (행_이름, key) in enumerate(rows):
        current_y = table_y + 28 + row_idx * row_height
        
        draw.rectangle([start_x, current_y, start_x + label_width, current_y + row_height],
                       fill='#F5F5F5', outline='#CCCCCC')
        draw.text((start_x + label_width // 2, current_y + row_height // 2), 행_이름[:4], 
                  font=font_small, fill='#333333', anchor='mm')
        
        for i, col in enumerate(['년', '월', '일', '시']):
            x = start_x + label_width + i * col_width
            if '십성' in 행_이름:
                값 = 육친[col][key]['십성']
                color = '#1565C0'
            else:
                값 = 육친[col][key]['육친']
                color = '#E65100'
            
            bg = '#FFFFFF' if '십성' in 행_이름 else '#FFF8E1'
            draw.rectangle([x, current_y, x + col_width, current_y + row_height],
                           fill=bg, outline='#CCCCCC')
            draw.text((x + col_width // 2, current_y + row_height // 2), 값, 
                      font=font_medium, fill=color, anchor='mm')
    
    ref_y = table_y + 28 + len(rows) * row_height + 20
    draw.rectangle([20, ref_y, width - 20, ref_y + 55], fill='#FAFAFA', outline='#E0E0E0')
    draw.text((width // 2, ref_y + 12), f"[ 육친 참고 ({성별_텍스트}) ]", font=font_header, fill='#333333', anchor='mm')
    
    if gender == '남':
        참고 = "정재=아내 | 편재=아버지 | 정관=딸 | 편관=아들 | 정인=어머니"
    else:
        참고 = "정관=남편 | 편관=애인 | 식신=딸 | 상관=아들 | 정인=어머니"
    draw.text((width // 2, ref_y + 38), 참고, font=font_small, fill='#666666', anchor='mm')
    
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 납음오행표 이미지 생성
# ============================================
def create_납음오행표(사주_data, 기본정보, output_path="납음오행표.png"):
    """납음오행 분석 이미지"""
    
    from saju_calculator import calc_납음오행
    
    납음 = calc_납음오행(사주_data)
    
    width = 650
    height = 250
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(16)
    font_header = get_font(13, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    draw.text((width // 2, 20), f"{기본정보['이름']}님 납음오행표", font=font_title, fill='#333333', anchor='mm')
    draw.text((width // 2, 40), "(60갑자의 소리 오행)", font=font_small, fill='#666666', anchor='mm')
    
    box_width = 145
    box_height = 120
    start_x = 30
    box_y = 60
    gap = 10
    
    오행_색상 = {'목': '#4CAF50', '화': '#F44336', '토': '#795548', '금': '#FFC107', '수': '#2196F3'}
    
    for i, (col, label) in enumerate([('년', '년주'), ('월', '월주'), ('일', '일주'), ('시', '시주')]):
        x = start_x + i * (box_width + gap)
        정보 = 납음[col]
        색상 = 오행_색상.get(정보['오행'], '#333333')
        
        draw.rectangle([x, box_y, x + box_width, box_y + box_height], fill='#FAFAFA', outline='#E0E0E0')
        draw.rectangle([x, box_y, x + box_width, box_y + 25], fill=색상, outline=색상)
        draw.text((x + box_width // 2, box_y + 12), label, font=font_header, fill='#FFFFFF', anchor='mm')
        
        draw.text((x + box_width // 2, box_y + 45), 정보['간지'], font=get_font(14, bold=True), fill='#333333', anchor='mm')
        draw.text((x + box_width // 2, box_y + 70), 정보['납음'], font=font_medium, fill=색상, anchor='mm')
        draw.text((x + box_width // 2, box_y + 90), f"({정보['오행']})", font=font_small, fill='#666666', anchor='mm')
        draw.text((x + box_width // 2, box_y + 108), 정보['설명'][:10], font=font_small, fill='#999999', anchor='mm')
    
    summary_y = box_y + box_height + 15
    draw.rectangle([20, summary_y, width - 20, summary_y + 40], fill='#FFF8E1', outline='#FFE082')
    일주_납음 = 납음['일']
    draw.text((width // 2, summary_y + 20), f"본명 납음: {일주_납음['납음']}({일주_납음['오행']}) - {일주_납음['설명'][:15]}", 
              font=font_medium, fill='#E65100', anchor='mm')
    
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 격국표 이미지 생성
# ============================================
def create_격국표(사주_data, 기본정보, output_path="격국표.png"):
    """격국 분석 이미지"""
    
    from saju_calculator import calc_격국
    
    격국 = calc_격국(사주_data)
    
    width = 550
    height = 240
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(16)
    font_header = get_font(14, bold=True)
    font_medium = get_font(12)
    font_small = get_font(10)
    
    draw.text((width // 2, 20), f"{기본정보['이름']}님 격국 분석", font=font_title, fill='#333333', anchor='mm')
    
    main_y = 50
    draw.rectangle([30, main_y, width - 30, main_y + 90], fill='#E3F2FD', outline='#90CAF9')
    draw.text((width // 2, main_y + 20), "정격 (월지 기준)", font=font_medium, fill='#666666', anchor='mm')
    draw.text((width // 2, main_y + 50), 격국['정격'], font=get_font(18, bold=True), fill='#1565C0', anchor='mm')
    draw.text((width // 2, main_y + 75), f"월지:{격국['월지']} 본기:{격국['월지_본기']} -> {격국['십성']}", 
              font=font_small, fill='#666666', anchor='mm')
    
    special_y = main_y + 105
    draw.rectangle([30, special_y, width - 30, special_y + 50], fill='#FFF3E0', outline='#FFE0B2')
    draw.text((width // 2, special_y + 12), "특수격 가능성", font=font_medium, fill='#E65100', anchor='mm')
    특수격_str = ', '.join(격국['특수격']) if 격국['특수격'] else '해당 없음'
    draw.text((width // 2, special_y + 35), 특수격_str, font=font_header, fill='#333333', anchor='mm')
    
    desc_y = special_y + 65
    격국_설명 = {
        '정관격': '규율/명예 중시', '편관격 (칠살격)': '권력/리더십', '정재격': '안정적 재물',
        '편재격': '사업적 재능', '식신격': '의식주 복', '상관격': '예술적 재능',
        '정인격': '학문/교육', '편인격 (효신격)': '특수 학문', '비견격': '독립심', '겁재격': '경쟁심',
    }
    설명 = 격국_설명.get(격국['정격'], '특수한 구성')
    draw.text((width // 2, desc_y), f"특성: {설명}", font=font_small, fill='#666666', anchor='mm')
    
    img.save(output_path, 'PNG')
    return output_path


# ============================================
# 공망표 이미지 생성
# ============================================
def create_공망표(사주_data, 기본정보, output_path="공망표.png"):
    """공망 분석 이미지"""
    
    from saju_calculator import calc_공망_전체
    
    공망 = calc_공망_전체(사주_data)
    
    width = 600
    height = 275
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(16)
    font_header = get_font(13, bold=True)
    font_medium = get_font(11)
    font_small = get_font(10)
    
    draw.text((width // 2, 20), f"{기본정보['이름']}님 공망 분석", font=font_title, fill='#333333', anchor='mm')
    
    main_y = 50
    draw.rectangle([30, main_y, width - 30, main_y + 70], fill='#F3E5F5', outline='#CE93D8')
    일주_공망 = 공망['일']['공망']
    draw.text((width // 2, main_y + 18), "일주 기준 공망 (가장 중요)", font=font_medium, fill='#7B1FA2', anchor='mm')
    draw.text((width // 2, main_y + 45), f"{일주_공망[0]} / {일주_공망[1]}", 
              font=get_font(20, bold=True), fill='#7B1FA2', anchor='mm')
    
    table_y = main_y + 85
    col_width = 130
    for i, (col, label) in enumerate([('년', '년주'), ('월', '월주'), ('일', '일주'), ('시', '시주')]):
        x = 35 + i * col_width
        공망_지지 = 공망[col]['공망']
        draw.rectangle([x, table_y, x + col_width - 5, table_y + 50], fill='#FAFAFA', outline='#E0E0E0')
        draw.text((x + (col_width-5) // 2, table_y + 13), label, font=font_header, fill='#333333', anchor='mm')
        draw.text((x + (col_width-5) // 2, table_y + 35), f"{공망_지지[0]}/{공망_지지[1]}", 
                  font=font_medium, fill='#7B1FA2', anchor='mm')
    
    해당_y = table_y + 65
    draw.rectangle([30, 해당_y, width - 30, 해당_y + 45], fill='#FFF8E1', outline='#FFE082')
    draw.text((width // 2, 해당_y + 12), "[ 원국 내 공망 해당 ]", font=font_header, fill='#E65100', anchor='mm')
    공망_해당 = 공망.get('공망_해당', [])
    if 공망_해당:
        해당_str = ', '.join([f"{x['위치']}지({x['지지']})" for x in 공망_해당])
        draw.text((width // 2, 해당_y + 32), f"해당: {해당_str}", font=font_medium, fill='#C62828', anchor='mm')
    else:
        draw.text((width // 2, 해당_y + 32), "공망 해당 없음", font=font_medium, fill='#4CAF50', anchor='mm')
    
    draw.text((30, 해당_y + 55), "* 공망: 해당 궁의 일이 허무하거나 늦게 이루어짐", font=font_small, fill='#666666', anchor='lm')
    
    img.save(output_path, 'PNG')
    return output_path



# ============================================
# 일진표 (달력) 이미지 생성
# ============================================
def create_일진표(year, month, output_path="일진표.png"):
    """월별 일진 달력 이미지"""
    
    from saju_calculator import calc_일진표
    import calendar
    
    일진_데이터 = calc_일진표(year, month)
    
    width = 750
    height = 455
    
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(18)
    font_header = get_font(12, bold=True)
    font_medium = get_font(11)
    font_small = get_font(9)
    font_tiny = get_font(8)
    
    draw.text((width // 2, 22), f"{year}년 {month}월 일진표", font=font_title, fill='#333333', anchor='mm')
    draw.text((width // 2, 45), f"월주: {일진_데이터['월주']}", font=font_medium, fill='#1565C0', anchor='mm')
    
    요일 = ['일', '월', '화', '수', '목', '금', '토']
    요일_색상 = ['#C62828', '#333333', '#333333', '#333333', '#333333', '#333333', '#1565C0']
    
    cell_width = 100
    cell_height = 70
    start_x = 30
    start_y = 70
    
    for i, (요일명, 색상) in enumerate(zip(요일, 요일_색상)):
        x = start_x + i * cell_width
        draw.rectangle([x, start_y, x + cell_width, start_y + 22], fill='#F5F5F5', outline='#E0E0E0')
        draw.text((x + cell_width // 2, start_y + 11), 요일명, font=font_header, fill=색상, anchor='mm')
    
    cal = calendar.Calendar()
    weeks = list(cal.monthdayscalendar(year, month))
    
    current_y = start_y + 22
    
    for week in weeks:
        for day_idx, day in enumerate(week):
            x = start_x + day_idx * cell_width
            
            if day == 0:
                draw.rectangle([x, current_y, x + cell_width, current_y + cell_height], fill='#FAFAFA', outline='#E0E0E0')
            else:
                bg_color = '#FFEBEE' if day_idx == 0 else '#E3F2FD' if day_idx == 6 else '#FFFFFF'
                draw.rectangle([x, current_y, x + cell_width, current_y + cell_height], fill=bg_color, outline='#E0E0E0')
                
                day_data = None
                for d in 일진_데이터['days']:
                    if d and d['day'] == day:
                        day_data = d
                        break
                
                if day_data:
                    날짜_색상 = '#C62828' if day_idx == 0 else '#1565C0' if day_idx == 6 else '#333333'
                    draw.text((x + 8, current_y + 12), str(day), font=font_header, fill=날짜_색상, anchor='lm')
                    draw.text((x + cell_width // 2, current_y + 32), day_data['일진'], font=font_medium, fill='#333333', anchor='mm')
                    draw.text((x + cell_width // 2, current_y + 48), f"{day_data['천간_한자']}{day_data['지지_한자']}", 
                              font=font_small, fill='#999999', anchor='mm')
                    draw.text((x + cell_width - 8, current_y + 12), day_data['음력'], font=font_tiny, fill='#999999', anchor='rm')
        
        current_y += cell_height
    
    img.save(output_path, 'PNG')
    return output_path
