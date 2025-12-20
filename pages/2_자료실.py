# -*- coding: utf-8 -*-
"""
📚 자료실 페이지
"""

import streamlit as st

st.set_page_config(page_title="자료실", page_icon="📚", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    is_admin, CATEGORIES
)
from services import (
    get_chapter_library, add_chapter_library, update_chapter_library, delete_chapter_library,
    get_guideline_library, add_guideline_library, update_guideline_library, delete_guideline_library
)

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

st.title("📚 자료실")

tab1, tab2 = st.tabs(["📑 목차 자료실", "📜 지침 자료실"])

# ===== 목차 자료실 =====
with tab1:
    st.markdown("### 📑 목차 자료실")
    
    # 새 목차 추가
    with st.expander("➕ 새 목차 추가", expanded=False):
        ch_title = st.text_input("목차 제목", key="lib_ch_title")
        ch_content = st.text_area("내용 (줄바꿈으로 구분)", height=150, key="lib_ch_content")
        ch_category = st.selectbox("카테고리", ["선택안함"] + CATEGORIES, key="lib_ch_cat")
        
        if st.button("💾 목차 저장", key="save_ch_lib"):
            if ch_title:
                cat = ch_category if ch_category != "선택안함" else None
                result = add_chapter_library(ch_title, ch_content, cat, user['id'])
                if result.get('success'):
                    st.toast("✅ 목차가 저장되었습니다!")
                    st.rerun()
                else:
                    st.error(result.get('error', '저장 실패'))
            else:
                st.warning("제목을 입력해주세요.")
    
    st.markdown("---")
    
    # 목차 목록
    chapters = get_chapter_library(user['id'])
    
    if chapters:
        for ch in chapters:
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    cat_badge = f"[{ch.get('category')}] " if ch.get('category') else ""
                    st.markdown(f"**{cat_badge}{ch.get('title', '')}**")
                    if ch.get('content'):
                        st.caption(ch['content'][:100] + "..." if len(ch.get('content', '')) > 100 else ch['content'])
                with col2:
                    if st.button("🗑️", key=f"del_ch_{ch['id']}"):
                        delete_chapter_library(ch['id'])
                        st.toast("🗑️ 삭제되었습니다")
                        st.rerun()
                st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
    else:
        st.info("저장된 목차가 없습니다.")

# ===== 지침 자료실 =====
with tab2:
    st.markdown("### 📜 지침 자료실")
    
    # 새 지침 추가
    with st.expander("➕ 새 지침 추가", expanded=False):
        g_title = st.text_input("지침 제목", key="lib_g_title")
        g_content = st.text_area("지침 내용", height=200, key="lib_g_content")
        g_category = st.selectbox("카테고리", ["선택안함"] + CATEGORIES, key="lib_g_cat")
        
        if st.button("💾 지침 저장", key="save_g_lib"):
            if g_title and g_content:
                cat = g_category if g_category != "선택안함" else None
                result = add_guideline_library(g_title, g_content, cat, user['id'])
                if result.get('success'):
                    st.toast("✅ 지침이 저장되었습니다!")
                    st.rerun()
                else:
                    st.error(result.get('error', '저장 실패'))
            else:
                st.warning("제목과 내용을 입력해주세요.")
    
    st.markdown("---")
    
    # 지침 목록
    guidelines = get_guideline_library(user['id'])
    
    if guidelines:
        for g in guidelines:
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    cat_badge = f"[{g.get('category')}] " if g.get('category') else ""
                    st.markdown(f"**{cat_badge}{g.get('title', '')}**")
                    if g.get('content'):
                        st.caption(g['content'][:100] + "..." if len(g.get('content', '')) > 100 else g['content'])
                with col2:
                    if st.button("🗑️", key=f"del_g_{g['id']}"):
                        delete_guideline_library(g['id'])
                        st.toast("🗑️ 삭제되었습니다")
                        st.rerun()
                st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
    else:
        st.info("저장된 지침이 없습니다.")
