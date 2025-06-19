from models.base import Base, intpk, created_at, updated_at
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[intpk]
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=False, index=True)

    chats: Mapped[list["Chat"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]