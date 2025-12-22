import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io, time, os
from supabase import create_client, Client
from korean_lunar_calendar import KoreanLunarCalendar

# 1. Supabase 설정 (사장님의 대시보드에서 URL과 Key를 복사해 넣으세요)
SUPABASE_URL = "사장님의_SUPABASE_URL"
SUPABASE_KEY = "사장님의_SUPABASE_ANON_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. 한글 폰트 설정
@st.cache_resource
def load_fonts():
    font_path = "NanumGothic-Regular.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Nanum', font_path))
        return 'Nanum'
    return 'Helvetica'

FONT = load_fonts()

st.set_page_config(page_title="사주 마스터 Pro (Supabase)", layout="wide")
st.title("🔮 사주/타로 리포트 시스템 (Supabase 연동)")

# --- 1. 설정 및 이미지 관리 ---
st.header("⚙️ 1. 시스템 설정")
c1, c2 = st.columns(2)
with c1: toc = st.text_area("📋 PDF 목차", "1. 기질\n2. 운세", height=80)
with c2: guide = st.text_area("🤖 AI 지침", "전문가 스타일", height=80)

# Storage에서 이미지 불러오기 또는 업로드
st.subheader("🖼️ 디자인 이미지 관리")
i1, i2, i3 = st.columns(3)
# (이미지는 Supabase Storage를 사용하거나 기존처럼 로컬 파일을 활용할 수 있습니다)
cv_img = i1.file_uploader("표지(1p)", type=["png", "jpg"])
bd_img = i2.file_uploader("내지(2p)", type=["png", "jpg"])
tl_img = i3.file_uploader("안내지(3p)", type=["png", "jpg"])

# --- 2. 데이터 연동 (DB 불러오기) ---
st.divider()
st.header("📂 2. 고객 DB 관리")

col_db1, col_db2 = st.columns([1, 4])
if col_db1.button("📥 DB에서 고객 불러오기"):
    # Supabase 'clients' 테이블에서 데이터 가져오기
    response = supabase.table("clients").select("*").execute()
    st.session_state.db_data = pd.DataFrame(response.data)

up_file = st.file_uploader("신규 고객 엑셀 업로드 (DB 저장용)", type=["xlsx"])
if up_file:
    new_df = pd.read_excel(up_file)
    if st.button("💾 이 명단을 DB에 저장하기"):
        data_to_save = new_df.to_dict(orient='records')
        supabase.table("clients").insert(data_to_save).execute()
        st.success("DB 저장 완료!")
        st.rerun()

# --- 3. 고객 선택 및 PDF 생성 ---
if 'db_data' in st.session_state:
    df = st.session_state.db_data
    st.subheader("📋 대상 고객 선택")
    sel_all = st.checkbox("전체 선택")
    
    selected_indices = []
    cols = st.columns(4)
    for i, row in df.iterrows():
        name = str(row.get('이름', '무명'))
        with cols[i % 4]:
            if st.checkbox(name, value=sel_all, key=f"db_u_{i}"):
                selected_indices.append(i)

    if st.button(f"🚀 {len(selected_indices)}명 PDF 생성"):
        if not (cv_img and bd_img and tl_img):
            st.error("이미지를 모두 업로드해주세요.")
        else:
            bar = st.progress(0)
            pdf_io = io.BytesIO()
            p = canvas.Canvas(pdf_io, pagesize=A4)
            w, h = A4
            
            c_r, b_r, t_r = ImageReader(cv_img), ImageReader(bd_img), ImageReader(tl_img)

            for idx, target_i in enumerate(selected_indices):
                row = df.iloc[target_i]
                name = str(row.get('이름'))
                
                # 표지
                p.drawImage(c_r, 0, 0, width=w, height=h)
                p.setFont(FONT, 40); p.drawCentredString(w/2, h/2 + 50, f"{name} 님"); p.showPage()
                
                # 내지 (사주 계산)
                calendar = KoreanLunarCalendar()
                calendar.setSolarDate(int(row.get('년')), int(row.get('월')), int(row.get('일')))
                gapja = calendar.getGapjaString()
                p.drawImage(b_r, 0, 0, width=w, height=h)
                p.setFont(FONT, 25); p.drawString(80, 720, f"성함: {name}")
                p.setFont(FONT, 18); p.drawString(80, 680, f"사주: {gapja}"); p.showPage()
                
                # 안내지
                p.drawImage(t_r, 0, 0, width=w, height=h); p.showPage()
                bar.progress((idx + 1) / len(selected_indices))

            p.save()
            st.balloons()
            st.download_button("📥 PDF 다운로드", pdf_io.getvalue(), "saju_pro_report.pdf")
