# -*- coding: utf-8 -*-
"""
🎯 개별제품 - 직접 입력 기반
"""

import streamlit as st
from datetime import date

st.set_page_config(page_title="개별제품", page_icon="🎯", layout="wide")

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
    prefix="ind",
    product_type="개별상품",
    title="개별제품",
    subtitle="고객 정보 직접 입력 · 맞춤형",
    icon="🎯"
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
# PDF 생성 탭 - 직접 입력 방식
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
    
    # 고객 정보 입력
    st.markdown("### ✍️ 고객 정보 입력")
    
    with st.form(f"{PREFIX}_customer_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름 *", placeholder="홍길동")
            birth = st.date_input("생년월일 *", value=date(1990, 1, 1))
            time_input = st.text_input("태어난 시간", placeholder="오전 6시")
        with col2:
            calendar = st.radio("음력/양력", ["양력", "음력"], horizontal=True)
            gender = st.radio("성별", ["남성", "여성"], horizontal=True)
            mbti = st.selectbox("MBTI", ["", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", 
                                         "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", 
                                         "ESTJ", "ESFJ", "ENFJ", "ENTJ"])
        
        blood = st.selectbox("혈액형", ["", "A형", "B형", "O형", "AB형"])
        question = st.text_area("상담 질문", placeholder="궁금하신 점을 입력하세요...")
        
        submitted = st.form_submit_button("➕ 고객 추가", type="primary", use_container_width=True)
        
        if submitted and name:
            customer = {
                '이름': name,
                '생년월일': str(birth),
                '시간': time_input,
                '음력양력': calendar,
                '성별': gender,
                'MBTI': mbti,
                '혈액형': blood,
                '질문': question
            }
            st.session_state[f'{PREFIX}_customers'].append(customer)
            st.toast(f"✅ {name}님 추가됨")
            st.rerun()
    
    st.markdown("---")
    
    # 고객 목록 및 PDF 생성
    customers = st.session_state[f'{PREFIX}_customers']
    if customers:
        render_customer_list(CONFIG, customers, selected_product)
        st.markdown("---")
        generate_pdfs(CONFIG, customers, selected_product)
    else:
        st.info("✍️ 위 양식에서 고객 정보를 입력하세요.")
