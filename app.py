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
            except:
                st.error("DB에 데이터가 없거나 'clients' 테이블이 없습니다.")

with up_file_col:
    up_file = st.file_uploader("신규 고객 엑셀 업로드", type=["xlsx"])

if up_file:
    df_new = pd.read_excel(up_file)
    if st.button("💾 업로드한 명단 DB에 저장"):
        if engine:
            df_new.to_sql('clients', engine, if_exists='append', index=False)
            st.success("저장 성공! 'DB에서 고객 불러오기'를 다시 눌러주세요.")
            st.rerun()

# --- 3구역: 선택 및 PDF 생성 (여기가 핵심!) ---
if 'db_data' in st.session_state:
    df = st.session_state.db_data
    st.subheader("✅ 리포트를 만들 고객 선택")
    sel_all = st.checkbox("전체 고객 선택")
    
    selected_indices = []
    cols = st.columns(4)
    for idx, row in df.iterrows():
        name = str(row.get('이름', '고객'))
        with cols[idx % 4]:
            if st.checkbox(f"{name}", value=sel_all, key=f"u_{idx}"):
                selected_indices.append(idx)

    st.divider()
    # [PDF 생성 버튼과 기능]
    if st.button(f"🚀 선택한 {len(selected_indices)}명 PDF 리포트 생성 시작"):
        if not (cv_img and bd_img and tl_img):
            st.error("❌ 디자인 이미지 3장을 모두 업로드해주셔야 PDF를 만들 수 있습니다.")
        elif not selected_indices:
            st.warning("⚠️ 선택된 고객이 없습니다.")
        else:
            prog_bar = st.progress(0)
            status_msg = st.empty()
            
            # PDF를 메모리에 생성
            pdf_buf = io.BytesIO()
            p = canvas.Canvas(pdf_buf, pagesize=A4)
            w, h = A4
            
            # 업로드한 이미지 읽기
            c_r, b_r, t_r = ImageReader(cv_img), ImageReader(bd_img), ImageReader(tl_img)

            for i, idx_in_df in enumerate(selected_indices):
                row = df.iloc[idx_in_df]
                name = str(row.get('이름', '고객'))
                status_msg.text(f"📝 {name}님 리포트 생성 중... ({i+1}/{len(selected_indices)})")
                
                # 1. 표지 작성
                p.drawImage(c_r, 0, 0, width=w, height=h)
                p.setFont(FONT, 35)
                p.drawCentredString(w/2, h/2 + 50, f"{name} 님")
                p.setFont(FONT, 20)
                p.drawCentredString(w/2, h/2 - 20, "연애 사주 리포트")
                p.showPage()
                
                # 2. 내지 작성 (사주 계산)
                p.drawImage(b_r, 0, 0, width=w, height=h)
                cal = KoreanLunarCalendar()
                cal.setSolarDate(int(row.get('년', 1990)), int(row.get('월', 1)), int(row.get('일', 1)))
                gapja = cal.getGapjaString()
                
                p.setFont(FONT, 22)
                p.drawString(80, 720, f"성함: {name}")
                p.setFont(FONT, 18)
                p.drawString(80, 680, f"사주팔자: {gapja}")
                p.showPage()
                
                # 3. 안내지 작성
                p.drawImage(t_r, 0, 0, width=w, height=h)
                p.showPage()
                
                prog_bar.progress((i + 1) / len(selected_indices))
                time.sleep(0.05)

            p.save() # PDF 저장 완료
            status_msg.empty()
            st.balloons()
            st.success(f"✅ 총 {len(selected_indices)}명의 리포트가 완성되었습니다!")
            
            # 생성된 PDF 다운로드 버튼 노출
            st.download_button(
                label="📥 완성된 PDF 다운로드 받기",
                data=pdf_buf.getvalue(),
                file_name="saju_reports.pdf",
                mime="application/pdf"
            )
