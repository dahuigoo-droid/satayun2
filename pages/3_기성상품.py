# -*- coding: utf-8 -*-
"""
📦 기성상품 페이지
- 상품 관리 (등록/수정/삭제)
- PDF 생성 (엑셀/TXT/직접입력)
- 디자인 설정
- 진행률 표시
"""

import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="기성상품", page_icon="📦", layout="wide")

from common import (
    check_login, show_user_info_sidebar, apply_common_css, init_session_state,
    is_admin, FONT_OPTIONS
)

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

st.title("📦 기성상품")
st.caption("대량 고객 처리용 · 단순 정보 기반")

# =====================================================
# 세션 상태 초기화
# =====================================================
if 'std_products' not in st.session_state:
    st.session_state.std_products = []
if 'std_view_id' not in st.session_state:
    st.session_state.std_view_id = None
if 'std_edit_mode' not in st.session_state:
    st.session_state.std_edit_mode = False
if 'std_new_mode' not in st.session_state:
    st.session_state.std_new_mode = False
if 'std_customers' not in st.session_state:
    st.session_state.std_customers = []
if 'std_selected_customers' not in st.session_state:
    st.session_state.std_selected_customers = set()
if 'std_progress' not in st.session_state:
    st.session_state.std_progress = {}
if 'std_completed' not in st.session_state:
    st.session_state.std_completed = set()

# =====================================================
# 탭 구성
# =====================================================
tab1, tab2 = st.tabs(["📦 상품 설정", "🚀 PDF 생성"])

# =====================================================
# 📦 상품 설정 탭
# =====================================================
with tab1:
    
    # ===== 새 상품 등록 모드 =====
    if st.session_state.std_new_mode:
        st.markdown("### ✏️ 새 상품 등록")
        
        new_name = st.text_input("상품명", key="new_std_name", placeholder="상품 이름을 입력하세요")
        
        col_ch, col_guide = st.columns(2)
        with col_ch:
            st.markdown("**📑 목차** (줄바꿈으로 구분)")
            new_chapters = st.text_area("목차", height=200, key="new_std_ch", label_visibility="collapsed", 
                                        placeholder="1. 총운\n2. 재물운\n3. 건강운\n...")
        with col_guide:
            st.markdown("**📜 AI 지침**")
            new_guideline = st.text_area("지침", height=200, key="new_std_guide", label_visibility="collapsed",
                                         placeholder="20년 경력 사주 전문가로서...\n친근하고 따뜻한 말투로...")
        
        # 폰트/디자인 설정
        with st.expander("⚙️ 폰트/디자인 설정", expanded=False):
            st.markdown("**📄 목표 페이지 수**")
            new_pages = st.number_input("목표 페이지", value=35, min_value=5, max_value=200, key="new_std_pages")
            
            st.markdown("**🔤 폰트 설정**")
            fcol1, fcol2, fcol3 = st.columns(3)
            with fcol1:
                new_font = st.selectbox("폰트", list(FONT_OPTIONS.keys()), key="new_std_font")
            with fcol2:
                new_line_height = st.slider("행간 %", 100, 300, 180, key="new_std_lh")
            with fcol3:
                new_letter_spacing = st.slider("자간 %", -5, 10, 0, key="new_std_ls")
            
            fcol4, fcol5, fcol6 = st.columns(3)
            with fcol4:
                new_title_size = st.number_input("대제목", value=30, min_value=12, max_value=48, key="new_std_title")
            with fcol5:
                new_subtitle_size = st.number_input("소제목", value=23, min_value=10, max_value=36, key="new_std_subtitle")
            with fcol6:
                new_body_size = st.number_input("본문", value=18, min_value=8, max_value=24, key="new_std_body")
            
            st.markdown("**📐 여백 설정 (mm)**")
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            with mcol1:
                new_mt = st.number_input("상단", value=25, min_value=10, max_value=50, key="new_std_mt")
            with mcol2:
                new_mb = st.number_input("하단", value=25, min_value=10, max_value=50, key="new_std_mb")
            with mcol3:
                new_ml = st.number_input("좌측", value=25, min_value=10, max_value=50, key="new_std_ml")
            with mcol4:
                new_mr = st.number_input("우측", value=25, min_value=10, max_value=50, key="new_std_mr")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 등록완료", type="primary", use_container_width=True):
                if new_name:
                    new_product = {
                        'id': len(st.session_state.std_products) + 1,
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
                        'margin_top': new_mt,
                        'margin_bottom': new_mb,
                        'margin_left': new_ml,
                        'margin_right': new_mr
                    }
                    st.session_state.std_products.append(new_product)
                    st.session_state.std_new_mode = False
                    st.toast("✅ 상품이 등록되었습니다!")
                    st.rerun()
                else:
                    st.warning("상품명을 입력하세요.")
        with col2:
            if st.button("❌ 취소", use_container_width=True):
                st.session_state.std_new_mode = False
                st.rerun()
    
    # ===== 상품 상세보기 모드 =====
    elif st.session_state.std_view_id:
        product = next((p for p in st.session_state.std_products if p['id'] == st.session_state.std_view_id), None)
        
        if product:
            # 뒤로가기
            if st.button("← 목록으로"):
                st.session_state.std_view_id = None
                st.session_state.std_edit_mode = False
                st.rerun()
            
            st.markdown("---")
            
            if st.session_state.std_edit_mode:
                # ===== 수정 모드 =====
                st.markdown("### ✏️ 상품 수정")
                
                edit_name = st.text_input("상품명", value=product['name'], key="edit_std_name")
                
                col_ch, col_guide = st.columns(2)
                with col_ch:
                    st.markdown("**📑 목차**")
                    edit_chapters = st.text_area("목차", value=product.get('chapters', ''), height=200, 
                                                  key="edit_std_ch", label_visibility="collapsed")
                with col_guide:
                    st.markdown("**📜 AI 지침**")
                    edit_guideline = st.text_area("지침", value=product.get('guideline', ''), height=200,
                                                   key="edit_std_guide", label_visibility="collapsed")
                
                with st.expander("⚙️ 폰트/디자인 설정", expanded=False):
                    edit_pages = st.number_input("목표 페이지", value=product.get('target_pages', 35), key="edit_std_pages")
                    
                    fcol1, fcol2, fcol3 = st.columns(3)
                    with fcol1:
                        font_list = list(FONT_OPTIONS.keys())
                        current_font = product.get('font_family', '나눔고딕')
                        font_idx = font_list.index(current_font) if current_font in font_list else 0
                        edit_font = st.selectbox("폰트", font_list, index=font_idx, key="edit_std_font")
                    with fcol2:
                        edit_line_height = st.slider("행간 %", 100, 300, product.get('line_height', 180), key="edit_std_lh")
                    with fcol3:
                        edit_letter_spacing = st.slider("자간 %", -5, 10, product.get('letter_spacing', 0), key="edit_std_ls")
                    
                    fcol4, fcol5, fcol6 = st.columns(3)
                    with fcol4:
                        edit_title_size = st.number_input("대제목", value=product.get('font_size_title', 30), key="edit_std_title")
                    with fcol5:
                        edit_subtitle_size = st.number_input("소제목", value=product.get('font_size_subtitle', 23), key="edit_std_subtitle")
                    with fcol6:
                        edit_body_size = st.number_input("본문", value=product.get('font_size_body', 18), key="edit_std_body")
                    
                    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                    with mcol1:
                        edit_mt = st.number_input("상단", value=product.get('margin_top', 25), key="edit_std_mt")
                    with mcol2:
                        edit_mb = st.number_input("하단", value=product.get('margin_bottom', 25), key="edit_std_mb")
                    with mcol3:
                        edit_ml = st.number_input("좌측", value=product.get('margin_left', 25), key="edit_std_ml")
                    with mcol4:
                        edit_mr = st.number_input("우측", value=product.get('margin_right', 25), key="edit_std_mr")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 수정완료", type="primary", use_container_width=True):
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
                        product['margin_top'] = edit_mt
                        product['margin_bottom'] = edit_mb
                        product['margin_left'] = edit_ml
                        product['margin_right'] = edit_mr
                        
                        st.session_state.std_edit_mode = False
                        st.toast("✅ 수정되었습니다!")
                        st.rerun()
                with col2:
                    if st.button("❌ 취소", use_container_width=True):
                        st.session_state.std_edit_mode = False
                        st.rerun()
            
            else:
                # ===== 보기 모드 =====
                st.markdown(f"### 📦 {product['name']}")
                
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
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("✏️ 수정", use_container_width=True):
                        st.session_state.std_edit_mode = True
                        st.rerun()
                with col2:
                    if st.button("🗑️ 삭제", use_container_width=True):
                        st.session_state.std_products.remove(product)
                        st.session_state.std_view_id = None
                        st.toast("🗑️ 삭제되었습니다!")
                        st.rerun()
    
    # ===== 목록 모드 =====
    else:
        if st.button("➕ 새 상품 등록", type="primary"):
            st.session_state.std_new_mode = True
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.std_products:
            for product in st.session_state.std_products:
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(f"📦 {product['name']}", key=f"std_prod_{product['id']}", use_container_width=True):
                        st.session_state.std_view_id = product['id']
                        st.rerun()
                with col2:
                    st.caption(f"{product.get('target_pages', 35)}p")
        else:
            st.info("📭 등록된 상품이 없습니다.")

# =====================================================
# 🚀 PDF 생성 탭
# =====================================================
with tab2:
    
    # 상품 선택
    if not st.session_state.std_products:
        st.warning("⚠️ 먼저 '상품 설정' 탭에서 상품을 등록하세요.")
        st.stop()
    
    product_names = [p['name'] for p in st.session_state.std_products]
    selected_product_name = st.selectbox("📦 상품 선택", product_names, key="std_select_product")
    selected_product = next((p for p in st.session_state.std_products if p['name'] == selected_product_name), None)
    
    st.markdown("---")
    
    # ===== 입력 방식 선택 =====
    st.markdown("### 📥 고객 정보 입력")
    
    input_mode = st.radio(
        "입력 방식",
        ["📊 엑셀 업로드", "📄 TXT 업로드", "✍️ 직접 입력"],
        horizontal=True,
        key="std_input_mode"
    )
    
    st.markdown("---")
    
    # ===== 엑셀 업로드 =====
    if input_mode == "📊 엑셀 업로드":
        uploaded_excel = st.file_uploader("엑셀 파일 업로드 (.xlsx, .xls)", type=['xlsx', 'xls'], key="std_excel")
        
        if uploaded_excel:
            try:
                df = pd.read_excel(uploaded_excel)
                st.success(f"✅ {len(df)}명의 고객 정보 로드됨")
                st.session_state.std_customers = df.to_dict('records')
                
                with st.expander("📋 데이터 미리보기", expanded=True):
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"파일 오류: {e}")
    
    # ===== TXT 업로드 =====
    elif input_mode == "📄 TXT 업로드":
        st.caption("💡 파일명 = 고객명으로 매칭됩니다 (예: 홍길동.txt)")
        
        uploaded_txts = st.file_uploader("TXT 파일 업로드 (여러 개 가능)", type=['txt'], 
                                          accept_multiple_files=True, key="std_txt")
        
        if uploaded_txts:
            customers = []
            for txt_file in uploaded_txts:
                name = txt_file.name.replace('.txt', '')
                content = txt_file.read().decode('utf-8')
                customers.append({'이름': name, '본문': content})
            
            st.session_state.std_customers = customers
            st.success(f"✅ {len(customers)}개 파일 로드됨")
            
            with st.expander("📋 파일 목록"):
                for c in customers:
                    st.text(f"📄 {c['이름']}.txt ({len(c['본문'])}자)")
    
    # ===== 직접 입력 =====
    elif input_mode == "✍️ 직접 입력":
        st.markdown("**고객 정보 입력**")
        
        col1, col2 = st.columns(2)
        with col1:
            di_name = st.text_input("이름", key="std_di_name")
            di_birth = st.date_input("생년월일", key="std_di_birth")
            di_time = st.time_input("태어난 시간", key="std_di_time")
        with col2:
            di_lunar = st.radio("음력/양력", ["양력", "음력"], horizontal=True, key="std_di_lunar")
            di_gender = st.radio("성별", ["남", "여"], horizontal=True, key="std_di_gender")
            di_mbti = st.selectbox("MBTI", ["선택안함"] + ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", 
                                                          "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"], key="std_di_mbti")
            di_blood = st.selectbox("혈액형", ["선택안함", "A형", "B형", "O형", "AB형"], key="std_di_blood")
        
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
                st.session_state.std_customers.append(customer)
                st.toast(f"✅ {di_name}님 추가!")
                st.rerun()
            else:
                st.warning("이름을 입력하세요.")
    
    st.markdown("---")
    
    # ===== 고객 목록 & 체크박스 =====
    if st.session_state.std_customers:
        st.markdown("### 👥 고객 목록")
        
        col_all, col_reset = st.columns([1, 1])
        with col_all:
            select_all = st.checkbox("✅ 전체 선택", key="std_select_all")
            if select_all:
                st.session_state.std_selected_customers = set(range(len(st.session_state.std_customers)))
            else:
                # 전체 선택 해제 시 개별 선택 유지
                pass
        with col_reset:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.std_customers = []
                st.session_state.std_selected_customers = set()
                st.session_state.std_progress = {}
                st.session_state.std_completed = set()
                st.toast("🔄 초기화되었습니다!")
                st.rerun()
        
        st.markdown("---")
        
        # 고객별 행
        for idx, customer in enumerate(st.session_state.std_customers):
            col_check, col_name, col_progress, col_download = st.columns([0.5, 2, 2, 1])
            
            with col_check:
                is_checked = idx in st.session_state.std_selected_customers
                if st.checkbox("", value=is_checked or select_all, key=f"std_chk_{idx}", label_visibility="collapsed"):
                    st.session_state.std_selected_customers.add(idx)
                else:
                    st.session_state.std_selected_customers.discard(idx)
            
            with col_name:
                name = customer.get('이름', customer.get('고객명', f'고객{idx+1}'))
                st.write(f"👤 {name}")
            
            with col_progress:
                progress = st.session_state.std_progress.get(idx, 0)
                st.progress(progress / 100)
                if idx in st.session_state.std_completed:
                    st.caption("✅ 완료")
                elif progress > 0:
                    st.caption(f"⏳ {progress}%")
            
            with col_download:
                if idx in st.session_state.std_completed:
                    st.button("📥", key=f"std_dl_{idx}", help="다운로드")
        
        st.markdown("---")
        
        # ===== 디자인 설정 =====
        with st.expander("🎨 디자인 설정", expanded=False):
            st.markdown("**📊 그래프 스타일**")
            graph_style = st.radio("", ["막대", "원형", "레이더", "게이지"], horizontal=True, key="std_graph")
            
            st.markdown("**📦 박스/카드 스타일**")
            box_style = st.radio("", ["심플", "모던", "클래식", "화려함"], horizontal=True, key="std_box")
            
            st.markdown("**🎨 컬러 테마**")
            color_theme = st.radio("", ["🔴 빨강", "🟡 금색", "🔵 파랑", "🟣 보라", "🟢 녹색"], horizontal=True, key="std_color")
            
            st.markdown("**📍 삽입 위치**")
            col_ins1, col_ins2 = st.columns(2)
            with col_ins1:
                ins_cover = st.checkbox("☑️ 표지", value=True, key="std_ins_cover")
                ins_zodiac = st.checkbox("☑️ 띠 이미지", value=True, key="std_ins_zodiac")
            with col_ins2:
                ins_graph = st.checkbox("☑️ 종합 그래프", value=True, key="std_ins_graph")
                ins_monthly = st.checkbox("☑️ 월별 그래프", value=True, key="std_ins_monthly")
        
        st.markdown("---")
        
        # ===== PDF 생성 버튼 =====
        selected_count = len(st.session_state.std_selected_customers)
        
        if selected_count > 0:
            if st.button(f"🚀 PDF 생성 ({selected_count}명)", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, idx in enumerate(st.session_state.std_selected_customers):
                    customer = st.session_state.std_customers[idx]
                    name = customer.get('이름', customer.get('고객명', f'고객{idx+1}'))
                    
                    status_text.text(f"⏳ {name}님 PDF 생성 중... ({i+1}/{selected_count})")
                    
                    # 진행률 시뮬레이션
                    for step in [20, 40, 60, 80, 100]:
                        st.session_state.std_progress[idx] = step
                        progress_bar.progress((i + step/100) / selected_count)
                        time.sleep(0.1)
                    
                    st.session_state.std_completed.add(idx)
                
                progress_bar.progress(1.0)
                status_text.text(f"✅ {selected_count}명 PDF 생성 완료!")
                st.balloons()
                st.rerun()
        else:
            st.button("🚀 PDF 생성 (0명 선택됨)", type="secondary", disabled=True, use_container_width=True)
    
    else:
        st.info("📥 위에서 고객 정보를 입력하세요.")
