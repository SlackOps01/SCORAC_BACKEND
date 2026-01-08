from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "teacher"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    
    class Config:
        from_attributes = True

class AssignmentCreate(BaseModel):
    title: str
    description: str
    criteria: str

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
    reasoning: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
