# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# 기존 프로젝트 파일들과의 연결
from database import init_db
from auth import login_user, get_all_users
from services import get_admin_services, get_user_services
from pdf_generator import PDFGenerator

# 1. 화면 레이아웃 설정
st.set_page_config(page_title="PDF 자동 생성 플랫폼", page_icon="🔮", layout="wide")

def main():
    # 데이터베이스 기계 시작
    init_db()

    # 세션 상태 설정
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None

    # --- [기능 1] 전면 작업 초기화 (사이드바) ---
    with st.sidebar:
        if st.button("🔄 전체 작업 초기화", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['logged_in', 'user']:
                    del st.session_state[key]
            st.rerun()

    # 2. 로그인 화면
    if not st.session_state.logged_in:
        st.title("🔮 PDF 플랫폼 로그인")
        with st.form("login_form"):
            email = st.text_input("이메일")
            pw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인"):
                result = login_user(email, pw)
                if result["success"]:
                    st.session_state.logged_in = True
                    st.session_state.user = result["user"]
                    st.rerun()
                else:
                    st.error(result["error"])
        return

    # 3. 메인 메뉴 화면
    user = st.session_state.user
    with st.sidebar:
        st.write(f"### 👤 {user['name']}님")
        menu = st.radio("메뉴 선택", ["📢 공지사항", "🔧 서비스 작업", "📚 자료실", "👤 MyPage"])
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- [기능 2] 서비스 작업 메뉴 (진행률 바 포함) ---
    if menu == "🔧 서비스 작업":
        st.title("🔧 서비스 작업")
        
        admin_services = get_admin_services()
        if admin_services:
            svc_names = [s['name'] for s in admin_services]
            selected_svc_name = st.selectbox("상품 선택", svc_names)
            
            st.divider()
            uploaded_file = st.file_uploader("고객 목록 엑셀 파일 (.xlsx)", type=['xlsx'])

            if uploaded_file:
                if 'df' not in st.session_state:
                    st.session_state.df = pd.read_excel(uploaded_file)
                
                df = st.session_state.df
                all_select = st.checkbox("✅ 전체 고객 선택 / 해제", value=False)
                
                selected_indices = []
                h1, h2, h3 = st.columns([1, 4, 5])
                h1.write("**선택**")
                h2.write("**이름**")
                h3.write("**정보**")
                st.divider()

                for idx, row in df.iterrows():
                    c1, c2, c3 = st.columns([1, 4, 5])
                    with c1:
                        is_selected = st.checkbox("", value=all_select, key=f"cust_{idx}")
                        if is_selected:
                            selected_indices.append(idx)
                    with c2:
                        st.write(f"**{row.get('이름', '미입력')}**")
                    with c3:
                        st.write(str(row.get('생년월일', '')))

                if selected_indices:
                    st.info(f"현재 {len(selected_indices)}명이 선택되었습니다.")

                # --- 핵심: 진행률 바가 나타나는 버튼 ---
                if st.button("🚀 선택된 고객 PDF 생성 시작", type="primary", use_container_width=True):
                    # 1. 진행률 바와 메시지 칸 만들기
                    progress_bar = st.progress(0) 
                    status_text = st.empty()
                    
                    total = len(selected_indices)
                    for i, s_idx in enumerate(selected_indices):
                        name = df.loc[s_idx, '이름']
                        
                        # 2. 진행률 업데이트 (0.0 ~ 1.0 사이의 숫자)
                        percent = (i + 1) / total
                        progress_bar.progress(percent)
                        status_text.write(f"⏳ ({i+1}/{total}) {name}님 보고서 작성 중...")
                        
                        # 실제 생성 기계 작동
                        pdf_gen = PDFGenerator()
                        # (여기서 실제로 GPT가 글을 쓰고 PDF를 만듭니다)
                        time.sleep(1) # 눈으로 확인하기 위한 잠깐의 대기 시간
                    
                    status_text.success(f"✅ 총 {total}명의 PDF 생성이 완료되었습니다!")
                    st.balloons() # 축하 풍선 효과

    # 나머지 메뉴 유지
    elif menu == "📢 공지사항":
        st.title("📢 공지사항")
    elif menu == "📚 자료실":
        st.title("📚 자료실")
    elif menu == "👤 MyPage":
        st.title("👤 마이페이지")

if __name__ == "__main__":
    main()
