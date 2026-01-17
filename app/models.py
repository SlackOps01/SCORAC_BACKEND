from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)  # Full name
    matric_number = Column(String, nullable=True, unique=True)  # Student ID
    role = Column(String, nullable=False, default="teacher") # admin, teacher, student
    
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    criteria = Column(Text, nullable=False)

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=False)
    strengths = Column(Text, nullable=True)  # JSON list stored as text
    weakpoints = Column(Text, nullable=True)  # JSON list stored as text
    cheating_detected = Column(Boolean, default=False)
    cheating_reason = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())