from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    matric_number: Optional[str] = None
    role: str = "student"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    matric_number: Optional[str] = None
    role: str
    
    class Config:
        from_attributes = True

class AssignmentCreate(BaseModel):
    title: str
    description: str
    criteria: str

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    criteria: Optional[str] = None

class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: str
    criteria: str
    
    class Config:
        from_attributes = True
 
class ScoreResponse(BaseModel):
    score: int
    feedback: str
    strengths: List[str] = []
    weakpoints: List[str] = []
    cheating_detected: bool = False
    cheating_reason: Optional[str] = None
    reasoning: Optional[str] = None

class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    user_id: int
    student_name: Optional[str] = None
    matric_number: Optional[str] = None
    score: int
    feedback: str
    strengths: List[str] = []
    weakpoints: List[str] = []
    cheating_detected: bool = False
    cheating_reason: Optional[str] = None
    reasoning: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

