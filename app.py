import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader # 이미지 처리를 위해 필수!
import io
import time
from korean_lunar_calendar import KoreanLunarCalendar
from PIL import Image

# 1. 사주 계산 함수
def get_saju_data(year, month, day):
    calendar = KoreanLunarCalendar()
    try:
        calendar.setSolarDate(int(year), int(month), int(day))
        return calendar.getGapjaString()
    except:
        return "날짜 오류"

# 2. 화면 설정
st.set_page_config(page_title="사주/타로 PDF 생성기", layout="wide")
st.title("🔮 사주/타로 리포트 생성 시스템")

# --- 디자인 및 내용 설정 ---
st.divider()
st.header("🖼️ 1. 디자인 및 내용 설정")
img_col1, img_col2, img_col3 = st.columns(3)
with img_col1:
    cover_img = st.file_uploader("표지 업로드", type=["png", "jpg"], key="cover")
with img_col2:
    body_img = st.file_uploader("내지 배경 업로드", type=["png", "jpg"], key="body")
with img_col3:
    tail_img = st.file_uploader("안내지 업로드", type=["png", "jpg"], key="tail")

col1, col2 = st.columns(2)
with col1:
    toc_list = st.text_area("📋 PDF 목차", value="1. 타고난 기질\n2. 올해의 연애운\n3. 타로 조언", height=150)
with col2:
    ai_guide = st.text_area("🤖 AI 지침", value="친절한 전문가 스타일로 작성하세요.", height=150)

# --- 데이터 업로드 및 실행 ---
st.divider()
st.header("📂 2. 데이터 업로드 및 실행")
uploaded_file = st.file_uploader("고객 엑셀 파일(.xlsx) 업로드", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    if st.button("🚀 PDF 생성 시작하기"):
        if not (cover_img and body_img and tail_img):
            st.error("❌ 모든 이미지(표지, 내지, 안내지)를 업로드해주세요!")
        else:
            progress_text = st.empty()
            my_bar = st.progress(0)
            
            pdf_buffer = io.BytesIO()
            p = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4

            # 에러 방지: 이미지를 ReportLab이 읽을 수 있는 형식으로 변환
            cover_reader = ImageReader(cover_img)
            body_reader = ImageReader(body_img)
            tail_reader = ImageReader(tail_img)

            for i, row in df.iterrows():
                name = row.get('이름', f'고객{i+1}')
                y, m, d = row.get('년', 1990), row.get('월', 1), row.get('일', 1)
                gapja_result = get_saju_data(y, m, d)

                # --- [1페이지: 표지] ---
                progress_text.text(f"📄 {name}님의 표지 생성 중...")
                p.drawImage(cover_reader, 0, 0, width=width, height=height)
                p.setFont("Helvetica-Bold", 30)
                p.drawCentredString(width/2, height/2 + 100, f"{name}'s Report")
                p.showPage()

                # --- [2페이지: 내지] ---
                progress_text.text(f"📝 {name}님의 분석 내용 작성 중...")
                p.drawImage(body_reader, 0, 0, width=width, height=height)
                p.setFont("Helvetica", 15)
                # 데이터 반영 (한글 폰트 설정 전까지는 영어로 출력 권장)
                p.drawString(100, 700, f"Name: {name}")
                p.drawString(100, 670, f"Saju: {gapja_result}")
                p.showPage()

                # --- [3페이지: 안내지] ---
                progress_text.text(f"🏁 마지막 페이지 합성 중...")
                p.drawImage(tail_reader, 0, 0, width=width, height=height)
                p.showPage()

                my_bar.progress(int(((i + 1) / len(df)) * 100))

            p.save()
            progress_text.empty()
            st.balloons()
            
            st.download_button(
                label="📥 완성된 PDF 다운로드",
                data=pdf_buffer.getvalue(),
                file_name="saju_report.pdf",
                mime="application/pdf"
            )
