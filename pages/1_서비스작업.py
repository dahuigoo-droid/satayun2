# -*- coding: utf-8 -*-
"""
📦 서비스 작업 페이지
"""

import streamlit as st
import pandas as pd
import os
import time
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="서비스 작업", page_icon="📦", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    cached_get_admin_services, cached_get_user_services, cached_get_chapters,
    cached_get_guidelines, cached_get_templates, clear_service_cache,
    is_admin, get_member_level, save_uploaded_file, get_api_key,
    verify_pdf_generation_ready, calculate_chars_per_page,
    render_font_settings, render_progress_card, render_error_card,
    TEMPLATE_TYPES, FONT_OPTIONS, CATEGORIES, UPLOAD_DIR, OUTPUT_DIR
)
from services import (
    add_service, update_service, delete_service, get_system_config, ConfigKeys
)
from contents import (
    add_chapters_bulk, delete_chapters_by_service,
    get_chapters_by_service, get_guidelines_by_service, get_templates_by_service,
    add_guideline, update_guideline, add_template, delete_template
)
from pdf_utils import (
    generate_chapters_parallel, generate_scores_with_gpt, create_pdf_document,
    generate_pdf_for_customer, generate_pdf_with_progress,
    generate_order_hash, is_already_generated, mark_as_generated
)
from notification import send_email_with_attachment

# ============================================
# 상품 수정 폼 함수
# ============================================

def show_service_edit_form(service, prefix):
    """기존 상품 수정 폼 (v1 스타일)"""
    svc_id = service['id']
    
    chapters = cached_get_chapters(svc_id)
    guidelines = cached_get_guidelines(svc_id)
    templates = cached_get_templates(svc_id)
    
    new_name = st.text_input("상품명", value=service.get('name', ''), key=f"{prefix}_edit_name_{svc_id}")
    
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**📑 목차**")
        chapter_text = "\n".join([ch.get('title', '') for ch in chapters]) if chapters else ""
        new_chapters = st.text_area("목차", value=chapter_text, height=250, key=f"{prefix}_edit_ch_{svc_id}", label_visibility="collapsed")
    
    with col_right:
        st.markdown("**📜 지침**")
        guideline_text = guidelines[0].get('content', '') if guidelines else ""
        new_guideline = st.text_area("지침", value=guideline_text, height=250, key=f"{prefix}_edit_guide_{svc_id}", label_visibility="collapsed")
    
    with st.expander("⚙️ 폰트/디자인 설정", expanded=False):
        st.markdown("**📄 목표 페이지 수**")
        col_page, col_info = st.columns([1, 2])
        with col_page:
            target_pages = st.number_input("목표 페이지", value=service.get('target_pages', 30), min_value=5, max_value=100, key=f"{prefix}_pages_{svc_id}")
        with col_info:
            chars_per_page = 840
            total_chars = chars_per_page * target_pages
            st.success(f"📊 현재 설정: 페이지당 약 {chars_per_page}자 | 총 {total_chars:,}자 예상")
        
        st.markdown("**🔤 폰트 설정**")
        font_cols = st.columns(4)
        with font_cols[0]:
            font_family = st.selectbox("폰트", list(FONT_OPTIONS.keys()), index=0, key=f"{prefix}_font_{svc_id}")
        with font_cols[1]:
            font_size_body = st.number_input("본문 크기", value=service.get('font_size_body', 12), min_value=8, max_value=24, key=f"{prefix}_fontsize_{svc_id}")
        with font_cols[2]:
            line_height = st.number_input("줄간격(%)", value=service.get('line_height', 180), min_value=100, max_value=300, key=f"{prefix}_lineheight_{svc_id}")
        with font_cols[3]:
            letter_spacing = st.number_input("자간", value=service.get('letter_spacing', 0), min_value=-5, max_value=10, key=f"{prefix}_letterspacing_{svc_id}")
        
        st.markdown("**📐 여백 설정 (mm)**")
        margin_cols = st.columns(4)
        with margin_cols[0]:
            margin_top = st.number_input("상단", value=service.get('margin_top', 25), min_value=10, max_value=50, key=f"{prefix}_mt_{svc_id}")
        with margin_cols[1]:
            margin_bottom = st.number_input("하단", value=service.get('margin_bottom', 25), min_value=10, max_value=50, key=f"{prefix}_mb_{svc_id}")
        with margin_cols[2]:
            margin_left = st.number_input("좌측", value=service.get('margin_left', 25), min_value=10, max_value=50, key=f"{prefix}_ml_{svc_id}")
        with margin_cols[3]:
            margin_right = st.number_input("우측", value=service.get('margin_right', 25), min_value=10, max_value=50, key=f"{prefix}_mr_{svc_id}")
        
        st.markdown("**🖼️ 디자인 이미지**")
        design_cols = st.columns(3)
        with design_cols[0]:
            st.caption("📕 표지")
            cover_tpl = next((t for t in templates if t.get('type') == 'cover'), None) if templates else None
            if cover_tpl and cover_tpl.get('image_url'):
                st.image(cover_tpl['image_url'], width=100)
            new_cover = st.file_uploader("표지 변경", type=["jpg","jpeg","png"], key=f"{prefix}_cover_{svc_id}", label_visibility="collapsed")
        with design_cols[1]:
            st.caption("📄 내지")
            bg_tpl = next((t for t in templates if t.get('type') == 'background'), None) if templates else None
            if bg_tpl and bg_tpl.get('image_url'):
                st.image(bg_tpl['image_url'], width=100)
            new_bg = st.file_uploader("내지 변경", type=["jpg","jpeg","png"], key=f"{prefix}_bg_{svc_id}", label_visibility="collapsed")
        with design_cols[2]:
            st.caption("📋 안내지")
            info_tpl = next((t for t in templates if t.get('type') == 'info'), None) if templates else None
            if info_tpl and info_tpl.get('image_url'):
                st.image(info_tpl['image_url'], width=100)
            new_info = st.file_uploader("안내지 변경", type=["jpg","jpeg","png"], key=f"{prefix}_info_{svc_id}", label_visibility="collapsed")
    
    st.markdown("---")
    
    col_save, col_delete = st.columns(2)
    with col_save:
        if st.button("💾 수정 저장", key=f"{prefix}_save_{svc_id}", type="primary", use_container_width=True):
            update_service(svc_id, name=new_name, target_pages=target_pages)
            new_chapter_list = [ch.strip() for ch in new_chapters.strip().split("\n") if ch.strip()]
            delete_chapters_by_service(svc_id)
            add_chapters_bulk(svc_id, new_chapter_list)
            if guidelines:
                update_guideline(guidelines[0]['id'], content=new_guideline)
            elif new_guideline:
                add_guideline(svc_id, f"{new_name} 지침", new_guideline)
            clear_service_cache()
            st.success("✅ 수정 완료!")
            st.rerun()
    
    with col_delete:
        if st.button("🗑️ 상품 삭제", key=f"{prefix}_del_{svc_id}", type="secondary", use_container_width=True):
            delete_service(svc_id)
            clear_service_cache()
            st.session_state.selected_individual_service = None
            st.warning("🗑️ 삭제됨")
            st.rerun()

# ============================================
# 초기화
# ============================================

init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

st.title("📦 서비스 작업")

user = st.session_state.user
level = user.get('member_level', 1) if not user.get('is_admin') else 3
api_key = get_api_key()
selected_service = None

# 1. 상품 유형 선택
st.markdown('<span class="section-title">1️⃣ 상품 유형 선택</span>', unsafe_allow_html=True)
if level == 1:
    options = ["📦 기성상품"]
elif level == 2:
    options = ["🔧 개별상품"]
else:
    options = ["📦 기성상품", "🔧 개별상품"]
product_type = st.radio("상품 유형", options, horizontal=True, key="prod_type")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# 2. 기성상품
if "기성상품" in product_type:
    st.markdown('<span class="section-title">2️⃣ 기성상품 선택</span>', unsafe_allow_html=True)
    admin_services = cached_get_admin_services()
    if admin_services:
        svc_names = [s.get('name', '이름없음') for s in admin_services]
        selected_idx = st.selectbox("기성상품 목록", range(len(admin_services)), 
                                   format_func=lambda x: svc_names[x], key="ready_svc")
        selected_service = admin_services[selected_idx]
        if selected_service:
            chapters = cached_get_chapters(selected_service['id'])
            st.success(f"✅ '{selected_service.get('name', '')}' 선택됨 (목차 {len(chapters) if chapters else 0}개)")
    else:
        st.warning("등록된 기성상품이 없습니다.")

# 2. 개별상품
elif "개별상품" in product_type:
    st.markdown('<span class="section-title">2️⃣ 개별상품</span>', unsafe_allow_html=True)
    my_services = cached_get_user_services(user['id'])
    
    # 세션 상태 초기화
    if 'individual_mode' not in st.session_state:
        st.session_state.individual_mode = 'select' if my_services else 'create'
    
    # 기존 상품 있으면 선택/새로 만들기 버튼 표시
    if my_services:
        col_select, col_create = st.columns(2)
        with col_select:
            if st.button("📋 기존 상품 선택", 
                        type="primary" if st.session_state.individual_mode == 'select' else "secondary",
                        use_container_width=True):
                st.session_state.individual_mode = 'select'
                st.rerun()
        with col_create:
            if st.button("➕ 새 상품 만들기",
                        type="primary" if st.session_state.individual_mode == 'create' else "secondary",
                        use_container_width=True):
                st.session_state.individual_mode = 'create'
                st.rerun()
    
    # ===== 기존 상품 선택 모드 =====
    if st.session_state.individual_mode == 'select' and my_services:
        st.caption("📦 내 상품 목록")
        
        # 상품 목록을 컴팩트하게 표시
        for idx, svc in enumerate(my_services):
            chapters = cached_get_chapters(svc['id'])
            is_selected = st.session_state.get('selected_individual_service') == svc['id']
            
            # 선택된 상품
            if is_selected:
                st.markdown(f"""
                <div class="product-card">
                    <span style="color: #4CAF50; font-weight: bold;">✅</span>
                    <b style="color: white; margin-left: 8px;">{svc.get('name', '')}</b>
                    <span style="color: #aaa; margin-left: 8px; font-size: 0.85rem;">목차 {len(chapters) if chapters else 0}개</span>
                </div>
                """, unsafe_allow_html=True)
                
                selected_service = svc
                with st.expander("✏️ 상품 수정", expanded=False):
                    show_service_edit_form(svc, "my")
            else:
                # 선택 안된 상품 - 한 줄 컴팩트
                col_info, col_action = st.columns([5, 1])
                with col_info:
                    ch_count = len(chapters) if chapters else 0
                    st.markdown(f"**{svc.get('name', '')}** <span style='color:#888; font-size:0.85rem;'>목차 {ch_count}개</span>", unsafe_allow_html=True)
                with col_action:
                    if st.button("선택", key=f"sel_svc_{svc['id']}", type="primary"):
                        st.session_state.selected_individual_service = svc['id']
                        st.rerun()
                st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
        
        # 선택된 상품 가져오기
        if st.session_state.get('selected_individual_service') and selected_service is None:
            for svc in my_services:
                if svc['id'] == st.session_state.selected_individual_service:
                    selected_service = svc
                    break
        
        # 선택 안내
        if not st.session_state.get('selected_individual_service'):
            st.caption("👆 상품을 선택하세요")
    
    # ===== 새 상품 만들기 모드 =====
    elif st.session_state.individual_mode == 'create' or not my_services:
        st.markdown("**➕ 새 상품 만들기**")
        
        my_name = st.text_input("상품명", key="my_prod", placeholder="예: 2025 신년운세")
        
        if my_name:  # 상품명 입력 후 나머지 필드 표시
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("**📑 목차** (줄바꿈으로 구분)")
                my_chapters = st.text_area("목차", height=300, key="my_ch", 
                                           placeholder="1. 총운\n2. 재물운\n3. 건강운")
            with col_right:
                st.markdown("**📜 AI 작성 지침**")
                my_guide = st.text_area("지침", height=300, key="my_g",
                                       placeholder="고객 정보를 바탕으로 긍정적인 톤으로 작성...")
            
            with st.expander("⚙️ 폰트/디자인 설정", expanded=False):
                font_settings = render_font_settings("new_my")
                
                st.markdown("**🖼️ 디자인**")
                d_cols = st.columns(3)
                with d_cols[0]:
                    my_cover = st.file_uploader("📕 표지", type=["jpg","jpeg","png"], key="my_cover")
                with d_cols[1]:
                    my_bg = st.file_uploader("📄 내지", type=["jpg","jpeg","png"], key="my_bg")
                with d_cols[2]:
                    my_info = st.file_uploader("📋 안내지", type=["jpg","jpeg","png"], key="my_info")
            
            st.markdown("---")
            
            # 저장 버튼 (조건 충족 시만)
            can_save = my_name.strip() and st.session_state.get('my_ch', '').strip()
            
            if can_save:
                if st.button("💾 상품 저장", type="primary", use_container_width=True):
                    with st.spinner("저장 중..."):
                        my_chapters = st.session_state.get('my_ch', '')
                        my_guide = st.session_state.get('my_g', '')
                        
                        # font_settings를 session_state에서 가져오기
                        settings_key = "new_my_font_settings"
                        font_settings = st.session_state.get(settings_key, {
                            "font_family": "NanumGothic", "font_size_title": 24, "font_size_subtitle": 16,
                            "font_size_body": 12, "letter_spacing": 0, "line_height": 180, "char_width": 100,
                            "margin_top": 25, "margin_bottom": 25, "margin_left": 25, "margin_right": 25,
                            "target_pages": 30
                        })
                        
                        result = add_service(my_name, "", user['id'], **font_settings)
                        if result.get("success"):
                            svc_id = result["id"]
                            chapter_list = [ch.strip() for ch in my_chapters.strip().split("\n") if ch.strip()]
                            add_chapters_bulk(svc_id, chapter_list)
                            if my_guide:
                                add_guideline(svc_id, f"{my_name} 지침", my_guide)
                            
                            # 이미지 업로드 처리
                            my_cover = st.session_state.get('my_cover')
                            my_bg = st.session_state.get('my_bg')
                            my_info = st.session_state.get('my_info')
                            
                            if my_cover:
                                add_template(svc_id, "cover", "표지", save_uploaded_file(my_cover, f"{my_name}_cover"))
                            if my_bg:
                                add_template(svc_id, "background", "내지", save_uploaded_file(my_bg, f"{my_name}_bg"))
                            if my_info:
                                add_template(svc_id, "info", "안내지", save_uploaded_file(my_info, f"{my_name}_info"))
                            
                            clear_service_cache()
                            st.session_state.individual_mode = 'select'
                            st.session_state.selected_individual_service = svc_id
                    st.success(f"✅ '{my_name}' 저장됨!")
                    st.rerun()
            else:
                st.button("💾 상품 저장", type="secondary", use_container_width=True, disabled=True)
                st.caption("⚠️ 상품명과 목차를 입력하세요")
        else:
            st.info("👆 상품명을 먼저 입력하세요")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# 3. PDF 생성
st.markdown('<span class="section-title">3️⃣ PDF 생성</span>', unsafe_allow_html=True)

if selected_service:
    is_ready, errors = verify_pdf_generation_ready(selected_service['id'], api_key)
    for err in errors:
        st.error(err) if "❌" in err else st.warning(err)
    if not is_ready:
        st.stop()
else:
    st.warning("⚠️ 상품을 먼저 선택하세요.")
    st.stop()

# 고객 정보 입력 방식 선택
st.markdown("**📋 고객 정보 입력 방식**")
input_method = st.radio(
    "입력 방식",
    ["📂 엑셀 업로드", "✏️ 직접 입력 (최대 2명)"],
    horizontal=True,
    key="input_method"
)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===== 엑셀 업로드 방식 =====
if "엑셀" in input_method:
    # 컬럼 형식 안내
    st.markdown("""
    **📋 엑셀 컬럼 형식**
    - **1인용**: 이름, 생년월일, 음력양력, 태어난시간, 이메일
    - **2인용 (궁합/재회)**: 고객1_이름, 고객1_생년월일, 고객1_음력양력, 고객1_태어난시간, 고객2_이름, 고객2_생년월일, 고객2_음력양력, 고객2_태어난시간, 이메일
    """)
    
    uploaded = st.file_uploader("📂 고객 엑셀 파일 (.xlsx)", type=["xlsx", "xls"], key="cust")
    
    if uploaded:
        df = pd.read_excel(uploaded)
        st.session_state.customers_df = df
        st.session_state.selected_customers = set(range(len(df)))
        st.session_state.input_mode = "excel"
        st.success(f"✅ {len(df)}건 로드됨")
    
    if st.session_state.get('customers_df') is not None and st.session_state.get('input_mode') == 'excel':
        df = st.session_state.customers_df
        
        # 컬럼명으로 1인/2인 자동 판별
        is_couple = any(col in df.columns for col in ['고객1_이름', '고객1이름', '고객2_이름', '고객2이름'])
        
        if is_couple:
            st.info("💑 **2인용 (궁합/재회)** 데이터로 인식됨")
            svc_type = 'couple'
            # 2인용 컬럼 찾기
            name1_col = None
            name2_col = None
            for col in ['고객1_이름', '고객1이름', 'name1', 'Name1']:
                if col in df.columns:
                    name1_col = col
                    break
            for col in ['고객2_이름', '고객2이름', 'name2', 'Name2']:
                if col in df.columns:
                    name2_col = col
                    break
            if not name1_col:
                name1_col = df.columns[0]
            if not name2_col and len(df.columns) > 1:
                name2_col = df.columns[1]
        else:
            st.info("👤 **1인용** 데이터로 인식됨")
            svc_type = 'single'
            # 1인용 컬럼 찾기
            name_col = None
            for col in ['이름', 'name', 'Name', '성명', '고객명']:
                if col in df.columns:
                    name_col = col
                    break
            if not name_col:
                name_col = df.columns[0]
        
        st.markdown("---")
        
        # ===== 업무 자동화 콘솔: 간소화된 UI =====
        # 요약 정보만 표시 (개별 선택 제거)
        total_count = len(df)
        completed_count = len(st.session_state.get('completed_customers', {}))
        pending_count = total_count - completed_count
        
        # 진행 상태 카드
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("📊 전체", f"{total_count}건")
        with col_stat2:
            st.metric("✅ 완료", f"{completed_count}건")
        with col_stat3:
            st.metric("⏳ 대기", f"{pending_count}건", delta=f"-{completed_count}" if completed_count > 0 else None)
        
        # 초기화 버튼만 (작은 크기)
        col_reset = st.columns([3, 1])
        with col_reset[1]:
            if st.button("🔄 초기화", use_container_width=True, disabled=st.session_state.get('work_processing', False)):
                st.session_state.customers_df = None
                st.session_state.completed_customers = {}
                st.session_state.generated_pdfs = {}
                st.session_state.selected_customers = set()
                st.session_state.input_mode = None
                st.session_state.work_errors = []
                st.rerun()
        
        st.markdown("---")
        
        # 결과 테이블 (간소화 - 완료/실패만 표시)
        if completed_count > 0 or st.session_state.get('work_errors'):
            with st.expander(f"📋 처리 결과 ({completed_count}건 완료)", expanded=False):
                # 완료된 항목
                for idx in st.session_state.get('completed_customers', {}):
                    if idx < len(df):
                        row = df.iloc[idx]
                        if is_couple:
                            cust_name1 = row.get(name1_col, "고객1") if name1_col else "고객1"
                            cust_name2 = row.get(name2_col, "고객2") if name2_col else "고객2"
                            display_name = f"{cust_name1} & {cust_name2}"
                            filename = f"{cust_name1}_{cust_name2}_궁합.pdf"
                        else:
                            display_name = row.get(name_col, "고객") if name_col else "고객"
                            filename = f"{display_name}_운세.pdf"
                        
                        col_name, col_dl = st.columns([3, 1])
                        col_name.markdown(f"✅ **{display_name}**")
                        pdf_data = st.session_state.get('generated_pdfs', {}).get(idx)
                        if pdf_data:
                            col_dl.download_button("⬇️", pdf_data, filename, "application/pdf", key=f"dl_{idx}")
                
                # 실패한 항목 (강조 표시)
                for err in st.session_state.get('work_errors', []):
                    render_error_card(err.get('name', '알 수 없음'), err.get('error', '오류 발생'))
        
        st.markdown("---")
        
        # ===== 핵심 버튼 1개: 전체 생성 시작 =====
        is_processing = st.session_state.get('work_processing', False)
        
        if pending_count > 0:
            # 예상 시간 안내
            est_minutes = pending_count * 1  # 병렬 처리 후 약 1분/건
            st.caption(f"⏱️ 예상 소요 시간: 약 {est_minutes}분 ({pending_count}건 × 1분)")
            
            # 전체 생성 버튼 (처리 중이면 비활성화)
            button_text = "⏳ 처리 중..." if is_processing else f"🚀 전체 {pending_count}건 생성 시작"
            
            if st.button(button_text, type="primary", use_container_width=True, disabled=is_processing):
                st.session_state.work_processing = True
                st.session_state.work_errors = []
                st.session_state.work_start_time = time.time()
                
                # 전체 고객 자동 선택 (개별 선택 없음)
                pending_indices = [i for i in range(len(df)) if i not in st.session_state.get('completed_customers', {})]
                
                # 진행 상태 영역
                progress_container = st.container()
                with progress_container:
                    status_area = st.empty()
                    progress_card_area = st.empty()
                    current_detail = st.empty()
                
                for i, idx in enumerate(pending_indices):
                    row = df.iloc[idx]
                    
                    # 이름 결정
                    if is_couple:
                        cust_name1 = row.get(name1_col, "고객1") if name1_col else "고객1"
                        cust_name2 = row.get(name2_col, "고객2") if name2_col else "고객2"
                        display_name = f"{cust_name1} & {cust_name2}"
                        cover_name = f"{cust_name1}님 & {cust_name2}님"
                        current_svc_type = "couple"
                    else:
                        display_name = row.get(name_col, "고객") if name_col else "고객"
                        cover_name = f"{display_name}님"
                        current_svc_type = "single"
                    
                    # 진행 상태 표시 (업무 자동화 콘솔 스타일)
                    with progress_card_area:
                        render_progress_card(i, len(pending_indices), display_name)
                    current_detail.caption(f"📝 {display_name} - GPT 생성 중...")
                    
                    # 멱등성 체크
                    order_hash = generate_order_hash(row.to_dict(), selected_service['id'])
                    if is_already_generated(order_hash):
                        cached_pdf = st.session_state.get('pdf_hashes', {}).get(order_hash)
                        if cached_pdf:
                            if 'completed_customers' not in st.session_state:
                                st.session_state.completed_customers = {}
                            st.session_state.completed_customers[idx] = True
                            if 'generated_pdfs' not in st.session_state:
                                st.session_state.generated_pdfs = {}
                            st.session_state.generated_pdfs[idx] = cached_pdf
                            continue
                    
                    try:
                        # 서비스 설정
                        temp_service = selected_service.copy()
                        temp_service['service_type'] = current_svc_type
                        
                        # PDF 생성 (진행률은 내부에서 처리)
                        current_progress_bar = st.empty()
                        pdf_bytes = generate_pdf_with_progress(
                            row.to_dict(), temp_service, api_key,
                            current_progress_bar, current_detail,
                            custom_name=cover_name
                        )
                        current_progress_bar.empty()
                        
                        if pdf_bytes:
                            if 'completed_customers' not in st.session_state:
                                st.session_state.completed_customers = {}
                            st.session_state.completed_customers[idx] = True
                            if 'generated_pdfs' not in st.session_state:
                                st.session_state.generated_pdfs = {}
                            st.session_state.generated_pdfs[idx] = pdf_bytes
                            mark_as_generated(order_hash, pdf_bytes)
                            # 성공은 조용히 (토스트만)
                        else:
                            # 실패 기록
                            if 'work_errors' not in st.session_state:
                                st.session_state.work_errors = []
                            st.session_state.work_errors.append({
                                'name': display_name,
                                'error': 'PDF 생성 실패'
                            })
                    except Exception as e:
                        # 실패 기록 (사용자 친화적 메시지)
                        if 'work_errors' not in st.session_state:
                            st.session_state.work_errors = []
                        st.session_state.work_errors.append({
                            'name': display_name,
                            'error': str(e)
                        })
                
                # 완료 처리
                st.session_state.work_processing = False
                
                # 결과 표시
                with progress_card_area:
                    render_progress_card(len(pending_indices), len(pending_indices), "완료!")
                
                # 실패가 있으면 강조
                if st.session_state.get('work_errors'):
                    status_area.error(f"⚠️ {len(st.session_state.work_errors)}건 처리 실패 - 아래 목록 확인")
                    for err in st.session_state.work_errors:
                        render_error_card(err['name'], err['error'])
                else:
                    status_area.success("✅ 모든 처리가 완료되었습니다")
                
                time.sleep(1)
                st.rerun()
        else:
            if completed_count > 0:
                st.success("✅ 모든 고객 처리가 완료되었습니다")
                st.caption("위 '처리 결과'에서 PDF를 다운로드하세요")

# ===== 직접 입력 방식 =====
else:
    st.markdown("**👤 고객 정보 직접 입력** (최대 2명)")
    st.caption("💡 2명 입력 시 궁합/재회용 PDF 생성")
    
    # 초기화 버튼
    col_reset = st.columns([3, 1])
    with col_reset[1]:
        if st.button("🔄 초기화", key="reset_manual", use_container_width=True):
            # 모든 직접 입력 관련 세션 완전 삭제
            st.session_state.manual_completed = False
            st.session_state.manual_pdf = None
            # 입력 폼 키들도 삭제
            keys_to_delete = [k for k in list(st.session_state.keys()) if k.startswith('manual_')]
            for k in keys_to_delete:
                del st.session_state[k]
            st.rerun()
    
    # 고객 수 선택
    num_customers = st.radio("고객 수", [1, 2], horizontal=True, key="num_cust",
                            help="2명 입력 시 궁합/재회 등 합산 PDF 1개 생성")
    
    manual_customers = []
    
    for i in range(num_customers):
        st.markdown(f"**고객 {i+1}**")
        
        # 1행: 이름, 이메일
        row1 = st.columns(2)
        with row1[0]:
            name = st.text_input("이름", key=f"manual_name_{i}", placeholder="홍길동")
        with row1[1]:
            email = st.text_input("이메일", key=f"manual_email_{i}", placeholder="example@email.com")
        
        # 2행: 생년월일, 음력/양력
        row2 = st.columns([2, 1])
        with row2[0]:
            birth_date = st.date_input("생년월일", key=f"manual_birth_{i}",
                                      value=datetime(1990, 1, 1).date(),
                                      min_value=datetime(1920, 1, 1).date(),
                                      max_value=datetime(2025, 12, 31).date())
        with row2[1]:
            calendar_type = st.radio("음력/양력", ["양력", "음력"], horizontal=True, key=f"manual_cal_{i}")
        
        # 3행: 태어난 시간
        row3 = st.columns([1, 1, 1])
        with row3[0]:
            birth_hour = st.selectbox("시", list(range(1, 13)), index=8, key=f"manual_hour_{i}")
        with row3[1]:
            birth_min = st.selectbox("분", list(range(0, 60, 5)), index=0, key=f"manual_min_{i}")
        with row3[2]:
            ampm = st.radio("오전/오후", ["오전", "오후"], horizontal=True, key=f"manual_ampm_{i}")
        
        if name:
            # 시간 포맷팅
            birth_date_str = birth_date.strftime("%Y-%m-%d")
            birth_time_str = f"{ampm} {birth_hour}시 {birth_min:02d}분"
            
            manual_customers.append({
                "이름": name,
                "생년월일": birth_date_str,
                "음력양력": calendar_type,
                "태어난시간": birth_time_str,
                "이메일": email
            })
        
        if i < num_customers - 1:
            st.markdown("---")
    
    # 세션 초기화
    if 'manual_completed' not in st.session_state:
        st.session_state.manual_completed = False
    if 'manual_pdf' not in st.session_state:
        st.session_state.manual_pdf = None
    
    # 필수 입력 확인
    required_count = num_customers
    has_all_names = len(manual_customers) == required_count
    
    if has_all_names:
        st.markdown("---")
        
        # 1명 또는 2명에 따른 표시
        if num_customers == 1:
            display_name = manual_customers[0]['이름']
            cover_name = f"{display_name}님"  # 표지용: "홍길동님"
            combined_data = manual_customers[0]
        else:
            # 2명: 궁합/재회용 - 데이터 합치기
            display_name = f"{manual_customers[0]['이름']} & {manual_customers[1]['이름']}"
            cover_name = f"{manual_customers[0]['이름']}님 & {manual_customers[1]['이름']}님"  # 표지용: "홍길동님 & 김철수님"
            combined_data = {
                "고객1_이름": manual_customers[0]['이름'],
                "고객1_생년월일": manual_customers[0]['생년월일'],
                "고객1_음력양력": manual_customers[0]['음력양력'],
                "고객1_태어난시간": manual_customers[0]['태어난시간'],
                "고객1_이메일": manual_customers[0]['이메일'],
                "고객2_이름": manual_customers[1]['이름'],
                "고객2_생년월일": manual_customers[1]['생년월일'],
                "고객2_음력양력": manual_customers[1]['음력양력'],
                "고객2_태어난시간": manual_customers[1]['태어난시간'],
                "고객2_이메일": manual_customers[1]['이메일'],
            }
        
        st.markdown("**📋 입력된 고객**")
        
        # 상세 정보 표시
        for idx, cust in enumerate(manual_customers):
            info_text = f"**{cust['이름']}** | {cust['생년월일']} ({cust['음력양력']}) | {cust['태어난시간']}"
            st.caption(info_text)
        
        st.markdown("---")
        
        # 상태 표시
        is_done = st.session_state.manual_completed
        
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.write(f"**{display_name}**")
        with col2:
            if is_done:
                st.progress(1.0, text="100%")
            else:
                st.progress(0.0, text="대기")
        with col3:
            if is_done:
                st.markdown("✅")
        with col4:
            if is_done and st.session_state.manual_pdf:
                filename = f"{manual_customers[0]['이름']}_운세.pdf" if num_customers == 1 else f"{manual_customers[0]['이름']}_{manual_customers[1]['이름']}_궁합.pdf"
                st.download_button("⬇️", st.session_state.manual_pdf, filename,
                                  "application/pdf", key="dl_manual")
        
        st.markdown("---")
        
        if not is_done:
            if num_customers == 1:
                st.info(f"👤 1명 입력 → 1인용 PDF 생성")
            else:
                st.info(f"💑 2명 입력 → 궁합/재회용 PDF 생성")
            
            if st.button("🚀 PDF 생성", type="primary", use_container_width=True, key="gen_manual"):
                status_area = st.empty()
                current_progress_bar = st.empty()
                current_detail = st.empty()
                
                status_area.markdown(f"### 📝 {display_name} 생성 중...")
                
                # 서비스에 현재 유형 임시 설정
                temp_service = selected_service.copy()
                temp_service['service_type'] = 'couple' if num_customers == 2 else 'single'
                
                # PDF 생성 (2명이면 합친 데이터로)
                pdf_bytes = generate_pdf_with_progress(
                    combined_data, temp_service, api_key,
                    current_progress_bar, current_detail,
                    custom_name=cover_name
                )
                
                if pdf_bytes:
                    st.session_state.manual_completed = True
                    st.session_state.manual_pdf = pdf_bytes
                    st.toast(f"🔔 {display_name} 완료!")
                
                current_progress_bar.progress(1.0, text="100% 완료")
                time.sleep(0.3)
                
                status_area.markdown("### ✅ PDF 생성 완료!")
                current_progress_bar.empty()
                current_detail.empty()
                st.balloons()
                time.sleep(1)
                st.rerun()
    else:
        if num_customers == 1:
            st.warning("⚠️ 이름을 입력하세요.")
        else:
            st.warning("⚠️ 두 고객의 이름을 모두 입력하세요.")
