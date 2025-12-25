# 사주/타로/연애 이미지 자동 생성기
import streamlit as st
import pandas as pd
from datetime import datetime
import zipfile
import io
import os
from korean_lunar_calendar import KoreanLunarCalendar

from saju_calculator import calc_사주, calc_대운, calc_세운, calc_월운, calc_신살
from image_generator import (
    create_원국표, create_대운표, create_세운표, create_월운표, 
    create_오행차트, create_십성표, create_신살표,
    create_12운성표, create_지장간표, create_합충형파해표,
    create_궁성표, create_육친표, create_납음오행표,
    create_격국표, create_공망표, create_일진표
)

# 12지 이미지 경로 설정
ZODIAC_PATH = os.path.join(os.path.dirname(__file__), 'images', 'zodiac')

# ============================================
# 음력 → 양력 변환 함수
# ============================================
def 음력_to_양력(year, month, day):
    """음력 날짜를 양력으로 변환"""
    calendar = KoreanLunarCalendar()
    calendar.setLunarDate(year, month, day, False)
    return calendar.solarYear, calendar.solarMonth, calendar.solarDay

def 양력_to_음력(year, month, day):
    """양력 날짜를 음력으로 변환"""
    calendar = KoreanLunarCalendar()
    calendar.setSolarDate(year, month, day)
    return calendar.lunarYear, calendar.lunarMonth, calendar.lunarDay

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="사주 이미지 생성기",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 사주/타로/연애 이미지 생성기")

# ============================================
# 사이드바
# ============================================
with st.sidebar:
    st.header("🔮 서비스 선택")
    서비스 = st.radio(
        "생성할 이미지 종류",
        ["사주", "타로 (준비중)", "연애상담 (준비중)"]
    )
    
    st.divider()
    
    st.header("📊 생성할 이미지")
    
    # 전체 선택 체크박스
    전체선택 = st.checkbox("✅ 전체 선택", value=True, key="select_all")
    
    st.divider()
    
    원국표_체크 = st.checkbox("원국표", value=전체선택)
    대운표_체크 = st.checkbox("대운표", value=전체선택)
    세운표_체크 = st.checkbox("세운표", value=전체선택)
    월운표_체크 = st.checkbox("월운표", value=전체선택)
    오행차트_체크 = st.checkbox("오행 분석", value=전체선택)
    십성표_체크 = st.checkbox("십성표", value=전체선택)
    신살표_체크 = st.checkbox("신살표", value=전체선택)
    운성표_체크 = st.checkbox("12운성표", value=전체선택)
    지장간표_체크 = st.checkbox("지장간표", value=전체선택)
    합충형파해표_체크 = st.checkbox("합충형파해표", value=전체선택)
    궁성표_체크 = st.checkbox("궁성표", value=전체선택)
    육친표_체크 = st.checkbox("육친표", value=전체선택)
    납음오행표_체크 = st.checkbox("납음오행표", value=전체선택)
    격국표_체크 = st.checkbox("격국표", value=전체선택)
    공망표_체크 = st.checkbox("공망표", value=전체선택)
    
    st.divider()
    st.caption("v1.0 - 사주 이미지 생성기")

# ============================================
# 탭 구성
# ============================================
tab1, tab2 = st.tabs(["📝 개별 입력", "📊 엑셀 일괄 처리"])

# ============================================
# 탭1: 개별 입력
# ============================================
with tab1:
    st.subheader("고객 정보 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        이름 = st.text_input("이름", placeholder="홍길동")
        성별 = st.radio("성별", ["남성", "여성"], horizontal=True)
        생년월일 = st.date_input(
            "생년월일", 
            datetime(1990, 1, 1),
            min_value=datetime(1900, 1, 1),
            max_value=datetime(2030, 12, 31)
        )
    
    with col2:
        시간_col1, 시간_col2 = st.columns(2)
        with 시간_col1:
            시 = st.number_input("시", min_value=0, max_value=23, value=12)
        with 시간_col2:
            분 = st.number_input("분", min_value=0, max_value=59, value=0)
        
        음양력 = st.radio("음력/양력", ["양력", "음력"], horizontal=True)
    
    st.divider()
    
    if st.button("🎯 이미지 생성", type="primary", use_container_width=True):
        if not 이름:
            st.error("이름을 입력해주세요.")
        else:
            with st.spinner("이미지 생성 중..."):
                # 입력 날짜
                input_year = 생년월일.year
                input_month = 생년월일.month
                input_day = 생년월일.day
                
                # 음력/양력 변환
                if 음양력 == "음력":
                    year, month, day = 음력_to_양력(input_year, input_month, input_day)
                    음력_str = f"{input_year}-{input_month:02d}-{input_day:02d}"
                    양력_str = f"{year}-{month:02d}-{day:02d} {시:02d}:{분:02d}"
                else:
                    year, month, day = input_year, input_month, input_day
                    양력_str = f"{year}-{month:02d}-{day:02d} {시:02d}:{분:02d}"
                    음력_year, 음력_month, 음력_day = 양력_to_음력(year, month, day)
                    음력_str = f"{음력_year}-{음력_month:02d}-{음력_day:02d}"
                
                # 사주 계산
                사주 = calc_사주(year, month, day, 시, 분)
                
                # 나이 계산
                today = datetime.now()
                나이 = today.year - year + 1
                
                # 기본정보
                기본정보 = {
                    '이름': 이름,
                    '성별': 성별,
                    '나이': 나이,
                    '양력': 양력_str,
                    '음력': 음력_str,
                }
                
                gender = '남' if 성별 == '남성' else '여'
                신살_data = calc_신살(사주, gender)
                
                # 생성된 이미지 경로 저장
                생성된_이미지 = {}
                
                # 체크된 이미지만 생성
                if 원국표_체크:
                    path = f"/tmp/{이름}_원국표.png"
                    create_원국표(사주, 기본정보, path, 신살_data, ZODIAC_PATH)
                    생성된_이미지['01_원국표'] = path
                
                if 대운표_체크:
                    대운_data = calc_대운(year, month, day, 시, 분, gender)
                    path = f"/tmp/{이름}_대운표.png"
                    create_대운표(대운_data, 기본정보, path)
                    생성된_이미지['02_대운표'] = path
                
                if 세운표_체크:
                    세운_data = calc_세운(year, month, day, 시, 분)
                    path = f"/tmp/{이름}_세운표.png"
                    create_세운표(세운_data, 기본정보, path)
                    생성된_이미지['03_세운표'] = path
                
                if 월운표_체크:
                    월운_data = calc_월운(year, month, day, 시, 분)
                    path = f"/tmp/{이름}_월운표.png"
                    create_월운표(월운_data, 기본정보, path)
                    생성된_이미지['04_월운표'] = path
                
                if 오행차트_체크:
                    path = f"/tmp/{이름}_오행분석.png"
                    create_오행차트(사주, 기본정보, path)
                    생성된_이미지['05_오행분석'] = path
                
                if 십성표_체크:
                    path = f"/tmp/{이름}_십성표.png"
                    create_십성표(사주, 기본정보, path)
                    생성된_이미지['06_십성표'] = path
                
                if 신살표_체크:
                    path = f"/tmp/{이름}_신살표.png"
                    create_신살표(신살_data, 기본정보, path)
                    생성된_이미지['07_신살표'] = path
                
                if 운성표_체크:
                    path = f"/tmp/{이름}_12운성표.png"
                    create_12운성표(사주, 기본정보, path)
                    생성된_이미지['08_12운성표'] = path
                
                if 지장간표_체크:
                    path = f"/tmp/{이름}_지장간표.png"
                    create_지장간표(사주, 기본정보, path)
                    생성된_이미지['09_지장간표'] = path
                
                if 합충형파해표_체크:
                    path = f"/tmp/{이름}_합충형파해표.png"
                    create_합충형파해표(사주, 기본정보, path)
                    생성된_이미지['10_합충형파해표'] = path
                
                if 궁성표_체크:
                    path = f"/tmp/{이름}_궁성표.png"
                    create_궁성표(사주, 기본정보, path)
                    생성된_이미지['11_궁성표'] = path
                
                if 육친표_체크:
                    path = f"/tmp/{이름}_육친표.png"
                    create_육친표(사주, 기본정보, gender, path)
                    생성된_이미지['12_육친표'] = path
                
                if 납음오행표_체크:
                    path = f"/tmp/{이름}_납음오행표.png"
                    create_납음오행표(사주, 기본정보, path)
                    생성된_이미지['13_납음오행표'] = path
                
                if 격국표_체크:
                    path = f"/tmp/{이름}_격국표.png"
                    create_격국표(사주, 기본정보, path)
                    생성된_이미지['14_격국표'] = path
                
                if 공망표_체크:
                    path = f"/tmp/{이름}_공망표.png"
                    create_공망표(사주, 기본정보, path)
                    생성된_이미지['15_공망표'] = path
                
                st.success(f"✅ 이미지 생성 완료! ({len(생성된_이미지)}개)")
                
                # ============================================
                # 전체 다운로드 버튼 (상단)
                # ============================================
                if len(생성된_이미지) > 0:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for 파일명, 경로 in 생성된_이미지.items():
                            zf.write(경로, f"{파일명}.png")
                    
                    zip_buffer.seek(0)
                    st.download_button(
                        label=f"📦 전체 다운로드 ({len(생성된_이미지)}개 ZIP)",
                        data=zip_buffer,
                        file_name=f"{이름}_사주분석.zip",
                        mime="application/zip",
                        use_container_width=True,
                        key="download_전체_zip"
                    )
                
                st.divider()
                
                # ============================================
                # 개별 이미지 표시
                # ============================================
                if '01_원국표' in 생성된_이미지:
                    st.subheader("📊 원국표")
                    st.image(생성된_이미지['01_원국표'], caption=f"{이름}님 원국표")
                
                if '02_대운표' in 생성된_이미지:
                    st.subheader("📈 대운표")
                    st.image(생성된_이미지['02_대운표'], caption=f"{이름}님 대운표")
                
                if '03_세운표' in 생성된_이미지:
                    st.subheader("📅 세운표")
                    st.image(생성된_이미지['03_세운표'], caption=f"{이름}님 세운표")
                
                if '04_월운표' in 생성된_이미지:
                    st.subheader("🗓️ 월운표")
                    st.image(생성된_이미지['04_월운표'], caption=f"{이름}님 월운표")
                
                if '05_오행분석' in 생성된_이미지:
                    st.subheader("🔥 오행 분석")
                    st.image(생성된_이미지['05_오행분석'], caption=f"{이름}님 오행분석")
                
                if '06_십성표' in 생성된_이미지:
                    st.subheader("⭐ 십성표")
                    st.image(생성된_이미지['06_십성표'], caption=f"{이름}님 십성표")
                
                if '07_신살표' in 생성된_이미지:
                    st.subheader("🔮 신살표")
                    st.image(생성된_이미지['07_신살표'], caption=f"{이름}님 신살표")
                
                if '08_12운성표' in 생성된_이미지:
                    st.subheader("🔄 12운성표")
                    st.image(생성된_이미지['08_12운성표'], caption=f"{이름}님 12운성표")
                
                if '09_지장간표' in 생성된_이미지:
                    st.subheader("📋 지장간표")
                    st.image(생성된_이미지['09_지장간표'], caption=f"{이름}님 지장간표")
                
                if '10_합충형파해표' in 생성된_이미지:
                    st.subheader("⚡ 합충형파해표")
                    st.image(생성된_이미지['10_합충형파해표'], caption=f"{이름}님 합충형파해표")
                
                if '11_궁성표' in 생성된_이미지:
                    st.subheader("🏠 궁성표")
                    st.image(생성된_이미지['11_궁성표'], caption=f"{이름}님 궁성표")
                
                if '12_육친표' in 생성된_이미지:
                    st.subheader("👨‍👩‍👧‍👦 육친표")
                    st.image(생성된_이미지['12_육친표'], caption=f"{이름}님 육친표")
                
                if '13_납음오행표' in 생성된_이미지:
                    st.subheader("🎵 납음오행표")
                    st.image(생성된_이미지['13_납음오행표'], caption=f"{이름}님 납음오행표")
                
                if '14_격국표' in 생성된_이미지:
                    st.subheader("🎯 격국표")
                    st.image(생성된_이미지['14_격국표'], caption=f"{이름}님 격국표")
                
                if '15_공망표' in 생성된_이미지:
                    st.subheader("🕳️ 공망표")
                    st.image(생성된_이미지['15_공망표'], caption=f"{이름}님 공망표")

# ============================================
# 탭2: 엑셀 일괄 처리
# ============================================
with tab2:
    st.subheader("엑셀 파일 업로드")
    
    # 샘플 다운로드
    sample_data = {
        '이름': ['홍길동', '김철수'],
        '성별': ['남성', '여성'],
        '생년': [1990, 1985],
        '생월': [5, 12],
        '생일': [15, 3],
        '시': [14, 8],
        '분': [30, 0],
        '음양력': ['양력', '양력'],
    }
    sample_df = pd.DataFrame(sample_data)
    
    buffer = io.BytesIO()
    sample_df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    
    st.download_button(
        label="📋 샘플 엑셀 다운로드",
        data=buffer,
        file_name="sample_input.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    uploaded_file = st.file_uploader("엑셀 파일 선택", type=['xlsx', 'xls'])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write(f"**{len(df)}명 데이터 확인:**")
        st.dataframe(df, use_container_width=True)
        
        if st.button("🎯 일괄 생성", type="primary", use_container_width=True):
            progress = st.progress(0)
            status = st.empty()
            
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for idx, row in df.iterrows():
                    status.text(f"처리 중: {row['이름']} ({idx+1}/{len(df)})")
                    
                    input_year = int(row['생년'])
                    input_month = int(row['생월'])
                    input_day = int(row['생일'])
                    
                    if row['음양력'] == "음력":
                        year, month, day = 음력_to_양력(input_year, input_month, input_day)
                        음력_str = f"{input_year}-{input_month:02d}-{input_day:02d}"
                        양력_str = f"{year}-{month:02d}-{day:02d} {int(row['시']):02d}:{int(row['분']):02d}"
                    else:
                        year, month, day = input_year, input_month, input_day
                        양력_str = f"{year}-{month:02d}-{day:02d} {int(row['시']):02d}:{int(row['분']):02d}"
                        음력_year, 음력_month, 음력_day = 양력_to_음력(year, month, day)
                        음력_str = f"{음력_year}-{음력_month:02d}-{음력_day:02d}"
                    
                    사주 = calc_사주(year, month, day, int(row['시']), int(row['분']))
                    나이 = datetime.now().year - year + 1
                    
                    기본정보 = {
                        '이름': row['이름'],
                        '성별': row['성별'],
                        '나이': 나이,
                        '양력': 양력_str,
                        '음력': 음력_str,
                    }
                    
                    gender = '남' if row['성별'] == '남성' else '여'
                    신살_data = calc_신살(사주, gender)
                    
                    folder_name = f"{row['이름']}_{row['생년']}-{row['생월']:02d}-{row['생일']:02d}"
                    
                    # 체크된 이미지만 생성
                    if 원국표_체크:
                        path = f"/tmp/{row['이름']}_원국표.png"
                        create_원국표(사주, 기본정보, path, 신살_data, ZODIAC_PATH)
                        zf.write(path, f"{folder_name}/01_원국표.png")
                    
                    if 대운표_체크:
                        대운_data = calc_대운(year, month, day, int(row['시']), int(row['분']), gender)
                        path = f"/tmp/{row['이름']}_대운표.png"
                        create_대운표(대운_data, 기본정보, path)
                        zf.write(path, f"{folder_name}/02_대운표.png")
                    
                    if 세운표_체크:
                        세운_data = calc_세운(year, month, day, int(row['시']), int(row['분']))
                        path = f"/tmp/{row['이름']}_세운표.png"
                        create_세운표(세운_data, 기본정보, path)
                        zf.write(path, f"{folder_name}/03_세운표.png")
                    
                    if 월운표_체크:
                        월운_data = calc_월운(year, month, day, int(row['시']), int(row['분']))
                        path = f"/tmp/{row['이름']}_월운표.png"
                        create_월운표(월운_data, 기본정보, path)
                        zf.write(path, f"{folder_name}/04_월운표.png")
                    
                    if 오행차트_체크:
                        path = f"/tmp/{row['이름']}_오행분석.png"
                        create_오행차트(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/05_오행분석.png")
                    
                    if 십성표_체크:
                        path = f"/tmp/{row['이름']}_십성표.png"
                        create_십성표(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/06_십성표.png")
                    
                    if 신살표_체크:
                        path = f"/tmp/{row['이름']}_신살표.png"
                        create_신살표(신살_data, 기본정보, path)
                        zf.write(path, f"{folder_name}/07_신살표.png")
                    
                    if 운성표_체크:
                        path = f"/tmp/{row['이름']}_12운성표.png"
                        create_12운성표(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/08_12운성표.png")
                    
                    if 지장간표_체크:
                        path = f"/tmp/{row['이름']}_지장간표.png"
                        create_지장간표(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/09_지장간표.png")
                    
                    if 합충형파해표_체크:
                        path = f"/tmp/{row['이름']}_합충형파해표.png"
                        create_합충형파해표(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/10_합충형파해표.png")
                    
                    if 궁성표_체크:
                        path = f"/tmp/{row['이름']}_궁성표.png"
                        create_궁성표(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/11_궁성표.png")
                    
                    if 육친표_체크:
                        path = f"/tmp/{row['이름']}_육친표.png"
                        create_육친표(사주, 기본정보, gender, path)
                        zf.write(path, f"{folder_name}/12_육친표.png")
                    
                    if 납음오행표_체크:
                        path = f"/tmp/{row['이름']}_납음오행표.png"
                        create_납음오행표(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/13_납음오행표.png")
                    
                    if 격국표_체크:
                        path = f"/tmp/{row['이름']}_격국표.png"
                        create_격국표(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/14_격국표.png")
                    
                    if 공망표_체크:
                        path = f"/tmp/{row['이름']}_공망표.png"
                        create_공망표(사주, 기본정보, path)
                        zf.write(path, f"{folder_name}/15_공망표.png")
                    
                    progress.progress((idx + 1) / len(df))
            
            status.text("✅ 완료!")
            
            zip_buffer.seek(0)
            st.download_button(
                label="📥 전체 다운로드 (ZIP)",
                data=zip_buffer,
                file_name="사주_이미지_결과.zip",
                mime="application/zip",
                use_container_width=True
            )
