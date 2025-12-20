# -*- coding: utf-8 -*-
"""
👤 내정보 페이지
"""

import streamlit as st

st.set_page_config(page_title="내정보", page_icon="👤", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    is_admin, cached_get_notices, clear_notice_cache
)
from auth import update_user_profile, change_password
from notices import get_all_notices, create_notice, update_notice, delete_notice, toggle_pin_notice

# ============================================
# 초기화
# ============================================

init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

# ============================================
# 내 정보
# ============================================

st.title("👤 내정보")

tab1, tab2, tab3 = st.tabs(["📋 내 정보", "🔑 API/이메일", "📢 공지사항"])

with tab1:
    new_name = st.text_input("이름", value=user['name'])
    st.text_input("이메일", value=user['email'], disabled=True)
    if st.button("💾 저장"):
        result = update_user_profile(user['id'], name=new_name)
        if result["success"]:
            st.session_state.user['name'] = new_name
            st.success("저장됨")
    st.markdown("---")
    old_pw = st.text_input("현재 비밀번호", type="password")
    new_pw = st.text_input("새 비밀번호", type="password")
    if st.button("🔒 비밀번호 변경"):
        if old_pw and new_pw:
            result = change_password(user['id'], old_pw, new_pw)
            st.success("변경됨") if result["success"] else st.error(result["error"])

with tab2:
    if user.get('api_mode') == 'separated':
        my_api = st.text_input("내 API 키", value=user.get('api_key', '') or '', type="password")
        if st.button("💾 API 저장"):
            result = update_user_profile(user['id'], api_key=my_api)
            if result["success"]:
                st.session_state.user['api_key'] = my_api
                st.success("저장됨")
    else:
        st.info("🔒 API: 관리자 통합 모드")
    
    if user.get('email_mode') == 'separated':
        my_gmail = st.text_input("Gmail", value=user.get('gmail_address', '') or '')
        my_pw = st.text_input("앱 비밀번호", value=user.get('gmail_app_password', '') or '', type="password")
        if st.button("💾 이메일 저장"):
            result = update_user_profile(user['id'], gmail_address=my_gmail, gmail_app_password=my_pw)
            if result["success"]:
                st.session_state.user['gmail_address'] = my_gmail
                st.session_state.user['gmail_app_password'] = my_pw
                st.success("저장됨")
    else:
        st.info("🔒 이메일: 관리자 통합 모드")

with tab3:
    st.subheader("📢 공지사항")
    
    if is_admin():
        with st.expander("✏️ 새 공지", expanded=False):
            title = st.text_input("제목", key="n_title")
            content = st.text_area("내용", height=150, key="n_content")
            pinned = st.checkbox("📌 고정")
            if st.button("💾 등록", type="primary"):
                if title and content:
                    create_notice(st.session_state.user['id'], title, content, None, pinned)
                    st.success("등록됨!")
                    clear_notice_cache()
                    st.rerun()
    
    st.markdown("---")
    notices = cached_get_notices()
    if not notices:
        st.info("공지가 없습니다.")
    else:
        for n in notices:
            pin = "📌 " if n['is_pinned'] else ""
            with st.expander(f"{pin}**{n['title']}**"):
                if is_admin():
                    ed_title = st.text_input("제목", value=n['title'], key=f"et_{n['id']}")
                    ed_content = st.text_area("내용", value=n['content'], height=80, key=f"ec_{n['id']}")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("💾", key=f"sv_{n['id']}"):
                            update_notice(n['id'], ed_title, ed_content)
                            clear_notice_cache()
                            st.toast("수정됨!")
                    with c2:
                        if st.button("📌", key=f"pn_{n['id']}"):
                            toggle_pin_notice(n['id'])
                            clear_notice_cache()
                            st.rerun()
                    with c3:
                        if st.button("🗑️", key=f"dl_{n['id']}"):
                            delete_notice(n['id'])
                            clear_notice_cache()
                            st.rerun()
                else:
                    st.write(n['content'])

