from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
import aiohttp
from core.config import settings


router = Router()


@router.message(CommandStart())
async def command_start(message: types.Message, state: FSMContext):
    assert message.from_user

    async with aiohttp.ClientSession() as session:
        headers = {
            "X-Internal-Token": settings.INTERNAL_TOKEN,
            "X-Telegram-User-Id": str(message.from_user.id),
        }
        async with session.get("http://backend:80/api/v1/users/me",
                                headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if not data.get("is_active"):
                    await message.answer(
                        "Your account is whitelisted. Please contact support.",
                    )
                    return
            elif response.status == 404:
                async with session.post("http://backend:80/api/v1/users",
                                        headers=headers, json={
                        "telegram_id": message.from_user.id,
                        "name": message.from_user.first_name,
                                        }) as create_response:
                    if create_response.status == 201:
                        await message.answer(
                            "Your account is whitelisted. Please contact support.",
                        )
                    else:
                        await message.answer(
                            "Failed to create your account. Please try again later.",
                        )
                    return
            else:
                await message.answer("Something went wrong.")
                return
    
    await command_new(message, state)


@router.message(Command("new"))
async def command_new(message: types.Message, state: FSMContext):
    await state.update_data(last_chat_id=None)
    await message.answer(
        "Welcome! I am your AI chatbot. How can I assist you today?",
    )


@router.message(F.text)
async def handle_message(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    
    last_chat_id = await state.get_value("last_chat_id")

    async with aiohttp.ClientSession() as session:
        headers = {
            "X-Internal-Token": settings.INTERNAL_TOKEN,
            "X-Telegram-User-Id": str(message.from_user.id),
        }
        if not last_chat_id:
            async with session.post("http://backend:80/api/v1/chats",
                                    headers=headers) as response:
                if response.status == 201:
                    data = await response.json()
                    last_chat_id = data.get("id")
                    await state.update_data(last_chat_id=last_chat_id)
                else:
                    await message.answer("Failed to create a new chat session. Make sure you are whitelisted.")
                    return
        
        msg = await message.reply("Generating response...")
        async with session.post(
            f"http://backend:80/api/v1/generate",
            headers=headers,
            json={"chat_id": last_chat_id, "content": message.text}
        ) as response:
            if response.status == 201:
                answer = await response.json()
                await msg.edit_text(answer.get("content", "No response content."))
                await state.update_data(last_chat_id=answer.chat_id)
            else:
                await message.answer("Failed to get a response from the server.")