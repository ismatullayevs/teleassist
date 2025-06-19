from sqlalchemy import ForeignKey
from models.base import Base, intpk, created_at, updated_at
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import relationship

from models.user import User
from enumerators import Role



class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped[User] = relationship(back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "message"

    id: Mapped[intpk]
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"), index=True)
    content: Mapped[str]
    role: Mapped[Role]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    chat: Mapped[Chat] = relationship(back_populates="messages")