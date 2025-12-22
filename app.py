import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io, time, os
from sqlalchemy import create_engine
from korean_lunar_calendar import KoreanLunarCalendar

# 1. 한글 폰트 설정
@st.cache_resource
def load_fonts():
    font_path = "NanumGothic-Regular.ttf"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('Hangeul', font_path))
            return 'Hangeul'
        except: return 'Helvetica'
    return 'Helvetica'

FONT = load_fonts()

# 2. Supabase DB 연결
def get_db_engine():
    try:
        if "DATABASE_URL" in st.secrets:
            db_url = st.secrets["DATABASE_URL"].replace("postgres://", "postgresql://", 1)
            return create_engine(db_url)
    except: return None
    return None

# 3. 화면 설정
st.set_page_config(page_title="사주 마스터 Pro", layout="wide")
st.title("🔮 사주/타로 리포트 생성기")

# --- 🔄 최상단 초기화 버튼 ---
if st.button("🔄 시스템 전체 초기화", use_container_width=True):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- 1구역: 설정 ---
st.header("⚙️ 1. 리포트 기본 설정")
c1, c2 = st.columns(2)
with c1: toc = st.text_area("📋 PDF 목차", "1. 타고난 기질\n2. 올해의 연애운", height=100)
with c2: guide = st.text_area("🤖 AI 지침", "친절한 상담가 스타일", height=100)

st.subheader("🖼️ 디자인 이미지 업로드")
i1, i2, i3 = st.columns(3)
cv_img = i1.file_uploader("표지(1p)", type=["png", "jpg"], key="cv")
bd_img = i2.file_uploader("내지(2p)", type=["png", "jpg"], key="bd")
tl_img = i3.file_uploader("안내지(3p)", type=["png", "jpg"], key="tl")

# --- 2구역: 데이터 관리 ---
st.divider()
st.header("📂 2. 고객 데이터 관리")
engine = get_db_engine()

up_file = st.file_uploader("📂 엑셀 파일(.xlsx) 업로드", type=["xlsx"])
if up_file:
    df_excel = pd.read_excel(up_file)
    st.session_state.current_data = df_excel
    st.subheader("📋 업로드된 고객 명단")
    st.dataframe(df_excel, use_container_width=True)
    
    if st.button("💾 이 명단을 DB에 저장하기"):
        if engine:
            df_excel.to_sql('clients', engine, if_exists='append', index=False)
            st.success("DB 저장 완료!")

if st.button("📥 DB에서 고객 불러오기", use_container_width=True):
    if engine:
        st.session_state.current_data = pd.read_sql("SELECT * FROM clients", engine)
        st.success("데이터 로드 완료!")

selected_indices = []
if 'current_data' in st.session_state:
    df = st.session_state.current_data
    st.subheader("✅ 대상 선택")
    sel_all = st.checkbox("전체 선택")
    cols = st.columns(4)
    for idx, row in df.iterrows():
        name = str(row.get('이름', '고객'))
        with cols[idx % 4]:
            if st.checkbox(name, value=sel_all, key=f"u_{idx}"):
                selected_indices.append(idx)

# --- 3구역: PDF 생성 (생년월일시 반영 로직) ---
st.divider()
st.header("📄 3. PDF 생성 실행")

if st.button(f"🚀 선택한 {len(selected_indices)}명 PDF 생성", type="primary", use_container_width=True):
    if not (cv_img and bd_img and tl_img):
        st.error("❌ 디자인 이미지를 모두 업로드해주세요.")
    elif not selected_indices:
        st.warning("⚠️ 고객을 선택해주세요.")
    else:
        prog_bar = st.progress(0)
        status_msg = st.empty()
        pdf_buf = io.BytesIO()
        p = canvas.Canvas(pdf_buf, pagesize=A4)
        w, h = A4
        c_r, b_r, t_r = ImageReader(cv_img), ImageReader(bd_img), ImageReader(tl_img)

        for i, idx in enumerate(selected_indices):
            row = df.iloc[idx]
            name = str(row.get('이름', '고객'))
            status_msg.text(f"📝 {name}님 리포트 생성 중...")
            
            p.drawImage(c_r, 0, 0, width=w, height=h)
            p.setFont(FONT, 35); p.drawCentredString(w/2, h/2 + 50, f"{name} 님"); p.showPage()
            
            p.drawImage(b_r, 0, 0, width=w, height=h)
            
            # [수정 핵심] 태어난 '시' 정보까지 포함하여 사주 계산
            try:
                cal = KoreanLunarCalendar()
                y = int(row.get('년', 1990))
                m = int(row.get('월', 1))
                d = int(row.get('일', 1))
                h_val = int(row.get('시', 0)) # '시' 정보 추가 (없으면 0시)
                
                cal.setSolarDate(y, m, d)
                gapja = cal.getGapjaString()
                # 시 정보를 포함한 상세 텍스트 (필요 시 사주 계산 로직에 시주 추가 가능)
                saju_text = f"{gapja} ({h_val}시생)"
            except:
                saju_text = "날짜/시간 데이터 확인 필요"

            p.setFont(FONT, 20); p.drawString(80, 720, f"성함: {name}")
            p.drawString(80, 680, f"사주: {saju_text}"); p.showPage()
            
            p.drawImage(t_r, 0, 0, width=w, height=h); p.showPage()
            prog_bar.progress((i + 1) / len(selected_indices))

        p.save()
        status_msg.empty(); st.balloons()
        st.success("✅ 생성 완료!")
        st.download_button("📥 PDF 다운로드", pdf_buf.getvalue(), "saju_report.pdf", "application/pdf")
