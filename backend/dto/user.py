from datetime import datetime
from pydantic import BaseModel


class UserInDTO(BaseModel):
    telegram_id: int
    name: str


class UserOutDTO(UserInDTO):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
