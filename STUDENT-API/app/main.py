"""
Security measures in place:
    - CORS: restricted to localhost 8501 & 3000 | Methods are also limited to "POST" & "GET", "PUT", "DELETE" and "PATCH" as they are needed for the student API.
    - Rate Limiting:
            login: 5 requests per minute
            all POST, PUT, DELETE, PATCH requests: 20 requests per minute
            all GET requests: 60 requests per minute
    - Input Validation (pydantic does this):
        user fields:
            username: (36 max characters)
            password: (8 min & 72 max characters)
            email: validated with EmailStr
        student fields:
            name: (100 max characters)
            email: (100 max characters)
            grade_level: (1-12)
            gpa: (greater than 0)
"""


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.routers import auth, students
from app.utils.exceptions import AppException
from app.routers import users
from app.utils.limiter import limiter

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI(
    title= "Student API (Background Tasks Practice)"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"]    
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Background Tasks Practice is running"}

@app.exception_handler(AppException)
def handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )