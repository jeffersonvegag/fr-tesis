
# backend/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from models.user import UserRole

class UserBase(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    rol: UserRole
    horario: Optional[str] = None
    facultad: Optional[str] = None
    universidad: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    cedula: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    horario: Optional[str] = None
    facultad: Optional[str] = None
    universidad: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True