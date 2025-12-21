# -*- coding: utf-8 -*-
"""
🎯 제품 공통 유틸리티
- 상품 설정 UI
- PDF 생성 로직
- 고객 목록 UI
- 중복 코드 제거
"""

import streamlit as st
from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass, field

from common import FONT_OPTIONS, save_uploaded_file, clear_service_cache
from services import (
    get_services_by_category, add_service, update_service, delete_service,
    get_system_config, ConfigKeys
)
from contents import (
    get_chapters_by_service, add_chapter, add_chapters_bulk, delete_chapters_by_service,
    get_guidelines_by_service, add_guideline, update_guideline, delete_guideline,
    get_templates_by_service, add_template, delete_template
)
from pdf_generator import generate_full_content, PDFGenerator


# ============================================
# 데이터 클래스
# ============================================

@dataclass
class ProductConfig:
    """제품 페이지 설정"""
    prefix: str                 # 세션 상태 접두어 (std, ind, prm)
    product_type: str           # 상품 유형 (기성상품, 개별상품, 고급상품)
    title: str                  # 페이지 제목
    subtitle: str               # 부제목
    icon: str                   # 아이콘


# ============================================
# 세션 상태 초기화
# ============================================

def init_product_session(prefix: str):
    """제품별 세션 상태 초기화"""
    defaults = {
        f'{prefix}_view_id': None,
        f'{prefix}_edit_mode': False,
        f'{prefix}_new_mode': False,
        f'{prefix}_customers': [],
        f'{prefix}_selected': set(),
        f'{prefix}_progress': {},
        f'{prefix}_completed': set(),
        f'{prefix}_reset': 0,
        f'{prefix}_pdfs': {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ============================================
# 상품 설정 UI 컴포넌트
# ============================================

def render_new_product_form(config: ProductConfig) -> bool:
    """새 상품 등록 폼"""
    prefix = config.prefix
    product_type = config.product_type
    
    st.markdown(f"### ✏️ 새 {config.title} 등록")
    
    new_name = st.text_input("상품명", placeholder="예: 2025 신년운세", key=f"{prefix}_new_name")
    
    col_ch, col_guide = st.columns(2)
    with col_ch:
        st.markdown("**📑 목차** (줄바꿈 구분)")
        new_chapters = st.text_area("", height=200, key=f"{prefix}_new_ch",
                                    placeholder="1. 총운\n2. 재물운\n3. 건강운")
    with col_guide:
        st.markdown("**📜 AI 지침**")
        new_guideline = st.text_area("", height=200, key=f"{prefix}_new_guide",
                                     placeholder="20년 경력의 사주 전문가로서...")
    
    # 디자인 설정
    design = render_design_settings(prefix, expanded=False)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 등록", type="primary", use_container_width=True, key=f"{prefix}_save_new"):
            if new_name:
                result = add_service(
                    name=new_name, product_category=product_type,
                    **design
                )
                if result.get('success'):
                    sid = result['id']
                    if new_chapters:
                        add_chapters_bulk(sid, [c.strip() for c in new_chapters.split('\n') if c.strip()])
                    if new_guideline:
                        add_guideline(sid, "기본 지침", new_guideline)
                    
                    # 이미지 저장
                    save_product_images(sid, prefix)
                    
                    clear_service_cache()
                    st.session_state[f'{prefix}_new_mode'] = False
                    st.toast("✅ 등록 완료!")
                    st.rerun()
            else:
                st.warning("상품명을 입력하세요.")
    
    with col2:
        if st.button("❌ 취소", use_container_width=True, key=f"{prefix}_cancel_new"):
            st.session_state[f'{prefix}_new_mode'] = False
            st.rerun()
    
    return False


def render_design_settings(prefix: str, expanded: bool = False, defaults: dict = None) -> dict:
    """디자인 설정 UI - 재사용 가능"""
    if defaults is None:
        defaults = {}
    
    with st.expander("🎨 디자인 설정", expanded=expanded):
        # 폰트 설정
        st.markdown("**🔤 폰트 설정**")
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            font_idx = list(FONT_OPTIONS.keys()).index(defaults.get('font_family', 'NanumGothic')) \
                if defaults.get('font_family') in FONT_OPTIONS else 0
            new_font = st.selectbox("폰트", list(FONT_OPTIONS.keys()), index=font_idx,
                                    format_func=lambda x: FONT_OPTIONS[x], key=f"{prefix}_font")
        with fcol2:
            new_title = st.number_input("대제목", value=defaults.get('font_size_title', 24), 
                                        min_value=16, max_value=40, key=f"{prefix}_title_size")
        with fcol3:
            new_subtitle = st.number_input("소제목", value=defaults.get('font_size_subtitle', 16),
                                           min_value=12, max_value=30, key=f"{prefix}_subtitle_size")
        with fcol4:
            new_body = st.number_input("본문", value=defaults.get('font_size_body', 12),
                                       min_value=8, max_value=20, key=f"{prefix}_body_size")
        
        # 행간 & 목표 페이지
        hcol1, hcol2 = st.columns(2)
        with hcol1:
            new_line_height = st.slider("행간 %", 100, 300, defaults.get('line_height', 180),
                                        key=f"{prefix}_lh")
        with hcol2:
            new_pages = st.number_input("목표 페이지", value=defaults.get('target_pages', 30), 
                                        min_value=10, max_value=200, key=f"{prefix}_pages")
        
        # 여백 설정
        st.markdown("**📐 여백 (mm)**")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            new_mt = st.number_input("상단", value=defaults.get('margin_top', 25), key=f"{prefix}_mt")
        with mcol2:
            new_mb = st.number_input("하단", value=defaults.get('margin_bottom', 25), key=f"{prefix}_mb")
        with mcol3:
            new_ml = st.number_input("좌측", value=defaults.get('margin_left', 25), key=f"{prefix}_ml")
        with mcol4:
            new_mr = st.number_input("우측", value=defaults.get('margin_right', 25), key=f"{prefix}_mr")
        
        # ======= 📊 예상 페이지 계산기 =======
        st.markdown("---")
        st.markdown("**📊 예상 결과 계산**")
        
        # 페이지당 글자 수 계산
        page_width_mm = 210
        page_height_mm = 297
        usable_width_mm = page_width_mm - new_ml - new_mr
        usable_height_mm = page_height_mm - new_mt - new_mb
        
        char_width_mm = new_body * 0.35  # 한글 기준
        line_height_mm = new_body * 0.35 * (new_line_height / 100)
        
        chars_per_line = int(usable_width_mm / char_width_mm)
        lines_per_page = int(usable_height_mm / line_height_mm)
        chars_per_page = int(chars_per_line * lines_per_page * 0.75)  # 여유 25%
        
        # 예상 정보 표시
        calc_col1, calc_col2 = st.columns(2)
        with calc_col1:
            st.info(f"""
**현재 설정 기준:**
- 한 줄: 약 **{chars_per_line}자**
- 한 페이지: 약 **{lines_per_page}줄**
- 페이지당: 약 **{chars_per_page:,}자**
            """)
        with calc_col2:
            total_chars = new_pages * chars_per_page
            st.success(f"""
**{new_pages}페이지 목표:**
- 필요 글자 수: **{total_chars:,}자**
- 목차 5개 기준: 목차당 **{total_chars//5:,}자**
- 목차 10개 기준: 목차당 **{total_chars//10:,}자**
            """)
        
        # 참고 가이드
        with st.expander("💡 설정 가이드", expanded=False):
            st.markdown("""
| 본문 크기 | 여백 25mm | 행간 180% | 페이지당 글자 |
|----------|----------|----------|-------------|
| 12pt | 25mm | 180% | ~850자 |
| 14pt | 25mm | 180% | ~620자 |
| 16pt | 25mm | 180% | ~480자 |
| 17pt | 25mm | 180% | ~420자 |

**팁:**
- 본문 크기 ↑ → 페이지당 글자 수 ↓ → 더 많은 페이지
- 여백 ↑ → 페이지당 글자 수 ↓
- 행간 ↑ → 페이지당 줄 수 ↓
            """)
        
        # 이미지 설정
        st.markdown("---")
        st.markdown("**🖼️ 이미지**")
        icol1, icol2, icol3 = st.columns(3)
        with icol1:
            st.file_uploader("표지", type=['jpg','jpeg','png'], key=f"{prefix}_cover_img")
            if st.session_state.get(f"{prefix}_cover_img"):
                st.image(st.session_state[f"{prefix}_cover_img"], width=80)
        with icol2:
            st.file_uploader("내지", type=['jpg','jpeg','png'], key=f"{prefix}_bg_img")
            if st.session_state.get(f"{prefix}_bg_img"):
                st.image(st.session_state[f"{prefix}_bg_img"], width=80)
        with icol3:
            st.file_uploader("안내지", type=['jpg','jpeg','png'], key=f"{prefix}_info_img")
            if st.session_state.get(f"{prefix}_info_img"):
                st.image(st.session_state[f"{prefix}_info_img"], width=80)
    
    return {
        'font_family': new_font, 'font_size_title': new_title,
        'font_size_subtitle': new_subtitle, 'font_size_body': new_body,
        'line_height': new_line_height, 
        'letter_spacing': 0,  # 고정값 (미사용)
        'char_width': 100,    # 고정값 (미사용)
        'margin_top': new_mt, 'margin_bottom': new_mb,
        'margin_left': new_ml, 'margin_right': new_mr, 'target_pages': new_pages
    }


def save_product_images(service_id: int, prefix: str):
    """업로드된 이미지 저장"""
    cover = st.session_state.get(f"{prefix}_cover_img")
    bg = st.session_state.get(f"{prefix}_bg_img")
    info = st.session_state.get(f"{prefix}_info_img")
    
    if cover:
        path = save_uploaded_file(cover, "cover")
        add_template(service_id, "cover", "표지", path)
    if bg:
        path = save_uploaded_file(bg, "bg")
        add_template(service_id, "background", "내지", path)
    if info:
        path = save_uploaded_file(info, "info")
        add_template(service_id, "info", "안내지", path)


# ============================================
# 상품 목록 UI
# ============================================

def render_product_list(config: ProductConfig, products: list):
    """상품 목록 표시"""
    prefix = config.prefix
    
    if st.button(f"➕ 새 {config.title} 등록", type="primary", key=f"{prefix}_new_btn"):
        st.session_state[f'{prefix}_new_mode'] = True
        st.rerun()
    
    if not products:
        st.info(f"등록된 {config.title}이 없습니다.")
        return
    
    st.markdown("---")
    
    for p in products:
        col1, col2, col3 = st.columns([3, 1, 0.5])
        with col1:
            if st.button(f"{config.icon} {p['name']}", key=f"view_{p['id']}", use_container_width=True):
                st.session_state[f'{prefix}_view_id'] = p['id']
                st.rerun()
        with col2:
            st.caption(f"{p.get('target_pages', 30)}p")
        with col3:
            pass


def render_product_detail(config: ProductConfig, product: dict):
    """상품 상세보기 + 편집 통합 화면"""
    prefix = config.prefix
    edit_mode = st.session_state.get(f'{prefix}_edit_mode', False)
    
    # 데이터 로드
    chapters = get_chapters_by_service(product['id'])
    guidelines = get_guidelines_by_service(product['id'])
    templates = get_templates_by_service(product['id'])
    
    # 이미지 경로 추출
    cover_img = next((t['image_path'] for t in templates if t['template_type'] == 'cover'), None)
    bg_img = next((t['image_path'] for t in templates if t['template_type'] == 'background'), None)
    info_img = next((t['image_path'] for t in templates if t['template_type'] == 'info'), None)
    
    # 헤더
    hcol1, hcol2 = st.columns([4, 1])
    with hcol1:
        st.markdown(f"### {config.icon} {product['name']}")
    with hcol2:
        if st.button("⬅️ 목록", use_container_width=True, key=f"{prefix}_back"):
            st.session_state[f'{prefix}_view_id'] = None
            st.session_state[f'{prefix}_edit_mode'] = False
            st.rerun()
    
    st.markdown("---")
    
    # ========== 기본 정보 ==========
    if edit_mode:
        edit_name = st.text_input("상품명", value=product['name'], key=f"{prefix}_edit_name")
    else:
        st.markdown(f"**상품명:** {product['name']}")
    
    # ========== 목차 & 지침 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📑 목차**")
        ch_text = "\n".join([c['title'] for c in chapters]) if chapters else ""
        if edit_mode:
            edit_chapters = st.text_area("", value=ch_text, height=150, key=f"{prefix}_edit_ch",
                                        placeholder="1. 총운\n2. 재물운\n3. 건강운")
        else:
            if chapters:
                for i, ch in enumerate(chapters):
                    st.caption(f"{i+1}. {ch['title']}")
            else:
                st.caption("목차 없음")
    
    with col2:
        st.markdown("**📜 AI 지침**")
        guide_text = guidelines[0]['content'] if guidelines else ""
        if edit_mode:
            edit_guide = st.text_area("", value=guide_text, height=150, key=f"{prefix}_edit_guide",
                                     placeholder="20년 경력의 전문가로서...")
        else:
            if guide_text:
                st.caption(guide_text[:150] + "..." if len(guide_text) > 150 else guide_text)
            else:
                st.caption("지침 없음")
    
    # ========== 디자인 설정 ==========
    with st.expander("🎨 디자인 설정", expanded=edit_mode):
        if edit_mode:
            # 편집 가능
            dcol1, dcol2, dcol3, dcol4 = st.columns(4)
            with dcol1:
                font_idx = list(FONT_OPTIONS.keys()).index(product.get('font_family', 'NanumGothic')) \
                    if product.get('font_family') in FONT_OPTIONS else 0
                edit_font = st.selectbox("폰트", list(FONT_OPTIONS.keys()), index=font_idx,
                                        format_func=lambda x: FONT_OPTIONS[x], key=f"{prefix}_edit_font")
            with dcol2:
                edit_title_size = st.number_input("대제목", value=product.get('font_size_title', 24),
                                                  min_value=16, max_value=40, key=f"{prefix}_edit_title")
            with dcol3:
                edit_subtitle_size = st.number_input("소제목", value=product.get('font_size_subtitle', 16),
                                                     min_value=12, max_value=30, key=f"{prefix}_edit_sub")
            with dcol4:
                edit_body_size = st.number_input("본문", value=product.get('font_size_body', 12),
                                                 min_value=8, max_value=20, key=f"{prefix}_edit_body")
            
            dcol5, dcol6 = st.columns(2)
            with dcol5:
                edit_line_height = st.slider("행간 %", 100, 300, product.get('line_height', 180),
                                            key=f"{prefix}_edit_lh")
            with dcol6:
                edit_pages = st.number_input("목표 페이지", value=product.get('target_pages', 30),
                                            min_value=10, max_value=200, key=f"{prefix}_edit_pages")
            
            st.markdown("**📐 여백 (mm)**")
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            with mcol1:
                edit_mt = st.number_input("상단", value=product.get('margin_top', 25), key=f"{prefix}_edit_mt")
            with mcol2:
                edit_mb = st.number_input("하단", value=product.get('margin_bottom', 25), key=f"{prefix}_edit_mb")
            with mcol3:
                edit_ml = st.number_input("좌측", value=product.get('margin_left', 25), key=f"{prefix}_edit_ml")
            with mcol4:
                edit_mr = st.number_input("우측", value=product.get('margin_right', 25), key=f"{prefix}_edit_mr")
            
            # ======= 📊 예상 페이지 계산기 =======
            st.markdown("---")
            st.markdown("**📊 예상 결과 계산**")
            
            # 현재 입력값으로 계산
            cur_body = edit_body_size
            cur_lh = edit_line_height
            cur_mt = edit_mt
            cur_mb = edit_mb
            cur_ml = edit_ml
            cur_mr = edit_mr
            cur_pages = edit_pages
            
            # 페이지당 글자 수 계산
            page_width_mm = 210
            page_height_mm = 297
            usable_width_mm = page_width_mm - cur_ml - cur_mr
            usable_height_mm = page_height_mm - cur_mt - cur_mb
            
            char_width_mm = cur_body * 0.35
            line_height_mm = cur_body * 0.35 * (cur_lh / 100)
            
            chars_per_line = int(usable_width_mm / char_width_mm)
            lines_per_page = int(usable_height_mm / line_height_mm)
            chars_per_page = int(chars_per_line * lines_per_page * 0.75)
            
            calc_col1, calc_col2 = st.columns(2)
            with calc_col1:
                st.info(f"""
**현재 설정 기준:**
- 한 줄: 약 **{chars_per_line}자**
- 한 페이지: 약 **{lines_per_page}줄**
- 페이지당: 약 **{chars_per_page:,}자**
                """)
            with calc_col2:
                total_chars = cur_pages * chars_per_page
                num_chapters = len(chapters) if chapters else 5
                st.success(f"""
**{cur_pages}페이지 목표:**
- 필요 글자 수: **{total_chars:,}자**
- 현재 목차 {num_chapters}개 기준:
- 목차당 **{total_chars//num_chapters:,}자**
                """)
        else:
            # 읽기 전용 - 계산 결과도 표시
            st.caption(f"폰트: {FONT_OPTIONS.get(product.get('font_family', 'NanumGothic'), '나눔고딕')}")
            st.caption(f"글자 크기: 대제목 {product.get('font_size_title', 24)}pt / 소제목 {product.get('font_size_subtitle', 16)}pt / 본문 {product.get('font_size_body', 12)}pt")
            st.caption(f"행간: {product.get('line_height', 180)}% / 목표: {product.get('target_pages', 30)}페이지")
            st.caption(f"여백: 상{product.get('margin_top', 25)} 하{product.get('margin_bottom', 25)} 좌{product.get('margin_left', 25)} 우{product.get('margin_right', 25)}mm")
            
            # 읽기 전용에서도 예상 계산 표시
            st.markdown("---")
            cur_body = product.get('font_size_body', 12)
            cur_lh = product.get('line_height', 180)
            cur_pages = product.get('target_pages', 30)
            cur_ml = product.get('margin_left', 25)
            cur_mr = product.get('margin_right', 25)
            cur_mt = product.get('margin_top', 25)
            cur_mb = product.get('margin_bottom', 25)
            
            usable_w = 210 - cur_ml - cur_mr
            usable_h = 297 - cur_mt - cur_mb
            cpl = int(usable_w / (cur_body * 0.35))
            lpp = int(usable_h / (cur_body * 0.35 * cur_lh / 100))
            cpp = int(cpl * lpp * 0.75)
            total = cur_pages * cpp
            num_ch = len(chapters) if chapters else 5
            
            st.caption(f"📊 예상: 페이지당 ~{cpp}자 / 총 {total:,}자 필요 / 목차당 ~{total//num_ch:,}자")
    
    # ========== 이미지 ==========
    st.markdown("**🖼️ 이미지**")
    icol1, icol2, icol3 = st.columns(3)
    
    with icol1:
        st.caption("📕 표지")
        if cover_img:
            try:
                st.image(cover_img, width=100)
            except:
                st.caption("(로드 실패)")
        else:
            st.caption("없음")
        if edit_mode:
            st.file_uploader("새 표지", type=['jpg','jpeg','png'], key=f"{prefix}_new_cover", label_visibility="collapsed")
    
    with icol2:
        st.caption("📄 내지")
        if bg_img:
            try:
                st.image(bg_img, width=100)
            except:
                st.caption("(로드 실패)")
        else:
            st.caption("없음")
        if edit_mode:
            st.file_uploader("새 내지", type=['jpg','jpeg','png'], key=f"{prefix}_new_bg", label_visibility="collapsed")
    
    with icol3:
        st.caption("📋 안내지")
        if info_img:
            try:
                st.image(info_img, width=100)
            except:
                st.caption("(로드 실패)")
        else:
            st.caption("없음")
        if edit_mode:
            st.file_uploader("새 안내지", type=['jpg','jpeg','png'], key=f"{prefix}_new_info", label_visibility="collapsed")
    
    # ========== 버튼 ==========
    st.markdown("---")
    
    if edit_mode:
        # 편집 모드 버튼
        bcol1, bcol2, bcol3 = st.columns(3)
        with bcol1:
            if st.button("💾 저장", type="primary", use_container_width=True, key=f"{prefix}_save"):
                # 기본 정보 저장
                update_service(
                    product['id'],
                    name=st.session_state.get(f"{prefix}_edit_name", product['name']),
                    font_family=st.session_state.get(f"{prefix}_edit_font", product.get('font_family')),
                    font_size_title=st.session_state.get(f"{prefix}_edit_title", product.get('font_size_title')),
                    font_size_subtitle=st.session_state.get(f"{prefix}_edit_sub", product.get('font_size_subtitle')),
                    font_size_body=st.session_state.get(f"{prefix}_edit_body", product.get('font_size_body')),
                    line_height=st.session_state.get(f"{prefix}_edit_lh", product.get('line_height')),
                    target_pages=st.session_state.get(f"{prefix}_edit_pages", product.get('target_pages')),
                    margin_top=st.session_state.get(f"{prefix}_edit_mt", product.get('margin_top')),
                    margin_bottom=st.session_state.get(f"{prefix}_edit_mb", product.get('margin_bottom')),
                    margin_left=st.session_state.get(f"{prefix}_edit_ml", product.get('margin_left')),
                    margin_right=st.session_state.get(f"{prefix}_edit_mr", product.get('margin_right'))
                )
                
                # 목차 업데이트
                edit_ch = st.session_state.get(f"{prefix}_edit_ch", "")
                delete_chapters_by_service(product['id'])
                if edit_ch:
                    add_chapters_bulk(product['id'], [c.strip() for c in edit_ch.split('\n') if c.strip()])
                
                # 지침 업데이트
                edit_gd = st.session_state.get(f"{prefix}_edit_guide", "")
                if guidelines:
                    update_guideline(guidelines[0]['id'], content=edit_gd)
                elif edit_gd:
                    add_guideline(product['id'], "기본 지침", edit_gd)
                
                # 이미지 업데이트
                new_cover = st.session_state.get(f"{prefix}_new_cover")
                new_bg = st.session_state.get(f"{prefix}_new_bg")
                new_info = st.session_state.get(f"{prefix}_new_info")
                
                if new_cover:
                    path = save_uploaded_file(new_cover, "cover")
                    # 기존 삭제 후 추가
                    for t in templates:
                        if t['template_type'] == 'cover':
                            delete_template(t['id'])
                    add_template(product['id'], "cover", "표지", path)
                if new_bg:
                    path = save_uploaded_file(new_bg, "bg")
                    for t in templates:
                        if t['template_type'] == 'background':
                            delete_template(t['id'])
                    add_template(product['id'], "background", "내지", path)
                if new_info:
                    path = save_uploaded_file(new_info, "info")
                    for t in templates:
                        if t['template_type'] == 'info':
                            delete_template(t['id'])
                    add_template(product['id'], "info", "안내지", path)
                
                clear_service_cache()
                st.session_state[f'{prefix}_edit_mode'] = False
                st.toast("✅ 저장 완료!")
                st.rerun()
        
        with bcol2:
            if st.button("❌ 취소", use_container_width=True, key=f"{prefix}_cancel"):
                st.session_state[f'{prefix}_edit_mode'] = False
                st.rerun()
        
        with bcol3:
            pass
    else:
        # 보기 모드 버튼
        bcol1, bcol2, bcol3 = st.columns(3)
        with bcol1:
            if st.button("✏️ 수정", type="primary", use_container_width=True, key=f"{prefix}_edit"):
                st.session_state[f'{prefix}_edit_mode'] = True
                st.rerun()
        with bcol2:
            if st.button("🗑️ 삭제", use_container_width=True, key=f"{prefix}_del"):
                delete_service(product['id'])
                clear_service_cache()
                st.session_state[f'{prefix}_view_id'] = None
                st.toast("🗑️ 삭제됨")
                st.rerun()
        with bcol3:
            pass


# ============================================
# 고객 목록 UI
# ============================================

def render_customer_list(config: ProductConfig, customers: list, product: dict):
    """고객 목록 및 선택 UI"""
    prefix = config.prefix
    rc = st.session_state[f'{prefix}_reset']
    
    if not customers:
        return
    
    total = len(customers)
    selected = st.session_state[f'{prefix}_selected']
    selected_count = len(selected)
    
    st.markdown(f"### 👥 고객 목록 ({selected_count}/{total}명 선택)")
    
    # 선택 버튼들
    bcol1, bcol2, bcol3 = st.columns([1, 1, 1])
    with bcol1:
        if st.button("✅ 전체 선택", use_container_width=True, key=f"{prefix}_sel_all_{rc}"):
            st.session_state[f'{prefix}_selected'] = set(range(total))
            st.rerun()
    with bcol2:
        if st.button("⬜ 전체 해제", use_container_width=True, key=f"{prefix}_desel_all_{rc}"):
            st.session_state[f'{prefix}_selected'] = set()
            st.rerun()
    with bcol3:
        if st.button("🔄 초기화", use_container_width=True, key=f"{prefix}_reset_btn_{rc}"):
            st.session_state[f'{prefix}_customers'] = []
            st.session_state[f'{prefix}_selected'] = set()
            st.session_state[f'{prefix}_progress'] = {}
            st.session_state[f'{prefix}_completed'] = set()
            st.session_state[f'{prefix}_pdfs'] = {}
            st.session_state[f'{prefix}_reset'] += 1
            st.rerun()
    
    st.markdown("---")
    
    # 고객 목록 - 체크박스를 value 기반으로 동기화
    for idx, cust in enumerate(customers):
        col_chk, col_name, col_prog, col_dl = st.columns([0.5, 2, 2, 1])
        
        with col_chk:
            # 세션 상태와 동기화된 체크박스
            is_selected = idx in st.session_state[f'{prefix}_selected']
            checked = st.checkbox(
                "", 
                value=is_selected,
                key=f"chk_{prefix}_{idx}_{rc}",
                label_visibility="collapsed"
            )
            # 체크 상태 변경 시 세션 업데이트
            if checked and idx not in st.session_state[f'{prefix}_selected']:
                st.session_state[f'{prefix}_selected'].add(idx)
            elif not checked and idx in st.session_state[f'{prefix}_selected']:
                st.session_state[f'{prefix}_selected'].discard(idx)
        
        with col_name:
            name = cust.get('이름', cust.get('고객명', f'고객{idx+1}'))
            st.write(f"👤 {name}")
        
        with col_prog:
            prog = st.session_state[f'{prefix}_progress'].get(idx, 0)
            st.progress(prog / 100)
            if idx in st.session_state[f'{prefix}_completed']:
                st.caption("✅ 완료")
        
        with col_dl:
            if idx in st.session_state[f'{prefix}_completed']:
                pdfs = st.session_state.get(f'{prefix}_pdfs', {})
                if idx in pdfs:
                    st.download_button(
                        "📥", data=pdfs[idx]['pdf'],
                        file_name=f"{pdfs[idx]['name']}_{product['name']}.pdf",
                        mime="application/pdf", key=f"dl_{prefix}_{idx}_{rc}"
                    )


# ============================================
# PDF 생성 로직
# ============================================

def generate_pdfs(config: ProductConfig, customers: list, product: dict) -> bool:
    """선택된 고객들의 PDF 생성"""
    prefix = config.prefix
    selected = st.session_state[f'{prefix}_selected']
    
    if not selected:
        st.button("🚀 PDF 생성 (0명 선택)", disabled=True, use_container_width=True)
        return False
    
    selected_count = len(selected)
    
    if st.button(f"🚀 PDF 생성 ({selected_count}명)", type="primary", use_container_width=True):
        # API 키 확인
        api_key = get_system_config(ConfigKeys.ADMIN_API_KEY, "")
        if not api_key:
            st.error("⚠️ API 키가 설정되지 않았습니다.")
            return False
        
        # 상품 정보
        chapters = get_chapters_by_service(product['id'])
        guidelines = get_guidelines_by_service(product['id'])
        templates = get_templates_by_service(product['id'])
        
        if not chapters:
            st.error("⚠️ 목차가 없습니다.")
            return False
        
        chapter_titles = [c['title'] for c in chapters]
        guideline_text = guidelines[0]['content'] if guidelines else ""
        
        # 이미지 경로
        cover_img = next((t['image_path'] for t in templates if t['template_type'] == 'cover'), None)
        bg_img = next((t['image_path'] for t in templates if t['template_type'] == 'background'), None)
        info_img = next((t['image_path'] for t in templates if t['template_type'] == 'info'), None)
        
        bar = st.progress(0)
        status = st.empty()
        
        # PDF 생성기
        pdf_gen = PDFGenerator(
            font_name=product.get('font_family', 'NanumGothic'),
            font_size_title=product.get('font_size_title', 24),
            font_size_subtitle=product.get('font_size_subtitle', 16),
            font_size_body=product.get('font_size_body', 12),
            line_height=product.get('line_height', 180),
            letter_spacing=product.get('letter_spacing', 0),
            char_width=product.get('char_width', 100),
            margin_top=product.get('margin_top', 25),
            margin_bottom=product.get('margin_bottom', 25),
            margin_left=product.get('margin_left', 25),
            margin_right=product.get('margin_right', 25),
            target_pages=product.get('target_pages', 30)
        )
        
        generated_pdfs = {}
        total_chapters = len(chapter_titles)
        selected_list = list(selected)  # set을 list로 변환
        
        for i, idx in enumerate(selected_list):
            cust = customers[idx]
            name = cust.get('이름', cust.get('고객명', f'고객{idx+1}'))
            
            # 고객별 기본 진행률 (0~100)
            base_progress = int((i / selected_count) * 100)
            customer_weight = 100 / selected_count  # 고객 1명당 차지하는 %
            
            def progress_cb(chapter_prog, msg):
                # chapter_prog: 0.0 ~ 1.0 (목차 진행률)
                # 고객별 진행률: 콘텐츠 생성 90%, PDF 생성 10%
                content_progress = int(chapter_prog * 90)
                st.session_state[f'{prefix}_progress'][idx] = content_progress
                
                # 전체 진행률 계산 (1% 단위)
                overall = base_progress + int(chapter_prog * customer_weight * 0.9)
                bar.progress(min(overall / 100, 0.99))
                
                # 상세 상태 표시
                current_chapter = int(chapter_prog * total_chapters)
                status.text(f"⏳ {name}님 ({i+1}/{selected_count}) - {current_chapter}/{total_chapters}장 생성 중... [{overall}%]")
            
            contents = generate_full_content(
                api_key=api_key,
                customer_info=cust,
                chapters=chapter_titles,
                guideline=guideline_text,
                service_type=product['name'],
                target_pages=product.get('target_pages', 30),
                font_size=product.get('font_size_body', 12),
                line_height=product.get('line_height', 180),
                margin_top=product.get('margin_top', 25),
                margin_bottom=product.get('margin_bottom', 25),
                margin_left=product.get('margin_left', 25),
                margin_right=product.get('margin_right', 25),
                progress_callback=progress_cb
            )
            
            # PDF 생성 단계 (90% → 100%)
            st.session_state[f'{prefix}_progress'][idx] = 95
            pdf_progress = base_progress + int(customer_weight * 0.95)
            bar.progress(min(pdf_progress / 100, 0.99))
            status.text(f"📄 {name}님 PDF 변환 중... [{pdf_progress}%]")
            
            pdf_bytes = pdf_gen.create_pdf(
                chapters_content=contents,
                customer_name=name,
                service_type=product['name'],
                cover_image=cover_img,
                background_image=bg_img,
                info_image=info_img
            )
            
            generated_pdfs[idx] = {'name': name, 'pdf': pdf_bytes}
            st.session_state[f'{prefix}_progress'][idx] = 100
            st.session_state[f'{prefix}_completed'].add(idx)
            
            # 고객 완료
            complete_progress = int(((i + 1) / selected_count) * 100)
            bar.progress(complete_progress / 100)
            status.text(f"✅ {name}님 완료! [{complete_progress}%]")
        
        st.session_state[f'{prefix}_pdfs'] = generated_pdfs
        bar.progress(1.0)
        status.text(f"✅ {selected_count}명 PDF 생성 완료! [100%]")
        st.balloons()
        st.rerun()
    
    return True
