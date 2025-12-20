# -*- coding: utf-8 -*-
"""
🔮 PDF 자동 생성 플랫폼
메인 페이지 (로그인/업무현황)
"""

import streamlit as st

st.set_page_config(
    page_title="PDF 자동 생성 플랫폼",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

from common import apply_common_css, init_session_state, initialize_database
from auth import login_user, register_user, check_admin_exists, create_first_admin
from database import SessionLocal
from sqlalchemy import text

# DB 초기화
initialize_database()

# 세션 초기화
init_session_state()
apply_common_css()

# ============================================
# 업무현황 DB 함수
# ============================================

def get_all_tasks():
    """모든 업무현황 조회"""
    try:
        db = SessionLocal()
        result = db.execute(text("""
            SELECT t.*, u.name as author_name 
            FROM tasks t 
            LEFT JOIN users u ON t.author_id = u.id 
            WHERE t.is_active = TRUE
            ORDER BY t.created_at DESC
        """))
        tasks = [dict(row._mapping) for row in result]
        db.close()
        return tasks
    except Exception as e:
        print(f"업무현황 조회 오류: {e}")
        return []

def create_task(author_id: int, title: str, content: str, status: str = "진행중"):
    """업무현황 등록"""
    try:
        db = SessionLocal()
        db.execute(text("""
            INSERT INTO tasks (author_id, title, content, status, is_active, created_at, updated_at)
            VALUES (:author_id, :title, :content, :status, TRUE, NOW(), NOW())
        """), {"author_id": author_id, "title": title, "content": content, "status": status})
        db.commit()
        db.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_task(task_id: int, title: str = None, content: str = None, status: str = None):
    """업무현황 수정"""
    try:
        db = SessionLocal()
        updates = []
        params = {"task_id": task_id}
        
        if title:
            updates.append("title = :title")
            params["title"] = title
        if content:
            updates.append("content = :content")
            params["content"] = content
        if status:
            updates.append("status = :status")
            params["status"] = status
        
        updates.append("updated_at = NOW()")
        
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = :task_id"
        db.execute(text(query), params)
        db.commit()
        db.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_task(task_id: int):
    """업무현황 삭제 (soft delete)"""
    try:
        db = SessionLocal()
        db.execute(text("UPDATE tasks SET is_active = FALSE WHERE id = :task_id"), {"task_id": task_id})
        db.commit()
        db.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# 메인 페이지
# ============================================

# 이미 로그인되어 있으면 - 업무현황 표시
if st.session_state.get('logged_in', False):
    st.title("🔮 PDF 자동 생성 플랫폼")
    st.success(f"👋 {st.session_state.user['name']}님, 환영합니다!")
    
    st.markdown("---")
    
    # ===== 업무현황 게시판 =====
    st.markdown("### 📋 업무현황")
    
    user = st.session_state.user
    is_admin = user.get('is_admin', False)
    
    # 새 업무 등록
    with st.expander("➕ 새 업무 등록", expanded=False):
        new_title = st.text_input("제목", key="new_task_title", placeholder="업무 제목을 입력하세요")
        new_content = st.text_area("내용", key="new_task_content", height=150, placeholder="업무 내용을 입력하세요")
        new_status = st.selectbox("상태", ["진행중", "완료", "보류", "긴급"], key="new_task_status")
        
        if st.button("📝 등록", type="primary", use_container_width=True):
            if new_title and new_content:
                result = create_task(user['id'], new_title, new_content, new_status)
                if result.get('success'):
                    st.toast("✅ 업무가 등록되었습니다!")
                    st.rerun()
                else:
                    st.error(result.get('error', '등록 실패'))
            else:
                st.warning("제목과 내용을 입력해주세요.")
    
    st.markdown("---")
    
    # 업무 목록
    tasks = get_all_tasks()
    
    if tasks:
        for task in tasks:
            # 상태별 색상
            status = task.get('status', '진행중')
            status_colors = {
                "진행중": "🔵",
                "완료": "✅",
                "보류": "⏸️",
                "긴급": "🔴"
            }
            status_icon = status_colors.get(status, "🔵")
            
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"**{status_icon} {task.get('title', '')}**")
                    st.caption(f"👤 {task.get('author_name', '알 수 없음')} | 📅 {str(task.get('created_at', ''))[:10]} | 상태: {status}")
                    
                    # 내용 (접기)
                    with st.expander("내용 보기", expanded=False):
                        st.markdown(task.get('content', ''))
                        
                        # 수정/삭제 (작성자 또는 관리자만)
                        if task.get('author_id') == user['id'] or is_admin:
                            st.markdown("---")
                            
                            edit_col1, edit_col2, edit_col3 = st.columns(3)
                            
                            with edit_col1:
                                edit_status = st.selectbox(
                                    "상태 변경",
                                    ["진행중", "완료", "보류", "긴급"],
                                    index=["진행중", "완료", "보류", "긴급"].index(status) if status in ["진행중", "완료", "보류", "긴급"] else 0,
                                    key=f"edit_status_{task['id']}"
                                )
                            
                            with edit_col2:
                                if st.button("💾 상태 저장", key=f"save_{task['id']}", use_container_width=True):
                                    update_task(task['id'], status=edit_status)
                                    st.toast("✅ 상태가 변경되었습니다!")
                                    st.rerun()
                            
                            with edit_col3:
                                if st.button("🗑️ 삭제", key=f"del_{task['id']}", use_container_width=True):
                                    delete_task(task['id'])
                                    st.toast("🗑️ 삭제되었습니다!")
                                    st.rerun()
                
                st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
    else:
        st.info("등록된 업무가 없습니다.")
    
    st.stop()

# ===== 로그인/회원가입 (미로그인 시) =====
st.markdown('<h1 class="main-title">🔮 PDF 자동 생성 플랫폼</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">사주 · 연애 · 타로 운세 PDF를 자동으로 생성합니다</p>', unsafe_allow_html=True)

# 최초 관리자 체크
admin_exists = check_admin_exists()

tab1, tab2 = st.tabs(["로그인", "회원가입"])

# ===== 로그인 =====
with tab1:
    st.markdown("### 🔐 로그인")
    
    login_email = st.text_input("이메일", key="login_email")
    login_password = st.text_input("비밀번호", type="password", key="login_pw")
    
    if st.button("로그인", type="primary", use_container_width=True):
        if login_email and login_password:
            result = login_user(login_email, login_password)
            if result.get('success'):
                st.session_state.logged_in = True
                st.session_state.user = result['user']
                st.toast(f"✅ {result['user']['name']}님, 환영합니다!")
                st.rerun()
            else:
                st.error(result.get('error', '로그인 실패'))
        else:
            st.warning("이메일과 비밀번호를 입력해주세요.")

# ===== 회원가입 =====
with tab2:
    st.markdown("### 📝 회원가입")
    
    reg_email = st.text_input("이메일", key="reg_email")
    reg_name = st.text_input("이름", key="reg_name")
    reg_password = st.text_input("비밀번호", type="password", key="reg_pw")
    reg_password2 = st.text_input("비밀번호 확인", type="password", key="reg_pw2")
    
    if st.button("회원가입", type="primary", use_container_width=True):
        if not reg_email or not reg_name or not reg_password:
            st.warning("모든 필드를 입력해주세요.")
        elif reg_password != reg_password2:
            st.error("비밀번호가 일치하지 않습니다.")
        elif len(reg_password) < 4:
            st.warning("비밀번호는 4자 이상이어야 합니다.")
        else:
            result = register_user(reg_email, reg_password, reg_name)
            if result.get('success'):
                st.toast("✅ 회원가입이 완료되었습니다!")
                st.success("✅ 회원가입이 완료되었습니다! 관리자 승인 후 로그인할 수 있습니다.")
            else:
                st.error(result.get('error', '회원가입 실패'))

# ===== 최초 관리자 설정 =====
if not admin_exists:
    st.markdown("---")
    
    with st.expander("🔧 최초 관리자 설정", expanded=True):
        st.warning("⚠️ 등록된 관리자가 없습니다. 최초 관리자를 설정해주세요.")
        
        admin_email = st.text_input("관리자 이메일", key="admin_email")
        admin_name = st.text_input("관리자 이름", key="admin_name", value="관리자")
        admin_password = st.text_input("관리자 비밀번호", type="password", key="admin_pw")
        
        if st.button("👑 관리자 계정 생성", type="primary"):
            if admin_email and admin_password:
                result = create_first_admin(admin_email, admin_password, admin_name)
                if result.get('success'):
                    st.toast("✅ 관리자 계정이 생성되었습니다!")
                    st.success("✅ 관리자 계정이 생성되었습니다! 위에서 로그인해주세요.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(result.get('error', '생성 실패'))
            else:
                st.warning("이메일과 비밀번호를 입력해주세요.")
