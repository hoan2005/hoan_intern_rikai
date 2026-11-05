from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "user"}
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(20), nullable=False, default="user", server_default="user"
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    posts = relationship(
        "Post", back_populates="user", cascade="all, delete-orphan"
    )
