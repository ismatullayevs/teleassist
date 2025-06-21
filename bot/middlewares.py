import logging

from aiogram import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging incoming messages.
    """

    async def __call__(self, handler, event, data):
        logging.info(f"Received event: {event}")
        return await handler(event, data)
