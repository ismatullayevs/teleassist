from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
import aiohttp
from config import settings
from mongo import client

router = Router()


@router.message(CommandStart())
async def command_start(message: types.Message, state: FSMContext):
    assert message.from_user

    async with aiohttp.ClientSession() as session:
        headers = {
            "X-Internal-Token": settings.INTERNAL_TOKEN,
            "X-Telegram-User-Id": str(message.from_user.id),
        }
        async with session.get(
            "http://backend:80/api/v1/users/me", headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                if not data.get("is_active"):
                    await message.answer(
                        "Your account is not whitelisted. Please contact support.",
                    )
                    return
            elif response.status == 404:
                async with session.post(
                    "http://backend:80/api/v1/users",
                    headers=headers,
                    json={
                        "telegram_id": message.from_user.id,
                        "name": message.from_user.first_name,
                    },
                ) as create_response:
                    if create_response.status == 201:
                        await message.answer(
                            "Your account is not whitelisted. Please contact support.",
                        )
                    else:
                        await message.answer(
                            "Failed to create your account. Please try again later.",
                        )
                    return
            else:
                await message.answer("Something went wrong.")
                return

    await state.update_data(last_chat_id=None)
    await message.answer(
        "Hi! I am your AI chatbot. You can start a new conversation by typing /new "
        "or reply to a message to continue a previous conversation.",
    )


@router.message(Command("new"))
async def command_new(message: types.Message, state: FSMContext):
    await state.update_data(last_chat_id=None)
    await message.answer(
        "Welcome! I am your AI chatbot. How can I assist you today?",
    )


@router.message(F.text)
async def handle_message(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    db = client["teleassist"]
    messages_collection = db["messages"]

    last_chat_id = await state.get_value("last_chat_id")

    if message.reply_to_message:
        orig_telegram_message_id = message.reply_to_message.message_id
        orig_telegram_chat_id = message.reply_to_message.chat.id

        orig_message = await messages_collection.find_one(
            {
                "telegram_message_id": orig_telegram_message_id,
                "telegram_chat_id": orig_telegram_chat_id,
            }
        )

        if orig_message:
            last_chat_id = orig_message["chat_id"]
            await state.update_data(last_chat_id=last_chat_id)
        else:
            await message.answer("Original message not found in the database.")
            return

    async with aiohttp.ClientSession() as session:
        headers = {
            "X-Internal-Token": settings.INTERNAL_TOKEN,
            "X-Telegram-User-Id": str(message.from_user.id),
        }
        if not last_chat_id:
            async with session.post(
                "http://backend:80/api/v1/chats", headers=headers
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    last_chat_id = data.get("id")
                    await state.update_data(last_chat_id=last_chat_id)
                else:
                    await message.answer(
                        "Failed to create a new chat session. Make sure you are whitelisted."
                    )
                    return

        message_doc = {
            "telegram_message_id": message.message_id,
            "telegram_chat_id": message.chat.id,
            "chat_id": last_chat_id,
        }
        await messages_collection.insert_one(message_doc)

        msg = await message.reply("Generating response...")
        async with session.post(
            f"http://backend:80/api/v1/generate",
            headers=headers,
            json={"chat_id": last_chat_id, "content": message.text},
        ) as response:
            if response.status == 201:
                answer = await response.json()
                await msg.edit_text(answer.get("content", "No response content."))
                await state.update_data(last_chat_id=answer["chat_id"])
                await messages_collection.insert_one(
                    {
                        "telegram_message_id": msg.message_id,
                        "telegram_chat_id": msg.chat.id,
                        "chat_id": answer["chat_id"],
                        "content": answer.get("content", ""),
                    }
                )
            elif response.status == 429:
                await msg.edit_text("You are already generating a response. Please wait.")
            else:
                await msg.edit_text("Failed to get a response from the server.")
