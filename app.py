import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import io
from korean_lunar_calendar import KoreanLunarCalendar

# --- 1. 사주 계산 엔진 (기능 구역) ---
def get_saju_data(year, month, day):
    calendar = KoreanLunarCalendar()
    # 양력 날짜 설정
    calendar.setSolarDate(int(year), int(month), int(day))
    # 간지(사주 글자) 가져오기
    gapja = calendar.getGapjaString() 
    
    # 오행 점수 계산 (단순 예시)
    scores = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    if "甲" in gapja or "乙" in gapja or "寅" in gapja or "卯" in gapja: scores["목"] += 20
    if "丙" in gapja or "丁" in gapja or "巳" in gapja or "午" in gapja: scores["화"] += 20
    if "戊" in gapja or "己" in gapja or "辰" in gapja or "戌" in gapja or "丑" in gapja or "未" in gapja: scores["토"] += 20
    if "庚" in gapja or "辛" in gapja or "申" in gapja or "酉" in gapja: scores["금"] += 20
    if "壬" in gapja or "癸" in gapja or "亥" in gapja or "子" in gapja: scores["수"] += 20
    
    return gapja, scores

# --- 2. 화면 구성 (보여지는 구역) ---
st.set_page_config(page_title="사주/타로 PDF 생성기", layout="wide")
st.title("🔮 사주/타로 PDF 자동 생성 시스템")

with st.sidebar:
    st.header("⚙️ 설정")
    toc_list = st.text_area("📋 PDF 목차", value="1. 타고난 기질\n2. 올해의 운세\n3. 타로의 조언")
    ai_guide = st.text_area("🤖 AI 지침", value="다정한 역술가 스타일로 써주세요.")

st.header("📂 1. 고객 데이터 업로드")
uploaded_file = st.file_uploader("고객 엑셀(.xlsx)을 올려주세요.", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("데이터를 불러왔습니다!")
    
    st.header("📊 2. 사주 분석 결과")
    
    # 엑셀의 각 줄(고객)마다 반복해서 계산
    for index, row in df.iterrows():
        try:
            # 엑셀 칸 이름이 '이름', '년', '월', '일'이어야 합니다.
            name = row['이름']
            y, m, d = row['년'], row['월'], row['일']
            
            gapja_text, element_scores = get_saju_data(y, m, d)
            
            with st.expander(f"👤 {name} 님의 분석 결과 보기"):
                st.write(f"**사주 팔자:** {gapja_text}")
                
                # 그래프 그리기
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.bar(element_scores.keys(), element_scores.values(), color=['green', 'red', 'brown', 'gray', 'blue'])
                st.pyplot(fig)
        except Exception as e:
            st.error(f"{index+1}번째 줄 데이터에 문제가 있어요. (칸 이름을 확인하세요)")

    # --- 3. PDF 생성 버튼 ---
    if st.button("📄 모든 고객 PDF 생성 및 다운로드"):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, "Saju Report")
        p.save()
        st.download_button("PDF 다운로드", data=buffer.getvalue(), file_name="report.pdf")
