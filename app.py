import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# --- 1. 화면 구성 (UI) ---
st.set_page_config(page_title="사주/타로 PDF 생성기", layout="wide")
st.title("🔮 사주/타로 PDF 자동 생성 시스템")

with st.sidebar:
    st.header("⚙️ 설정")
    # 여기에 Supabase 주소와 키를 넣게 됩니다.
    supabase_url = st.text_input("Supabase URL")
    supabase_key = st.text_input("Supabase API Key", type="password")
    
    st.divider()
    toc_list = st.text_area("📋 PDF 목차 (엔터로 구분)", 
                           value="1. 타고난 기질\n2. 올해의 운세\n3. 타로의 조언")
    ai_guide = st.text_area("🤖 AI 지침(프롬프트)", 
                           value="당신은 다정한 상담가입니다. 전문 용어를 쉽게 풀어서 설명하세요.")

# --- 2. 엑셀 업로드 및 데이터베이스 저장 로직 ---
st.header("📂 1. 고객 데이터 업로드")
uploaded_file = st.file_uploader("고객 정보 엑셀 파일(.xlsx)을 올려주세요.", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("엑셀 파일을 성공적으로 읽었습니다!")
    st.dataframe(df.head()) # 데이터 확인용

    # --- 3. 그래프 생성 (Matplotlib) ---
    st.header("📊 2. 사주 오행 분석 (샘플 그래프)")
    
    def create_element_chart():
        elements = ['목', '화', '토', '금', '수']
        values = [20, 15, 30, 10, 25] # 임시 데이터 (나중에 사주 로직으로 계산)
        
        fig, ax = plt.subplots()
        ax.bar(elements, values, color=['green', 'red', 'brown', 'gray', 'blue'])
        plt.rcParams['font.family'] = 'Malgun Gothic' # 한글 깨짐 방지
        return fig

    fig = create_element_chart()
    st.pyplot(fig)

    # --- 4. PDF 생성 (ReportLab) ---
    st.header("📄 3. PDF 리포트 생성")
    
    if st.button("모든 고객 PDF 생성 및 다운로드"):
        # PDF를 메모리에 생성
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        
        # 간단한 내용 채우기
        p.setFont("Helvetica", 20)
        p.drawString(100, 800, "Saju & Tarot Report")
        
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Guide: {ai_guide}")
        
        # 목차 그리기
        y_pos = 700
        for line in toc_list.split('\n'):
            p.drawString(100, y_pos, line)
            y_pos -= 20
            
        p.showPage()
        p.save()
        
        st.download_button(
            label="PDF 다운로드",
            data=buffer.getvalue(),
            file_name="report.pdf",
            mime="application/pdf"
        )
# 먼저 터미널에 설치: pip install korean-lunar-calendar
from korean_lunar_calendar import KoreanLunarCalendar

def get_saju_data(year, month, day, hour):
    # 1. 만세력 도구 가져오기
    calendar = KoreanLunarCalendar()
    # 2. 양력 날짜를 넣어서 사주 글자 뽑기
    calendar.setSolarDate(year, month, day)
    
    # 3. 사주 팔자 글자들 (예: 경오, 무인..)
    gapja = calendar.getGapjaString() 
    
    # 4. 오행 점수 계산기 (아주 단순화한 버전)
    # 실제로는 '갑/을=목', '병/정=화' 식으로 매칭합니다.
    element_scores = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    
    # 예시: 사주 글자에 특정 한자가 포함되면 점수 플러스!
    if "甲" in gapja or "乙" in gapja: element_scores["목"] += 20
    if "丙" in gapja or "丁" in gapja: element_scores["화"] += 20
    # ... 이런식으로 8글자를 다 검사합니다.
    
    return gapja, element_scores

# --- 스트림릿 화면에서 사용 예시 ---
st.header("🔮 사주 분석 엔진 가동")
if uploaded_file:
    for index, row in df.iterrows():
        # 엑셀에 '년', '월', '일' 컬럼이 있다고 가정
        gapja_text, scores = get_saju_data(row['년'], row['월'], row['일'], 12)
        st.write(f"### {row['이름']} 님의 사주: {gapja_text}")
        
        # 이 점수를 아까 만든 Matplotlib 그래프에 연결!
        fig, ax = plt.subplots()
        ax.bar(scores.keys(), scores.values(), color=['green', 'red', 'yellow', 'gray', 'blue'])
        st.pyplot(fig)

from korean_lunar_calendar import KoreanLunarCalendar

def 사주_계산기(연, 월, 일):
    calendar = KoreanLunarCalendar()
    
    # 1. 양력 날짜를 설정합니다.
    calendar.setSolarDate(연, 월, 일)
    
    # 2. 사주 팔자(간지)를 한자로 가져옵니다.
    # 예: "庚午年 戊寅月 丙戌日" 이런 식으로 나옵니다.
    간지_결과 = calendar.getGapjaString()
    
    return 간지_결과
