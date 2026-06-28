from sqlalchemy import String, Column, Integer
from app.database import Base

class User(Base):
    """SQLAlchemy model for the users table"""
    __tablename__="users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
