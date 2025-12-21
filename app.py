# -*- coding: utf-8 -*-
import streamlit as st
import os
from database import init_db
from pdf_generator import PDFGenerator

# 페이지 설정
st.set_page_config(page_title="PDF 자동 생성 플랫폼", layout="wide")

def main():
    # 1. 데이터베이스 초기화 (기본 설정)
    init_db()

    st.title("🔮 PDF 보고서 자동 생성기")

    # 2. 사용자 입력 창구
    with st.form("pdf_form"):
        st.subheader("📋 정보를 입력해주세요")
        c_name = st.text_input("고객 이름", value="홍길동")
        
        # [중요] 목표 페이지 수 설정 칸
        target_pages = st.number_input("목표 페이지 수 (최소 1페이지 이상)", min_value=1, value=10, step=1)
        
        submitted = st.form_submit_button("PDF 생성 및 페이지 맞추기 시작! ✨")
        
        if submitted:
            # 에러 방지를 위해 가짜 내용물(바구니)을 미리 만듭니다.
            # 실제로는 GPT가 이 바구니를 채우게 됩니다.
            all_chapters = [
                {"title": "1. 서론", "content": f"{c_name}님의 분석 결과 서론입니다."},
                {"title": "2. 본론", "content": "상세 분석 내용이 여기에 들어갑니다."},
                {"title": "3. 결론", "content": "마지막 결론 부분입니다."}
            ]
            
            with st.status("PDF를 제작하고 있습니다...") as status:
                st.write("설정하신 페이지 수에 맞춰 종이를 채우는 중...")
                
                # PDF 기계 불러오기
                pdf_gen = PDFGenerator()
                
                # 기계에게 내용물과 목표 페이지 수를 전달!
                pdf_bytes = pdf_gen.create_pdf(
                    chapters_content=all_chapters, 
                    target_page_count=target_pages
                )
                
                status.update(label="모든 페이지가 준비되었습니다!", state="complete")
                
            # 다운로드 버튼 생성
            st.download_button(
                label="PDF 결과물 받기 📥",
                data=pdf_bytes,
                file_name=f"{c_name}_분석보고서.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
