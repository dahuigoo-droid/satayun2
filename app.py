import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io, time, os
from sqlalchemy import create_client, create_engine
from korean_lunar_calendar import KoreanLunarCalendar

# 1. 한글 폰트 설정 (사장님이 올리신 파일명과 일치시켰습니다)
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

# 2. Supabase DB 연결 (Secrets에 등록하신 DATABASE_URL 사용)
def get_db_engine():
    try:
        db_url = st.secrets["DATABASE_URL"]
        # SQLAlchemy는 postgresql:// 형태를 지원하므로 필요시 수정
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return create_engine(db_url)
    except Exception as e:
        st.error(f"DB 연결 설정 오류: {e}")
        return None

# 3. 화면 설정
st.set_page_config(page_title="사주 마스터 Pro", layout="wide")
st.title("🔮 사주/타로 리포트 생성 시스템 (Supabase 연동)")

# --- 1구역: 기본 설정 ---
st.header("⚙️ 1. 리포트 기본 설정")
c1, c2 = st.columns(2)
with c1: toc = st.text_area("📋 PDF 목차", "1. 타고난 기질\n2. 올해의 연애운", height=100)
with c2: guide = st.text_area("🤖 AI 지침", "친절하고 상세한 전문가 스타일", height=100)

st.subheader("🖼️ 디자인 이미지 업로드")
i1, i2, i3 = st.columns(3)
with i1: cv_img = i1.file_uploader("표지(1p)", type=["png", "jpg"])
with i2: bd_img = i2.file_uploader("내지(2p)", type=["png", "jpg"])
with i3: tl_img = i3.file_uploader("안내지(3p)", type=["png", "jpg"])

# --- 2구역: 데이터 관리 (Supabase 연동) ---
st.divider()
st.header("📂 2. 고객 데이터 관리")
engine = get_db_engine()

col_db1, col_db2 = st.columns([1, 4])
if col_db1.button("📥 DB에서 고객 불러오기"):
    if engine:
        try:
            st.session_state.db_data = pd.read_sql("SELECT * FROM clients", engine)
            st.success("데이터를 성공적으로 불러왔습니다.")
        except Exception as e:
            st.error(f"데이터 불러오기 실패: {e}")

up_file = st.file_uploader("신규 엑셀 업로드 (DB 저장용)", type=["xlsx"])
if up_file:
    df_new = pd.read_excel(up_file)
    if st.button("💾 이 명단을 DB에 저장하기"):
        if engine:
            try:
                df_new.to_sql('clients', engine, if_exists='append', index=False)
                st.success("DB에 고객 정보가 저장되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"저장 실패: {e}")

# --- 3구역: 선택 및 PDF 생성 ---
if 'db_data' in st.session_state:
    df = st.session_state.db_data
    st.subheader("✅ 출력 대상 선택")
    sel_all = st.checkbox("전체 선택")
    
    selected_indices = []
    cols = st.columns(4)
    for idx, row in df.iterrows():
        name = row.get('이름', '고객')
        with cols[idx % 4]:
            if st.checkbox(name, value=sel_all, key=f"user_{idx}"):
                selected_indices.append(idx)

    if st.button(f"🚀 {len(selected_indices)}명 PDF 생성 시작"):
        if not (cv_img and bd_img and tl_img):
            st.error("이미지를 모두 업로드해주세요.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            pdf_buf = io.BytesIO()
            p = canvas.Canvas(pdf_buf, pagesize=A4)
            w, h = A4
            
            c_r, b_r, t_r = ImageReader(cv_img), ImageReader(bd_img), ImageReader(tl_img)

            for i, idx in enumerate(selected_indices):
                row = df.iloc[idx]
                name = str(row.get('이름'))
                
                status_text.text(f"⏳ {name}님 작업 중... ({i+1}/{len(selected_indices)})")
                
                # 1. 표지
                p.drawImage(c_r, 0, 0, width=w, height=h)
                p.setFont(FONT, 35)
                p.drawCentredString(w/2, h/2, f"{name} 님 리포트")
                p.showPage()
                
                # 2. 내지 (사주 계산)
                p.drawImage(b_r, 0, 0, width=w, height=h)
                calendar = KoreanLunarCalendar()
                calendar.setSolarDate(int(row.get('년')), int(row.get('월')), int(row.get('일')))
                gapja = calendar.getGapjaString()
                
                p.setFont(FONT, 20)
                p.drawString(100, 700, f"성함: {name}")
                p.drawString(100, 670, f"사주팔자: {gapja}")
                p.showPage()
                
                # 3. 안내지
                p.drawImage(t_r, 0, 0, width=w, height=h)
                p.showPage()
                
                progress_bar.progress((i + 1) / len(selected_indices))
                time.sleep(0.1)

            p.save()
            status_text.empty()
            st.balloons()
            st.download_button("📥 PDF 다운로드", pdf_buf.getvalue(), "saju_report.pdf")
