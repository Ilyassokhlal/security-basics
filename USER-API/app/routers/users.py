from fastapi import APIRouter, Depends, Request

from app.models.user import User
from app.schemas.user import UserResponse
from app.utils.security import get_current_user

from app.limiter import limiter

router = APIRouter(prefix="/users", tags= ["Users"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("60/minute")
def get_my_profile(request: Request, current_user: User = Depends(get_current_user)):
    return current_user