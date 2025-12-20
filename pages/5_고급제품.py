# -*- coding: utf-8 -*-
"""
👑 고급제품 - TXT 파일 기반
"""

import streamlit as st
import os

st.set_page_config(page_title="고급제품", page_icon="👑", layout="wide")

from common import check_login, show_user_info_sidebar, apply_common_css, init_session_state
from services import get_services_by_category
from product_utils import (
    ProductConfig, init_product_session,
    render_new_product_form, render_product_list, render_product_detail,
    render_customer_list, generate_pdfs
)

# 초기화
init_session_state()
apply_common_css()
user = check_login()
show_user_info_sidebar()

# 설정
CONFIG = ProductConfig(
    prefix="prm",
    product_type="고급상품",
    title="고급제품",
    subtitle="TXT 파일 기반 · VIP 대용량",
    icon="👑"
)

init_product_session(CONFIG.prefix)
PREFIX = CONFIG.prefix

st.title(f"{CONFIG.icon} {CONFIG.title}")
st.caption(CONFIG.subtitle)

# =====================================================
# 탭 구성
# =====================================================
tab1, tab2 = st.tabs(["⚙️ 상품 설정", "🚀 PDF 생성"])

# =====================================================
# 상품 설정 탭
# =====================================================
with tab1:
    products = get_services_by_category(CONFIG.product_type)
    
    if st.session_state[f'{PREFIX}_new_mode']:
        render_new_product_form(CONFIG)
    elif st.session_state[f'{PREFIX}_view_id']:
        product = next((p for p in products if p['id'] == st.session_state[f'{PREFIX}_view_id']), None)
        if product:
            render_product_detail(CONFIG, product)
        else:
            st.session_state[f'{PREFIX}_view_id'] = None
            st.rerun()
    else:
        render_product_list(CONFIG, products)

# =====================================================
# PDF 생성 탭 - TXT 업로드 방식
# =====================================================
with tab2:
    products = get_services_by_category(CONFIG.product_type)
    
    if not products:
        st.warning("⚠️ 먼저 '상품 설정' 탭에서 상품을 등록하세요.")
        st.stop()
    
    # 상품 선택
    product_names = [f"{CONFIG.icon} {p['name']}" for p in products]
    selected_idx = st.selectbox("상품 선택", range(len(products)), format_func=lambda x: product_names[x])
    selected_product = products[selected_idx]
    
    st.markdown("---")
    
    # TXT 파일 업로드
    st.markdown("### 📄 TXT 파일 업로드")
    st.caption("파일명 = 고객명 (예: 홍길동.txt)")
    
    rc = st.session_state[f'{PREFIX}_reset']
    uploaded_files = st.file_uploader(
        "TXT 파일 선택 (여러 개 가능)", 
        type=['txt'], 
        accept_multiple_files=True,
        key=f"txt_{rc}"
    )
    
    if uploaded_files:
        new_customers = []
        for f in uploaded_files:
            try:
                content = f.read().decode('utf-8')
                name = os.path.splitext(f.name)[0]
                new_customers.append({
                    '이름': name,
                    '파일명': f.name,
                    '내용': content,
                    '글자수': len(content),
                    '상세정보': content  # GPT에 전달할 내용
                })
            except Exception as e:
                st.warning(f"⚠️ {f.name} 로드 실패: {e}")
        
        if new_customers:
            st.session_state[f'{PREFIX}_customers'] = new_customers
            st.success(f"✅ {len(new_customers)}개 파일 로드됨")
            
            with st.expander("📋 파일 목록", expanded=True):
                for c in new_customers:
                    st.caption(f"📄 {c['파일명']} ({c['글자수']:,}자)")
    
    st.markdown("---")
    
    # 고객 목록 및 PDF 생성
    customers = st.session_state[f'{PREFIX}_customers']
    if customers:
        render_customer_list(CONFIG, customers, selected_product)
        st.markdown("---")
        generate_pdfs(CONFIG, customers, selected_product)
    else:
        st.info("📄 TXT 파일을 업로드하세요.")
