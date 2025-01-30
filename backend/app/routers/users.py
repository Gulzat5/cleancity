from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import User
from ..auth import get_password_hash

router = APIRouter(prefix="/users", tags=["users"]) 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/", summary="Создать пользователя")
def create_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    return {"message": "User created"}

@router.get("/users/", summary="Получить пользователей")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
