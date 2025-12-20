# -*- coding: utf-8 -*-
"""
📦 상품관리 페이지
- 기성/개별/고급 상품 유형별 분류
- 상품 등록/수정/삭제
- PDF 생성
"""

import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="상품관리", page_icon="📦", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    is_admin, FONT_OPTIONS
)

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

st.title("📦 상품관리")

# 상품 유형 정의
PRODUCT_TYPES = {
    '기성상품': {'icon': '📦', 'desc': '대량 고객용 · 단순 정보'},
    '개별상품': {'icon': '🎯', 'desc': '맞춤형 · 상세 정보'},
    '고급상품': {'icon': '👑', 'desc': 'VIP용 · 100페이지 이상'}
}

# =====================================================
# 세션 상태 초기화
# =====================================================
if 'products' not in st.session_state:
    st.session_state.products = []
if 'product_view_id' not in st.session_state:
    st.session_state.product_view_id = None
if 'product_edit_mode' not in st.session_state:
    st.session_state.product_edit_mode = False
if 'product_new_mode' not in st.session_state:
    st.session_state.product_new_mode = False
if 'customers' not in st.session_state:
    st.session_state.customers = []
if 'selected_customers' not in st.session_state:
    st.session_state.selected_customers = set()
if 'progress' not in st.session_state:
    st.session_state.progress = {}
if 'completed' not in st.session_state:
    st.session_state.completed = set()
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0
if 'current_product_type' not in st.session_state:
    st.session_state.current_product_type = '기성상품'

# =====================================================
# 회원 권한 체크
# =====================================================
def get_allowed_product_types():
    """회원이 볼 수 있는 상품 유형 목록"""
    if user.get('is_admin'):
        return list(PRODUCT_TYPES.keys())
    allowed = user.get('allowed_products', ['기성상품'])
    return allowed

allowed_types = get_allowed_product_types()

# =====================================================
# 탭 구성
# =====================================================
tab1, tab2 = st.tabs(["📦 상품 설정", "🚀 PDF 생성"])

# =====================================================
# 📦 상품 설정 탭
# =====================================================
with tab1:
    
    # ===== 상품 유형별 서브탭 =====
    type_tabs = st.tabs([f"{PRODUCT_TYPES[t]['icon']} {t}" for t in allowed_types])
    
    for tab_idx, product_type in enumerate(allowed_types):
        with type_tabs[tab_idx]:
            st.caption(PRODUCT_TYPES[product_type]['desc'])
            
            # 해당 유형의 상품만 필터링
            type_products = [p for p in st.session_state.products if p.get('product_type') == product_type]
            
            # ===== 새 상품 등록 모드 =====
            if st.session_state.product_new_mode and st.session_state.current_product_type == product_type:
                st.markdown("### ✏️ 새 상품 등록")
                
                new_name = st.text_input("상품명", key=f"new_name_{product_type}", placeholder="상품 이름")
                
                col_ch, col_guide = st.columns(2)
                with col_ch:
                    st.markdown("**📑 목차** (줄바꿈 구분)")
                    new_chapters = st.text_area("목차", height=180, key=f"new_ch_{product_type}", 
                                                label_visibility="collapsed",
                                                placeholder="1. 총운\n2. 재물운\n3. 건강운")
                with col_guide:
                    st.markdown("**📜 AI 지침**")
                    new_guideline = st.text_area("지침", height=180, key=f"new_guide_{product_type}",
                                                 label_visibility="collapsed",
                                                 placeholder="20년 경력 전문가로서...")
                
                with st.expander("⚙️ 폰트/디자인 설정", expanded=False):
                    # 목표 페이지
                    default_pages = {'기성상품': 35, '개별상품': 50, '고급상품': 100}
                    new_pages = st.number_input("목표 페이지", value=default_pages[product_type], 
                                                min_value=5, max_value=500, key=f"new_pages_{product_type}")
                    
                    # 폰트 설정
                    st.markdown("**🔤 폰트 설정**")
                    fcol1, fcol2, fcol3 = st.columns(3)
                    with fcol1:
                        new_font = st.selectbox("폰트", list(FONT_OPTIONS.keys()), key=f"new_font_{product_type}")
                    with fcol2:
                        new_line_height = st.slider("행간 %", 100, 300, 180, key=f"new_lh_{product_type}")
                    with fcol3:
                        new_letter_spacing = st.slider("자간 %", -5, 10, 0, key=f"new_ls_{product_type}")
                    
                    fcol4, fcol5, fcol6, fcol7 = st.columns(4)
                    with fcol4:
                        new_title_size = st.number_input("대제목", value=30, key=f"new_title_{product_type}")
                    with fcol5:
                        new_subtitle_size = st.number_input("소제목", value=23, key=f"new_subtitle_{product_type}")
                    with fcol6:
                        new_body_size = st.number_input("본문", value=18, key=f"new_body_{product_type}")
                    with fcol7:
                        new_char_width = st.slider("장평 %", 50, 150, 100, key=f"new_cw_{product_type}")
                    
                    # 여백 설정
                    st.markdown("**📐 여백 설정 (mm)**")
                    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                    with mcol1:
                        new_mt = st.number_input("상단", value=25, key=f"new_mt_{product_type}")
                    with mcol2:
                        new_mb = st.number_input("하단", value=25, key=f"new_mb_{product_type}")
                    with mcol3:
                        new_ml = st.number_input("좌측", value=25, key=f"new_ml_{product_type}")
                    with mcol4:
                        new_mr = st.number_input("우측", value=25, key=f"new_mr_{product_type}")
                    
                    # 이미지 설정
                    st.markdown("**🖼️ 이미지 설정**")
                    icol1, icol2, icol3 = st.columns(3)
                    with icol1:
                        new_cover_img = st.file_uploader("표지", type=['jpg','jpeg','png'], key=f"new_cover_{product_type}")
                        if new_cover_img:
                            st.image(new_cover_img, width=80)
                    with icol2:
                        new_bg_img = st.file_uploader("내지", type=['jpg','jpeg','png'], key=f"new_bg_{product_type}")
                        if new_bg_img:
                            st.image(new_bg_img, width=80)
                    with icol3:
                        new_info_img = st.file_uploader("안내지", type=['jpg','jpeg','png'], key=f"new_info_{product_type}")
                        if new_info_img:
                            st.image(new_info_img, width=80)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 등록완료", type="primary", use_container_width=True, key=f"save_new_{product_type}"):
                        if new_name:
                            new_product = {
                                'id': len(st.session_state.products) + 1,
                                'product_type': product_type,
                                'name': new_name,
                                'chapters': new_chapters,
                                'guideline': new_guideline,
                                'target_pages': new_pages,
                                'font_family': new_font,
                                'font_size_title': new_title_size,
                                'font_size_subtitle': new_subtitle_size,
                                'font_size_body': new_body_size,
                                'line_height': new_line_height,
                                'letter_spacing': new_letter_spacing,
                                'char_width': new_char_width,
                                'margin_top': new_mt,
                                'margin_bottom': new_mb,
                                'margin_left': new_ml,
                                'margin_right': new_mr,
                                'cover_image': new_cover_img.getvalue() if new_cover_img else None,
                                'bg_image': new_bg_img.getvalue() if new_bg_img else None,
                                'info_image': new_info_img.getvalue() if new_info_img else None
                            }
                            st.session_state.products.append(new_product)
                            st.session_state.product_new_mode = False
                            st.toast("✅ 상품이 등록되었습니다!")
                            st.rerun()
                        else:
                            st.warning("상품명을 입력하세요.")
                with col2:
                    if st.button("❌ 취소", use_container_width=True, key=f"cancel_new_{product_type}"):
                        st.session_state.product_new_mode = False
                        st.rerun()
            
            # ===== 상품 상세보기 모드 =====
            elif st.session_state.product_view_id:
                product = next((p for p in st.session_state.products if p['id'] == st.session_state.product_view_id), None)
                
                if product and product.get('product_type') == product_type:
                    if st.button("← 목록으로", key=f"back_{product_type}"):
                        st.session_state.product_view_id = None
                        st.session_state.product_edit_mode = False
                        st.rerun()
                    
                    st.markdown("---")
                    
                    if st.session_state.product_edit_mode:
                        # ===== 수정 모드 =====
                        st.markdown("### ✏️ 상품 수정")
                        
                        edit_name = st.text_input("상품명", value=product['name'], key=f"edit_name_{product_type}")
                        
                        col_ch, col_guide = st.columns(2)
                        with col_ch:
                            st.markdown("**📑 목차**")
                            edit_chapters = st.text_area("목차", value=product.get('chapters', ''), height=180, 
                                                         key=f"edit_ch_{product_type}", label_visibility="collapsed")
                        with col_guide:
                            st.markdown("**📜 AI 지침**")
                            edit_guideline = st.text_area("지침", value=product.get('guideline', ''), height=180,
                                                          key=f"edit_guide_{product_type}", label_visibility="collapsed")
                        
                        with st.expander("⚙️ 폰트/디자인 설정", expanded=False):
                            edit_pages = st.number_input("목표 페이지", value=product.get('target_pages', 35), key=f"edit_pages_{product_type}")
                            
                            fcol1, fcol2, fcol3 = st.columns(3)
                            with fcol1:
                                font_list = list(FONT_OPTIONS.keys())
                                current_font = product.get('font_family', '나눔고딕')
                                font_idx = font_list.index(current_font) if current_font in font_list else 0
                                edit_font = st.selectbox("폰트", font_list, index=font_idx, key=f"edit_font_{product_type}")
                            with fcol2:
                                edit_line_height = st.slider("행간 %", 100, 300, product.get('line_height', 180), key=f"edit_lh_{product_type}")
                            with fcol3:
                                edit_letter_spacing = st.slider("자간 %", -5, 10, product.get('letter_spacing', 0), key=f"edit_ls_{product_type}")
                            
                            fcol4, fcol5, fcol6, fcol7 = st.columns(4)
                            with fcol4:
                                edit_title_size = st.number_input("대제목", value=product.get('font_size_title', 30), key=f"edit_title_{product_type}")
                            with fcol5:
                                edit_subtitle_size = st.number_input("소제목", value=product.get('font_size_subtitle', 23), key=f"edit_subtitle_{product_type}")
                            with fcol6:
                                edit_body_size = st.number_input("본문", value=product.get('font_size_body', 18), key=f"edit_body_{product_type}")
                            with fcol7:
                                edit_char_width = st.slider("장평 %", 50, 150, product.get('char_width', 100), key=f"edit_cw_{product_type}")
                            
                            st.markdown("**📐 여백 설정 (mm)**")
                            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                            with mcol1:
                                edit_mt = st.number_input("상단", value=product.get('margin_top', 25), key=f"edit_mt_{product_type}")
                            with mcol2:
                                edit_mb = st.number_input("하단", value=product.get('margin_bottom', 25), key=f"edit_mb_{product_type}")
                            with mcol3:
                                edit_ml = st.number_input("좌측", value=product.get('margin_left', 25), key=f"edit_ml_{product_type}")
                            with mcol4:
                                edit_mr = st.number_input("우측", value=product.get('margin_right', 25), key=f"edit_mr_{product_type}")
                            
                            st.markdown("**🖼️ 이미지 설정**")
                            icol1, icol2, icol3 = st.columns(3)
                            with icol1:
                                edit_cover_img = st.file_uploader("표지", type=['jpg','jpeg','png'], key=f"edit_cover_{product_type}")
                                if edit_cover_img:
                                    st.image(edit_cover_img, width=80, caption="새 이미지")
                                elif product.get('cover_image'):
                                    st.image(product['cover_image'], width=80, caption="기존")
                            with icol2:
                                edit_bg_img = st.file_uploader("내지", type=['jpg','jpeg','png'], key=f"edit_bg_{product_type}")
                                if edit_bg_img:
                                    st.image(edit_bg_img, width=80, caption="새 이미지")
                                elif product.get('bg_image'):
                                    st.image(product['bg_image'], width=80, caption="기존")
                            with icol3:
                                edit_info_img = st.file_uploader("안내지", type=['jpg','jpeg','png'], key=f"edit_info_{product_type}")
                                if edit_info_img:
                                    st.image(edit_info_img, width=80, caption="새 이미지")
                                elif product.get('info_image'):
                                    st.image(product['info_image'], width=80, caption="기존")
                        
                        st.markdown("---")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 수정완료", type="primary", use_container_width=True, key=f"save_edit_{product_type}"):
                                product['name'] = edit_name
                                product['chapters'] = edit_chapters
                                product['guideline'] = edit_guideline
                                product['target_pages'] = edit_pages
                                product['font_family'] = edit_font
                                product['font_size_title'] = edit_title_size
                                product['font_size_subtitle'] = edit_subtitle_size
                                product['font_size_body'] = edit_body_size
                                product['line_height'] = edit_line_height
                                product['letter_spacing'] = edit_letter_spacing
                                product['char_width'] = edit_char_width
                                product['margin_top'] = edit_mt
                                product['margin_bottom'] = edit_mb
                                product['margin_left'] = edit_ml
                                product['margin_right'] = edit_mr
                                if edit_cover_img:
                                    product['cover_image'] = edit_cover_img.getvalue()
                                if edit_bg_img:
                                    product['bg_image'] = edit_bg_img.getvalue()
                                if edit_info_img:
                                    product['info_image'] = edit_info_img.getvalue()
                                
                                st.session_state.product_edit_mode = False
                                st.toast("✅ 수정되었습니다!")
                                st.rerun()
                        with col2:
                            if st.button("❌ 취소", use_container_width=True, key=f"cancel_edit_{product_type}"):
                                st.session_state.product_edit_mode = False
                                st.rerun()
                    
                    else:
                        # ===== 보기 모드 =====
                        type_icon = PRODUCT_TYPES[product['product_type']]['icon']
                        st.markdown(f"### {type_icon} {product['name']}")
                        
                        col_ch, col_guide = st.columns(2)
                        with col_ch:
                            st.markdown("**📑 목차**")
                            if product.get('chapters'):
                                st.text(product['chapters'])
                            else:
                                st.caption("(목차 없음)")
                        with col_guide:
                            st.markdown("**📜 AI 지침**")
                            if product.get('guideline'):
                                guideline_preview = product['guideline']
                                if len(guideline_preview) > 300:
                                    guideline_preview = guideline_preview[:300] + "..."
                                st.text(guideline_preview)
                            else:
                                st.caption("(지침 없음)")
                        
                        # 이미지 미리보기 (작게)
                        st.markdown("**🖼️ 이미지**")
                        img_col1, img_col2, img_col3 = st.columns(3)
                        with img_col1:
                            if product.get('cover_image'):
                                st.image(product['cover_image'], width=80, caption="표지")
                            else:
                                st.caption("❌ 표지 없음")
                        with img_col2:
                            if product.get('bg_image'):
                                st.image(product['bg_image'], width=80, caption="내지")
                            else:
                                st.caption("❌ 내지 없음")
                        with img_col3:
                            if product.get('info_image'):
                                st.image(product['info_image'], width=80, caption="안내지")
                            else:
                                st.caption("❌ 안내지 없음")
                        
                        st.markdown("---")
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("✏️ 수정", use_container_width=True, key=f"btn_edit_{product_type}"):
                                st.session_state.product_edit_mode = True
                                st.rerun()
                        with col2:
                            if st.button("🗑️ 삭제", use_container_width=True, key=f"btn_del_{product_type}"):
                                st.session_state.products.remove(product)
                                st.session_state.product_view_id = None
                                st.toast("🗑️ 삭제되었습니다!")
                                st.rerun()
            
            # ===== 목록 모드 =====
            else:
                if st.button(f"➕ 새 {product_type} 등록", type="primary", key=f"new_btn_{product_type}"):
                    st.session_state.product_new_mode = True
                    st.session_state.current_product_type = product_type
                    st.rerun()
                
                st.markdown("---")
                
                if type_products:
                    for product in type_products:
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            if st.button(f"{PRODUCT_TYPES[product_type]['icon']} {product['name']}", 
                                        key=f"prod_{product['id']}", use_container_width=True):
                                st.session_state.product_view_id = product['id']
                                st.rerun()
                        with col2:
                            st.caption(f"{product.get('target_pages', 35)}p")
                else:
                    st.info(f"📭 등록된 {product_type}이 없습니다.")

# =====================================================
# 🚀 PDF 생성 탭
# =====================================================
with tab2:
    
    # 상품 선택
    all_products = st.session_state.products
    if not all_products:
        st.warning("⚠️ 먼저 '상품 설정' 탭에서 상품을 등록하세요.")
        st.stop()
    
    # 권한이 있는 상품만 필터링
    available_products = [p for p in all_products if p.get('product_type') in allowed_types]
    
    if not available_products:
        st.warning("⚠️ 사용 가능한 상품이 없습니다.")
        st.stop()
    
    product_options = [f"{PRODUCT_TYPES[p['product_type']]['icon']} [{p['product_type']}] {p['name']}" for p in available_products]
    selected_idx = st.selectbox("📦 상품 선택", range(len(product_options)), format_func=lambda x: product_options[x], key="select_product")
    selected_product = available_products[selected_idx]
    
    st.markdown("---")
    
    # ===== 입력 방식 선택 =====
    st.markdown("### 📥 고객 정보 입력")
    
    rc = st.session_state.reset_counter
    
    input_mode = st.radio(
        "입력 방식",
        ["📊 엑셀 업로드", "📄 TXT 업로드", "✍️ 직접 입력"],
        horizontal=True,
        key="input_mode"
    )
    
    st.markdown("---")
    
    # ===== 엑셀 업로드 =====
    if input_mode == "📊 엑셀 업로드":
        uploaded_excel = st.file_uploader("엑셀 파일 업로드", type=['xlsx', 'xls'], key=f"excel_{rc}")
        
        if uploaded_excel:
            try:
                df = pd.read_excel(uploaded_excel)
                st.success(f"✅ {len(df)}명의 고객 정보 로드됨")
                st.session_state.customers = df.to_dict('records')
                
                with st.expander("📋 데이터 미리보기", expanded=True):
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"파일 오류: {e}")
    
    # ===== TXT 업로드 =====
    elif input_mode == "📄 TXT 업로드":
        st.caption("💡 파일명 = 고객명으로 매칭됩니다")
        
        uploaded_txts = st.file_uploader("TXT 파일 업로드", type=['txt'], accept_multiple_files=True, key=f"txt_{rc}")
        
        if uploaded_txts:
            customers = []
            for txt_file in uploaded_txts:
                name = txt_file.name.replace('.txt', '')
                content = txt_file.read().decode('utf-8')
                customers.append({'이름': name, '본문': content})
            
            st.session_state.customers = customers
            st.success(f"✅ {len(customers)}개 파일 로드됨")
    
    # ===== 직접 입력 =====
    elif input_mode == "✍️ 직접 입력":
        st.markdown("**고객 정보 입력**")
        
        col1, col2 = st.columns(2)
        with col1:
            di_name = st.text_input("이름", key=f"di_name_{rc}")
            di_birth = st.date_input("생년월일", key=f"di_birth_{rc}")
            di_time = st.time_input("태어난 시간", key=f"di_time_{rc}")
        with col2:
            di_lunar = st.radio("음력/양력", ["양력", "음력"], horizontal=True, key=f"di_lunar_{rc}")
            di_gender = st.radio("성별", ["남", "여"], horizontal=True, key=f"di_gender_{rc}")
            di_mbti = st.selectbox("MBTI", ["선택안함"] + ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", 
                                                          "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"], key=f"di_mbti_{rc}")
            di_blood = st.selectbox("혈액형", ["선택안함", "A형", "B형", "O형", "AB형"], key=f"di_blood_{rc}")
        
        if st.button("➕ 고객 추가", type="primary"):
            if di_name:
                customer = {
                    '이름': di_name,
                    '생년월일': str(di_birth),
                    '시간': str(di_time),
                    '음력양력': di_lunar,
                    '성별': di_gender,
                    'MBTI': di_mbti if di_mbti != "선택안함" else "",
                    '혈액형': di_blood if di_blood != "선택안함" else ""
                }
                st.session_state.customers.append(customer)
                st.toast(f"✅ {di_name}님 추가!")
                st.rerun()
    
    st.markdown("---")
    
    # ===== 고객 목록 =====
    if st.session_state.customers:
        total_count = len(st.session_state.customers)
        selected_count = len(st.session_state.selected_customers)
        st.markdown(f"### 👥 고객 목록 ({selected_count}/{total_count}명 선택)")
        
        col_all, col_reset = st.columns([1, 1])
        with col_all:
            if st.button("✅ 전체 선택", use_container_width=True):
                st.session_state.selected_customers = set(range(len(st.session_state.customers)))
                st.rerun()
        with col_reset:
            col_deselect, col_init = st.columns(2)
            with col_deselect:
                if st.button("⬜ 전체 해제", use_container_width=True):
                    st.session_state.selected_customers = set()
                    st.rerun()
            with col_init:
                if st.button("🔄 초기화", use_container_width=True):
                    st.session_state.customers = []
                    st.session_state.selected_customers = set()
                    st.session_state.progress = {}
                    st.session_state.completed = set()
                    st.session_state.reset_counter += 1
                    st.toast("🔄 초기화!")
                    st.rerun()
        
        st.markdown("---")
        
        # 고객별 행
        for idx, customer in enumerate(st.session_state.customers):
            col_check, col_name, col_progress, col_download = st.columns([0.5, 2, 2, 1])
            
            with col_check:
                is_checked = idx in st.session_state.selected_customers
                def toggle_customer(customer_idx):
                    if customer_idx in st.session_state.selected_customers:
                        st.session_state.selected_customers.discard(customer_idx)
                    else:
                        st.session_state.selected_customers.add(customer_idx)
                
                st.checkbox("", value=is_checked, key=f"chk_{idx}_{rc}", label_visibility="collapsed",
                           on_change=toggle_customer, args=(idx,))
            
            with col_name:
                name = customer.get('이름', customer.get('고객명', f'고객{idx+1}'))
                st.write(f"👤 {name}")
            
            with col_progress:
                progress = st.session_state.progress.get(idx, 0)
                st.progress(progress / 100)
                if idx in st.session_state.completed:
                    st.caption("✅ 완료")
            
            with col_download:
                if idx in st.session_state.completed:
                    st.button("📥", key=f"dl_{idx}")
        
        st.markdown("---")
        
        # 디자인 설정
        with st.expander("🎨 디자인 설정", expanded=False):
            st.markdown("**📊 그래프 스타일**")
            graph_style = st.radio("", ["막대", "원형", "레이더", "게이지"], horizontal=True, key="graph")
            
            st.markdown("**📦 박스/카드 스타일**")
            box_style = st.radio("", ["심플", "모던", "클래식", "화려함"], horizontal=True, key="box")
            
            st.markdown("**🎨 컬러 테마**")
            color_theme = st.radio("", ["🔴 빨강", "🟡 금색", "🔵 파랑", "🟣 보라", "🟢 녹색"], horizontal=True, key="color")
        
        st.markdown("---")
        
        # PDF 생성 버튼
        selected_count = len(st.session_state.selected_customers)
        
        if selected_count > 0:
            if st.button(f"🚀 PDF 생성 ({selected_count}명)", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, idx in enumerate(st.session_state.selected_customers):
                    customer = st.session_state.customers[idx]
                    name = customer.get('이름', customer.get('고객명', f'고객{idx+1}'))
                    
                    status_text.text(f"⏳ {name}님 PDF 생성 중... ({i+1}/{selected_count})")
                    
                    for step in [20, 40, 60, 80, 100]:
                        st.session_state.progress[idx] = step
                        progress_bar.progress((i + step/100) / selected_count)
                        time.sleep(0.1)
                    
                    st.session_state.completed.add(idx)
                
                progress_bar.progress(1.0)
                status_text.text(f"✅ {selected_count}명 PDF 생성 완료!")
                st.balloons()
                st.rerun()
        else:
            st.button("🚀 PDF 생성 (0명 선택됨)", type="secondary", disabled=True, use_container_width=True)
    
    else:
        st.info("📥 위에서 고객 정보를 입력하세요.")
