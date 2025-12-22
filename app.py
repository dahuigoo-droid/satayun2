import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io, time, os
from korean_lunar_calendar import KoreanLunarCalendar

# [1] 폰트 설정: 사장님이 깃허브에 올린 파일 이름과 똑같이 맞췄습니다.
@st.cache_resource
def load_fonts():
    # 깃허브에 올리신 파일명 그대로 사용
    font_path = "NanumGothic-Regular.ttf" 
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('Nanum', font_path))
            return 'Nanum'
        except:
            return 'Helvetica'
    return 'Helvetica'

FONT = load_fonts()

# 화면 설정
st.set_page_config(page_title="사주/타로 마스터", layout="wide")
st.title("🔮 사주/타로 리포트 생성기 (최종본)")

# --- 1. 기본 설정 (좌우 배치) ---
st.header("⚙️ 1. 리포트 기본 설정")
c1, c2 = st.columns(2)
with c1: 
    toc = st.text_area("📋 PDF 목차", "1. 타고난 기질\n2. 올해의 운세", height=100)
with c2: 
    guide = st.text_area("🤖 AI 지침", "친절하고 상세하게 설명해주는 전문가 스타일", height=100)

st.subheader("🖼️ 디자인 이미지 업로드")
i1, i2, i3 = st.columns(3)
with i1: cv_img = st.file_uploader("표지(1p) 업로드", type=["png", "jpg"])
with i2: bd_img = st.file_uploader("내지(2p) 업로드", type=["png", "jpg"])
with i3: tl_img = st.file_uploader("안내지(3p) 업로드", type=["png", "jpg"])

# --- 2. 데이터 관리 및 고객 선택 ---
st.divider()
st.header("📂 2. 고객 데이터 선택")

# 초기화 버튼
if st.button("🔄 모든 설정 및 파일 초기화"):
    st.rerun()

up_file = st.file_uploader("엑셀 파일(.xlsx) 업로드", type=["xlsx"])

if up_file:
    df = pd.read_excel(up_file)
    st.subheader("📊 업로드된 고객 리스트")
    # 엑셀 정보 노출
    st.dataframe(df, use_container_width=True)

    st.subheader("✅ 출력 대상 선택")
    sel_all = st.checkbox("전체 선택")
    
    selected_indices = []
    cols = st.columns(4)
    for i, row in df.iterrows():
        name = str(row.get('이름', f'고객{i+1}'))
        with cols[i % 4]:
            if st.checkbox(name, value=sel_all, key=f"user_{i}"):
                selected_indices.append(i)

    # --- 3. PDF 생성 및 다운로드 ---
    st.divider()
    if st.button(f"🚀 선택한 {len(selected_indices)}명 PDF 생성 시작"):
        if not (cv_img and bd_img and tl_img):
            st.error("❌ 디자인 이미지 3장을 모두 업로드해주세요.")
        elif not selected_indices:
            st.warning("⚠️ 대상을 선택해주세요.")
        else:
            bar = st.progress(0)
            status = st.empty()
            
            pdf_io = io.BytesIO()
            p = canvas.Canvas(pdf_io, pagesize=A4)
            w, h = A4
            
            # 이미지 리더 준비
            c_r, b_r, t_r = ImageReader(cv_img), ImageReader(bd_img), ImageReader(tl_img)

            for idx, target_i in enumerate(selected_indices):
                row = df.iloc[target_i]
                name = str(row.get('이름', '고객'))
                
                # 진행률 및 텍스트 업데이트
                status.text(f"⏳ {name}님 리포트 작성 중... ({idx+1}/{len(selected_indices)})")
                
                # 1. 표지 (배경 이미지를 깔고 위에 글자 쓰기)
                p.drawImage(c_r, 0, 0, width=w, height=h)
                p.setFont(FONT, 40)
                p.drawCentredString(w/2, h/2 + 50, f"{name} 님")
                p.setFont(FONT, 20)
                p.drawCentredString(w/2, h/2 - 20, "사주 팔자 분석 리포트")
                p.showPage()
                
                # 2. 내지 (사주 데이터 포함)
                calendar = KoreanLunarCalendar()
                calendar.setSolarDate(int(row.get('년', 1990)), int(row.get('월', 1)), int(row.get('일', 1)))
                gapja = calendar.getGapjaString() # 한자와 한글이 섞여 나옵니다.
                
                p.drawImage(b_r, 0, 0, width=w, height=h)
                p.setFont(FONT, 25)
                p.drawString(80, 720, f"성함: {name}")
                p.setFont(FONT, 18)
                p.drawString(80, 680, f"사주: {gapja}")
                
                p.setFont(FONT, 12)
                p.drawString(80, 630, f"[목차] {toc.splitlines()[0]}")
                p.showPage()
                
                # 3. 안내지
                p.drawImage(t_r, 0, 0, width=
