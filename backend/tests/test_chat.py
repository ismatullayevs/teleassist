import pytest
from core.config import settings
from fastapi.testclient import TestClient
from models.chat import Chat
from models.user import User


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token,status_code",
    [
        (settings.INTERNAL_TOKEN, 201),
        ("invalid_token", 401),
    ],
)
async def test_create_chat(client: TestClient, session, token, status_code):
    user = User(telegram_id=111111, name="Chat User", is_active=True)
    session.add(user)
    await session.commit()

    headers = {
        "X-Internal-Token": token,
        "X-Telegram-User-Id": str(user.telegram_id),
    }
    response = client.post("/api/v1/chats", headers=headers)
    assert response.status_code == status_code
    if status_code == 201:
        data = response.json()
        assert data["user_id"] == user.id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token,expected_status",
    [
        (settings.INTERNAL_TOKEN, 201),
        ("invalid_token", 401),
    ],
)
async def test_generate_response(
    client: TestClient, session, monkeypatch, token, expected_status
):
    user = User(telegram_id=333333, name="Chat User", is_active=True)
    chat = Chat(user=user)
    session.add(user)
    session.add(chat)
    await session.commit()

    from api.v1 import chat as chat_module

    class DummyResponse:
        output_text = "dummy response"

    async def dummy_create(*args, **kwargs):
        return DummyResponse()

    monkeypatch.setattr(chat_module.client.responses, "create", dummy_create)

    headers = {
        "X-Internal-Token": token,
        "X-Telegram-User-Id": str(user.telegram_id),
    }
    payload = {"chat_id": chat.id, "content": "Hello"}
    response = client.post("/api/v1/generate", json=payload, headers=headers)
    assert response.status_code == expected_status
    if expected_status == 201:
        data = response.json()
        assert data["chat_id"] == chat.id
        assert data["content"] == "dummy response"
        assert data["id"]
        assert data["created_at"]
        assert data["updated_at"]


@pytest.mark.asyncio
async def test_generate_response_locked(client: TestClient, session, monkeypatch):
    user = User(telegram_id=222222, name="Chat User", is_active=True)
    chat = Chat(user=user)
    session.add(user)
    session.add(chat)
    await session.commit()

    from api.v1 import chat as chat_module

    lock = chat_module.get_user_lock(str(user.id))
    await lock.acquire()

    headers = {
        "X-Internal-Token": settings.INTERNAL_TOKEN,
        "X-Telegram-User-Id": str(user.telegram_id),
    }
    payload = {"chat_id": chat.id, "content": "Hello"}
    response = client.post("/api/v1/generate", json=payload, headers=headers)
    assert response.status_code == 429
    assert response.json()["detail"] == "Already generating response"
    lock.release()
