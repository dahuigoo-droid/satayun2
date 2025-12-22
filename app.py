import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io, time, urllib.request, os # os를 제대로 불러왔습니다.
from korean_lunar_calendar import KoreanLunarCalendar

# [1] 한글 폰트 자동 설치 (에러 수정 완료)
@st.cache_resource
def load_hangeul_font():
    font_url = "https://github.com/googlefonts/nanumgothic/raw/main/fonts/NanumGothic-Regular.ttf"
    font_path = "NanumGothic.ttf"
    # io.os 대신 os.path로 수정했습니다.
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(font_url, font_path)
    pdfmetrics.registerFont(TTFont('Hangeul', font_path))
    return 'Hangeul'

FONT = load_hangeul_font()

# 화면 설정
st.set_page_config(page_title="사주 PDF 마스터", layout="wide")
st.title("🔮 사주/타로 리포트 생성기")

# 1. 설정창 (좌우 배치)
st.header("⚙️ 1. 기본 설정")
c1, c2 = st.columns(2)
with c1: toc = st.text_area("📋 PDF 목차", "1. 타고난 기질\n2. 올해의 운세", height=100)
with c2: guide = st.text_area("🤖 AI 지침", "친절한 전문가 스타일로 작성", height=100)

st.subheader("🖼️ 디자인 이미지 업로드")
i1, i2, i3 = st.columns(3)
with i1: cv_img = st.file_uploader("표지(1p)", type=["png", "jpg"])
with i2: bd_img = st.file_uploader("내지(2p)", type=["png", "jpg"])
with i3: tl_img = st.file_uploader("안내지(3p)", type=["png", "jpg"])

# 2. 데이터 관리 및 선택
st.divider()
st.header("📂 2. 데이터 관리")

if st.button("🔄 전체 초기화"):
    st.rerun()

up_file = st.file_uploader("엑셀 파일(.xlsx) 업로드", type=["xlsx"])

if up_file:
    df = pd.read_excel(up_file)
    st.subheader("📊 고객 목록 및 선택")
    sel_all = st.checkbox("전체 선택")
    
    selected = []
    cols = st.columns(4)
    for i, row in df.iterrows():
        name = row.get('이름', f'고객{i+1}')
        with cols[i % 4]:
            if st.checkbox(name, value=sel_all, key=f"u_{i}"):
                selected.append(i)

    # 3. PDF 생성 실행
    if st.button(f"🚀 {len(selected)}명 PDF 만들기 시작"):
        if not (cv_img and bd_img and tl_img):
            st.error("이미지 3장을 모두 올려주세요!")
        else:
            bar = st.progress(0)
            msg = st.empty()
            pdf_io = io.BytesIO()
            p = canvas.Canvas(pdf_io, pagesize=A4)
            w, h = A4
            
            # 이미지 읽기
            c_r, b_r, t_r = ImageReader(cv_img), ImageReader(bd_img), ImageReader(tl_img)

            for idx, target_i in enumerate(selected):
                row = df.iloc[target_i]
                name = str(row.get('이름', '고객'))
                
                msg.text(f"⏳ {name}님 작업 중... ({idx+1}/{len(selected)})")
                
                # 표지
                p.drawImage(c_r, 0, 0, width=w, height=h)
                p.setFont(FONT, 30); p.drawCentredString(w/2, h/2, f"{name}님 리포트"); p.showPage()
                
                # 내지
                p.drawImage(b_r, 0, 0, width=w, height=h)
                p.setFont(FONT, 20); p.drawString(100, 700, f"성함: {name}"); p.showPage()
                
                # 안내지
                p.drawImage(t_r, 0, 0, width=w, height=h)
                p.showPage()
                
                bar.progress((idx + 1) / len(selected))

            p.save()
            msg.empty(); st.balloons()
            st.success("완성되었습니다!")
            st.download_button("📥 PDF 다운로드", pdf_io.getvalue(), "report.pdf")
