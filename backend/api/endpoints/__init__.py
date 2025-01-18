# backend/api/endpoints/__init__.py
from .recognition import router as recognition_router
from .users import router as user_router
from .attendance import router as attendance_router

__all__ = ['recognition_router', 'user_router', 'attendance_router']