# backend/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.user import User, UserRole
from schemas.user import UserCreate, UserUpdate, UserResponse
import os
from core.config import settings
from pathlib import Path
# En todos los archivos de endpoints
from db.session import get_db  # Actualizar esta importación

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.cedula == user.cedula).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Crear directorio para las imágenes del usuario
    user_dir = Path(settings.DATASET_DIR) / f"user_{new_user.id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    
    return new_user

@router.get("/users/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Eliminar directorio de imágenes del usuario
    user_dir = Path(settings.DATASET_DIR) / f"user_{user_id}"
    if user_dir.exists():
        for file in user_dir.glob("*"):
            file.unlink()
        user_dir.rmdir()
    
    db.delete(db_user)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}