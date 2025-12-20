# -*- coding: utf-8 -*-
"""
📚 자료실 페이지 (목차 + 지침)
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

# 세션 상태 초기화
if 'chapter_view_id' not in st.session_state:
    st.session_state.chapter_view_id = None
if 'chapter_edit_mode' not in st.session_state:
    st.session_state.chapter_edit_mode = False
if 'chapter_new_mode' not in st.session_state:
    st.session_state.chapter_new_mode = False

if 'guideline_view_id' not in st.session_state:
    st.session_state.guideline_view_id = None
if 'guideline_edit_mode' not in st.session_state:
    st.session_state.guideline_edit_mode = False
if 'guideline_new_mode' not in st.session_state:
    st.session_state.guideline_new_mode = False

tab1, tab2 = st.tabs(["📑 목차 자료실", "📜 지침 자료실"])

# =========================================================
# 📑 목차 자료실
# =========================================================
with tab1:
    st.markdown("### 📑 목차 자료실")
    
    chapters = get_chapter_library(user['id'])
    
    # ===== 새 글 작성 모드 =====
    if st.session_state.chapter_new_mode:
        st.markdown("#### ✏️ 새 목차 추가")
        
        new_title = st.text_input("제목", key="new_ch_title", placeholder="목차 제목")
        new_content = st.text_area("내용", height=150, key="new_ch_content", placeholder="목차 내용")
        new_category = st.selectbox("카테고리", ["선택안함"] + CATEGORIES, key="new_ch_cat")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 등록완료", type="primary", use_container_width=True, key="ch_save_new"):
                if new_title:
                    cat = new_category if new_category != "선택안함" else None
                    result = add_chapter_library(new_title, new_content, cat, user['id'])
                    if result.get('success'):
                        st.session_state.chapter_new_mode = False
                        st.toast("✅ 등록되었습니다!")
                        st.rerun()
                    else:
                        st.error(result.get('error', '등록 실패'))
                else:
                    st.warning("제목을 입력하세요.")
        with col2:
            if st.button("❌ 취소", use_container_width=True, key="ch_cancel_new"):
                st.session_state.chapter_new_mode = False
                st.rerun()
    
    # ===== 글 상세보기 모드 =====
    elif st.session_state.chapter_view_id:
        chapter = next((c for c in chapters if c['id'] == st.session_state.chapter_view_id), None)
        
        if chapter:
            # 뒤로가기
            if st.button("← 목록으로", key="ch_back"):
                st.session_state.chapter_view_id = None
                st.session_state.chapter_edit_mode = False
                st.rerun()
            
            st.markdown("---")
            
            if st.session_state.chapter_edit_mode:
                # ===== 수정 모드 =====
                st.markdown("#### ✏️ 수정 중")
                
                edit_title = st.text_input("제목", value=chapter.get('title', ''), key="edit_ch_title")
                edit_content = st.text_area("내용", value=chapter.get('content', ''), height=150, key="edit_ch_content")
                edit_category = st.selectbox(
                    "카테고리",
                    ["선택안함"] + CATEGORIES,
                    index=(CATEGORIES.index(chapter.get('category')) + 1) if chapter.get('category') in CATEGORIES else 0,
                    key="edit_ch_cat"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 수정완료", type="primary", use_container_width=True, key="ch_save_edit"):
                        cat = edit_category if edit_category != "선택안함" else None
                        update_chapter_library(chapter['id'], title=edit_title, content=edit_content, category=cat)
                        st.session_state.chapter_edit_mode = False
                        st.toast("✅ 수정되었습니다!")
                        st.rerun()
                with col2:
                    if st.button("❌ 취소", use_container_width=True, key="ch_cancel_edit"):
                        st.session_state.chapter_edit_mode = False
                        st.rerun()
            else:
                # ===== 보기 모드 =====
                cat_badge = f"`{chapter.get('category')}`" if chapter.get('category') else ""
                st.markdown(f"## {cat_badge} {chapter.get('title', '')}")
                
                st.markdown("---")
                st.markdown(chapter.get('content', '') or "(내용 없음)")
                st.markdown("---")
                
                # 버튼
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("✏️ 수정", use_container_width=True, key="ch_btn_edit"):
                        st.session_state.chapter_edit_mode = True
                        st.rerun()
                with col2:
                    if st.button("🗑️ 삭제", use_container_width=True, key="ch_btn_del"):
                        delete_chapter_library(chapter['id'])
                        st.session_state.chapter_view_id = None
                        st.toast("🗑️ 삭제되었습니다!")
                        st.rerun()
    
    # ===== 목록 모드 =====
    else:
        # 새 글 작성 버튼
        if st.button("➕ 새 목차 추가", type="primary", key="ch_btn_new"):
            st.session_state.chapter_new_mode = True
            st.rerun()
        
        st.markdown("---")
        
        if chapters:
            for ch in chapters:
                cat_badge = f"`{ch.get('category')}`" if ch.get('category') else ""
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(f"{cat_badge} {ch.get('title', '')}", key=f"ch_{ch['id']}", use_container_width=True):
                        st.session_state.chapter_view_id = ch['id']
                        st.rerun()
                with col2:
                    st.caption(ch.get('category', '-'))
        else:
            st.info("📭 저장된 목차가 없습니다.")

# =========================================================
# 📜 지침 자료실
# =========================================================
with tab2:
    st.markdown("### 📜 지침 자료실")
    
    guidelines = get_guideline_library(user['id'])
    
    # ===== 새 글 작성 모드 =====
    if st.session_state.guideline_new_mode:
        st.markdown("#### ✏️ 새 지침 추가")
        
        new_title = st.text_input("제목", key="new_g_title", placeholder="지침 제목")
        new_content = st.text_area("내용", height=200, key="new_g_content", placeholder="지침 내용")
        new_category = st.selectbox("카테고리", ["선택안함"] + CATEGORIES, key="new_g_cat")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 등록완료", type="primary", use_container_width=True, key="g_save_new"):
                if new_title and new_content:
                    cat = new_category if new_category != "선택안함" else None
                    result = add_guideline_library(new_title, new_content, cat, user['id'])
                    if result.get('success'):
                        st.session_state.guideline_new_mode = False
                        st.toast("✅ 등록되었습니다!")
                        st.rerun()
                    else:
                        st.error(result.get('error', '등록 실패'))
                else:
                    st.warning("제목과 내용을 입력하세요.")
        with col2:
            if st.button("❌ 취소", use_container_width=True, key="g_cancel_new"):
                st.session_state.guideline_new_mode = False
                st.rerun()
    
    # ===== 글 상세보기 모드 =====
    elif st.session_state.guideline_view_id:
        guideline = next((g for g in guidelines if g['id'] == st.session_state.guideline_view_id), None)
        
        if guideline:
            # 뒤로가기
            if st.button("← 목록으로", key="g_back"):
                st.session_state.guideline_view_id = None
                st.session_state.guideline_edit_mode = False
                st.rerun()
            
            st.markdown("---")
            
            if st.session_state.guideline_edit_mode:
                # ===== 수정 모드 =====
                st.markdown("#### ✏️ 수정 중")
                
                edit_title = st.text_input("제목", value=guideline.get('title', ''), key="edit_g_title")
                edit_content = st.text_area("내용", value=guideline.get('content', ''), height=200, key="edit_g_content")
                edit_category = st.selectbox(
                    "카테고리",
                    ["선택안함"] + CATEGORIES,
                    index=(CATEGORIES.index(guideline.get('category')) + 1) if guideline.get('category') in CATEGORIES else 0,
                    key="edit_g_cat"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 수정완료", type="primary", use_container_width=True, key="g_save_edit"):
                        cat = edit_category if edit_category != "선택안함" else None
                        update_guideline_library(guideline['id'], title=edit_title, content=edit_content, category=cat)
                        st.session_state.guideline_edit_mode = False
                        st.toast("✅ 수정되었습니다!")
                        st.rerun()
                with col2:
                    if st.button("❌ 취소", use_container_width=True, key="g_cancel_edit"):
                        st.session_state.guideline_edit_mode = False
                        st.rerun()
            else:
                # ===== 보기 모드 =====
                cat_badge = f"`{guideline.get('category')}`" if guideline.get('category') else ""
                st.markdown(f"## {cat_badge} {guideline.get('title', '')}")
                
                st.markdown("---")
                st.markdown(guideline.get('content', '') or "(내용 없음)")
                st.markdown("---")
                
                # 버튼
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("✏️ 수정", use_container_width=True, key="g_btn_edit"):
                        st.session_state.guideline_edit_mode = True
                        st.rerun()
                with col2:
                    if st.button("🗑️ 삭제", use_container_width=True, key="g_btn_del"):
                        delete_guideline_library(guideline['id'])
                        st.session_state.guideline_view_id = None
                        st.toast("🗑️ 삭제되었습니다!")
                        st.rerun()
    
    # ===== 목록 모드 =====
    else:
        # 새 글 작성 버튼
        if st.button("➕ 새 지침 추가", type="primary", key="g_btn_new"):
            st.session_state.guideline_new_mode = True
            st.rerun()
        
        st.markdown("---")
        
        if guidelines:
            for g in guidelines:
                cat_badge = f"`{g.get('category')}`" if g.get('category') else ""
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(f"{cat_badge} {g.get('title', '')}", key=f"g_{g['id']}", use_container_width=True):
                        st.session_state.guideline_view_id = g['id']
                        st.rerun()
                with col2:
                    st.caption(g.get('category', '-'))
        else:
            st.info("📭 저장된 지침이 없습니다.")
