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

# 관리자: 공지 작성
if is_admin():
    with st.expander("➕ 새 공지 작성", expanded=False):
        new_title = st.text_input("제목", key="new_notice_title")
        new_content = st.text_area("내용", height=200, key="new_notice_content")
        new_pinned = st.checkbox("📌 상단 고정", key="new_notice_pin")
        
        if st.button("📢 공지 등록", type="primary"):
            if new_title and new_content:
                result = create_notice(
                    author_id=user['id'],
                    title=new_title,
                    content=new_content,
                    is_pinned=new_pinned
                )
                if result.get('success'):
                    clear_notice_cache()
                    st.toast("✅ 공지가 등록되었습니다!")
                    st.rerun()
                else:
                    st.error(result.get('error', '등록 실패'))
            else:
                st.warning("제목과 내용을 입력해주세요.")

st.markdown("---")

# 공지 목록
if notices:
    # 고정 공지 먼저
    pinned = [n for n in notices if n.get('is_pinned')]
    normal = [n for n in notices if not n.get('is_pinned')]
    
    for notice in pinned + normal:
        with st.container():
            col1, col2 = st.columns([6, 1])
            
            with col1:
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
                
                st.markdown(notice.get('content', ''))
            
            with col2:
                if is_admin():
                    if st.button("📌", key=f"pin_{notice['id']}", help="고정/해제"):
                        toggle_pin_notice(notice['id'])
                        clear_notice_cache()
                        st.rerun()
                    
                    if st.button("🗑️", key=f"del_{notice['id']}", help="삭제"):
                        delete_notice(notice['id'])
                        clear_notice_cache()
                        st.toast("🗑️ 삭제되었습니다")
                        st.rerun()
            
            st.markdown("---")
else:
    st.info("등록된 공지사항이 없습니다.")
