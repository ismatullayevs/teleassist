from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from openai import OpenAI

from api.dependencies import get_current_active_user, DbDep
from core.config import settings
from models.chat import Chat, Message
from models.user import User
from dto.chat import ChatOutDTO, MessageInDTO, MessageOutDTO


router = APIRouter()
client = OpenAI(api_key=settings.OPENAI_API_KEY)


@router.post("/chats", response_model=ChatOutDTO)
async def create_chat(user: Annotated[User, Depends(get_current_active_user)], db: DbDep):
    """
    Endpoint to create a new chat for the user.
    """
    chat = Chat(user_id=user.id)
    db.add(chat)
    await db.commit()
    return chat


@router.post("/generate", response_model=MessageOutDTO)
async def generate_response(user: Annotated[User, Depends(get_current_active_user)],
                            message: MessageInDTO,
                            db: DbDep):
    """
    Endpoint to generate a response based on the user's message.
    """
    query = (
        select(Message)
        .join(Chat, and_(Message.chat_id == Chat.id, Chat.user_id == user.id))
        .where(Message.chat_id == message.chat_id)
        .order_by(Message.created_at.asc())
    )

    result = await db.scalars(query)
    messages = result.all()
    current_time = datetime.now(timezone.utc)
    question = Message(
        chat_id=message.chat_id,
        role="user",
        content=message.content,
        created_at=current_time,
        updated_at=current_time,
    )
    response = client.responses.create(
        model="gpt-3.5-turbo",
        input=[
            *[{"role": msg.role.name, "content": msg.content} for msg in messages],
            {"role": "user", "content": message.content}
        ]
    )
    response_content = response.output_text
    current_time = datetime.now(timezone.utc)
    answer = Message(
        chat_id=message.chat_id,
        role="assistant",
        content=response_content,
        created_at=current_time,
        updated_at=current_time,
    )
    db.add_all([question, answer])
    await db.commit()
    return answer