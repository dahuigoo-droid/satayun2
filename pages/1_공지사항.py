# -*- coding: utf-8 -*-
"""
📢 공지사항 페이지
"""

import streamlit as st

st.set_page_config(page_title="공지사항", page_icon="📢", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    cached_get_notices, clear_notice_cache, is_admin
)
from notices import get_all_notices, create_notice, update_notice, delete_notice, toggle_pin_notice

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

st.title("📢 공지사항")

# 세션 상태 초기화
if 'notice_view_id' not in st.session_state:
    st.session_state.notice_view_id = None
if 'notice_edit_mode' not in st.session_state:
    st.session_state.notice_edit_mode = False
if 'notice_new_mode' not in st.session_state:
    st.session_state.notice_new_mode = False

notices = cached_get_notices()

# ===== 새 글 작성 모드 =====
if st.session_state.notice_new_mode and is_admin():
    st.markdown("#### ✏️ 새 공지 작성")
    
    new_title = st.text_input("제목", key="new_notice_title", placeholder="공지 제목")
    new_content = st.text_area("내용", height=200, key="new_notice_content", placeholder="공지 내용")
    new_pinned = st.checkbox("📌 상단 고정", key="new_notice_pinned")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 등록완료", type="primary", use_container_width=True):
            if new_title and new_content:
                result = create_notice(user['id'], new_title, new_content, is_pinned=new_pinned)
                if result.get('success'):
                    clear_notice_cache()
                    st.session_state.notice_new_mode = False
                    st.toast("✅ 등록되었습니다!")
                    st.rerun()
                else:
                    st.error(result.get('error', '등록 실패'))
            else:
                st.warning("제목과 내용을 입력하세요.")
    with col2:
        if st.button("❌ 취소", use_container_width=True):
            st.session_state.notice_new_mode = False
            st.rerun()

# ===== 글 상세보기 모드 =====
elif st.session_state.notice_view_id:
    notice = next((n for n in notices if n['id'] == st.session_state.notice_view_id), None)
    
    if notice:
        # 뒤로가기
        if st.button("← 목록으로"):
            st.session_state.notice_view_id = None
            st.session_state.notice_edit_mode = False
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.notice_edit_mode and is_admin():
            # ===== 수정 모드 =====
            st.markdown("#### ✏️ 수정 중")
            
            edit_title = st.text_input("제목", value=notice.get('title', ''), key="edit_notice_title")
            edit_content = st.text_area("내용", value=notice.get('content', ''), height=200, key="edit_notice_content")
            edit_pinned = st.checkbox("📌 상단 고정", value=notice.get('is_pinned', False), key="edit_notice_pinned")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 수정완료", type="primary", use_container_width=True):
                    update_notice(notice['id'], title=edit_title, content=edit_content, is_pinned=edit_pinned)
                    clear_notice_cache()
                    st.session_state.notice_edit_mode = False
                    st.toast("✅ 수정되었습니다!")
                    st.rerun()
            with col2:
                if st.button("❌ 취소", use_container_width=True):
                    st.session_state.notice_edit_mode = False
                    st.rerun()
        else:
            # ===== 보기 모드 =====
            pin_icon = "📌 " if notice.get('is_pinned') else ""
            st.markdown(f"## {pin_icon}{notice.get('title', '')}")
            
            created = notice.get('created_at')
            date_str = str(created)[:10] if created else ""
            st.caption(f"📅 {date_str}")
            
            st.markdown("---")
            st.markdown(notice.get('content', ''))
            st.markdown("---")
            
            # 버튼 (관리자만)
            if is_admin():
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                with col1:
                    if st.button("✏️ 수정", use_container_width=True):
                        st.session_state.notice_edit_mode = True
                        st.rerun()
                with col2:
                    pin_text = "📌 고정해제" if notice.get('is_pinned') else "📌 상단고정"
                    if st.button(pin_text, use_container_width=True):
                        toggle_pin_notice(notice['id'])
                        clear_notice_cache()
                        st.toast("📌 고정 상태 변경!")
                        st.rerun()
                with col3:
                    pass
                with col4:
                    if st.button("🗑️ 삭제", use_container_width=True):
                        delete_notice(notice['id'])
                        clear_notice_cache()
                        st.session_state.notice_view_id = None
                        st.toast("🗑️ 삭제되었습니다!")
                        st.rerun()

# ===== 목록 모드 =====
else:
    # 새 글 작성 버튼 (관리자만)
    if is_admin():
        if st.button("➕ 새 공지 작성", type="primary"):
            st.session_state.notice_new_mode = True
            st.rerun()
    
    st.markdown("---")
    
    if notices:
        # 고정 공지 먼저
        pinned = [n for n in notices if n.get('is_pinned')]
        normal = [n for n in notices if not n.get('is_pinned')]
        
        for notice in pinned + normal:
            pin_icon = "📌 " if notice.get('is_pinned') else ""
            created = notice.get('created_at')
            date_str = str(created)[:10] if created else ""
            
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(f"{pin_icon}{notice.get('title', '')}", key=f"notice_{notice['id']}", use_container_width=True):
                    st.session_state.notice_view_id = notice['id']
                    st.rerun()
            with col2:
                st.caption(date_str)
    else:
        st.info("📭 등록된 공지사항이 없습니다.")
