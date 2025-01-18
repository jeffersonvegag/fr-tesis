# backend/api/routes.py
from fastapi import APIRouter
from api.endpoints import user_router, attendance_router, recognition_router

router = APIRouter()

router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(attendance_router, prefix="/attendance", tags=["attendance"])
router.include_router(recognition_router, prefix="/recognition", tags=["recognition"])