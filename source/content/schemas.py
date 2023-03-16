from typing import Optional

from pydantic import BaseModel

from authentication.schemas import UserRead


class ContentCreate(BaseModel):
    """Модель загружаемого контента."""

    title: str
    description: str
    tags: Optional[str]


class ContentRead(BaseModel):
    """Модель для отображения загруженного контента."""

    id: int
    title: str
    description: str
    tags: Optional[str]
    content_class: str
    author: UserRead

    class Config:
        orm_mode = True


class ContentUpdate(BaseModel):
    """Модель для обновления контента."""

    title: Optional[str]
    description: Optional[str]
    tags: Optional[str]
    content_extension: Optional[str]
