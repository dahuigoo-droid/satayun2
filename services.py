# -*- coding: utf-8 -*-
"""
📦 서비스 관리 (최적화 버전)
- Context Manager로 DB 세션 관리
- 중복 코드 제거
"""

from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from database import SessionLocal, Service, SystemConfig, ChapterLibrary, GuidelineLibrary


# ============================================
# DB 세션 관리
# ============================================

@contextmanager
def get_db():
    """DB 세션 컨텍스트 매니저"""
    if not SessionLocal:
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _safe_query(func):
    """안전한 쿼리 데코레이터"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"DB 오류: {e}")
            return [] if 'get' in func.__name__ else {"success": False, "error": str(e)}
    return wrapper


# ============================================
# 서비스 변환
# ============================================

def _to_dict(s: Service) -> dict:
    """Service → dict"""
    return {
        "id": s.id,
        "name": s.name,
        "description": s.description or "",
        "owner_id": s.owner_id,
        "is_active": s.is_active,
        "service_type": s.service_type or "single",
        "product_category": getattr(s, 'product_category', None) or "기성상품",
        "font_family": s.font_family or "NanumGothic",
        "font_size_title": s.font_size_title or 24,
        "font_size_subtitle": s.font_size_subtitle or 16,
        "font_size_body": s.font_size_body or 12,
        "letter_spacing": s.letter_spacing or 0,
        "line_height": s.line_height or 180,
        "char_width": s.char_width or 100,
        "margin_top": s.margin_top or 25,
        "margin_bottom": s.margin_bottom or 25,
        "margin_left": s.margin_left or 25,
        "margin_right": s.margin_right or 25,
        "target_pages": s.target_pages or 30,
    }


# ============================================
# 서비스 조회
# ============================================

@_safe_query
def get_services_by_category(category: str) -> List[dict]:
    """상품 유형별 서비스 조회"""
    with get_db() as db:
        if not db:
            return []
        services = db.query(Service).filter(
            Service.is_active == True,
            Service.product_category == category
        ).order_by(Service.created_at.desc()).all()
        return [_to_dict(s) for s in services]


@_safe_query
def get_all_services(include_inactive=False) -> List[dict]:
    """모든 서비스 조회"""
    with get_db() as db:
        if not db:
            return []
        query = db.query(Service)
        if not include_inactive:
            query = query.filter(Service.is_active == True)
        return [_to_dict(s) for s in query.order_by(Service.created_at.desc()).all()]


@_safe_query
def get_admin_services() -> List[dict]:
    """관리자 공용 서비스"""
    with get_db() as db:
        if not db:
            return []
        services = db.query(Service).filter(
            Service.owner_id == None,
            Service.is_active == True
        ).order_by(Service.created_at.desc()).all()
        return [_to_dict(s) for s in services]


@_safe_query
def get_user_services(user_id: int) -> List[dict]:
    """사용자별 서비스"""
    with get_db() as db:
        if not db:
            return []
        services = db.query(Service).filter(
            Service.owner_id == user_id,
            Service.is_active == True
        ).order_by(Service.created_at.desc()).all()
        return [_to_dict(s) for s in services]


# ============================================
# 서비스 CRUD
# ============================================

def add_service(name: str, description: str = "", owner_id: int = None,
                service_type: str = "single", product_category: str = "기성상품",
                **kwargs) -> dict:
    """서비스 추가"""
    if not name or not name.strip():
        return {"success": False, "error": "서비스 이름을 입력해주세요."}
    
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        
        new_service = Service(
            name=name.strip(),
            description=description.strip() if description else "",
            owner_id=owner_id,
            is_active=True,
            service_type=service_type,
            product_category=product_category,
            font_family=kwargs.get('font_family', 'NanumGothic'),
            font_size_title=kwargs.get('font_size_title', 24),
            font_size_subtitle=kwargs.get('font_size_subtitle', 16),
            font_size_body=kwargs.get('font_size_body', 12),
            letter_spacing=kwargs.get('letter_spacing', 0),
            line_height=kwargs.get('line_height', 180),
            char_width=kwargs.get('char_width', 100),
            margin_top=kwargs.get('margin_top', 25),
            margin_bottom=kwargs.get('margin_bottom', 25),
            margin_left=kwargs.get('margin_left', 25),
            margin_right=kwargs.get('margin_right', 25),
            target_pages=kwargs.get('target_pages', 30)
        )
        db.add(new_service)
        db.flush()
        return {"success": True, "message": f"'{name}' 추가됨", "id": new_service.id}


def update_service(service_id: int, **kwargs) -> dict:
    """서비스 수정"""
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return {"success": False, "error": "서비스 없음"}
        
        for key, value in kwargs.items():
            if value is not None and hasattr(service, key):
                setattr(service, key, value.strip() if isinstance(value, str) else value)
        
        return {"success": True, "message": "수정됨"}


def delete_service(service_id: int) -> dict:
    """서비스 삭제 (soft delete)"""
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        
        service = db.query(Service).filter(Service.id == service_id).first()
        if service:
            service.is_active = False
        return {"success": True, "message": "삭제됨"}


# ============================================
# 시스템 설정
# ============================================

class ConfigKeys:
    ADMIN_API_KEY = "admin_api_key"
    ADMIN_GMAIL_ADDRESS = "admin_gmail_address"
    ADMIN_GMAIL_PASSWORD = "admin_gmail_password"


def get_system_config(key: str, default: str = "") -> str:
    """시스템 설정 조회"""
    with get_db() as db:
        if not db:
            return default
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        return config.value if config else default


def set_system_config(key: str, value: str) -> dict:
    """시스템 설정 저장"""
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = value
        else:
            db.add(SystemConfig(key=key, value=value))
        return {"success": True}


# ============================================
# 자료실 - 목차
# ============================================

def _library_to_dict(item) -> dict:
    return {
        "id": item.id,
        "user_id": item.user_id,
        "title": item.title,
        "content": item.content,
        "category": item.category,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


@_safe_query
def get_chapter_library(user_id: int = None, category: str = None) -> List[dict]:
    """목차 자료실 조회"""
    with get_db() as db:
        if not db:
            return []
        query = db.query(ChapterLibrary).filter(ChapterLibrary.is_active == True)
        if user_id:
            query = query.filter((ChapterLibrary.user_id == user_id) | (ChapterLibrary.user_id == None))
        if category:
            query = query.filter(ChapterLibrary.category == category)
        return [_library_to_dict(i) for i in query.order_by(ChapterLibrary.created_at.desc()).all()]


def add_chapter_library(title: str, content: str = "", category: str = None, user_id: int = None) -> dict:
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        item = ChapterLibrary(user_id=user_id, title=title.strip(), content=content.strip() if content else "", category=category)
        db.add(item)
        db.flush()
        return {"success": True, "id": item.id}


def update_chapter_library(item_id: int, **kwargs) -> dict:
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        item = db.query(ChapterLibrary).filter(ChapterLibrary.id == item_id).first()
        if not item:
            return {"success": False, "error": "항목 없음"}
        for k, v in kwargs.items():
            if v is not None and hasattr(item, k):
                setattr(item, k, v.strip() if isinstance(v, str) else v)
        return {"success": True}


def delete_chapter_library(item_id: int) -> dict:
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        item = db.query(ChapterLibrary).filter(ChapterLibrary.id == item_id).first()
        if item:
            item.is_active = False
        return {"success": True}


# ============================================
# 자료실 - 지침
# ============================================

@_safe_query
def get_guideline_library(user_id: int = None, category: str = None) -> List[dict]:
    """지침 자료실 조회"""
    with get_db() as db:
        if not db:
            return []
        query = db.query(GuidelineLibrary).filter(GuidelineLibrary.is_active == True)
        if user_id:
            query = query.filter((GuidelineLibrary.user_id == user_id) | (GuidelineLibrary.user_id == None))
        if category:
            query = query.filter(GuidelineLibrary.category == category)
        return [_library_to_dict(i) for i in query.order_by(GuidelineLibrary.created_at.desc()).all()]


def add_guideline_library(title: str, content: str, category: str = None, user_id: int = None) -> dict:
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        item = GuidelineLibrary(user_id=user_id, title=title.strip(), content=content.strip(), category=category)
        db.add(item)
        db.flush()
        return {"success": True, "id": item.id}


def update_guideline_library(item_id: int, **kwargs) -> dict:
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        item = db.query(GuidelineLibrary).filter(GuidelineLibrary.id == item_id).first()
        if not item:
            return {"success": False, "error": "항목 없음"}
        for k, v in kwargs.items():
            if v is not None and hasattr(item, k):
                setattr(item, k, v.strip() if isinstance(v, str) else v)
        return {"success": True}


def delete_guideline_library(item_id: int) -> dict:
    with get_db() as db:
        if not db:
            return {"success": False, "error": "DB 연결 실패"}
        item = db.query(GuidelineLibrary).filter(GuidelineLibrary.id == item_id).first()
        if item:
            item.is_active = False
        return {"success": True}
