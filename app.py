# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# 기존 프로젝트 파일들 연결
from database import init_db
from auth import login_user
from services import get_admin_services
from pdf_generator import PDFGenerator  # PDF 기계 가져오기

# 1. 화면 설정
st.set_page_config(page_title="PDF 자동 생성 플랫폼", page_icon="🔮", layout="wide")

def main():
    init_db() # DB 시동

    # [cite_start]로그인 상태 기억 [cite: 2]
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- [기능] 전체 작업 초기화 (사이드바) ---
    with st.sidebar:
        if st.button("🔄 전체 작업 초기화", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'logged_in':
                    del st.session_state[key]
            st.rerun()

    # [cite_start]2. 로그인 화면 (로그아웃 상태일 때) [cite: 2]
    if not st.session_state.logged_in:
        st.title("🔮 로그인")
        with st.form("login"):
            u_email = st.text_input("이메일")
            u_pw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인"):
                res = login_user(u_email, u_pw)
                if res["success"]:
                    st.session_state.logged_in = True
                    st.session_state.user = res["user"]
                    st.rerun()
                else:
                    st.error(res["error"])
        return

    # 3. 메인 메뉴 (로그인 성공 시)
    user = st.session_state.user
    with st.sidebar:
        st.write(f"### 👤 {user['name']}님")
        menu = st.radio("메뉴", ["📢 공지사항", "🔧 서비스 작업", "📚 자료실"])
        if st.button("🚪 로그아웃"):
            st.session_state.logged_in = False
            st.rerun()

    # --- [핵심] 서비스 작업 및 PDF 생성 로직 ---
    if menu == "🔧 서비스 작업":
        st.title("🔧 서비스 작업")
        
        # 상품 선택
        services = get_admin_services()
        if services:
            svc_names = [s['name'] for s in services]
            sel_svc = st.selectbox("상품을 선택하세요", svc_names)
            
            st.divider()
            uploaded_file = st.file_uploader("엑셀 업로드", type=['xlsx'])

            if uploaded_file:
                if 'df' not in st.session_state:
                    st.session_state.df = pd.read_excel(uploaded_file)
                
                df = st.session_state.df
                
                # 전체 선택 기능
                all_select = st.checkbox("✅ 전체 고객 선택 / 해제")
                selected_indices = []
                
                for idx, row in df.iterrows():
                    c1, c2, c3 = st.columns([1, 4, 5])
                    with c1:
                        is_sel = st.checkbox("", value=all_select, key=f"c_{idx}")
                        if is_sel: selected_indices.append(idx)
                    with c2: st.write(f"**{row.get('이름', '고객')}**")
                    with c3: st.caption(f"{row.get('생년월일', '')}")

                if st.button("🚀 PDF 생성 시작", type="primary", use_container_width=True):
                    if not selected_indices:
                        st.warning("고객을 선택해주세요.")
                    else:
                        # 진행률 바 생성
                        prog_bar = st.progress(0)
                        status_msg = st.empty()
                        
                        # 진짜 PDF 생성 기계 돌리기
                        pdf_worker = PDFGenerator() 
                        
                        for i, s_idx in enumerate(selected_indices):
                            cust_name = df.loc[s_idx, '이름']
                            
                            # 진행률 계산
                            percent = (i + 1) / len(selected_indices)
                            prog_bar.progress(percent)
                            status_msg.write(f"⏳ ({i+1}/{len(selected_indices)}) {cust_name}님 보고서 작성 중...")
                            
                            # 가짜 내용(테스트용) - 나중에 GPT 연결 가능
                            test_content = [{"title": "운세 분석", "content": f"{cust_name}님의 상세 운세 내용입니다."}]
                            
                            # PDF 파일 만들기 실행
                            pdf_data = pdf_worker.create_pdf(
                                chapters_content=test_content,
                                customer_name=cust_name,
                                service_type=sel_svc
                            )
                            
                            # 생성된 파일을 세션에 임시 저장 (다운로드용)
                            st.session_state[f"pdf_{s_idx}"] = pdf_data
                        
                        status_msg.success("✅ 모든 PDF 생성이 완료되었습니다!")
                        st.balloons()

                        # 다운로드 버튼들 보여주기
                        for s_idx in selected_indices:
                            if f"pdf_{s_idx}" in st.session_state:
                                st.download_button(
                                    label=f"📥 {df.loc[s_idx, '이름']}님 PDF 다운로드",
                                    data=st.session_state[f"pdf_{s_idx}"],
                                    file_name=f"{df.loc[s_idx, '이름']}_보고서.pdf",
                                    mime="application/pdf",
                                    key=f"dl_{s_idx}"
                                )

    # 나머지 메뉴 (내용 보존)
    elif menu == "📢 공지사항":
        st.info("공지사항 메뉴입니다.")
    elif menu == "📚 자료실":
        st.info("자료실 메뉴입니다.")

if __name__ == "__main__":
    main()
