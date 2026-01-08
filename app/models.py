from sqlalchemy import Column, Integer, String, Boolean, Text
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="teacher") # admin, teacher
    
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    criteria = Column(Text, nullable=False)