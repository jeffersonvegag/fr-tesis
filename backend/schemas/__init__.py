# backend/schemas/__init__.py
from .user import UserCreate, UserUpdate, UserResponse
from .attendance import AttendanceCreate, AttendanceResponse
from .course import CourseCreate, CourseUpdate, CourseResponse

__all__ = [
    'UserCreate', 'UserUpdate', 'UserResponse',
    'AttendanceCreate', 'AttendanceResponse',
    'CourseCreate', 'CourseUpdate', 'CourseResponse'
]