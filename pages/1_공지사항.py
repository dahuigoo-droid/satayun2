# -*- coding: utf-8 -*-
"""
📢 공지사항 페이지
"""

import streamlit as st
from datetime import datetime

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

notices = cached_get_notices()

# ===== 관리자: 새 공지 작성 =====
if is_admin():
    st.markdown("---")
    
    # 작성 모드 토글
    if 'show_notice_form' not in st.session_state:
        st.session_state.show_notice_form = False
    
    col_btn, col_space = st.columns([1, 4])
    with col_btn:
        if st.button("➕ 새 공지 작성", type="primary", use_container_width=True):
            st.session_state.show_notice_form = not st.session_state.show_notice_form
    
    if st.session_state.show_notice_form:
        st.markdown("### ✏️ 새 공지 작성")
        
        with st.container():
            new_title = st.text_input("제목", key="new_notice_title", placeholder="공지 제목을 입력하세요")
            new_content = st.text_area("내용", height=200, key="new_notice_content", placeholder="공지 내용을 입력하세요")
            new_pinned = st.checkbox("📌 상단 고정", key="new_notice_pin")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📢 공지 등록", type="primary", use_container_width=True):
                    if new_title and new_content:
                        result = create_notice(
                            author_id=user['id'],
                            title=new_title,
                            content=new_content,
                            is_pinned=new_pinned
                        )
                        if result.get('success'):
                            clear_notice_cache()
                            st.session_state.show_notice_form = False
                            st.toast("✅ 공지가 등록되었습니다!")
                            st.rerun()
                        else:
                            st.error(result.get('error', '등록 실패'))
                    else:
                        st.warning("제목과 내용을 입력해주세요.")
            with col2:
                if st.button("❌ 취소", use_container_width=True):
                    st.session_state.show_notice_form = False
                    st.rerun()
        
        st.markdown("---")

st.markdown("---")

# ===== 공지 목록 =====
if notices:
    # 고정 공지 먼저
    pinned = [n for n in notices if n.get('is_pinned')]
    normal = [n for n in notices if not n.get('is_pinned')]
    
    for notice in pinned + normal:
        with st.container():
            # 제목 & 정보
            pin_icon = "📌 " if notice.get('is_pinned') else ""
            st.markdown(f"### {pin_icon}{notice.get('title', '제목 없음')}")
            
            # 날짜 표시
            created = notice.get('created_at')
            if created:
                if isinstance(created, str):
                    date_str = created[:10]
                else:
                    date_str = created.strftime("%Y-%m-%d")
                st.caption(f"📅 {date_str}")
            
            # 내용
            st.markdown(notice.get('content', ''))
            
            # 관리자 기능
            if is_admin():
                with st.expander("⚙️ 관리", expanded=False):
                    # 수정 폼
                    edit_title = st.text_input(
                        "제목 수정", 
                        value=notice.get('title', ''), 
                        key=f"edit_title_{notice['id']}"
                    )
                    edit_content = st.text_area(
                        "내용 수정", 
                        value=notice.get('content', ''), 
                        height=150,
                        key=f"edit_content_{notice['id']}"
                    )
                    edit_pinned = st.checkbox(
                        "📌 상단 고정",
                        value=notice.get('is_pinned', False),
                        key=f"edit_pin_{notice['id']}"
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("💾 수정 저장", key=f"save_{notice['id']}", type="primary", use_container_width=True):
                            update_notice(
                                notice['id'], 
                                title=edit_title, 
                                content=edit_content,
                                is_pinned=edit_pinned
                            )
                            clear_notice_cache()
                            st.toast("✅ 수정되었습니다!")
                            st.rerun()
                    
                    with col2:
                        if st.button("📌 고정 토글", key=f"pin_{notice['id']}", use_container_width=True):
                            toggle_pin_notice(notice['id'])
                            clear_notice_cache()
                            st.toast("📌 고정 상태가 변경되었습니다!")
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️ 삭제", key=f"del_{notice['id']}", use_container_width=True):
                            delete_notice(notice['id'])
                            clear_notice_cache()
                            st.toast("🗑️ 삭제되었습니다!")
                            st.rerun()
            
            st.markdown("---")
else:
    st.info("📭 등록된 공지사항이 없습니다.")
