from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StudentCreate(BaseModel):
    """Schema for adding a new student"""
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=100)
    grade_level: int = Field(ge=1, le=12)
    gpa: Optional[float] = Field(default=None, gt=0)
    is_enrolled: bool = Field(default=True)

class StudentUpdate(BaseModel):
    """Schema for fully updating a student"""
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=100)
    grade_level: int = Field(ge=1, le=12)
    gpa: Optional[float] = Field(default=None, gt=0)
    is_enrolled: bool = Field(default=True)

class StudentPatch(BaseModel):
    """Schema for partially updating a student"""
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=100)
    grade_level: Optional[int] = Field(default=None, ge=1, le=12)
    gpa: Optional[float] = Field(default=None, gt=0)
    is_enrolled: Optional[bool] = Field(default=None)

class StudentResponse(BaseModel):
    """Schema for returning a student"""
    id: int
    name: str
    email: str
    grade_level: int
    gpa: Optional[float]
    is_enrolled: bool
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True
