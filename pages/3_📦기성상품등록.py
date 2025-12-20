# -*- coding: utf-8 -*-
"""
📦 기성상품 등록 페이지 (관리자 전용)
"""

import streamlit as st
import os

st.set_page_config(page_title="기성상품 등록", page_icon="📦", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    cached_get_admin_services, cached_get_chapters, cached_get_guidelines, 
    cached_get_templates, clear_service_cache, is_admin, save_uploaded_file,
    FONT_OPTIONS, TEMPLATE_TYPES
)
from services import add_service, update_service, delete_service
from contents import (
    add_chapters_bulk, delete_chapters_by_service,
    add_guideline, update_guideline,
    add_template, delete_template
)

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

# 관리자 체크
if not is_admin():
    st.error("🔒 관리자만 접근할 수 있습니다.")
    st.stop()

st.title("📦 기성상품 등록")
st.caption("회원들이 사용할 기성상품을 등록하고 관리합니다.")

# ===== 새 상품 등록 =====
with st.expander("➕ 새 기성상품 등록", expanded=False):
    new_name = st.text_input("상품명", key="new_admin_name", placeholder="예: 2025 신년운세")
    
    if new_name:
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("**📑 목차** (줄바꿈으로 구분)")
            new_chapters = st.text_area("목차", height=250, key="new_admin_ch",
                                        placeholder="1. 총운\n2. 재물운\n3. 건강운")
        with col_right:
            st.markdown("**📜 AI 작성 지침**")
            new_guideline = st.text_area("지침", height=250, key="new_admin_guide",
                                         placeholder="고객 정보를 바탕으로 긍정적인 톤으로...")
        
        with st.expander("⚙️ 폰트/디자인 설정", expanded=False):
            # 목표 페이지 수
            st.markdown("**📄 목표 페이지 수**")
            col_page, col_info = st.columns([1, 2])
            with col_page:
                new_target_pages = st.number_input("목표 페이지", value=35, min_value=5, max_value=100, key="new_admin_pages", label_visibility="collapsed")
            with col_info:
                chars_per_page = 840
                total_chars = chars_per_page * new_target_pages
                st.success(f"📊 현재 설정: 페이지당 약 {chars_per_page}자 | 총 {total_chars:,}자 예상")
            
            # 폰트 설정
            st.markdown("**🔤 폰트 설정**")
            font_row1 = st.columns([2, 2, 2])
            with font_row1[0]:
                st.caption("폰트")
                new_font_family = st.selectbox("폰트", list(FONT_OPTIONS.keys()), index=0, key="new_admin_font", label_visibility="collapsed")
            with font_row1[1]:
                st.caption("행간 (%)")
                new_line_height = st.slider("행간", min_value=100, max_value=300, value=180, key="new_admin_lh", label_visibility="collapsed")
            with font_row1[2]:
                st.caption("자간 (%)")
                new_letter_spacing = st.slider("자간", min_value=-5, max_value=10, value=0, key="new_admin_ls", label_visibility="collapsed")
            
            font_row2 = st.columns(4)
            with font_row2[0]:
                st.caption("대제목")
                new_font_size_title = st.number_input("대제목", value=30, min_value=12, max_value=48, key="new_admin_title", label_visibility="collapsed")
            with font_row2[1]:
                st.caption("소제목")
                new_font_size_subtitle = st.number_input("소제목", value=23, min_value=10, max_value=36, key="new_admin_subtitle", label_visibility="collapsed")
            with font_row2[2]:
                st.caption("본문")
                new_font_size_body = st.number_input("본문", value=18, min_value=8, max_value=24, key="new_admin_body", label_visibility="collapsed")
            with font_row2[3]:
                st.caption("장평 (%)")
                new_char_width = st.slider("장평", min_value=50, max_value=150, value=100, key="new_admin_cw", label_visibility="collapsed")
            
            # 여백 설정
            st.markdown("**📐 여백 설정 (mm)**")
            margin_cols = st.columns(4)
            with margin_cols[0]:
                st.caption("상단")
                new_margin_top = st.number_input("상단", value=25, min_value=10, max_value=50, key="new_admin_mt", label_visibility="collapsed")
            with margin_cols[1]:
                st.caption("하단")
                new_margin_bottom = st.number_input("하단", value=25, min_value=10, max_value=50, key="new_admin_mb", label_visibility="collapsed")
            with margin_cols[2]:
                st.caption("좌측")
                new_margin_left = st.number_input("좌측", value=25, min_value=10, max_value=50, key="new_admin_ml", label_visibility="collapsed")
            with margin_cols[3]:
                st.caption("우측")
                new_margin_right = st.number_input("우측", value=25, min_value=10, max_value=50, key="new_admin_mr", label_visibility="collapsed")
            
            # 디자인 이미지
            st.markdown("**🖼️ 디자인**")
            d_cols = st.columns(3)
            with d_cols[0]:
                st.caption("📕 표지")
                new_cover = st.file_uploader("표지", type=["jpg","jpeg","png"], key="new_admin_cover", label_visibility="collapsed")
            with d_cols[1]:
                st.caption("📄 내지")
                new_bg = st.file_uploader("내지", type=["jpg","jpeg","png"], key="new_admin_bg", label_visibility="collapsed")
            with d_cols[2]:
                st.caption("📋 안내지")
                new_info = st.file_uploader("안내지", type=["jpg","jpeg","png"], key="new_admin_info", label_visibility="collapsed")
        
        st.markdown("---")
        
        can_save = new_name.strip() and st.session_state.get('new_admin_ch', '').strip()
        
        if can_save:
            if st.button("💾 기성상품 등록", type="primary", use_container_width=True):
                with st.spinner("저장 중..."):
                    font_settings = {
                        "font_family": new_font_family,
                        "font_size_title": new_font_size_title,
                        "font_size_subtitle": new_font_size_subtitle,
                        "font_size_body": new_font_size_body,
                        "letter_spacing": new_letter_spacing,
                        "line_height": new_line_height,
                        "char_width": new_char_width,
                        "margin_top": new_margin_top,
                        "margin_bottom": new_margin_bottom,
                        "margin_left": new_margin_left,
                        "margin_right": new_margin_right,
                        "target_pages": new_target_pages
                    }
                    
                    # 서비스 추가 (owner_id=None이면 기성상품)
                    result = add_service(new_name, "", owner_id=None, **font_settings)
                    
                    if result.get("success"):
                        svc_id = result["id"]
                        
                        # 목차 추가
                        chapters_text = st.session_state.get('new_admin_ch', '')
                        chapter_list = [ch.strip() for ch in chapters_text.strip().split("\n") if ch.strip()]
                        add_chapters_bulk(svc_id, chapter_list)
                        
                        # 지침 추가
                        guideline_text = st.session_state.get('new_admin_guide', '')
                        if guideline_text:
                            add_guideline(svc_id, f"{new_name} 지침", guideline_text)
                        
                        # 이미지 업로드
                        if new_cover:
                            add_template(svc_id, "cover", "표지", save_uploaded_file(new_cover, f"{new_name}_cover"))
                        if new_bg:
                            add_template(svc_id, "background", "내지", save_uploaded_file(new_bg, f"{new_name}_bg"))
                        if new_info:
                            add_template(svc_id, "info", "안내지", save_uploaded_file(new_info, f"{new_name}_info"))
                        
                        clear_service_cache()
                        st.toast(f"✅ '{new_name}' 기성상품이 등록되었습니다!")
                        st.rerun()
                    else:
                        st.error(result.get('error', '등록 실패'))
        else:
            st.button("💾 기성상품 등록", type="secondary", use_container_width=True, disabled=True)
            st.caption("⚠️ 상품명과 목차를 입력하세요")

st.markdown("---")

# ===== 기성상품 목록 =====
st.markdown("### 📋 등록된 기성상품")

admin_services = cached_get_admin_services()

if admin_services:
    for svc in admin_services:
        chapters = cached_get_chapters(svc['id'])
        guidelines = cached_get_guidelines(svc['id'])
        templates = cached_get_templates(svc['id'])
        
        with st.expander(f"📦 {svc.get('name', '')} (목차 {len(chapters) if chapters else 0}개)", expanded=False):
            # 상품명 수정
            edit_name = st.text_input("상품명", value=svc.get('name', ''), key=f"edit_name_{svc['id']}")
            
            # 목차 & 지침
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("**📑 목차**")
                chapter_text = "\n".join([ch.get('title', '') for ch in chapters]) if chapters else ""
                edit_chapters = st.text_area("목차", value=chapter_text, height=200, key=f"edit_ch_{svc['id']}", label_visibility="collapsed")
            with col_right:
                st.markdown("**📜 지침**")
                guideline_text = guidelines[0].get('content', '') if guidelines else ""
                edit_guideline = st.text_area("지침", value=guideline_text, height=200, key=f"edit_guide_{svc['id']}", label_visibility="collapsed")
            
            # 디자인 이미지 미리보기
            st.markdown("**🖼️ 디자인 이미지**")
            img_cols = st.columns(3)
            with img_cols[0]:
                st.caption("📕 표지")
                cover_tpl = next((t for t in templates if t.get('template_type') == 'cover'), None) if templates else None
                if cover_tpl and cover_tpl.get('image_path'):
                    img_path = cover_tpl['image_path']
                    if img_path.startswith("http") or os.path.exists(img_path):
                        st.image(img_path, width=100)
                    else:
                        st.caption("(이미지 없음)")
                edit_cover = st.file_uploader("표지 변경", type=["jpg","jpeg","png"], key=f"edit_cover_{svc['id']}", label_visibility="collapsed")
            with img_cols[1]:
                st.caption("📄 내지")
                bg_tpl = next((t for t in templates if t.get('template_type') == 'background'), None) if templates else None
                if bg_tpl and bg_tpl.get('image_path'):
                    img_path = bg_tpl['image_path']
                    if img_path.startswith("http") or os.path.exists(img_path):
                        st.image(img_path, width=100)
                    else:
                        st.caption("(이미지 없음)")
                edit_bg = st.file_uploader("내지 변경", type=["jpg","jpeg","png"], key=f"edit_bg_{svc['id']}", label_visibility="collapsed")
            with img_cols[2]:
                st.caption("📋 안내지")
                info_tpl = next((t for t in templates if t.get('template_type') == 'info'), None) if templates else None
                if info_tpl and info_tpl.get('image_path'):
                    img_path = info_tpl['image_path']
                    if img_path.startswith("http") or os.path.exists(img_path):
                        st.image(img_path, width=100)
                    else:
                        st.caption("(이미지 없음)")
                edit_info = st.file_uploader("안내지 변경", type=["jpg","jpeg","png"], key=f"edit_info_{svc['id']}", label_visibility="collapsed")
            
            st.markdown("---")
            
            # 버튼
            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("💾 수정 저장", key=f"save_{svc['id']}", type="primary", use_container_width=True):
                    # 상품 업데이트
                    update_service(svc['id'], name=edit_name)
                    
                    # 목차 업데이트
                    new_chapter_list = [ch.strip() for ch in edit_chapters.strip().split("\n") if ch.strip()]
                    delete_chapters_by_service(svc['id'])
                    add_chapters_bulk(svc['id'], new_chapter_list)
                    
                    # 지침 업데이트
                    if guidelines:
                        update_guideline(guidelines[0]['id'], content=edit_guideline)
                    elif edit_guideline:
                        add_guideline(svc['id'], f"{edit_name} 지침", edit_guideline)
                    
                    # 이미지 업데이트
                    if edit_cover:
                        if cover_tpl:
                            delete_template(cover_tpl['id'])
                        add_template(svc['id'], "cover", "표지", save_uploaded_file(edit_cover, f"{edit_name}_cover"))
                    if edit_bg:
                        if bg_tpl:
                            delete_template(bg_tpl['id'])
                        add_template(svc['id'], "background", "내지", save_uploaded_file(edit_bg, f"{edit_name}_bg"))
                    if edit_info:
                        if info_tpl:
                            delete_template(info_tpl['id'])
                        add_template(svc['id'], "info", "안내지", save_uploaded_file(edit_info, f"{edit_name}_info"))
                    
                    clear_service_cache()
                    st.toast("✅ 수정되었습니다!")
                    st.rerun()
            
            with col_del:
                if st.button("🗑️ 삭제", key=f"del_{svc['id']}", type="secondary", use_container_width=True):
                    delete_service(svc['id'])
                    clear_service_cache()
                    st.toast("🗑️ 삭제되었습니다")
                    st.rerun()
else:
    st.info("등록된 기성상품이 없습니다.")
