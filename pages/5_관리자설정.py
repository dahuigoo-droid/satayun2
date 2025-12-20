# -*- coding: utf-8 -*-
"""
⚙️ 관리자 설정 페이지
- 회원 관리
- 상품 권한 설정 (기성/개별/고급)
- 시스템 설정
"""

import streamlit as st

st.set_page_config(page_title="관리자 설정", page_icon="⚙️", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    is_admin
)
from auth import (
    get_all_users, get_pending_users, approve_user, suspend_user, activate_user,
    update_user_settings
)
from services import get_system_config, set_system_config, ConfigKeys

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

# 관리자 체크
if not is_admin():
    st.error("🔒 관리자만 접근할 수 있습니다.")
    st.stop()

st.title("⚙️ 관리자 설정")

tab1, tab2, tab3 = st.tabs(["👥 회원 관리", "📦 상품 권한", "🔧 시스템 설정"])

# =====================================================
# 👥 회원 관리
# =====================================================
with tab1:
    st.markdown("### 👥 회원 관리")
    
    # 승인 대기 회원
    pending = get_pending_users()
    if pending:
        st.markdown("#### ⏳ 승인 대기")
        for u in pending:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{u['name']}** ({u['email']})")
            with col2:
                if st.button("✅ 승인", key=f"approve_{u['id']}"):
                    approve_user(u['id'])
                    st.toast(f"✅ {u['name']} 승인됨")
                    st.rerun()
            with col3:
                if st.button("❌ 거부", key=f"reject_{u['id']}"):
                    suspend_user(u['id'])
                    st.toast(f"❌ {u['name']} 거부됨")
                    st.rerun()
        st.markdown("---")
    
    # 전체 회원 목록
    st.markdown("#### 📋 전체 회원")
    
    all_users = get_all_users()
    
    if all_users:
        for u in all_users:
            if u['id'] == user['id']:
                continue
            
            with st.expander(f"{'👑 ' if u.get('is_admin') else ''}{u['name']} ({u['email']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**기본 정보**")
                    st.text(f"이메일: {u['email']}")
                    st.text(f"이름: {u['name']}")
                    
                    status = u.get('status', 'pending')
                    status_icons = {'approved': '✅ 승인됨', 'pending': '⏳ 대기', 'suspended': '🚫 정지'}
                    st.text(f"상태: {status_icons.get(status, status)}")
                
                with col2:
                    st.markdown("**설정**")
                    
                    # API 모드
                    api_mode = st.selectbox(
                        "API 모드",
                        options=['unified', 'separated'],
                        index=0 if u.get('api_mode', 'unified') == 'unified' else 1,
                        format_func=lambda x: '통합 (관리자 API)' if x == 'unified' else '분리 (개인 API)',
                        key=f"api_{u['id']}"
                    )
                    
                    # 이메일 모드
                    email_mode = st.selectbox(
                        "이메일 모드",
                        options=['unified', 'separated'],
                        index=0 if u.get('email_mode', 'unified') == 'unified' else 1,
                        format_func=lambda x: '통합 (관리자 Gmail)' if x == 'unified' else '분리 (개인 Gmail)',
                        key=f"email_{u['id']}"
                    )
                
                st.markdown("---")
                
                col_save, col_status = st.columns(2)
                
                with col_save:
                    if st.button("💾 설정 저장", key=f"save_user_{u['id']}", type="primary", use_container_width=True):
                        update_user_settings(u['id'], api_mode=api_mode, email_mode=email_mode)
                        st.toast(f"✅ {u['name']} 설정 저장됨")
                        st.rerun()
                
                with col_status:
                    if u.get('status') == 'approved':
                        if st.button("🚫 정지", key=f"suspend_{u['id']}", use_container_width=True):
                            suspend_user(u['id'])
                            st.toast(f"🚫 {u['name']} 정지됨")
                            st.rerun()
                    else:
                        if st.button("✅ 활성화", key=f"activate_{u['id']}", use_container_width=True):
                            activate_user(u['id'])
                            st.toast(f"✅ {u['name']} 활성화됨")
                            st.rerun()
    else:
        st.info("등록된 회원이 없습니다.")

# =====================================================
# 📦 상품 권한 설정
# =====================================================
with tab2:
    st.markdown("### 📦 상품 권한 설정")
    st.caption("각 회원이 볼 수 있는 상품 유형을 설정합니다.")
    
    st.markdown("---")
    
    all_users = get_all_users()
    
    if all_users:
        # 헤더
        col_name, col_std, col_ind, col_prm, col_save = st.columns([2.5, 1, 1, 1, 1])
        with col_name:
            st.markdown("**회원**")
        with col_std:
            st.markdown("**📦 기성**")
        with col_ind:
            st.markdown("**🎯 개별**")
        with col_prm:
            st.markdown("**👑 고급**")
        with col_save:
            st.markdown("**저장**")
        
        st.markdown("---")
        
        for u in all_users:
            if u['id'] == user['id']:
                continue
            
            # 현재 권한 가져오기 (기본값: 기성상품만)
            current_products = u.get('allowed_products', ['기성상품'])
            if isinstance(current_products, str):
                current_products = [current_products]
            
            col_name, col_std, col_ind, col_prm, col_save = st.columns([2.5, 1, 1, 1, 1])
            
            with col_name:
                admin_icon = "👑 " if u.get('is_admin') else ""
                st.write(f"{admin_icon}{u['name']}")
            
            with col_std:
                std_checked = st.checkbox(
                    "기성", 
                    value='기성상품' in current_products,
                    key=f"perm_std_{u['id']}",
                    label_visibility="collapsed"
                )
            
            with col_ind:
                ind_checked = st.checkbox(
                    "개별",
                    value='개별상품' in current_products,
                    key=f"perm_ind_{u['id']}",
                    label_visibility="collapsed"
                )
            
            with col_prm:
                prm_checked = st.checkbox(
                    "고급",
                    value='고급상품' in current_products,
                    key=f"perm_prm_{u['id']}",
                    label_visibility="collapsed"
                )
            
            with col_save:
                if st.button("💾", key=f"save_perm_{u['id']}", help="권한 저장"):
                    new_products = []
                    if std_checked:
                        new_products.append('기성상품')
                    if ind_checked:
                        new_products.append('개별상품')
                    if prm_checked:
                        new_products.append('고급상품')
                    
                    update_user_settings(u['id'], allowed_products=new_products)
                    st.toast(f"✅ {u['name']} 권한 저장됨")
                    st.rerun()
        
        st.markdown("---")
        
        # 일괄 설정
        st.markdown("#### 🔧 일괄 설정")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📦 전체 기성만", use_container_width=True):
                for u in all_users:
                    if u['id'] != user['id']:
                        update_user_settings(u['id'], allowed_products=['기성상품'])
                st.toast("✅ 전체: 기성상품만")
                st.rerun()
        with col2:
            if st.button("🎯 전체 기성+개별", use_container_width=True):
                for u in all_users:
                    if u['id'] != user['id']:
                        update_user_settings(u['id'], allowed_products=['기성상품', '개별상품'])
                st.toast("✅ 전체: 기성+개별")
                st.rerun()
        with col3:
            if st.button("👑 전체 모든 상품", use_container_width=True):
                for u in all_users:
                    if u['id'] != user['id']:
                        update_user_settings(u['id'], allowed_products=['기성상품', '개별상품', '고급상품'])
                st.toast("✅ 전체: 모든 상품")
                st.rerun()
    else:
        st.info("등록된 회원이 없습니다.")

# =====================================================
# 🔧 시스템 설정
# =====================================================
with tab3:
    st.markdown("### 🔧 시스템 설정")
    
    # API 키 설정
    st.markdown("#### 🤖 OpenAI API 키")
    current_api = get_system_config(ConfigKeys.ADMIN_API_KEY, "")
    new_api_key = st.text_input(
        "API 키",
        value=current_api,
        type="password",
        key="admin_api_key",
        help="통합 모드 회원들이 사용할 API 키"
    )
    
    if st.button("💾 API 키 저장", key="save_api"):
        set_system_config(ConfigKeys.ADMIN_API_KEY, new_api_key)
        st.toast("✅ API 키가 저장되었습니다!")
    
    st.markdown("---")
    
    # Gmail 설정
    st.markdown("#### 📧 Gmail 설정")
    
    current_gmail = get_system_config(ConfigKeys.ADMIN_GMAIL, "")
    current_gmail_pw = get_system_config(ConfigKeys.ADMIN_GMAIL_PASSWORD, "")
    
    new_gmail = st.text_input("Gmail 주소", value=current_gmail, key="admin_gmail")
    new_gmail_pw = st.text_input("Gmail 앱 비밀번호", value=current_gmail_pw, type="password", key="admin_gmail_pw")
    
    if st.button("💾 Gmail 설정 저장", key="save_gmail"):
        set_system_config(ConfigKeys.ADMIN_GMAIL, new_gmail)
        set_system_config(ConfigKeys.ADMIN_GMAIL_PASSWORD, new_gmail_pw)
        st.toast("✅ Gmail 설정이 저장되었습니다!")
    
    st.markdown("---")
    
    # 캐싱 설정
    st.markdown("#### 💾 캐싱 설정")
    
    cache_enabled = st.checkbox("캐싱 활성화", value=True, key="cache_enabled")
    st.caption("동일한 조건의 운세 결과를 저장하여 속도를 높입니다.")
    
    if st.button("🗑️ 캐시 전체 삭제", key="clear_cache"):
        st.toast("🗑️ 캐시가 삭제되었습니다!")
    
    st.markdown("---")
    st.caption("💡 Gmail 앱 비밀번호는 Google 계정 → 보안 → 2단계 인증 → 앱 비밀번호에서 생성합니다.")
