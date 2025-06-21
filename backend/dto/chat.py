from datetime import datetime

from pydantic import BaseModel


class ChatOutDTO(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class MessageInDTO(BaseModel):
    chat_id: int
    content: str


class MessageOutDTO(MessageInDTO):
    id: int
    created_at: datetime
    updated_at: datetime
