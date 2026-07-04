from fastapi import APIRouter, Depends, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.database import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentUpdate, StudentPatch, StudentResponse
from app.utils.exceptions import NotFoundException, DuplicateException, BadRequestException
from app.utils.security import get_current_user
from app.utils.notifications import log_activity, send_notification
from app.utils.limiter import limiter

router = APIRouter(prefix="/students", tags= ["Students"])

def get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFoundException("Student", student_id)
    return student

@router.post("/", response_model=StudentResponse, status_code=201)
@limiter.limit("20/minute")
def add_student(request: Request, student: StudentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    existing_profile = db.query(Student).filter(Student.user_id == current_user.id).first()
    if existing_profile:
        raise BadRequestException("This user already has a student profile. Only one student profile is allowed per user.")

    db_student = Student(**student.model_dump(), user_id=current_user.id)
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
    except IntegrityError:
        db.rollback()
        raise DuplicateException("Student", "email", student.email)
    
    background_tasks.add_task(send_notification, email=student.email, message=f"Hi {student.name}. You have been successfully added as a student!")

    print(f"Background task added to send confirmation email to {student.email}")

    background_tasks.add_task(log_activity, user_id=current_user.id, action="Student added")

    return db_student

@router.get("/", response_model=list[StudentResponse])
@limiter.limit("60/minute")
def list_students(
    request: Request,
    grade_level: Optional[int] = None,
    is_enrolled: Optional[bool] = Query(default=True),
    db: Session = Depends(get_db)
):
    query = db.query(Student)

    if is_enrolled is not None:
        query = query.filter(Student.is_enrolled == is_enrolled)
    if grade_level:
        query = query.filter(Student.grade_level == grade_level)

    return query.all()

@router.get("/{student_id}", response_model=StudentResponse)
@limiter.limit("60/minute")
def get_student(request: Request,student_id: int, db: Session = Depends(get_db)):
    return get_student_or_404(db, student_id)

@router.put("/{student_id}", response_model=StudentResponse)
@limiter.limit("20/minute")
def update_student(request: Request, student_id: int, data: StudentUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    db_student = get_student_or_404(db, student_id)

    if db_student.is_enrolled is False and data.is_enrolled is True:
        raise BadRequestException("Archived students cannot be re-enrolled")

    for field, value in data.model_dump().items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)

    background_tasks.add_task(send_notification, email=db_student.email, message=f"Hi {db_student.name}. Your information has been fully updated!")

    print(f"Background task added to send update confirmation email to {db_student.email}")

    background_tasks.add_task(log_activity, user_id=current_user.id, action="Student fully updated")

    return db_student

@router.patch("/{student_id}", response_model=StudentResponse)
@limiter.limit("20/minute")
def patch_student(request: Request, student_id: int, data: StudentPatch, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if data.grade_level is not None and (data.grade_level < 1 or data.grade_level > 12):
        raise BadRequestException("grade level must be between 1 and 12")

    db_student = get_student_or_404(db, student_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    
    background_tasks.add_task(send_notification, email=db_student.email, message=f"Hi {db_student.name}. Your information has been partially updated!")

    print(f"Background task added to send confirmation email to {db_student.email}")
    
    background_tasks.add_task(log_activity, user_id=current_user.id, action="Student partially updated")
    
    return db_student

@router.delete("/{student_id}", status_code=204)
@limiter.limit("20/minute")
def delete_student(request: Request, student_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_student = get_student_or_404(db, student_id)
    if db_student.is_enrolled is True:
        raise BadRequestException("Active students cannot be deleted")
    db.delete(db_student)
    db.commit()

    background_tasks.add_task(log_activity, user_id=current_user.id, action="Student deleted")
