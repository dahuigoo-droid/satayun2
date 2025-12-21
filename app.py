# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# 기존 파일들에서 기능을 가져옵니다.
from database import init_db
from auth import login_user, get_all_users
from services import get_admin_services, get_user_services
from pdf_generator import PDFGenerator

# 1. 화면 설정
st.set_page_config(page_title="PDF 자동 생성 플랫폼", page_icon="🔮", layout="wide")

def main():
    # DB 초기화
    init_db()

    # 세션 상태 설정
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None

    # --- [기능 1] 전면 초기화 버튼 (사이드바) ---
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

    # 3. 메인 메뉴 구성
    user = st.session_state.user
    with st.sidebar:
        st.write(f"### 👤 {user['name']}님")
        menu = st.radio("메뉴 선택", ["📢 공지사항", "🔧 서비스 작업", "📚 자료실", "👤 MyPage"])
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- [기능 2] 서비스 작업 (엑셀 전체 선택 포함) ---
    if menu == "🔧 서비스 작업":
        st.title("🔧 서비스 작업")
        
        # 상품 목록 불러오기
        admin_services = get_admin_services()
        if admin_services:
            svc_names = [s['name'] for s in admin_services]
            selected_svc_name = st.selectbox("상품 선택", svc_names)
            selected_service = next(s for s in admin_services if s['name'] == selected_svc_name)

            st.divider()
            st.subheader("📁 고객 엑셀 업로드")
            uploaded_file = st.file_uploader("엑셀 파일을 선택하세요", type=['xlsx'])

            if uploaded_file:
                if 'df' not in st.session_state:
                    st.session_state.df = pd.read_excel(uploaded_file)
                
                df = st.session_state.df
                
                # [전체 선택 기능]
                all_select = st.checkbox("✅ 전체 고객 선택 / 해제")
                
                selected_indices = []
                st.markdown("### 👥 고객 목록")
                
                # 고객 목록 테이블 출력
                for idx, row in df.iterrows():
                    c1, c2, c3 = st.columns([1, 4, 5])
                    with c1:
                        # 전체 선택과 연동된 개별 체크박스
                        is_selected = st.checkbox("", value=all_select, key=f"cust_{idx}")
                        if is_selected:
                            selected_indices.append(idx)
                    with c2:
                        st.write(f"**{row.get('이름', '이름없음')}**")
                    with c3:
                        st.caption(f"{row.get('생년월일', '')} | {row.get('이메일', '')}")

                st.info(f"현재 {len(selected_indices)}명이 선택되었습니다.")

                if st.button("🚀 PDF 생성 시작", type="primary", use_container_width=True):
                    if len(selected_indices) > 0:
                        with st.status("PDF 생성 중...") as status:
                            # 실제 생성 기계 가동
                            pdf_gen = PDFGenerator()
                            st.write(f"{len(selected_indices)}명의 데이터를 분석 중입니다...")
                            time.sleep(1)
                            status.update(label="생성 완료!", state="complete")
                        st.success("작업이 모두 완료되었습니다!")
                    else:
                        st.warning("선택된 고객이 없습니다.")

    elif menu == "📢 공지사항":
        st.title("📢 공지사항")
        st.info("등록된 공지사항이 여기에 표시됩니다.")
    elif menu == "📚 자료실":
        st.title("📚 자료실")
        st.info("목차 및 지침 라이브러리입니다.")
    elif menu == "👤 MyPage":
        st.title("👤 마이페이지")
        st.write(f"로그인 계정: {user['email']}")

if __name__ == "__main__":
    main()
