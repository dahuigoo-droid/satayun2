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

# ============================================
# 초기화
# ============================================

init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

st.title("📚 자료실")
user = st.session_state.user

tab1, tab2 = st.tabs(["📑 목차 게시판", "📜 지침 게시판"])

with tab1:
    st.markdown('<span class="section-title">📑 목차 게시판</span>', unsafe_allow_html=True)
    
    with st.expander("➕ 새 목차 등록", expanded=False):
        ch_title = st.text_input("제목", key="lib_ch_title")
        ch_category = st.selectbox("카테고리", CATEGORIES, key="lib_ch_cat")
        ch_content = st.text_area("목차 내용 (줄바꿈 구분)", height=300, key="lib_ch_content",
                                 placeholder="1. 총운\n2. 재물운\n3. 건강운\n4. 연애운")
        
        if st.button("💾 목차 등록", type="primary", key="lib_ch_save"):
            if ch_title and ch_content:
                user_id = None if is_admin() else user['id']
                add_chapter_library(ch_title, ch_content, ch_category, user_id)
                st.success("등록됨!")
                st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 필터
    filter_cat = st.selectbox("카테고리 필터", ["전체"] + CATEGORIES, key="lib_ch_filter")
    cat_filter = None if filter_cat == "전체" else filter_cat
    
    items = get_chapter_library(user['id'] if not is_admin() else None, cat_filter)
    if not items:
        st.info("등록된 목차가 없습니다.")
    else:
        for item in items:
            with st.expander(f"{'🔓' if item['user_id'] is None else '🔒'} {item['title']} ({item['category'] or '미분류'})"):
                ed_title = st.text_input("제목", value=item['title'], key=f"lib_ch_t_{item['id']}")
                ed_cat = st.selectbox("카테고리", CATEGORIES, 
                                     index=CATEGORIES.index(item['category']) if item['category'] in CATEGORIES else 0,
                                     key=f"lib_ch_c_{item['id']}")
                ed_content = st.text_area("내용", value=item['content'], height=200, key=f"lib_ch_ct_{item['id']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 수정", key=f"lib_ch_sv_{item['id']}"):
                        update_chapter_library(item['id'], ed_title, ed_content, ed_cat)
                        st.success("수정됨!")
                        # st.rerun() 제거 - 수정은 즉시 반영 불필요
                with col2:
                    if st.button("📋 복사", key=f"lib_ch_cp_{item['id']}"):
                        st.session_state['clipboard_chapters'] = ed_content
                        st.success("클립보드에 복사됨!")
                with col3:
                    if st.button("🗑️ 삭제", key=f"lib_ch_dl_{item['id']}"):
                        delete_chapter_library(item['id'])
                        st.rerun()

with tab2:
    st.markdown('<span class="section-title">📜 지침 게시판</span>', unsafe_allow_html=True)
    
    with st.expander("➕ 새 지침 등록", expanded=False):
        g_title = st.text_input("제목", key="lib_g_title")
        g_category = st.selectbox("카테고리", CATEGORIES, key="lib_g_cat")
        g_content = st.text_area("지침 내용", height=400, key="lib_g_content",
                                placeholder="- 긍정적이고 희망적인 톤으로 작성\n- 300-500자 분량\n- 고객 정보 자연스럽게 반영")
        
        if st.button("💾 지침 등록", type="primary", key="lib_g_save"):
            if g_title and g_content:
                user_id = None if is_admin() else user['id']
                add_guideline_library(g_title, g_content, g_category, user_id)
                st.success("등록됨!")
                st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    filter_cat2 = st.selectbox("카테고리 필터", ["전체"] + CATEGORIES, key="lib_g_filter")
    cat_filter2 = None if filter_cat2 == "전체" else filter_cat2
    
    items2 = get_guideline_library(user['id'] if not is_admin() else None, cat_filter2)
    if not items2:
        st.info("등록된 지침이 없습니다.")
    else:
        for item in items2:
            with st.expander(f"{'🔓' if item['user_id'] is None else '🔒'} {item['title']} ({item['category'] or '미분류'})"):
                ed_title = st.text_input("제목", value=item['title'], key=f"lib_g_t_{item['id']}")
                ed_cat = st.selectbox("카테고리", CATEGORIES,
                                     index=CATEGORIES.index(item['category']) if item['category'] in CATEGORIES else 0,
                                     key=f"lib_g_c_{item['id']}")
                ed_content = st.text_area("내용", value=item['content'], height=300, key=f"lib_g_ct_{item['id']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 수정", key=f"lib_g_sv_{item['id']}"):
                        update_guideline_library(item['id'], ed_title, ed_content, ed_cat)
                        st.success("수정됨!")
                        # st.rerun() 제거 - 수정은 즉시 반영 불필요
                with col2:
                    if st.button("📋 복사", key=f"lib_g_cp_{item['id']}"):
                        st.session_state['clipboard_guideline'] = ed_content
                        st.success("클립보드에 복사됨!")
                with col3:
                    if st.button("🗑️ 삭제", key=f"lib_g_dl_{item['id']}"):
                        delete_guideline_library(item['id'])
                        st.rerun()

