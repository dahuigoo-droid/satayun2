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

# 수정 모드 관리
if 'edit_chapter_id' not in st.session_state:
    st.session_state.edit_chapter_id = None
if 'edit_guideline_id' not in st.session_state:
    st.session_state.edit_guideline_id = None
if 'show_new_chapter' not in st.session_state:
    st.session_state.show_new_chapter = False
if 'show_new_guideline' not in st.session_state:
    st.session_state.show_new_guideline = False

st.title("📚 자료실")

tab1, tab2 = st.tabs(["📑 목차 자료실", "📜 지침 자료실"])

# ===== 목차 자료실 =====
with tab1:
    st.markdown("### 📑 목차 자료실")
    
    # 새 목차 버튼
    if st.button("➕ 새 목차 추가", type="primary", key="btn_new_ch"):
        st.session_state.show_new_chapter = not st.session_state.show_new_chapter
        st.session_state.edit_chapter_id = None
    
    # 새 목차 폼
    if st.session_state.show_new_chapter:
        st.markdown("---")
        st.markdown("#### ✏️ 새 목차 추가")
        
        new_ch_title = st.text_input("제목", key="new_ch_title", placeholder="목차 제목")
        new_ch_content = st.text_area("내용", height=120, key="new_ch_content", placeholder="목차 내용")
        new_ch_cat = st.selectbox("카테고리", ["선택안함"] + CATEGORIES, key="new_ch_cat")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 등록", type="primary", use_container_width=True, key="save_new_ch"):
                if new_ch_title:
                    cat = new_ch_cat if new_ch_cat != "선택안함" else None
                    result = add_chapter_library(new_ch_title, new_ch_content, cat, user['id'])
                    if result.get('success'):
                        st.session_state.show_new_chapter = False
                        st.toast("✅ 등록되었습니다!")
                        st.rerun()
                    else:
                        st.error(result.get('error', '등록 실패'))
                else:
                    st.warning("제목을 입력하세요.")
        with col2:
            if st.button("❌ 취소", use_container_width=True, key="cancel_new_ch"):
                st.session_state.show_new_chapter = False
                st.rerun()
    
    st.markdown("---")
    
    # 목차 목록
    chapters = get_chapter_library(user['id'])
    
    if chapters:
        for ch in chapters:
            ch_id = ch['id']
            is_editing = st.session_state.edit_chapter_id == ch_id
            
            with st.container():
                if is_editing:
                    # ===== 수정 모드 =====
                    st.markdown("#### ✏️ 수정 중...")
                    
                    edit_title = st.text_input("제목", value=ch.get('title', ''), key=f"edit_ch_title_{ch_id}")
                    edit_content = st.text_area("내용", value=ch.get('content', ''), height=100, key=f"edit_ch_content_{ch_id}")
                    edit_cat = st.selectbox(
                        "카테고리", 
                        ["선택안함"] + CATEGORIES,
                        index=(CATEGORIES.index(ch.get('category')) + 1) if ch.get('category') in CATEGORIES else 0,
                        key=f"edit_ch_cat_{ch_id}"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 저장", type="primary", use_container_width=True, key=f"save_ch_{ch_id}"):
                            cat = edit_cat if edit_cat != "선택안함" else None
                            update_chapter_library(ch_id, title=edit_title, content=edit_content, category=cat)
                            st.session_state.edit_chapter_id = None
                            st.toast("✅ 저장되었습니다!")
                            st.rerun()
                    with col2:
                        if st.button("❌ 취소", use_container_width=True, key=f"cancel_ch_{ch_id}"):
                            st.session_state.edit_chapter_id = None
                            st.rerun()
                else:
                    # ===== 보기 모드 =====
                    cat_badge = f"`{ch.get('category')}`" if ch.get('category') else ""
                    st.markdown(f"**{cat_badge} {ch.get('title', '')}**")
                    
                    if ch.get('content'):
                        content_preview = ch['content'][:150] + "..." if len(ch.get('content', '')) > 150 else ch['content']
                        st.caption(content_preview)
                    
                    # 버튼
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("✏️ 수정", key=f"btn_edit_ch_{ch_id}", use_container_width=True):
                            st.session_state.edit_chapter_id = ch_id
                            st.session_state.show_new_chapter = False
                            st.rerun()
                    with col2:
                        if st.button("🗑️ 삭제", key=f"btn_del_ch_{ch_id}", use_container_width=True):
                            delete_chapter_library(ch_id)
                            st.toast("🗑️ 삭제되었습니다!")
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("📭 저장된 목차가 없습니다.")

# ===== 지침 자료실 =====
with tab2:
    st.markdown("### 📜 지침 자료실")
    
    # 새 지침 버튼
    if st.button("➕ 새 지침 추가", type="primary", key="btn_new_g"):
        st.session_state.show_new_guideline = not st.session_state.show_new_guideline
        st.session_state.edit_guideline_id = None
    
    # 새 지침 폼
    if st.session_state.show_new_guideline:
        st.markdown("---")
        st.markdown("#### ✏️ 새 지침 추가")
        
        new_g_title = st.text_input("제목", key="new_g_title", placeholder="지침 제목")
        new_g_content = st.text_area("내용", height=150, key="new_g_content", placeholder="지침 내용")
        new_g_cat = st.selectbox("카테고리", ["선택안함"] + CATEGORIES, key="new_g_cat")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 등록", type="primary", use_container_width=True, key="save_new_g"):
                if new_g_title and new_g_content:
                    cat = new_g_cat if new_g_cat != "선택안함" else None
                    result = add_guideline_library(new_g_title, new_g_content, cat, user['id'])
                    if result.get('success'):
                        st.session_state.show_new_guideline = False
                        st.toast("✅ 등록되었습니다!")
                        st.rerun()
                    else:
                        st.error(result.get('error', '등록 실패'))
                else:
                    st.warning("제목과 내용을 입력하세요.")
        with col2:
            if st.button("❌ 취소", use_container_width=True, key="cancel_new_g"):
                st.session_state.show_new_guideline = False
                st.rerun()
    
    st.markdown("---")
    
    # 지침 목록
    guidelines = get_guideline_library(user['id'])
    
    if guidelines:
        for g in guidelines:
            g_id = g['id']
            is_editing = st.session_state.edit_guideline_id == g_id
            
            with st.container():
                if is_editing:
                    # ===== 수정 모드 =====
                    st.markdown("#### ✏️ 수정 중...")
                    
                    edit_title = st.text_input("제목", value=g.get('title', ''), key=f"edit_g_title_{g_id}")
                    edit_content = st.text_area("내용", value=g.get('content', ''), height=150, key=f"edit_g_content_{g_id}")
                    edit_cat = st.selectbox(
                        "카테고리",
                        ["선택안함"] + CATEGORIES,
                        index=(CATEGORIES.index(g.get('category')) + 1) if g.get('category') in CATEGORIES else 0,
                        key=f"edit_g_cat_{g_id}"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 저장", type="primary", use_container_width=True, key=f"save_g_{g_id}"):
                            cat = edit_cat if edit_cat != "선택안함" else None
                            update_guideline_library(g_id, title=edit_title, content=edit_content, category=cat)
                            st.session_state.edit_guideline_id = None
                            st.toast("✅ 저장되었습니다!")
                            st.rerun()
                    with col2:
                        if st.button("❌ 취소", use_container_width=True, key=f"cancel_g_{g_id}"):
                            st.session_state.edit_guideline_id = None
                            st.rerun()
                else:
                    # ===== 보기 모드 =====
                    cat_badge = f"`{g.get('category')}`" if g.get('category') else ""
                    st.markdown(f"**{cat_badge} {g.get('title', '')}**")
                    
                    if g.get('content'):
                        content_preview = g['content'][:150] + "..." if len(g.get('content', '')) > 150 else g['content']
                        st.caption(content_preview)
                    
                    # 버튼
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("✏️ 수정", key=f"btn_edit_g_{g_id}", use_container_width=True):
                            st.session_state.edit_guideline_id = g_id
                            st.session_state.show_new_guideline = False
                            st.rerun()
                    with col2:
                        if st.button("🗑️ 삭제", key=f"btn_del_g_{g_id}", use_container_width=True):
                            delete_guideline_library(g_id)
                            st.toast("🗑️ 삭제되었습니다!")
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("📭 저장된 지침이 없습니다.")
