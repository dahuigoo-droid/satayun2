import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
from korean_lunar_calendar import KoreanLunarCalendar

# 1. 한글 폰트 등록 (font.ttf 파일이 같은 폴더에 있어야 함)
try:
    pdfmetrics.registerFont(TTFont('HangeulFont', 'font.ttf'))
    FONT_NAME = 'HangeulFont'
except:
    FONT_NAME = 'Helvetica' # 파일이 없을 경우 대비

# 2. 사주 계산 함수
def get_saju_data(year, month, day):
    calendar = KoreanLunarCalendar()
    try:
        calendar.setSolarDate(int(year), int(month), int(day))
        return calendar.getGapjaString()
    except:
        return "날짜 오류"

# 3. 화면 설정
st.set_page_config(page_title="사주/타로 마스터", layout="wide")
st.title("🔮 사주/타로 리포트 생성 시스템")

# --- 1구역: 디자인 및 지침 설정 ---
st.header("🖼️ 1. 디자인 및 AI 지침 설정")
col_img1, col_img2, col_img3 = st.columns(3)
with col_img1: cover_img = st.file_uploader("표지(1p)", type=["png", "jpg"])
with col_img2: body_img = st.file_uploader("내지(2p)", type=["png", "jpg"])
with col_img3: tail_img = st.file_uploader("안내지(3p)", type=["png", "jpg"])

col_t1, col_t2 = st.columns(2)
with col_t1: toc_list = st.text_area("📋 PDF 목차", value="1. 타고난 기질\n2. 올해의 연애운", height=100)
with col_t2: ai_guide = st.text_area("🤖 AI 지침", value="친절하고 전문적인 스타일", height=100)

# --- 2구역: 데이터 업로드 및 초기화 ---
st.divider()
st.header("📂 2. 데이터 관리 및 고객 선택")

if 'reset_flag' not in st.session_state: st.session_state.reset_flag = False

def trigger_reset():
    st.session_state.reset_flag = True
    st.rerun()

up_col, btn_col = st.columns([4, 1])
with up_col:
    uploaded_file = st.file_uploader("엑셀 파일(.xlsx) 업로드", type=["xlsx"], key="file_uploader")
with btn_col:
    st.button("🔄 데이터 초기화", on_click=trigger_reset, use_container_width=True)

# --- 3구역: 엑셀 데이터 노출 및 선택 ---
if uploaded_file and not st.session_state.reset_flag:
    df = pd.read_excel(uploaded_file)
    
    # 엑셀 정보 노출
    st.subheader("📊 업로드 데이터 확인")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("✅ 출력 대상 고객 선택")
    
    # 전체 선택 버튼
    select_all = st.checkbox("전체 고객 선택")
    
    selected_indices = []
    # 고객 목록 표시
    cols = st.columns(3) # 3열로 나누어 표시
    for i, row in df.iterrows():
        name = row.get('이름', f'고객{i+1}')
        birth = f"{row.get('년')}-{row.get('월')}-{row.get('일')}"
        with cols[i % 3]:
            if st.checkbox(f"{name} ({birth})", value=select_all, key=f"user_{i}"):
                selected_indices.append(i)

    # --- 4구역: 실행 및 PDF 생성 ---
    st.divider()
    if st.button(f"🚀 선택한 {len(selected_indices)}명 PDF 생성"):
        if not (cover_img and body_img and tail_img):
            st.error("❌ 모든 디자인 이미지를 업로드해주세요.")
        elif not selected_indices:
            st.warning("⚠️ 선택된 고객이 없습니다.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            pdf_output = io.BytesIO()
            p = canvas.Canvas(pdf_output, pagesize=A4)
            w, h = A4
            
            c_r = ImageReader(cover_img)
            b_r = ImageReader(body_img)
            t_r = ImageReader(tail_img)

            for idx, target_i in enumerate(selected_indices):
                row = df.iloc[target_i]
                name = row.get('이름', '고객')
                
                status_text.text(f"📝 {name}님 리포트 생성 중... ({idx+1}/{len(selected_indices)})")
                
                # 1. 표지
                p.drawImage(c_r, 0, 0, width=w, height=h)
                p.setFont(FONT_NAME, 30)
                p.drawCentredString(w/2, h/2, f"{name} 님 리포트")
                p.showPage()
                
                # 2. 내지
                gapja = get_saju_data(row.get('년'), row.get('월'), row.get('일'))
                p.drawImage(b_r, 0, 0, width=w, height=h)
                p.setFont(FONT_NAME, 18)
                p.drawString(100, 720, f"이름: {name}")
                p.drawString(100, 690, f"사주팔자: {gapja}")
                p.setFont(FONT_NAME, 12)
                p.drawString(100, 650, f"[목차] {toc_list.splitlines()[0]}...")
                p.showPage()
                
                # 3. 안내지
                p.drawImage(t_r, 0, 0, width=w, height=h)
                p.showPage()
                
                progress_bar.progress((idx + 1) / len(selected_indices))

            p.save()
            status_text.empty()
            st.balloons()
            st.success(f"✅ {len(selected_indices)}명의 리포트가 생성되었습니다!")
            st.download_button("📥 PDF 전체 다운로드", pdf_output.getvalue(), "saju_reports.pdf")

# 리셋 로직
if st.session_state.reset_flag:
    st.session_state.reset_flag = False
    st.rerun()
