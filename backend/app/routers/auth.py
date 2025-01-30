from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..auth import (
    get_current_user,
    create_access_token,
    verify_password,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ..schemas import Token, UserCreate, UserResponse
from datetime import timedelta

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserResponse, summary="Регистрация пользователя")
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Проверка уникальности email и username
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | 
        (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            detail = "Пользователь с таким email уже зарегистрирован"
        else:
            detail = "Имя пользователя уже занято"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

    # Хеширование пароля
    hashed_password = get_password_hash(user_data.password)
    
    # Создание нового пользователя
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role="user"  # Роль по умолчанию
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/token", response_model=Token, summary="Авторизация")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse, summary="Текущий пользователь")
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user