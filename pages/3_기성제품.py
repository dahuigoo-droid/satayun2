# -*- coding: utf-8 -*-
"""
📦 기성제품 - 엑셀 파일 기반
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="기성제품", page_icon="📦", layout="wide")

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
    prefix="std",
    product_type="기성상품",
    title="기성제품",
    subtitle="엑셀 파일 기반 · 대량 고객 처리용",
    icon="📦"
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
# PDF 생성 탭 - 엑셀 업로드 방식
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
    
    # 엑셀 업로드
    st.markdown("### 📊 엑셀 파일 업로드")
    rc = st.session_state[f'{PREFIX}_reset']
    uploaded = st.file_uploader("엑셀 파일 선택", type=['xlsx', 'xls'], key=f"excel_{rc}")
    
    if uploaded:
        try:
            df = pd.read_excel(uploaded)
            st.success(f"✅ {len(df)}명 로드됨")
            st.session_state[f'{PREFIX}_customers'] = df.to_dict('records')
            with st.expander("📋 데이터 미리보기", expanded=True):
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"파일 오류: {e}")
    
    st.markdown("---")
    
    # 고객 목록 및 PDF 생성
    customers = st.session_state[f'{PREFIX}_customers']
    if customers:
        render_customer_list(CONFIG, customers, selected_product)
        st.markdown("---")
        generate_pdfs(CONFIG, customers, selected_product)
    else:
        st.info("📥 엑셀 파일을 업로드하세요.")
