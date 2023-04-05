from datetime import datetime
from typing import List, Optional

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    """Модель пользователя."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(String(length=50), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(
        String(length=100), nullable=True
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(length=150), nullable=True
    )
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    created: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_date(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    contents: Mapped[List['Content']] = relationship(
        back_populates='author', cascade='all, delete-orphan'
    )


class Content(Base):
    """Модель загружаемого контента."""

    __tablename__ = 'contents'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String(length=150), nullable=False)
    description: Mapped[str] = mapped_column(
        String(length=750), nullable=False
    )
    tags: Mapped[Optional[str]] = mapped_column(
        String(length=100), nullable=True
    )
    content_class: Mapped[str] = mapped_column(
        String(length=10), nullable=False
    )
    created: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.now(), nullable=False
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False
    )
    author: Mapped['User'] = relationship(back_populates='contents')
    content_extension: Mapped[str] = mapped_column(
        String(length=500), nullable=False
    )
    content_path: Mapped[str] = mapped_column(
        String(length=1000), nullable=False
    )


class Message(Base):
    """Модель сообщения."""

    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    message: Mapped[str] = mapped_column(String(length=1000), nullable=False)
