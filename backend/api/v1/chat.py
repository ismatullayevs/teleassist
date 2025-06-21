import asyncio
from datetime import datetime, timezone
from typing import Annotated

from api.dependencies import DbDep, get_current_active_user
from core.config import settings
from dto.chat import ChatOutDTO, MessageInDTO, MessageOutDTO
from fastapi import APIRouter, Depends, HTTPException
from models.chat import Chat, Message
from models.user import User
from openai import AsyncOpenAI
from sqlalchemy import and_, select

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

user_locks: dict[str, asyncio.Lock] = {}


def get_user_lock(user_id: str) -> asyncio.Lock:
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock()
    return user_locks[user_id]


@router.post("/chats", response_model=ChatOutDTO, status_code=201)
async def create_chat(
    user: Annotated[User, Depends(get_current_active_user)], db: DbDep
):
    """
    Endpoint to create a new chat for the user.
    """
    chat = Chat(user_id=user.id)
    db.add(chat)
    await db.commit()
    return chat


@router.post("/generate", response_model=MessageOutDTO, status_code=201)
async def generate_response(
    user: Annotated[User, Depends(get_current_active_user)],
    message: MessageInDTO,
    db: DbDep,
):
    """
    Endpoint to generate a response based on the user's message.
    """

    lock = get_user_lock(str(user.id))
    if lock.locked():
        raise HTTPException(status_code=429, detail="Already generating response")

    async with lock:
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

        with open("bot_instructions.txt", "r") as f:
            instructions = f.read().strip()

        response = await client.responses.create(
            model=settings.OPENAI_MODEL,
            input=[
                {"role": "system", "content": instructions},
                *[{"role": msg.role.name, "content": msg.content} for msg in messages],
                {"role": "user", "content": message.content},
            ],
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
