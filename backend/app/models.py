from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime
from enum import Enum as PyEnum

class Role(PyEnum):
    USER = "user"
    VOLUNTEER = "volunteer"
    MODERATOR = "moderator"

class Status(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(Enum(Role), default=Role.USER)
    city = Column(String(50))
    
    complaints = relationship("Complaint", back_populates="user")
    messages = relationship("Message", back_populates="sender")

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    image_path = Column(String(255))
    city = Column(String(50))
    category = Column(String(50))
    status = Column(Enum(Status), default=Status.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="complaints")
    volunteer = relationship("User", foreign_keys=[volunteer_id])
    messages = relationship("Message", back_populates="complaint")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    
    complaint = relationship("Complaint", back_populates="messages")
    sender = relationship("User", back_populates="messages")