import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import io
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
st.title("🔮 사주/타로 리포트 커스터마이징 시스템")

# --- 3. 이미지 업로드 섹션 (새로 추가됨) ---
st.divider()
st.header("🖼️ PDF 디자인 이미지 설정")
img_col1, img_col2, img_col3 = st.columns(3)

with img_col1:
    st.subheader("1. 표지 이미지")
    cover_img = st.file_uploader("표지(첫장) 업로드", type=["png", "jpg", "jpeg"], key="cover")
    if cover_img:
        st.image(cover_img, caption="업로드된 표지", width=150)

with img_col2:
    st.subheader("2. 내지 배경")
    body_img = st.file_uploader("본문 배경 업로드", type=["png", "jpg", "jpeg"], key="body")
    if body_img:
        st.image(body_img, caption="업로드된 내지", width=150)

with img_col3:
    st.subheader("3. 마지막 안내지")
    tail_img = st.file_uploader("마지막장 업로드", type=["png", "jpg", "jpeg"], key="tail")
    if tail_img:
        st.image(tail_img, caption="업로드된 안내지", width=150)

# --- 4. 리포트 기본 설정 (좌우 배치) ---
st.divider()
st.header("⚙️ 리포트 기본 설정")
col1, col2 = st.columns(2)

with col1:
    toc_list = st.text_area("📋 PDF 목차 (리포트 순서)", 
                           value="1. 타고난 기질\n2. 올해의 연애운\n3. 타로 카드의 조언", 
                           height=150)

with col2:
    ai_guide = st.text_area("🤖 AI 상담사 지침 (말투 및 스타일)", 
                           value="친절하고 상세하게 설명해주는 전문가 스타일로 작성하세요.", 
                           height=150)

# 5. 엑셀 파일 업로드
st.divider()
st.header("📂 2. 고객 데이터 업로드")
uploaded_file = st.file_uploader("고객 정보 엑셀 파일(.xlsx)을 업로드하세요.", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"총 {len(df)}명의 데이터를 확인했습니다.")
    
    # PDF 생성 버튼 (기능은 추후 이미지 합성 로직 추가 예정)
    if st.button("📄 설정된 이미지와 내용으로 PDF 생성하기"):
        if not cover_img or not body_img or not tail_img:
            st.warning("표지, 내지, 안내지 이미지를 모두 업로드해야 완벽한 PDF가 생성됩니다.")
        else:
            st.info("현재 설정된 이미지와 데이터를 바탕으로 PDF를 굽고 있습니다... (잠시만 기다려주세요)")
