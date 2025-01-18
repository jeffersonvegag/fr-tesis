# backend/models/__init__.py
from db.base import Base
from .base import TimestampMixin
from .user import User, UserRole
from .attendance import Attendance
from .course import Course

__all__ = ['Base', 'TimestampMixin', 'User', 'UserRole', 'Attendance', 'Course']