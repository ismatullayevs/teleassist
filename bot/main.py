import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.enums import ParseMode
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.methods import GetUpdates, SetMyCommands
from aiogram.types import BotCommand
from config import settings
from handlers import router
from middlewares import LoggingMiddleware
from motor.motor_asyncio import AsyncIOMotorClient


async def main():
    bot = Bot(
        settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    bot.session.middleware(RequestLogging(ignore_methods=[GetUpdates]))

    await bot(
        SetMyCommands(
            commands=[
                BotCommand(command="start", description="Start the bot"),
                BotCommand(command="help", description="Show help information"),
                BotCommand(command="new", description="Start a new chat"),
            ]
        )
    )

    mongo = AsyncIOMotorClient(
        host=settings.mongo_url,
        uuidRepresentation="standard",
    )
    mongo_storage = MongoStorage(mongo)

    dp = Dispatcher(storage=mongo_storage)
    dp.include_router(router)
    dp.update.outer_middleware(LoggingMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
