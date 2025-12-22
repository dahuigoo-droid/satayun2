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
# 테스트
# ============================================
if __name__ == "__main__":
    from saju_calculator import calc_사주
    
    # 구대회 테스트
    사주 = calc_사주(1981, 3, 13, 3, 30)
    기본정보 = {
        '이름': '구대회',
        '성별': '남성',
        '나이': 45,
        '양력': '1981-03-13 03:30',
        '음력': '1981-02-08',
    }
    
    output = create_원국표(사주, 기본정보, "test_원국표.png")
    print(f"이미지 생성 완료: {output}")
