"""
Security measures in place:
    - CORS: restricted to localhost 8501 & 3000 | Methods are also limited to "POST" & "GET"
    - Rate Limiting:
            login: 5 requests per minute
            register: 20 requests per minute
            user_own_profile: 60 requests per minute
    - Input Validation (pydantic does this):
        username: (36 max characters)
        password: (8 min & 48 max characters)
        email: validated with EmailStr
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models.user import User
from app.routers import auth, users
from app.limiter import limiter

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


app = FastAPI(
    title= "Security Basics Demo"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Security Basics Practice is running"}

