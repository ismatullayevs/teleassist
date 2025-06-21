from unittest.mock import AsyncMock, MagicMock, patch

import handlers
import pytest
from aiogram import types
from aiogram.fsm.context import FSMContext
from aioresponses import aioresponses


@pytest.mark.asyncio
async def test_command_new():
    message = MagicMock(spec=types.Message)
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    await handlers.command_new(message, state)
    message.answer.assert_called_with(
        "Welcome! I am your AI chatbot. How can I assist you today?",
    )
    state.update_data.assert_called_with(last_chat_id=None)


@pytest.mark.asyncio
async def test_command_start_active_user():
    user = MagicMock()
    user.id = 123
    user.first_name = "Test"
    message = MagicMock(spec=types.Message)
    message.from_user = user
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    url = "http://backend:80/api/v1/users/me"
    with aioresponses() as m:
        m.get(url, status=200, payload={"is_active": True})
        with patch("handlers.settings.INTERNAL_TOKEN", "token"):
            await handlers.command_start(message, state)

    state.update_data.assert_called_with(last_chat_id=None)
    message.answer.assert_called_with(
        "Hi! I am your AI chatbot. You can start a new conversation by typing /new "
        "or reply to a message to continue a previous conversation.",
    )


@pytest.mark.asyncio
async def test_command_start_inactive_user():
    user = MagicMock()
    user.id = 123
    user.first_name = "Test"
    message = MagicMock(spec=types.Message)
    message.from_user = user
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    url = "http://backend:80/api/v1/users/me"
    with aioresponses() as m:
        m.get(url, status=200, payload={"is_active": False})
        with patch("handlers.settings.INTERNAL_TOKEN", "token"):
            await handlers.command_start(message, state)

    message.answer.assert_called_with(
        "Your account is not whitelisted. Please contact support.",
    )


@pytest.mark.asyncio
async def test_command_start_user_not_exist():
    user = MagicMock()
    user.id = 123
    user.first_name = "Test"
    message = MagicMock(spec=types.Message)
    message.from_user = user
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    url_me = "http://backend:80/api/v1/users/me"
    url_create = "http://backend:80/api/v1/users"
    with aioresponses() as m:
        m.get(url_me, status=404)
        m.post(url_create, status=201)
        with patch("handlers.settings.INTERNAL_TOKEN", "token"):
            await handlers.command_start(message, state)

    message.answer.assert_called_with(
        "Your account is not whitelisted. Please contact support.",
    )


@pytest.mark.asyncio
async def test_command_start_create_user_failed():
    user = MagicMock()
    user.id = 123
    user.first_name = "Test"
    message = MagicMock(spec=types.Message)
    message.from_user = user
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    url_me = "http://backend:80/api/v1/users/me"
    url_create = "http://backend:80/api/v1/users"
    with aioresponses() as m:
        m.get(url_me, status=404)
        m.post(url_create, status=500)
        with patch("handlers.settings.INTERNAL_TOKEN", "token"):
            await handlers.command_start(message, state)

    message.answer.assert_called_with(
        "Failed to create your account. Please try again later.",
    )


@pytest.mark.asyncio
async def test_command_start_backend_error():
    user = MagicMock()
    user.id = 123
    user.first_name = "Test"
    message = MagicMock(spec=types.Message)
    message.from_user = user
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    url = "http://backend:80/api/v1/users/me"
    with aioresponses() as m:
        m.get(url, status=500)
        with patch("handlers.settings.INTERNAL_TOKEN", "token"):
            await handlers.command_start(message, state)

    message.answer.assert_called_with("Something went wrong.")
