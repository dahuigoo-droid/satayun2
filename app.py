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

# --- 1구역: 설정 (좌우) ---
st.header("⚙️ 1. 리포트 기본 설정")
c1, c2 = st.columns(2)
with c1: toc = st.text_area("📋 PDF 목차", "1. 타고난 기질\n2. 올해의 연애운", height=100)
with c2: guide = st.text_area("🤖 AI 지침", "친절한 상담가 스타일", height=100)

st.subheader("🖼️ 디자인 이미지 업로드")
i1, i2, i3 = st.columns(3)
cv_img = i1.file_uploader("표지(1p)", type=["png", "jpg"])
bd_img = i2.file_uploader("내지(2p)", type=["png", "jpg"])
tl_img = i3.file_uploader("안내지(3p)", type=["png", "jpg"])

# --- 2구역: 데이터 관리 ---
st.divider()
st.header("📂 2. 고객 데이터 선택")
engine = get_db_engine()

# DB 불러오기 버튼을 크게 배치
if st.button("📥 DB에서 고객 명단 불러오기", use_container_width=True):
    if engine:
        try:
            st.session_state.db_data = pd.read_sql("SELECT * FROM clients", engine)
            st.success("데이터를 성공적으로 불러왔습니다!")
        except: st.error("DB에 'clients' 테이블이 없거나 데이터가 없습니다.")

# 데이터가 있을 때만 체크박스 노출
selected_indices = []
if 'db_data' in st.session_state:
    df = st.session_state.db_data
    sel_all = st.checkbox("전체 고객 선택")
    cols = st.columns(4)
    for idx, row in df.iterrows():
        name = str(row.get('이름', '고객'))
        with cols[idx % 4]:
            if st.checkbox(name, value=sel_all, key=f"u_{idx}"):
                selected_indices.append(idx)

# --- 3구역: PDF 생성 (버튼을 밖으로 빼서 무조건 보이게 함) ---
st.divider()
st.header("📄 3. PDF 생성 실행")

# 버튼을 조건문 밖으로 빼서 무조건 보이게 설정
generate_btn = st.button(f"🚀 선택한 {len(selected_indices)}명 PDF 생성 시작", type="primary", use_container_width=True)

if generate_btn:
    if not (cv_img and bd_img and tl_img):
        st.error("❌ 에러: 디자인 이미지 3장을 모두 업로드해야 PDF를 만들 수 있습니다!")
    elif len(selected_indices) == 0:
        st.warning("⚠️ 경고: 리포트를 만들 고객을 먼저 선택해주세요.")
    else:
        # 생성 로직 시작
        prog_bar = st.progress(0)
        status_msg = st.empty()
        pdf_buf = io.BytesIO()
        p = canvas.Canvas(pdf_buf, pagesize=A4)
        w, h = A4
        
        c_r, b_r, t_r = ImageReader(cv_img), ImageReader(bd_img), ImageReader(tl_img)

        for i, idx in enumerate(selected_indices):
            row = df.iloc[idx]
            name = str(row.get('이름', '고객'))
            status_msg.text(f"📝 {name}님 리포트 생성 중... ({i+1}/{len(selected_indices)})")
            
            # 1. 표지
            p.drawImage(c_r, 0, 0, width=w, height=h)
            p.setFont(FONT, 35); p.drawCentredString(w/2, h/2 + 50, f"{name} 님"); p.showPage()
            
            # 2. 내지
            p.drawImage(b_r, 0, 0, width=w, height=h)
            cal = KoreanLunarCalendar()
            cal.setSolarDate(int(row.get('년', 1990)), int(row.get('월', 1)), int(row.get('일', 1)))
            p.setFont(FONT, 20); p.drawString(80, 720, f"성함: {name}")
            p.drawString(80, 680, f"사주: {cal.getGapjaString()}"); p.showPage()
            
            # 3. 안내지
            p.drawImage(t_r, 0, 0, width=w, height=h); p.showPage()
            prog_bar.progress((i + 1) / len(selected_indices))

        p.save()
        status_msg.empty(); st.balloons()
        st.success("✅ 생성이 완료되었습니다! 아래 다운로드 버튼을 눌러주세요.")
        st.download_button("📥 완성된 PDF 다운로드", pdf_buf.getvalue(), "saju_report.pdf", "application/pdf")
