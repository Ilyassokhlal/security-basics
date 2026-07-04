from pydantic import BaseModel, ConfigDict, Field, EmailStr


class RegisterRequest(BaseModel):
    """Schema for user registration"""
    username: str = Field(max_length=36)
    email: EmailStr
    password: str = Field(min_length=8, max_length=48)

class LoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserResponse(BaseModel):
    """Schema for returning user data(no password fields)"""
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes = True)

class TokenResponse(BaseModel):
    """Schema for the JWT response."""
    access_token: str
    token_type: str = "bearer"