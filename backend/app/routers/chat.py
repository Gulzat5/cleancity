from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Message, Complaint, User
from ..dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{complaint_id}", summary="Получить историю сообщений")
def get_messages(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверяем доступ к чату
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Жалоба не найдена")
    
    if current_user.id not in [complaint.user_id, complaint.volunteer_id]:
        raise HTTPException(status_code=403, detail="Нет доступа к чату")
    
    return db.query(Message).filter(Message.complaint_id == complaint_id).all()

@router.post("/{complaint_id}", summary="Отправить сообщение")
def send_message(
    complaint_id: int,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверяем доступ к чату
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Жалоба не найдена")
    
    if current_user.id not in [complaint.user_id, complaint.volunteer_id]:
        raise HTTPException(status_code=403, detail="Нет доступа к чату")
    
    message = Message(
        text=text,
        complaint_id=complaint_id,
        sender_id=current_user.id
    )
    
    db.add(message)
    db.commit()
    return {"message": "Сообщение отправлено"}