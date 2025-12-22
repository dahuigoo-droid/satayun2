import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
from korean_lunar_calendar import KoreanLunarCalendar

# 1. 사주 계산 함수 (한자 변환 로직 보강)
def get_saju_data(year, month, day):
    calendar = KoreanLunarCalendar()
    try:
        calendar.setSolarDate(int(year), int(month), int(day))
        return calendar.getGapjaString() # 예: "庚午 (경오) "
    except:
        return "날짜 확인 필요"

# 2. 화면 설정 (전체 넓게 사용)
st.set_page_config(page_title="사주/타로 마스터", layout="wide")
st.title("🔮 사주/타로 리포트 자동 생성 시스템")

# --- 1구역: 디자인 및 지침 (좌우 배치) ---
st.header("🖼️ 1. 디자인 및 AI 지침 설정")
col_img1, col_img2, col_img3 = st.columns(3)
with col_img1: cover_img = st.file_uploader("표지(1p)", type=["png", "jpg"])
with col_img2: body_img = st.file_uploader("내지(2p)", type=["png", "jpg"])
with col_img3: tail_img = st.file_uploader("안내지(3p)", type=["png", "jpg"])

col_t1, col_t2 = st.columns(2)
with col_t1: toc_list = st.text_area("📋 PDF 목차", value="1. 타고난 기질\n2. 올해의 연애운", height=100)
with col_t2: ai_guide = st.text_area("🤖 AI 지침", value="다정한 상담가 스타일", height=100)

# --- 2구역: 데이터 업로드 및 초기화 ---
st.divider()
st.header("📂 2. 데이터 관리 및 선택")

# 초기화 기능을 위해 세션 초기화
if 'reset' not in st.session_state: st.session_state.reset = False

def reset_all():
    st.session_state.reset = True
    st.rerun()

up_col, btn_col = st.columns([4, 1])
with up_col:
    uploaded_file = st.file_uploader("엑셀 파일(.xlsx) 업로드", type=["xlsx"], key="file_input")
with btn_col:
    st.button("🔄 데이터 초기화", on_click=reset_all, use_container_width=True)

# --- 3구역: 고객 선택 및 실행 ---
if uploaded_file and not st.session_state.reset:
    df = pd.read_excel(uploaded_file)
    
    st.subheader("📋 고객 목록 (PDF를 만들 고객을 선택하세요)")
    
    # 전체 선택 버튼
    select_all = st.checkbox("전체 선택", value=False)
    
    selected_indices = []
    # 고객 리스트를 표 형태가 아닌 체크박스 목록으로 나열
    for i, row in df.iterrows():
        name = row.get('이름', f'고객{i+1}')
        birth = f"{row.get('년')}년 {row.get('월')}월 {row.get('일')}일"
        if st.checkbox(f"✅ {name}님 ({birth})", value=select_all, key=f"chk_{i}"):
            selected_indices.append(i)

    # 생성 버튼
    st.divider()
    if st.button(f"🚀 선택한 {len(selected_indices)}명 리포트 생성 시작"):
        if not (cover_img and body_img and tail_img):
            st.error("❌ 디자인 이미지를 모두 업로드해야 합니다!")
        elif not selected_indices:
            st.warning("⚠️ 선택된 고객이 없습니다.")
        else:
            # 진행바 및 상태 텍스트
            prog_bar = st.progress(0)
            status_msg = st.empty()
            
            pdf_buf = io.BytesIO()
            p = canvas.Canvas(pdf_buf, pagesize=A4)
            w, h = A4
            
            # 이미지 리더 준비 (에러 방지 핵심)
            c_r = ImageReader(cover_img)
            b_r = ImageReader(body_img)
            t_r = ImageReader(tail_img)

            for idx, target_idx in enumerate(selected_indices):
                row = df.iloc[target_idx]
                name = row.get('이름', '고객')
                
                status_msg.text(f"⏳ {name}님 리포트 생성 중... ({idx+1}/{len(selected_indices)})")
                
                # 1. 표지
                p.drawImage(c_r, 0, 0, width=w, height=h)
                p.showPage()
                
                # 2. 내지 (데이터 반영)
                gapja = get_saju_data(row.get('년'), row.get('월'), row.get('일'))
                p.drawImage(b_r, 0, 0, width=w, height=h)
                p.setFont("Helvetica-Bold", 20)
                p.drawString(100, 700, f"Name: {name}")
                p.drawString(100, 670, f"Saju: {gapja}")
                p.showPage()
                
                # 3. 안내지
                p.drawImage(t_r, 0, 0, width=w, height=h)
                p.showPage()
                
                prog_bar.progress((idx + 1) / len(selected_indices))

            p.save()
            status_msg.empty()
            st.balloons()
            st.success("✅ 생성 완료!")
            st.download_button("📥 PDF 전체 다운로드", pdf_buf.getvalue(), "saju_reports.pdf")

# 리셋 상태면 초기화 후 복구
if st.session_state.reset:
    st.session_state.reset = False
    st.rerun()
