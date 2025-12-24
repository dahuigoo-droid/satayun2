# 사주/타로/연애 이미지 자동 생성기
import streamlit as st
import pandas as pd
from datetime import datetime
import zipfile
import io
import os
from korean_lunar_calendar import KoreanLunarCalendar

from saju_calculator import calc_사주, calc_대운, calc_세운, calc_월운
from image_generator import create_원국표, create_대운표, create_세운표, create_월운표, create_오행차트, create_십성표, create_오행도

# ============================================
# 음력 → 양력 변환 함수
# ============================================
def 음력_to_양력(year, month, day):
    """음력 날짜를 양력으로 변환"""
    calendar = KoreanLunarCalendar()
    calendar.setLunarDate(year, month, day, False)  # False = 평달
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
        생년월일 = st.date_input("생년월일", datetime(1990, 1, 1))
    
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
                    # 음력 → 양력 변환
                    year, month, day = 음력_to_양력(input_year, input_month, input_day)
                    음력_str = f"{input_year}-{input_month:02d}-{input_day:02d}"
                    양력_str = f"{year}-{month:02d}-{day:02d} {시:02d}:{분:02d}"
                else:
                    # 양력 그대로
                    year, month, day = input_year, input_month, input_day
                    양력_str = f"{year}-{month:02d}-{day:02d} {시:02d}:{분:02d}"
                    # 양력 → 음력 변환 (표시용)
                    음력_year, 음력_month, 음력_day = 양력_to_음력(year, month, day)
                    음력_str = f"{음력_year}-{음력_month:02d}-{음력_day:02d}"
                
                # 사주 계산 (항상 양력으로)
                사주 = calc_사주(year, month, day, 시, 분)
                
                # 나이 계산
                today = datetime.now()
                나이 = today.year - year + 1  # 한국 나이
                
                # 기본정보
                기본정보 = {
                    '이름': 이름,
                    '성별': 성별,
                    '나이': 나이,
                    '양력': 양력_str,
                    '음력': 음력_str,
                }
                
                # 성별 변환 (대운 계산용)
                gender = '남' if 성별 == '남성' else '여'
                
                # 이미지 생성
                output_path = f"/tmp/{이름}_원국표.png"
                create_원국표(사주, 기본정보, output_path)
                
                # 대운 계산 및 이미지 생성
                대운_data = calc_대운(year, month, day, 시, 분, gender)
                대운_output_path = f"/tmp/{이름}_대운표.png"
                create_대운표(대운_data, 기본정보, 대운_output_path)
                
                st.success("✅ 이미지 생성 완료!")
                
                # 결과 표시 - 원국표
                st.subheader("📊 원국표")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.image(output_path, caption=f"{이름}님 원국표")
                
                with col2:
                    st.write("**사주 정보:**")
                    st.write(f"- 년주: {사주['년주'][0]}{사주['년주'][1]}")
                    st.write(f"- 월주: {사주['월주'][0]}{사주['월주'][1]}")
                    st.write(f"- 일주: {사주['일주'][0]}{사주['일주'][1]}")
                    st.write(f"- 시주: {사주['시주'][0]}{사주['시주'][1]}")
                    st.write(f"- 오행: 목{사주['오행']['목']} 화{사주['오행']['화']} 토{사주['오행']['토']} 금{사주['오행']['금']} 수{사주['오행']['수']}")
                
                # 원국표 다운로드 버튼
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="📥 원국표 다운로드",
                        data=f,
                        file_name=f"{이름}_원국표.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                # 대운표 표시
                st.subheader("📈 대운표")
                st.image(대운_output_path, caption=f"{이름}님 대운표")
                
                방향 = "순행" if 대운_data['순행'] else "역행"
                st.write(f"**대운 정보:** 대운수 {대운_data['대운수']}세, {방향}")
                
                # 대운표 다운로드 버튼
                with open(대운_output_path, "rb") as f:
                    st.download_button(
                        label="📥 대운표 다운로드",
                        data=f,
                        file_name=f"{이름}_대운표.png",
                        mime="image/png",
                        use_container_width=True,
                        key="download_대운표"
                    )
                
                # 세운 계산 및 이미지 생성
                세운_data = calc_세운(year, month, day, 시, 분)
                세운_output_path = f"/tmp/{이름}_세운표.png"
                create_세운표(세운_data, 기본정보, 세운_output_path)
                
                # 세운표 표시
                st.subheader("📅 세운표 (10년)")
                st.image(세운_output_path, caption=f"{이름}님 세운표")
                
                with open(세운_output_path, "rb") as f:
                    st.download_button(
                        label="📥 세운표 다운로드",
                        data=f,
                        file_name=f"{이름}_세운표.png",
                        mime="image/png",
                        use_container_width=True,
                        key="download_세운표"
                    )
                
                # 월운 계산 및 이미지 생성
                월운_data = calc_월운(year, month, day, 시, 분)
                월운_output_path = f"/tmp/{이름}_월운표.png"
                create_월운표(월운_data, 기본정보, 월운_output_path)
                
                # 월운표 표시
                st.subheader("🗓️ 월운표 (12개월)")
                st.image(월운_output_path, caption=f"{이름}님 월운표")
                
                with open(월운_output_path, "rb") as f:
                    st.download_button(
                        label="📥 월운표 다운로드",
                        data=f,
                        file_name=f"{이름}_월운표.png",
                        mime="image/png",
                        use_container_width=True,
                        key="download_월운표"
                    )
                
                # 오행 차트 이미지 생성
                오행_output_path = f"/tmp/{이름}_오행차트.png"
                create_오행차트(사주, 기본정보, 오행_output_path)
                
                # 오행 차트 표시
                st.subheader("🔥 오행 분포")
                st.image(오행_output_path, caption=f"{이름}님 오행 차트")
                
                with open(오행_output_path, "rb") as f:
                    st.download_button(
                        label="📥 오행차트 다운로드",
                        data=f,
                        file_name=f"{이름}_오행차트.png",
                        mime="image/png",
                        use_container_width=True,
                        key="download_오행차트"
                    )
                
                # 십성표 이미지 생성
                십성_output_path = f"/tmp/{이름}_십성표.png"
                create_십성표(사주, 기본정보, 십성_output_path)
                
                # 십성표 표시
                st.subheader("⭐ 십성 분석표")
                st.image(십성_output_path, caption=f"{이름}님 십성표")
                
                with open(십성_output_path, "rb") as f:
                    st.download_button(
                        label="📥 십성표 다운로드",
                        data=f,
                        file_name=f"{이름}_십성표.png",
                        mime="image/png",
                        use_container_width=True,
                        key="download_십성표"
                    )
                
                # 오행도 이미지 생성
                오행도_output_path = f"/tmp/{이름}_오행도.png"
                create_오행도(사주, 기본정보, 오행도_output_path)
                
                # 오행도 표시
                st.subheader("☯ 오행 상생상극도")
                st.image(오행도_output_path, caption=f"{이름}님 오행도")
                
                with open(오행도_output_path, "rb") as f:
                    st.download_button(
                        label="📥 오행도 다운로드",
                        data=f,
                        file_name=f"{이름}_오행도.png",
                        mime="image/png",
                        use_container_width=True,
                        key="download_오행도"
                    )

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
    
    # 샘플 엑셀 다운로드
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
            
            # ZIP 파일 생성
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for idx, row in df.iterrows():
                    status.text(f"처리 중: {row['이름']} ({idx+1}/{len(df)})")
                    
                    # 입력 날짜
                    input_year = int(row['생년'])
                    input_month = int(row['생월'])
                    input_day = int(row['생일'])
                    
                    # 음력/양력 변환
                    if row['음양력'] == "음력":
                        year, month, day = 음력_to_양력(input_year, input_month, input_day)
                        음력_str = f"{input_year}-{input_month:02d}-{input_day:02d}"
                        양력_str = f"{year}-{month:02d}-{day:02d} {int(row['시']):02d}:{int(row['분']):02d}"
                    else:
                        year, month, day = input_year, input_month, input_day
                        양력_str = f"{year}-{month:02d}-{day:02d} {int(row['시']):02d}:{int(row['분']):02d}"
                        음력_year, 음력_month, 음력_day = 양력_to_음력(year, month, day)
                        음력_str = f"{음력_year}-{음력_month:02d}-{음력_day:02d}"
                    
                    # 사주 계산 (항상 양력으로)
                    사주 = calc_사주(year, month, day, int(row['시']), int(row['분']))
                    
                    # 나이 계산
                    나이 = datetime.now().year - year + 1
                    
                    # 기본정보
                    기본정보 = {
                        '이름': row['이름'],
                        '성별': row['성별'],
                        '나이': 나이,
                        '양력': 양력_str,
                        '음력': 음력_str,
                    }
                    
                    # 성별 변환
                    gender = '남' if row['성별'] == '남성' else '여'
                    
                    # 원국표 이미지 생성
                    output_path = f"/tmp/{row['이름']}_원국표.png"
                    create_원국표(사주, 기본정보, output_path)
                    
                    # 대운 계산 및 이미지 생성
                    대운_data = calc_대운(year, month, day, int(row['시']), int(row['분']), gender)
                    대운_output_path = f"/tmp/{row['이름']}_대운표.png"
                    create_대운표(대운_data, 기본정보, 대운_output_path)
                    
                    # 세운 계산 및 이미지 생성
                    세운_data = calc_세운(year, month, day, int(row['시']), int(row['분']))
                    세운_output_path = f"/tmp/{row['이름']}_세운표.png"
                    create_세운표(세운_data, 기본정보, 세운_output_path)
                    
                    # 월운 계산 및 이미지 생성
                    월운_data = calc_월운(year, month, day, int(row['시']), int(row['분']))
                    월운_output_path = f"/tmp/{row['이름']}_월운표.png"
                    create_월운표(월운_data, 기본정보, 월운_output_path)
                    
                    # 오행 차트 이미지 생성
                    오행_output_path = f"/tmp/{row['이름']}_오행차트.png"
                    create_오행차트(사주, 기본정보, 오행_output_path)
                    
                    # 십성표 이미지 생성
                    십성_output_path = f"/tmp/{row['이름']}_십성표.png"
                    create_십성표(사주, 기본정보, 십성_output_path)
                    
                    # 오행도 이미지 생성
                    오행도_output_path = f"/tmp/{row['이름']}_오행도.png"
                    create_오행도(사주, 기본정보, 오행도_output_path)
                    
                    # ZIP에 추가 (폴더 구조)
                    folder_name = f"{row['이름']}_{row['생년']}-{row['생월']:02d}-{row['생일']:02d}"
                    zf.write(output_path, f"{folder_name}/원국표.png")
                    zf.write(대운_output_path, f"{folder_name}/대운표.png")
                    zf.write(세운_output_path, f"{folder_name}/세운표.png")
                    zf.write(월운_output_path, f"{folder_name}/월운표.png")
                    zf.write(오행_output_path, f"{folder_name}/오행차트.png")
                    zf.write(십성_output_path, f"{folder_name}/십성표.png")
                    zf.write(오행도_output_path, f"{folder_name}/오행도.png")
                    
                    progress.progress((idx + 1) / len(df))
            
            status.text("✅ 완료!")
            
            # ZIP 다운로드
            zip_buffer.seek(0)
            st.download_button(
                label="📥 전체 다운로드 (ZIP)",
                data=zip_buffer,
                file_name="사주_이미지_결과.zip",
                mime="application/zip",
                use_container_width=True
            )

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
    원국표_체크 = st.checkbox("원국표", value=True)
    대운표_체크 = st.checkbox("대운표", value=True)
    세운표_체크 = st.checkbox("세운표", value=True)
    월운표_체크 = st.checkbox("월운표", value=True)
    오행차트_체크 = st.checkbox("오행 차트", value=True)
    오행도_체크 = st.checkbox("오행 상생상극도", value=True)
    십성표_체크 = st.checkbox("십성표", value=True)
    
    st.divider()
    st.caption("v1.0 - 사주 이미지 생성기")
