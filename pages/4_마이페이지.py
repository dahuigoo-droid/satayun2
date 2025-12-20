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

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

st.title("👤 마이페이지")

tab1, tab2, tab3 = st.tabs(["📋 내 정보", "🔑 비밀번호 변경", "📦 내 상품 권한"])

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
        
        if user.get('is_admin'):
            st.success("👑 관리자")
        else:
            st.info("📊 일반 회원")
        
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

# ===== 내 상품 권한 =====
with tab3:
    st.markdown("### 📦 내 상품 권한")
    st.caption("관리자가 설정한 내 상품 사용 권한입니다.")
    
    st.markdown("---")
    
    # 현재 권한 가져오기
    allowed_products = user.get('allowed_products', ['기성상품'])
    if isinstance(allowed_products, str):
        allowed_products = [allowed_products]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📦 기성상품")
        if '기성상품' in allowed_products:
            st.success("✅ 사용 가능")
        else:
            st.error("❌ 권한 없음")
    
    with col2:
        st.markdown("### 🎯 개별상품")
        if '개별상품' in allowed_products:
            st.success("✅ 사용 가능")
        else:
            st.error("❌ 권한 없음")
    
    with col3:
        st.markdown("### 👑 고급상품")
        if '고급상품' in allowed_products:
            st.success("✅ 사용 가능")
        else:
            st.error("❌ 권한 없음")
    
    st.markdown("---")
    st.caption("💡 권한이 필요하시면 관리자에게 문의하세요.")
