from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.notifications import send_notification, log_activity

from app.utils.limiter import limiter


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def register(request: Request, payload: RegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    background_tasks.add_task(send_notification, email=payload.email, message=f"Hi {payload.username}, thank you for registering using my API!")

    print(f"Background task added to send welcome email to {payload.email}")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Email already registered"
        )
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})

    background_tasks.add_task(log_activity, user_id=user.id, action="User registered")

    print(f"Background task added to log registration activity for user_id {user.id}")

    return{
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=TokenResponse, description="Login using email instead of username")
@limiter.limit("5/minute")
def login(request: Request,credentials: LoginRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    # No email sent upon login, but we will log the activity in the background

    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_access_token(data={"sub": str(user.id)})

    background_tasks.add_task(log_activity, user_id=user.id, action="User logged in")

    return {
        "access_token": token,
        "token_type": "bearer"
    }
