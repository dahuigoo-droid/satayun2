# -*- coding: utf-8 -*-
"""
🔮 PDF 자동 생성 플랫폼
메인 페이지 (로그인/회원가입)
"""

import streamlit as st

st.set_page_config(
    page_title="PDF 자동 생성 플랫폼",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

from common import apply_common_css, init_session_state, initialize_database
from auth import login_user, register_user, check_admin_exists, create_first_admin

# DB 초기화
initialize_database()

# 세션 초기화
init_session_state()
apply_common_css()

# 이미 로그인되어 있으면
if st.session_state.get('logged_in', False):
    st.title("🔮 PDF 자동 생성 플랫폼")
    st.success(f"👋 {st.session_state.user['name']}님, 환영합니다!")
    st.markdown("왼쪽 메뉴에서 원하는 기능을 선택하세요.")
    
    st.markdown("---")
    
    # 퀵 메뉴
    st.markdown("### 🚀 빠른 메뉴")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/4_🔧서비스작업.py", label="🔧 서비스 작업", icon="🔧")
    with col2:
        st.page_link("pages/1_📢공지사항.py", label="📢 공지사항", icon="📢")
    with col3:
        st.page_link("pages/2_📚자료실.py", label="📚 자료실", icon="📚")
    
    st.stop()

# ===== 로그인/회원가입 =====
st.markdown('<h1 class="main-title">🔮 PDF 자동 생성 플랫폼</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">사주 · 연애 · 타로 운세 PDF를 자동으로 생성합니다</p>', unsafe_allow_html=True)

# 최초 관리자 체크
admin_exists = check_admin_exists()

tab1, tab2 = st.tabs(["로그인", "회원가입"])

# ===== 로그인 =====
with tab1:
    st.markdown("### 🔐 로그인")
    
    login_email = st.text_input("이메일", key="login_email")
    login_password = st.text_input("비밀번호", type="password", key="login_pw")
    
    if st.button("로그인", type="primary", use_container_width=True):
        if login_email and login_password:
            result = login_user(login_email, login_password)
            if result.get('success'):
                st.session_state.logged_in = True
                st.session_state.user = result['user']
                st.toast(f"✅ {result['user']['name']}님, 환영합니다!")
                st.rerun()
            else:
                st.error(result.get('error', '로그인 실패'))
        else:
            st.warning("이메일과 비밀번호를 입력해주세요.")

# ===== 회원가입 =====
with tab2:
    st.markdown("### 📝 회원가입")
    
    reg_email = st.text_input("이메일", key="reg_email")
    reg_name = st.text_input("이름", key="reg_name")
    reg_password = st.text_input("비밀번호", type="password", key="reg_pw")
    reg_password2 = st.text_input("비밀번호 확인", type="password", key="reg_pw2")
    
    if st.button("회원가입", type="primary", use_container_width=True):
        if not reg_email or not reg_name or not reg_password:
            st.warning("모든 필드를 입력해주세요.")
        elif reg_password != reg_password2:
            st.error("비밀번호가 일치하지 않습니다.")
        elif len(reg_password) < 4:
            st.warning("비밀번호는 4자 이상이어야 합니다.")
        else:
            result = register_user(reg_email, reg_password, reg_name)
            if result.get('success'):
                st.toast("✅ 회원가입이 완료되었습니다!")
                st.success("✅ 회원가입이 완료되었습니다! 관리자 승인 후 로그인할 수 있습니다.")
            else:
                st.error(result.get('error', '회원가입 실패'))

# ===== 최초 관리자 설정 =====
if not admin_exists:
    st.markdown("---")
    
    with st.expander("🔧 최초 관리자 설정", expanded=True):
        st.warning("⚠️ 등록된 관리자가 없습니다. 최초 관리자를 설정해주세요.")
        
        admin_email = st.text_input("관리자 이메일", key="admin_email")
        admin_name = st.text_input("관리자 이름", key="admin_name", value="관리자")
        admin_password = st.text_input("관리자 비밀번호", type="password", key="admin_pw")
        
        if st.button("👑 관리자 계정 생성", type="primary"):
            if admin_email and admin_password:
                result = create_first_admin(admin_email, admin_password, admin_name)
                if result.get('success'):
                    st.toast("✅ 관리자 계정이 생성되었습니다!")
                    st.success("✅ 관리자 계정이 생성되었습니다! 위에서 로그인해주세요.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(result.get('error', '생성 실패'))
            else:
                st.warning("이메일과 비밀번호를 입력해주세요.")
