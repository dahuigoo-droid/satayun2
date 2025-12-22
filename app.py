import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
import requests
from korean_lunar_calendar import KoreanLunarCalendar

# 1. 무료 한글/한자 폰트 다운로드 및 등록 (Noto Sans KR)
@st.cache_resource
def load_fonts():
    # 나눔고딕 또는 Noto Sans 한글 폰트 URL (무료)
    font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
    # 실제 운영시에는 로컬에 .ttf 파일을 두고 TTFont("Hangeul", "font.ttf")로 등록하는 것이 가장 안전합니다.
    # 여기서는 기본 폰트로 설정하되, PDF 생성 시 에러 방지를 위해 Helvetica를 기본으로 사용합니다.
    pass

# 2. 사주 계산 함수
def get_saju_data(year, month, day):
    calendar = KoreanLunarCalendar()
    try:
        calendar.setSolarDate(int(year), int(month), int(day))
        return calendar.getGapjaString()
    except:
        return "날짜 오류"

# 3. 화면 설정
st.set_page_config(page_title="사주/타로 마스터 시스템", layout="wide")
st.title("🔮 사주/타로 리포트 커스텀 생성기")

# 초기화 버튼 기능 구현을 위한 세션 상태 관리
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# --- [상단] 리포트 디자인 및 지침 설정 ---
st.header("🖼️ 1. 디자인 및 AI 지침 설정")
img_col1, img_col2, img_col3 = st.columns(3)
with img_col1: cover_img = st.file_uploader("표지 이미지", type=["png", "jpg"])
with img_col2: body_img = st.file_uploader("내지 배경", type=["png", "jpg"])
with img_col3: tail_img = st.file_uploader("안내지 이미지", type=["png", "jpg"])

col_t1, col_t2 = st.columns(2)
with col_t1: toc_list = st.text_area("📋 PDF 목차", value="1. 타고난 기질\n2. 올해의 운세", height=100)
with col_t2: ai_guide = st.text_area("🤖 AI 지침", value="다정한 상담가 스타일", height=100)

# --- [중단] 데이터 업로드 및 초기화 ---
st.divider()
st.header("📂 2. 데이터 관리")
up_col, reset_col = st.columns([4, 1])

with up_col:
    uploaded_file = st.file_uploader("엑셀 파일(.xlsx)을 업로드하세요", type=["xlsx"])
with reset_col:
    if st.button("🔄 전체 데이터 초기화", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # 엑셀 정보 노출
    st.subheader("📋 업로드된 데이터 미리보기")
    st.dataframe(df, use_container_width=True)

    # 고객 선택 기능 (체크박스)
    st.subheader("✅ 출력할 고객 선택")
    
    c_all, c_none = st.columns([1, 10])
    select_all = c_all.checkbox("전체 선택", value=True)
    
    selected_indices = []
    # 목록 형태로 고객 리스트 표시
    for i, row in df.iterrows():
        name = row.get('이름', f'고객{i+1}')
        is_selected = st.checkbox(f"{name} ({row.get('년')}년생)", value=select_all, key=f"user_{i}")
        if is_selected:
            selected_indices.append(i)

    # --- [하단] 실행 버튼 ---
    st.divider()
    if st.button(f"🚀 선택한 {len(selected_indices)}명 PDF 생성 시작"):
        if not (cover_img and body_img and tail_img):
            st.error("이미지를 모두 업로드해야 합니다.")
        elif len(selected_indices) == 0:
            st.warning("선택된 고객이 없습니다.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            pdf_buffer = io.BytesIO()
            p = canvas.Canvas(pdf_buffer, pagesize=A4)
            w, h = A4
            
            cover_r = ImageReader(cover_img)
            body_r = ImageReader(body_img)
            tail_r = ImageReader(tail_img)

            for idx, i in enumerate(selected_indices):
                row = df.iloc[i]
                name = row.get('이름', '고객')
                
                status_text.text(f"📝 {name}님 리포트 작업 중... ({idx+1}/{len(selected_indices)})")
                
                # 1. 표지
                p.drawImage(cover_r, 0, 0, width=w, height=h)
                p.showPage()
                
                # 2. 내지 (사주 데이터 포함)
                gapja = get_saju_data(row.get('년'), row.get('월'), row.get('일'))
                p.drawImage(body_r, 0, 0, width=w, height=h)
                p.setFont("Helvetica", 20) # 폰트 설정
                p.drawString(100, 700, f"Client: {name}")
                p.drawString(100, 670, f"Saju: {gapja}")
                p.showPage()
                
                # 3. 안내지
                p.drawImage(tail_r, 0, 0, width=w, height=h)
                p.showPage()
                
                progress_bar.progress((idx + 1) / len(selected_indices))

            p.save()
            status_text.empty()
            st.success("✅ 모든 리포트 생성 완료!")
            st.download_button("📥 완성된 PDF 다운로드", pdf_buffer.getvalue(), "saju_reports.pdf")
