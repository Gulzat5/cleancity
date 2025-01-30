from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Complaint, User, Status
from app.schemas import ComplaintCreate, ComplaintResponse
from app.dependencies import get_current_user, require_role
from app.enums import Role, Status
import shutil
import os
from typing import List

router = APIRouter(prefix="/complaints", tags=["complaints"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", summary="Создать жалобу")
async def create_complaint(
    description: str,
    city: str,
    category: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Сохраняем файл локально (или в Cloudinary)
    UPLOAD_DIR = "app/static/uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Создаем запись в БД
    db_complaint = Complaint(
        description=description,
        image_path=file_path,
        city=city,
        category=category,
        user_id=current_user.id,
        status=Status.PENDING
    )
    
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    
    return {"message": "Жалоба создана", "id": db_complaint.id}

@router.get("/", response_model=List[ComplaintResponse], summary="Получить жалобы")
def get_complaints(
    status: Status = Query(None, description="Фильтр по статусу"),
    city: str = Query(None, description="Фильтр по городу"),
    category: str = Query(None, description="Фильтр по категории"),
    db: Session = Depends(get_db),
):
    query = db.query(Complaint)
    
    if status:
        query = query.filter(Complaint.status == status)
    if city:
        query = query.filter(Complaint.city == city)
    if category:
        query = query.filter(Complaint.category == category)
    
    return query.all()

@router.post("/{complaint_id}/take", summary="Взять жалобу в работу")
def take_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.VOLUNTEER)),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Жалоба не найдена")
    
    if complaint.status != Status.PENDING:
        raise HTTPException(status_code=400, detail="Жалоба уже в работе")
    
    complaint.status = Status.IN_PROGRESS
    complaint.volunteer_id = current_user.id
    db.commit()
    
    return {"message": "Жалоба взята в работу"}