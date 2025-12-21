# -*- coding: utf-8 -*-
import streamlit as st
import os
from database import init_db
from pdf_generator import PDFGenerator

# 페이지 설정
st.set_page_config(page_title="PDF 자동 생성 플랫폼", layout="wide")

def main():
    init_db()
    st.title("🔮 PDF 보고서 자동 생성기")

    # 변수 초기화 (가방 밖에서 쓰기 위해 미리 준비)
    pdf_bytes = None
    c_name = "고객"

    # --- 1. 입력 가방 시작 ---
    with st.form("pdf_form"):
        st.subheader("📋 정보를 입력해주세요")
        c_name = st.text_input("고객 이름", value="홍길동")
        target_pages = st.number_input("목표 페이지 수", min_value=1, value=10, step=1)
        
        submitted = st.form_submit_button("PDF 생성하기 ✨")
        
        if submitted:
            # 가짜 내용물 생성
            all_chapters = [
                {"title": "1. 서론", "content": f"{c_name}님의 분석 결과입니다."},
                {"title": "2. 본론", "content": "내용이 적어도 페이지가 채워집니다."},
                {"title": "3. 결론", "content": "자동 생성 완료!"}
            ]
            
            with st.status("PDF 제작 중...") as status:
                pdf_gen = PDFGenerator()
                pdf_bytes = pdf_gen.create_pdf(
                    chapters_content=all_chapters, 
                    target_page_count=target_pages
                )
                status.update(label="제작 완료!", state="complete")
            
            # 여기서 바로 다운로드 버튼을 만들지 않고, 
            # 제작이 완료되었다는 표시를 위해 '세션'이라는 메모리에 저장합니다.
            st.session_state.finished_pdf = pdf_bytes
            st.session_state.file_name = f"{c_name}_보고서.pdf"

    # --- 2. 입력 가방 끝 ---

    # --- 3. 가방 밖에서 다운로드 버튼 보여주기 ---
    if "finished_pdf" in st.session_state:
        st.success("✅ PDF가 준비되었습니다! 아래 버튼을 눌러 저장하세요.")
        st.download_button(
            label="PDF 결과물 다운로드 받기 📥",
            data=st.session_state.finished_pdf,
            file_name=st.session_state.file_name,
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
