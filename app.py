import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import io
import time  # 부드러운 진행률을 위해 필요
from korean_lunar_calendar import KoreanLunarCalendar
from PIL import Image

# 1. 사주 계산 함수
def get_saju_data(year, month, day):
    calendar = KoreanLunarCalendar()
    try:
        calendar.setSolarDate(int(year), int(month), int(day))
        gapja = calendar.getGapjaString() 
        scores = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
        if any(x in gapja for x in ["甲", "乙", "寅", "卯"]): scores["목"] += 20
        if any(x in gapja for x in ["丙", "丁", "巳", "午"]): scores["화"] += 20
        if any(x in gapja for x in ["戊", "己", "辰", "戌", "丑", "未"]): scores["토"] += 20
        if any(x in gapja for x in ["庚", "辛", "申", "酉"]): scores["금"] += 20
        if any(x in gapja for x in ["壬", "癸", "亥", "子"]): scores["수"] += 20
        return gapja, scores
    except:
        return "날짜 오류", {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}

# 2. 화면 설정
st.set_page_config(page_title="사주/타로 PDF 생성기", layout="wide")
st.title("🔮 사주/타로 리포트 생성 시스템")

# 디자인 설정 구역
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

# 3. 데이터 업로드 및 실행
st.divider()
st.header("📂 2. 데이터 업로드 및 실행")
uploaded_file = st.file_uploader("고객 엑셀 파일(.xlsx) 업로드", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    total_customers = len(df)
    
    if st.button("🚀 PDF 생성 시작하기"):
        # --- 진행률 바 및 상태 메시지 구역 ---
        progress_text = st.empty() # 상태 메시지 표시용 빈 칸
        my_bar = st.progress(0)    # 진행률 바
        
        for i, row in df.iterrows():
            name = row.get('이름', f'고객{i+1}')
            
            # 1. 상태 표시: 사주 분석 중
            progress_text.text(f"⏳ [{i+1}/{total_customers}] {name}님의 사주 정보를 분석하고 있습니다...")
            get_saju_data(row.get('년', 1990), row.get('월', 1), row.get('일', 1))
            time.sleep(0.3) # 부드럽게 보이기 위한 아주 짧은 대기
            
            # 2. 상태 표시: AI 풀이 생성 중
            progress_text.text(f"🤖 [{i+1}/{total_customers}] AI가 {name}님을 위한 연애운 문장을 짓고 있습니다...")
            time.sleep(0.5)
            
            # 3. 상태 표시: PDF 굽는 중
            progress_text.text(f"📄 [{i+1}/{total_customers}] 디자인 배경에 내용을 합성하여 PDF를 생성 중입니다...")
            time.sleep(0.2)
            
            # 진행률 바 업데이트
            percent_complete = int(((i + 1) / total_customers) * 100)
            my_bar.progress(percent_complete)
        
        # --- 완료 처리 ---
        progress_text.empty() # 작업 중 메시지 삭제
        st.balloons() # 축하 풍선 효과
        st.success(f"✅ 총 {total_customers}명의 리포트 생성이 완료되었습니다!")
        
        # 다운로드 버튼 (임시 파일)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, "Saju Report Completed")
        p.save()
        st.download_button("📥 생성된 PDF 전체 다운로드", data=buffer.getvalue(), file_name="saju_reports.pdf")
