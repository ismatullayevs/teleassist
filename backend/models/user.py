from models.base import Base, created_at, intpk, updated_at
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BIGINT


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[intpk]
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, index=True)
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=False, index=True)

    chats: Mapped[list["Chat"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
