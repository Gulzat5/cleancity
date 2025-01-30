from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Complaint, Status
from ..dependencies import get_current_user, require_role
from ..auth import Role

router = APIRouter(prefix="/moderation", tags=["moderation"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pending", summary="Список жалоб на модерации")
def get_pending_complaints(
    db: Session = Depends(get_db),
    moderator: User = Depends(require_role(Role.MODERATOR)),
):
    return db.query(Complaint).filter(Complaint.status == Status.PENDING).all()

@router.post("/{complaint_id}/approve", summary="Одобрить жалобу")
def approve_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_role(Role.MODERATOR)),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Жалоба не найдена")
    
    complaint.status = Status.APPROVED
    db.commit()
    return {"message": "Жалоба одобрена"}

@router.post("/{complaint_id}/reject", summary="Отклонить жалобу")
def reject_complaint(
    complaint_id: int,
    reason: str,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_role(Role.MODERATOR)),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Жалоба не найдена")
    
    complaint.status = Status.REJECTED
    complaint.rejection_reason = reason  # Добавляем поле в модель Complaint!
    db.commit()
    return {"message": "Жалоба отклонена"}