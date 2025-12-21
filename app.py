# -*- coding: utf-8 -*-
import streamlit as st
# (기타 필요한 임포트들은 기존과 동일)

def main():
    # ... (기존 코드들) ...
    
    st.title("🔮 PDF 자동 생성 조종석")
    
    with st.form("pdf_form"):
        st.subheader("1. 고객 정보 입력")
        c_name = st.text_input("고객 이름", value="홍길동")
        
        st.subheader("2. PDF 설정")
        # [핵심] 여기서 사용자가 원하는 페이지 수를 숫자로 입력받습니다!
        target_pages = st.number_input("목표 페이지 수 (최소 1페이지 이상)", min_value=1, value=10, step=1)
        
        submitted = st.form_submit_button("PDF 생성 시작! ✨")
        
        if submitted:
            with st.status("PDF를 열심히 만드는 중...") as status:
                st.write("GPT가 내용을 쓰고 있어요...")
                # (중략: GPT로 내용을 가져오는 과정)
                
                st.write("설정하신 페이지 수에 맞춰 종이를 채우는 중...")
                # [중심] 우리가 아까 만든 pdf_generator에게 'target_pages' 숫자를 전달합니다.
                from pdf_generator import PDFGenerator
                pdf_gen = PDFGenerator()
                
                # 생성 함수에 target_page_count라는 이름으로 숫자를 보내줍니다.
                pdf_bytes = pdf_gen.create_pdf(
                    chapters_content=all_chapters, # GPT가 만든 내용
                    target_page_count=target_pages  # 사용자가 입력한 숫자
                )
                
                status.update(label="PDF 생성 완료!", state="complete")
                
            st.download_button(
                label="결과물 다운로드 📥",
                data=pdf_bytes,
                file_name=f"{c_name}_분석보고서.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
