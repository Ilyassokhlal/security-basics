from sqlalchemy import String, Column, Integer, Float, DateTime, Boolean, func 
from app.database import Base
from sqlalchemy import ForeignKey

class Student(Base):
    __tablename__="students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    grade_level = Column(Integer, nullable=False)
    gpa = Column(Float, nullable=True)
    is_enrolled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)