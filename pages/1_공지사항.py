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

# 수정 모드 관리
if 'edit_notice_id' not in st.session_state:
    st.session_state.edit_notice_id = None
if 'show_new_notice' not in st.session_state:
    st.session_state.show_new_notice = False

st.title("📢 공지사항")

notices = cached_get_notices()

# ===== 관리자: 새 공지 작성 버튼 =====
if is_admin():
    if st.button("➕ 새 공지 작성", type="primary"):
        st.session_state.show_new_notice = not st.session_state.show_new_notice
        st.session_state.edit_notice_id = None
    
    # 새 공지 작성 폼
    if st.session_state.show_new_notice:
        st.markdown("---")
        st.markdown("### ✏️ 새 공지 작성")
        
        new_title = st.text_input("제목", key="new_title", placeholder="공지 제목")
        new_content = st.text_area("내용", height=150, key="new_content", placeholder="공지 내용")
        new_pinned = st.checkbox("📌 상단 고정", key="new_pinned")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 등록", type="primary", use_container_width=True):
                if new_title and new_content:
                    result = create_notice(user['id'], new_title, new_content, is_pinned=new_pinned)
                    if result.get('success'):
                        clear_notice_cache()
                        st.session_state.show_new_notice = False
                        st.toast("✅ 등록되었습니다!")
                        st.rerun()
                    else:
                        st.error(result.get('error', '등록 실패'))
                else:
                    st.warning("제목과 내용을 입력하세요.")
        with col2:
            if st.button("❌ 취소", use_container_width=True):
                st.session_state.show_new_notice = False
                st.rerun()

st.markdown("---")

# ===== 공지 목록 =====
if notices:
    pinned = [n for n in notices if n.get('is_pinned')]
    normal = [n for n in notices if not n.get('is_pinned')]
    
    for notice in pinned + normal:
        notice_id = notice['id']
        is_editing = st.session_state.edit_notice_id == notice_id
        
        with st.container():
            # 고정 아이콘 + 제목
            pin_icon = "📌 " if notice.get('is_pinned') else ""
            
            # 날짜
            created = notice.get('created_at')
            date_str = str(created)[:10] if created else ""
            
            if is_editing:
                # ===== 수정 모드 =====
                st.markdown(f"### ✏️ 수정 중...")
                
                edit_title = st.text_input("제목", value=notice.get('title', ''), key=f"edit_title_{notice_id}")
                edit_content = st.text_area("내용", value=notice.get('content', ''), height=150, key=f"edit_content_{notice_id}")
                edit_pinned = st.checkbox("📌 상단 고정", value=notice.get('is_pinned', False), key=f"edit_pin_{notice_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 저장", type="primary", use_container_width=True, key=f"save_{notice_id}"):
                        update_notice(notice_id, title=edit_title, content=edit_content, is_pinned=edit_pinned)
                        clear_notice_cache()
                        st.session_state.edit_notice_id = None
                        st.toast("✅ 저장되었습니다!")
                        st.rerun()
                with col2:
                    if st.button("❌ 취소", use_container_width=True, key=f"cancel_{notice_id}"):
                        st.session_state.edit_notice_id = None
                        st.rerun()
            else:
                # ===== 보기 모드 =====
                st.markdown(f"### {pin_icon}{notice.get('title', '')}")
                st.caption(f"📅 {date_str}")
                st.markdown(notice.get('content', ''))
                
                # 관리자 버튼
                if is_admin():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("✏️ 수정", key=f"btn_edit_{notice_id}", use_container_width=True):
                            st.session_state.edit_notice_id = notice_id
                            st.session_state.show_new_notice = False
                            st.rerun()
                    with col2:
                        pin_text = "📌 고정해제" if notice.get('is_pinned') else "📌 상단고정"
                        if st.button(pin_text, key=f"btn_pin_{notice_id}", use_container_width=True):
                            toggle_pin_notice(notice_id)
                            clear_notice_cache()
                            st.toast("📌 고정 상태 변경!")
                            st.rerun()
                    with col3:
                        pass  # 빈 공간
                    with col4:
                        if st.button("🗑️ 삭제", key=f"btn_del_{notice_id}", use_container_width=True):
                            delete_notice(notice_id)
                            clear_notice_cache()
                            st.toast("🗑️ 삭제되었습니다!")
                            st.rerun()
            
            st.markdown("---")
else:
    st.info("📭 등록된 공지사항이 없습니다.")
