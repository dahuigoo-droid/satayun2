# -*- coding: utf-8 -*-
"""
👤 마이페이지
"""

import streamlit as st

st.set_page_config(page_title="마이페이지", page_icon="👤", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state
)
from auth import update_user_profile, change_password
from services import get_system_config, set_system_config, ConfigKeys

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

st.title("👤 마이페이지")

tab1, tab2, tab3 = st.tabs(["📋 내 정보", "🔑 비밀번호 변경", "⚙️ API/이메일 설정"])

# ===== 내 정보 =====
with tab1:
    st.markdown("### 📋 내 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**기본 정보**")
        st.text_input("이메일", value=user.get('email', ''), disabled=True)
        new_name = st.text_input("이름", value=user.get('name', ''), key="my_name")
    
    with col2:
        st.markdown("**계정 상태**")
        
        # 등급 표시
        if user.get('is_admin'):
            st.success("👑 관리자")
        else:
            level = user.get('member_level', 1)
            level_names = {1: "1단계 (기성상품만)", 2: "2단계 (개별상품만)", 3: "3단계 (모두 사용)"}
            st.info(f"📊 회원등급: {level_names.get(level, '1단계')}")
        
        # 상태 표시
        status = user.get('status', 'pending')
        status_icons = {'approved': '✅ 승인됨', 'pending': '⏳ 승인 대기', 'suspended': '🚫 정지됨'}
        st.text(f"상태: {status_icons.get(status, status)}")
    
    st.markdown("---")
    
    if st.button("💾 정보 수정", type="primary"):
        result = update_user_profile(user['id'], name=new_name)
        if result.get('success'):
            st.session_state.user['name'] = new_name
            st.toast("✅ 정보가 수정되었습니다!")
            st.rerun()
        else:
            st.error(result.get('error', '수정 실패'))

# ===== 비밀번호 변경 =====
with tab2:
    st.markdown("### 🔑 비밀번호 변경")
    
    current_pw = st.text_input("현재 비밀번호", type="password", key="current_pw")
    new_pw = st.text_input("새 비밀번호", type="password", key="new_pw")
    confirm_pw = st.text_input("새 비밀번호 확인", type="password", key="confirm_pw")
    
    if st.button("🔑 비밀번호 변경", type="primary"):
        if not current_pw or not new_pw or not confirm_pw:
            st.warning("모든 필드를 입력해주세요.")
        elif new_pw != confirm_pw:
            st.error("새 비밀번호가 일치하지 않습니다.")
        elif len(new_pw) < 4:
            st.warning("비밀번호는 4자 이상이어야 합니다.")
        else:
            result = change_password(user['id'], current_pw, new_pw)
            if result.get('success'):
                st.toast("✅ 비밀번호가 변경되었습니다!")
            else:
                st.error(result.get('error', '변경 실패'))

# ===== API/이메일 설정 =====
with tab3:
    st.markdown("### ⚙️ API/이메일 설정")
    
    # API 모드 확인
    api_mode = user.get('api_mode', 'unified')
    email_mode = user.get('email_mode', 'unified')
    
    st.markdown("**🤖 API 설정**")
    if api_mode == 'unified':
        st.info("📌 통합 모드: 관리자 API 키를 사용합니다.")
    else:
        st.warning("📌 분리 모드: 개인 API 키를 사용합니다.")
        my_api_key = st.text_input("내 OpenAI API 키", value=user.get('api_key', ''), type="password", key="my_api")
    
    st.markdown("---")
    
    st.markdown("**📧 이메일 설정**")
    if email_mode == 'unified':
        st.info("📌 통합 모드: 관리자 Gmail을 사용합니다.")
    else:
        st.warning("📌 분리 모드: 개인 Gmail을 사용합니다.")
        my_gmail = st.text_input("내 Gmail 주소", value=user.get('gmail_address', ''), key="my_gmail")
        my_gmail_pw = st.text_input("Gmail 앱 비밀번호", value=user.get('gmail_app_password', ''), type="password", key="my_gmail_pw")
    
    st.caption("💡 API/이메일 모드는 관리자가 설정합니다.")
