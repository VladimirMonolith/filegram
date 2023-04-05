from pydantic import BaseModel

class MessageRead(BaseModel):
    """Модель для отображения сообщения."""

    id: int
    message: str

    class Config:
        orm_mode = True