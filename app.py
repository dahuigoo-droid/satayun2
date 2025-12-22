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

# 1. 한글 폰트 설정 (NanumGothic-Regular.ttf 사용)
@st.cache_resource
def load_fonts():
    font_path = "NanumGothic-Regular.ttf"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('Hangeul', font_path))
            return 'Hangeul'
        except Exception as e:
            st.error(f"폰트 등록 오류: {e}")
            return 'Helvetica'
    return 'Helvetica'

FONT = load_fonts()

# 2. Supabase DB 연결 (Secrets의 DATABASE_URL 사용)
def get_db_engine():
    try:
        if "DATABASE_URL" not in st.secrets:
            st.error("Secrets에 DATABASE_URL이 설정되지 않았습니다.")
            return None
        
        db_url = st.secrets["DATABASE_URL"]
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        return create_engine(db_url)
    except Exception as e:
        st.error(f"DB 연결 설정 오류: {e}")
        return None

# 3. 화면 설정
st.set_page_config(page_title="사주 마스터 Pro", layout="wide")
st.title("🔮 사주/타로 리포트 생성 시스템")

# --- 1구역: 기본 설정 (좌우 배치) ---
st.header("⚙️ 1. 리포트 기본 설정")
col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    toc = st.text_area("📋 PDF 목차", value="1. 타고난 기질\n2. 올해의 연애운\n3. 타로 카드의 조언", height=120)
with col_cfg2:
    guide = st.text_area("🤖 AI 지침", value="친절하고 상세하게 설명해주는 전문가 스타일로 작성하세요.", height=120)

st.subheader("🖼️ 디자인 이미지 업로드")
i1, i2, i3 = st.columns(3)
with i1: cv_img = i1.file_uploader("표지(1p)", type=["png", "jpg"])
with i2: bd_img = i2.file_uploader("내지(2p)", type=["png", "jpg"])
with i3: tl_img = i3.file_uploader("안내지(3p)", type=["png", "jpg"])

# --- 2구역: 데이터 관리 (DB 연동) ---
st.divider()
st.header("📂 2. 고객 데이터 관리")
engine = get_db_engine()

db_btn_col, up_file_col = st.columns([1, 3])

with db_btn_col:
    if st.button("📥 DB에서 고객 불러오기", use_container_width=True):
        if engine:
            try:
                st.session_state.db_data = pd.read_sql("SELECT * FROM clients", engine)
                st.success("데이터 로드 완료!")
            except Exception as e:
                st.error("DB에 'clients' 테이블이 없거나 데이터가 없습니다.")

with up_file_col:
    up_file = st.file_uploader("신규 고객 엑셀 업로드 (DB 저장용)", type=["xlsx"])

if up_file:
    df_new = pd.read_excel(up_file)
    st.dataframe(df_new.head(3), use_container_width=True)
    if st.button("💾 이 명단을 DB에 저장하기"):
        if engine:
            try:
                df_new.to_sql('clients', engine, if_exists='append', index=False)
                st.success("DB 저장 성공! '불러오기'를 눌러주세요.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"저장 실패: {e}")

# --- 3구역: 선택 및 PDF 생성 ---
if 'db_data' in st.session_state:
    df = st.session_state.db_data
    st.subheader("✅ 출력 대상 고객 선택")
    sel_all = st.checkbox("전체 고객 선택")
    
    selected_indices = []
    cols = st.columns(4)
    for idx, row in df.iterrows():
        name = str(row.get('이름', f'고객{idx}'))
        with cols[idx % 4]:
            if st.checkbox(f"{name}", value=sel_all, key=f"user_{idx}"):
                selected_indices.append(idx)

    # 에러 났던 루프 구문 수정 완료
    if st.button(f"🚀 선택한 {len(selected_
