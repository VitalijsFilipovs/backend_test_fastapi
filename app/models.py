from sqlalchemy import Column, Integer, String, UniqueConstraint
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint('email', name='uq_users_email'),
    )
