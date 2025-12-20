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
        st.markdown("**📄 목표 페이지**")
        new_pages = st.number_input("페이지 수", value=defaults.get('target_pages', 30), 
                                    min_value=1, max_value=500, key=f"{prefix}_pages")
        
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
        
        fcol5, fcol6, fcol7 = st.columns(3)
        with fcol5:
            new_line_height = st.slider("행간 %", 100, 300, defaults.get('line_height', 180),
                                        key=f"{prefix}_lh")
        with fcol6:
            new_letter_spacing = st.slider("자간 %", -5, 10, defaults.get('letter_spacing', 0),
                                           key=f"{prefix}_ls")
        with fcol7:
            new_char_width = st.slider("장평 %", 50, 150, defaults.get('char_width', 100),
                                       key=f"{prefix}_cw")
        
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
        'line_height': new_line_height, 'letter_spacing': new_letter_spacing,
        'char_width': new_char_width, 'margin_top': new_mt, 'margin_bottom': new_mb,
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
    """상품 상세/편집 화면"""
    prefix = config.prefix
    
    # 편집 모드
    if st.session_state[f'{prefix}_edit_mode']:
        render_product_edit_form(config, product)
        return
    
    # 상세 보기 모드
    st.markdown(f"### {config.icon} {product['name']}")
    
    # 목차, 지침 표시
    chapters = get_chapters_by_service(product['id'])
    guidelines = get_guidelines_by_service(product['id'])
    templates = get_templates_by_service(product['id'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📑 목차**")
        if chapters:
            for i, ch in enumerate(chapters):
                st.caption(f"{i+1}. {ch['title']}")
        else:
            st.caption("목차 없음")
    
    with col2:
        st.markdown("**📜 AI 지침**")
        if guidelines:
            st.caption(guidelines[0]['content'][:100] + "..." if len(guidelines[0]['content']) > 100 else guidelines[0]['content'])
        else:
            st.caption("지침 없음")
    
    # 이미지 미리보기
    if templates:
        st.markdown("**🖼️ 이미지**")
        icols = st.columns(3)
        for i, t in enumerate(templates[:3]):
            with icols[i]:
                st.caption(t['name'])
                if t.get('image_path'):
                    try:
                        st.image(t['image_path'], width=60)
                    except:
                        st.caption("(로드 실패)")
    
    st.markdown("---")
    bcol1, bcol2, bcol3 = st.columns(3)
    with bcol1:
        if st.button("✏️ 편집", use_container_width=True, key=f"{prefix}_edit_btn"):
            st.session_state[f'{prefix}_edit_mode'] = True
            st.rerun()
    with bcol2:
        if st.button("🗑️ 삭제", use_container_width=True, key=f"{prefix}_del_btn"):
            delete_service(product['id'])
            clear_service_cache()
            st.session_state[f'{prefix}_view_id'] = None
            st.toast("🗑️ 삭제됨")
            st.rerun()
    with bcol3:
        if st.button("⬅️ 목록", use_container_width=True, key=f"{prefix}_back_btn"):
            st.session_state[f'{prefix}_view_id'] = None
            st.rerun()


def render_product_edit_form(config: ProductConfig, product: dict):
    """상품 편집 폼"""
    prefix = config.prefix
    
    st.markdown(f"### ✏️ {product['name']} 편집")
    
    edit_name = st.text_input("상품명", value=product['name'], key=f"{prefix}_edit_name")
    
    chapters = get_chapters_by_service(product['id'])
    guidelines = get_guidelines_by_service(product['id'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📑 목차**")
        ch_text = "\n".join([c['title'] for c in chapters]) if chapters else ""
        edit_chapters = st.text_area("", value=ch_text, height=200, key=f"{prefix}_edit_ch")
    with col2:
        st.markdown("**📜 AI 지침**")
        guide_text = guidelines[0]['content'] if guidelines else ""
        edit_guide = st.text_area("", value=guide_text, height=200, key=f"{prefix}_edit_guide")
    
    design = render_design_settings(prefix + "_edit", expanded=True, defaults=product)
    
    st.markdown("---")
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if st.button("💾 저장", type="primary", use_container_width=True, key=f"{prefix}_save_edit"):
            update_service(product['id'], name=edit_name, **design)
            
            # 목차 업데이트
            delete_chapters_by_service(product['id'])
            if edit_chapters:
                add_chapters_bulk(product['id'], [c.strip() for c in edit_chapters.split('\n') if c.strip()])
            
            # 지침 업데이트
            if guidelines:
                update_guideline(guidelines[0]['id'], content=edit_guide)
            elif edit_guide:
                add_guideline(product['id'], "기본 지침", edit_guide)
            
            # 이미지 업데이트
            save_product_images(product['id'], prefix + "_edit")
            
            clear_service_cache()
            st.session_state[f'{prefix}_edit_mode'] = False
            st.toast("✅ 저장됨")
            st.rerun()
    
    with bcol2:
        if st.button("❌ 취소", use_container_width=True, key=f"{prefix}_cancel_edit"):
            st.session_state[f'{prefix}_edit_mode'] = False
            st.rerun()


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
        if st.button("✅ 전체 선택", use_container_width=True, key=f"{prefix}_sel_all"):
            st.session_state[f'{prefix}_selected'] = set(range(total))
            st.rerun()
    with bcol2:
        if st.button("⬜ 전체 해제", use_container_width=True, key=f"{prefix}_desel_all"):
            st.session_state[f'{prefix}_selected'] = set()
            st.rerun()
    with bcol3:
        if st.button("🔄 초기화", use_container_width=True, key=f"{prefix}_reset_btn"):
            st.session_state[f'{prefix}_customers'] = []
            st.session_state[f'{prefix}_selected'] = set()
            st.session_state[f'{prefix}_progress'] = {}
            st.session_state[f'{prefix}_completed'] = set()
            st.session_state[f'{prefix}_pdfs'] = {}
            st.session_state[f'{prefix}_reset'] += 1
            st.rerun()
    
    st.markdown("---")
    
    # 고객 목록
    for idx, cust in enumerate(customers):
        col_chk, col_name, col_prog, col_dl = st.columns([0.5, 2, 2, 1])
        
        with col_chk:
            checked = idx in selected
            def toggle(i):
                if i in st.session_state[f'{prefix}_selected']:
                    st.session_state[f'{prefix}_selected'].discard(i)
                else:
                    st.session_state[f'{prefix}_selected'].add(i)
            st.checkbox("", value=checked, key=f"chk_{prefix}_{idx}_{rc}", 
                       label_visibility="collapsed", on_change=toggle, args=(idx,))
        
        with col_name:
            name = cust.get('이름', cust.get('고객명', f'고객{idx+1}'))
            st.write(f"👤 {name}")
        
        with col_prog:
            prog = st.session_state[f'{prefix}_progress'].get(idx, 0)
            st.progress(prog / 100)
        
        with col_dl:
            if idx in st.session_state[f'{prefix}_completed']:
                pdfs = st.session_state.get(f'{prefix}_pdfs', {})
                if idx in pdfs:
                    st.download_button(
                        "📥", data=pdfs[idx]['pdf'],
                        file_name=f"{pdfs[idx]['name']}_{product['name']}.pdf",
                        mime="application/pdf", key=f"dl_{prefix}_{idx}"
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
        
        for i, idx in enumerate(selected):
            cust = customers[idx]
            name = cust.get('이름', cust.get('고객명', f'고객{idx+1}'))
            status.text(f"⏳ {name}님 콘텐츠 생성 중... ({i+1}/{selected_count})")
            
            def progress_cb(prog, msg):
                st.session_state[f'{prefix}_progress'][idx] = int(prog * 80)
                bar.progress((i + prog * 0.8) / selected_count)
            
            contents = generate_full_content(
                api_key=api_key,
                customer_info=cust,
                chapters=chapter_titles,
                guideline=guideline_text,
                service_type=product['name'],
                progress_callback=progress_cb
            )
            
            status.text(f"📄 {name}님 PDF 생성 중... ({i+1}/{selected_count})")
            
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
            bar.progress((i + 1) / selected_count)
        
        st.session_state[f'{prefix}_pdfs'] = generated_pdfs
        bar.progress(1.0)
        status.text(f"✅ {selected_count}명 PDF 생성 완료!")
        st.balloons()
        st.rerun()
    
    return True
