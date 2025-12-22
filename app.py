import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import io
from korean_lunar_calendar import KoreanLunarCalendar

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

# 2. 화면 설정 (전체 넓게 사용)
st.set_page_config(page_title="사주/타로 PDF 생성기", layout="wide")
st.title("🔮 사주/타로 PDF 자동 생성 시스템")

st.divider()
st.header("⚙️ 리포트 기본 설정")

# --- 좌우 나란히 배치하는 부분 ---
# 화면을 1:1 비율로 두 개의 기둥(col1, col2)으로 나눕니다.
col1, col2 = st.columns(2)

with col1:
    toc_list = st.text_area("📋 PDF 목차 (리포트 순서)", 
                           value="1. 타고난 기질\n2. 올해의 연애운\n3. 타로 카드의 조언", 
                           height=200) # 높이를 충분히 주어 내용이 다 보이게 함

with col2:
    ai_guide = st.text_area("🤖 AI 상담사 지침 (말투 및 스타일)", 
                           value="친절하고 상세하게 설명해주는 전문가 스타일로 작성하세요.", 
                           height=200)

st.divider()

# 3. 엑셀 파일 업로드
st.header("📂 1. 고객 데이터 업로드")
uploaded_file = st.file_uploader("고객 정보 엑셀 파일(.xlsx)을 업로드하세요.", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"총 {len(df)}명의 데이터를 확인했습니다.")
    
    st.header("📊 2. 고객별 사주 분석 결과")
    
    for index, row in df.iterrows():
        name = row.get('이름', f'고객{index+1}')
        y, m, d = row.get('년', 1990), row.get('월', 1), row.get('일', 1)
        gapja_text, element_scores = get_saju_data(y, m, d)
        
        with st.expander(f"👤 {name} 님의 사주 분석 결과"):
            st.write(f"**사주 팔자:** {gapja_text}")
            fig, ax = plt.subplots(figsize=(10, 2)) # 분석 그래프도 가로로 길게
            colors = ['#2ECC71', '#E74C3C', '#F1C40F', '#BDC3C7', '#3498DB']
            ax.bar(element_scores.keys(), element_scores.values(), color=colors)
            st.pyplot(fig)

    # 4. PDF 생성 버튼
    st.divider()
    if st.button("📄 모든 결과 PDF로 한꺼번에 만들기"):
        st.info("PDF 생성 기능을 준비 중입니다...")
