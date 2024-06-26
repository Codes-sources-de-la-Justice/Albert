from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ApiToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    hash = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, unique=False, nullable=False)

    user = relationship("User", back_populates="api_tokens")
    user_id = Column(Integer, ForeignKey("users.id"))



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # is_confirmed:
    #  - None (default) = Account creation neither accepted nor declined
    #  - False = Account creation declined
    #  - True = Account creation accepted
    is_confirmed = Column(Boolean, nullable=True, default=None)

    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    chats = relationship("Chat", back_populates="user")
    streams = relationship("Stream", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    password_reset_token = relationship("PasswordResetToken", back_populates="user")

    api_tokens = relationship("ApiToken", back_populates="user")
