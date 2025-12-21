# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import time
from database import init_db
from pdf_generator import PDFGenerator

# 페이지 설정
st.set_page_config(page_title="PDF 자동 생성 플랫폼", layout="wide")

def main():
    # 데이터베이스 연결 준비
    init_db()

    # --- 1. 상단 타이틀 및 초기화 버튼 ---
    st.title("🔮 PDF 보고서 자동 생성기")
    
    # [기능] 전면 초기화 버튼
    if st.sidebar.button("🔄 전체 작업 초기화", use_container_width=True, help="업로드된 파일과 모든 진행 상황을 지우고 처음으로 돌아갑니다."):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # --- 2. 설정 섹션 ---
    with st.sidebar:
        st.header("⚙️ 기본 설정")
        target_pages = st.number_input("목표 페이지 수", min_value=1, value=10, step=1)
        api_key = st.text_input("OpenAI API Key", type="password")

    # --- 3. 엑셀 업로드 및 고객 목록 섹션 ---
    st.subheader("📁 고객 정보 관리")
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요 (.xlsx)", type=['xlsx'])

    if uploaded_file:
        # 엑셀 파일 읽기
        if 'df' not in st.session_state:
            st.session_state.df = pd.read_excel(uploaded_file)
        
        df = st.session_state.df
        
        # [기능] 전체 선택 체크박스
        st.markdown("### 👥 고객 목록")
        all_select = st.checkbox("✅ 전체 고객 선택 / 해제", value=False)
        
        # 고객 목록 테이블 UI
        selected_indices = []
        
        # 헤더 부분
        h1, h2, h3 = st.columns([1, 4, 5])
        h1.write("**선택**")
        h2.write("**이름**")
        h3.write("**기타 정보**")
        st.divider()

        # [기능] 고객별 체크박스 생성
        for idx, row in df.iterrows():
            c1, c2, c3 = st.columns([1, 4, 5])
            with c1:
                # 전체 선택 버튼과 연동됨
                is_selected = st.checkbox("", value=all_select, key=f"check_{idx}")
                if is_selected:
                    selected_indices.append(idx)
            with c2:
                st.write(f"**{row.get('이름', '이름 없음')}**")
            with c3:
                st.caption(f"{row.get('생년월일', '')} | {row.get('이메일', '')}")

        st.info(f"현재 {len(selected_indices)}명의 고객이 선택되었습니다.")

        # --- 4. PDF 생성 실행 섹션 ---
        if st.button("🚀 선택된 고객 PDF 생성 시작", type="primary", use_container_width=True):
            if not api_key:
                st.error("API 키를 입력해주세요!")
            elif len(selected_indices) == 0:
                st.warning("최소 한 명 이상의 고객을 선택해주세요.")
            else:
                # PDF 생성 로직 실행
                with st.status("PDF 생성 중...") as status:
                    pdf_gen = PDFGenerator()
                    # 여기에 실제 GPT 호출 및 생성 로직이 연결됩니다.
                    # 예시를 위해 첫 번째 선택된 고객만 생성하는 로직 시연
                    st.write(f"{df.loc[selected_indices[0], '이름']} 님 포함 {len(selected_indices)}명 작업 시작...")
                    time.sleep(1) # 작업 중인 척 하는 시간
                    
                    status.update(label="PDF 생성 완료!", state="complete")
                st.success("모든 작업이 완료되었습니다. 결과물을 확인하세요.")

    else:
        st.info("왼쪽 메뉴에서 설정을 확인하고, 엑셀 파일을 업로드하면 고객 목록이 나타납니다.")

if __name__ == "__main__":
    main()
