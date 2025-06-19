from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.mongo import MongoStorage
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from handlers import router
import asyncio
import logging
import sys


async def main():
    bot = Bot(
        settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    mongo = AsyncIOMotorClient(
        host=settings.mongo_url,
        uuidRepresentation="standard",
    )
    mongo_storage = MongoStorage(mongo)

    dp = Dispatcher(storage=mongo_storage)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
