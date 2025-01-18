# backend/db/init_db.py
from sqlalchemy.orm import Session
from models import Base
from .base import engine

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)