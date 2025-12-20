# -*- coding: utf-8 -*-
"""
⚙️ 관리자 페이지
"""

import streamlit as st
import os
import time

st.set_page_config(page_title="관리자", page_icon="⚙️", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    is_admin, cached_get_admin_services, cached_get_chapters, cached_get_guidelines,
    cached_get_templates, clear_service_cache, save_uploaded_file, render_font_settings,
    TEMPLATE_TYPES, FONT_OPTIONS, CATEGORIES
)
from auth import (
    get_all_users, get_pending_users, approve_user, suspend_user, activate_user,
    update_user_settings
)
from services import (
    add_service, update_service, delete_service, get_system_config, set_system_config, ConfigKeys
)
from contents import (
    add_chapters_bulk, delete_chapters_by_service,
    get_chapters_by_service, get_guidelines_by_service, get_templates_by_service,
    add_guideline, update_guideline, add_template, delete_template
)

# ============================================
# 초기화
# ============================================

init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

# 관리자 권한 체크
if not is_admin():
    st.error("🚫 관리자만 접근 가능합니다.")
    st.stop()


# ============================================
# 상품 수정 폼
# ============================================


def show_service_edit_form(svc: dict, prefix: str):
    """상품 수정 폼"""
    svc_id = svc['id']
    chapters = cached_get_chapters(svc_id)
    guidelines = cached_get_guidelines(svc_id)
    templates = cached_get_templates(svc_id)
    
    edit_name = st.text_input("상품명", value=svc['name'], key=f"{prefix}_name_{svc_id}")
    
    # 좌우 배치
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**📑 목차**")
        current_chapters = "\n".join([ch['title'] for ch in chapters])
        edit_chapters = st.text_area("목차", value=current_chapters, height=300, key=f"{prefix}_ch_{svc_id}")
    with col_right:
        st.markdown("**📜 지침**")
        current_guideline = guidelines[0]['content'] if guidelines else ""
        edit_guideline = st.text_area("지침", value=current_guideline, height=300, key=f"{prefix}_g_{svc_id}")
    
    # 폰트 설정 (expander로 숨김 - 기본값 사용 권장)
    with st.expander("⚙️ 폰트/디자인 설정", expanded=False):
        font_defaults = {k: svc.get(k, v) for k, v in 
                         {"font_family": "NanumGothic", "font_size_title": 24, "font_size_subtitle": 16,
                          "font_size_body": 12, "letter_spacing": 0, "line_height": 180, "char_width": 100,
                          "margin_top": 25, "margin_bottom": 25, "margin_left": 25, "margin_right": 25,
                          "target_pages": 30}.items()}
        font_settings = render_font_settings(f"{prefix}_{svc_id}", font_defaults)
        
        st.markdown("**🖼️ 디자인**")
        t_cols = st.columns(3)
        for idx, tt in enumerate(["cover", "background", "info"]):
            with t_cols[idx]:
                t_list = [t for t in templates if t['template_type'] == tt]
                # 이미지 미리보기 (존재할 때만)
                if t_list and t_list[0].get('image_path') and os.path.exists(t_list[0]['image_path']):
                    st.image(t_list[0]['image_path'], width=60, caption=TEMPLATE_TYPES[tt])
                st.file_uploader(TEMPLATE_TYPES[tt], type=["jpg","jpeg","png"], key=f"{prefix}_{tt}_{svc_id}")
    
    # 저장/삭제 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 저장", key=f"{prefix}_save_{svc_id}", type="primary", use_container_width=True):
            with st.spinner("저장 중..."):
                # font_settings를 session_state에서 가져오기
                settings_key = f"{prefix}_{svc_id}_font_settings"
                font_settings = st.session_state.get(settings_key, {
                    "font_family": "NanumGothic", "font_size_title": 24, "font_size_subtitle": 16,
                    "font_size_body": 12, "letter_spacing": 0, "line_height": 180, "char_width": 100,
                    "margin_top": 25, "margin_bottom": 25, "margin_left": 25, "margin_right": 25,
                    "target_pages": 30
                })
                
                # 1. 먼저 모든 DB 작업 수행 (캐시 초기화 전)
                # 목차 업데이트 (삭제 후 추가)
                delete_chapters_by_service(svc_id)
                chapter_list = [ch.strip() for ch in edit_chapters.strip().split("\n") if ch.strip()]
                add_chapters_bulk(svc_id, chapter_list)
                
                # 서비스 업데이트
                update_service(svc_id, name=edit_name, **font_settings)
                
                # 지침 업데이트 (DB 직접 조회 - 캐시 우회)
                fresh_guidelines = get_guidelines_by_service(svc_id)
                if fresh_guidelines:
                    update_guideline(fresh_guidelines[0]['id'], fresh_guidelines[0]['title'], edit_guideline)
                elif edit_guideline:
                    add_guideline(svc_id, f"{edit_name} 지침", edit_guideline)
                
                # 템플릿 업데이트 (파일 있을 때만)
                fresh_templates = get_templates_by_service(svc_id)
                for tt in ["cover", "background", "info"]:
                    new_file = st.session_state.get(f"{prefix}_{tt}_{svc_id}")
                    if new_file:
                        for t in fresh_templates:
                            if t['template_type'] == tt:
                                delete_template(t['id'])
                        add_template(svc_id, tt, TEMPLATE_TYPES[tt], save_uploaded_file(new_file, f"{edit_name}_{tt}"))
                
                # 2. 모든 작업 완료 후 캐시 한번에 초기화
                clear_service_cache()
                
            st.success("저장됨!")
            # st.rerun() 제거 - 다음 상호작용에서 자동 반영
    with col2:
        if st.button("🗑️ 삭제", key=f"{prefix}_del_{svc_id}", use_container_width=True):
            with st.spinner("삭제 중..."):
                delete_service(svc_id)
                clear_service_cache()
            st.success("삭제됨!")
            time.sleep(0.5)
            st.rerun()  # 삭제는 목록 갱신 필요

# ============================================
# 메인 - 관리자 설정
# ============================================

st.title("⚙️ 관리자 설정")
tab1, tab2, tab3 = st.tabs(["📦 기성상품 등록", "👥 회원관리", "🔑 API/이메일"])

with tab1:
    st.markdown('<span class="section-title">📦 기성상품 등록</span>', unsafe_allow_html=True)
    
    # 새 상품 등록 토글
    if 'show_new_product' not in st.session_state:
        st.session_state.show_new_product = False
    
    if st.button("➕ 새 기성상품 등록" if not st.session_state.show_new_product else "➖ 접기"):
        st.session_state.show_new_product = not st.session_state.show_new_product
        st.rerun()
    
    if st.session_state.show_new_product:
        st.markdown("---")
        product_name = st.text_input("상품명", key="new_prod")
        
        # 목차/지침 좌우 배치
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("**📑 목차** (줄바꿈 구분)")
            new_chapters = st.text_area("목차", height=500, key="new_ch", placeholder="1. 총운\n2. 재물운\n3. 건강운")
        with col_right:
            st.markdown("**📜 AI 작성 지침**")
            new_guideline = st.text_area("지침", height=500, key="new_g", placeholder="- 긍정적 톤\n- 300자 이상")
        
        font_settings = render_font_settings("new_admin")
        
        st.markdown("**🖼️ 디자인**")
        d_cols = st.columns(3)
        with d_cols[0]:
            cover = st.file_uploader("📕 표지", type=["jpg","jpeg","png"], key="new_cover")
        with d_cols[1]:
            bg = st.file_uploader("📄 내지", type=["jpg","jpeg","png"], key="new_bg")
        with d_cols[2]:
            info = st.file_uploader("📋 안내지", type=["jpg","jpeg","png"], key="new_info")
        
        if st.button("💾 기성상품 등록", type="primary", use_container_width=True):
            if product_name:
                with st.spinner("등록 중..."):
                    result = add_service(product_name, "", None, **font_settings)
                    if result.get("success"):
                        svc_id = result["id"]
                        if new_chapters:
                            chapter_list = [ch.strip() for ch in new_chapters.strip().split("\n") if ch.strip()]
                            add_chapters_bulk(svc_id, chapter_list)
                        if new_guideline:
                            add_guideline(svc_id, f"{product_name} 지침", new_guideline)
                        if cover:
                            add_template(svc_id, "cover", "표지", save_uploaded_file(cover, f"{product_name}_cover"))
                        if bg:
                            add_template(svc_id, "background", "내지", save_uploaded_file(bg, f"{product_name}_bg"))
                        if info:
                            add_template(svc_id, "info", "안내지", save_uploaded_file(info, f"{product_name}_info"))
                        clear_service_cache()
                st.success(f"'{product_name}' 등록됨!")
                st.session_state.show_new_product = False
                st.rerun()
        st.markdown("---")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("**등록된 기성상품**")
    
    services = cached_get_admin_services()
    if not services:
        st.info("등록된 기성상품이 없습니다.")
    else:
        for svc in services:
            with st.expander(f"📌 {svc['name']}"):
                show_service_edit_form(svc, "admin")

with tab2:
    st.markdown('<span class="section-title">👥 회원 관리</span>', unsafe_allow_html=True)
    st.markdown("**1단계**: 기성상품만 | **2단계**: 개별상품만 | **3단계**: 둘 다")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    subtab1, subtab2 = st.tabs(["전체 회원", "승인 대기"])
    with subtab1:
        for u in get_all_users():
            if u['id'] == st.session_state.user['id']:
                continue
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                status_icon = "🟢" if u['status'] == 'approved' else "🔴"
                admin_mark = "👑" if u['is_admin'] else ""
                st.write(f"{status_icon} {admin_mark} **{u['name']}**")
                st.caption(u['email'])
            with col2:
                new_level = st.selectbox("등급", [1, 2, 3], index=u.get('member_level', 1) - 1,
                                        format_func=lambda x: f"{x}단계", key=f"lvl_{u['id']}")
            with col3:
                new_api = st.selectbox("API", ["unified", "separated"],
                                      index=0 if u.get('api_mode') == 'unified' else 1,
                                      format_func=lambda x: "통합" if x == "unified" else "분리",
                                      key=f"api_{u['id']}")
            with col4:
                new_email = st.selectbox("이메일", ["unified", "separated"],
                                        index=0 if u.get('email_mode') == 'unified' else 1,
                                        format_func=lambda x: "통합" if x == "unified" else "분리",
                                        key=f"email_{u['id']}")
            with col5:
                if st.button("💾", key=f"save_{u['id']}"):
                    update_user_settings(u['id'], new_level, new_api, new_email)
                    st.toast("저장됨!")
                    # st.rerun() 제거 - 설정 저장은 즉시 반영 불필요
                if u['status'] == 'approved':
                    if st.button("🚫", key=f"sus_{u['id']}"):
                        suspend_user(u['id'])
                        st.rerun()
                elif u['status'] == 'suspended':
                    if st.button("✅", key=f"act_{u['id']}"):
                        activate_user(u['id'])
                        st.rerun()
            st.markdown("---")
    
    with subtab2:
        pending = get_pending_users()
        if not pending:
            st.success("대기 중인 회원이 없습니다.")
        for u in pending:
            col1, col2 = st.columns([4, 1])
            col1.write(f"**{u['name']}** ({u['email']})")
            if col2.button("✅ 승인", key=f"ap_{u['id']}", type="primary"):
                approve_user(u['id'])
                st.rerun()

with tab3:
    st.markdown('<span class="section-title">🔑 관리자 API/이메일</span>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        api = st.text_input("OpenAI API 키", value=get_system_config(ConfigKeys.ADMIN_API_KEY, ""), type="password")
        if st.button("💾 API 저장"):
            set_system_config(ConfigKeys.ADMIN_API_KEY, api)
            st.success("저장됨")
    with col2:
        gmail = st.text_input("Gmail", value=get_system_config(ConfigKeys.ADMIN_GMAIL, ""))
        gmail_pw = st.text_input("앱 비밀번호", value=get_system_config(ConfigKeys.ADMIN_GMAIL_PASSWORD, ""), type="password")
        if st.button("💾 이메일 저장"):
            set_system_config(ConfigKeys.ADMIN_GMAIL, gmail)
            set_system_config(ConfigKeys.ADMIN_GMAIL_PASSWORD, gmail_pw)

