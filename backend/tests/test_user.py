import pytest
import pytest_asyncio
from core.config import settings
from fastapi.testclient import TestClient
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.parametrize(
    "token,status_code", [(settings.INTERNAL_TOKEN, 201), ("invalid_token", 401)]
)
def test_create_user(client: TestClient, token: str, status_code: int):
    response = client.post(
        "/api/v1/users/",
        json={"telegram_id": 123456789, "name": "Test User"},
        headers={
            "X-Internal-Token": token,
        },
    )
    assert response.status_code == status_code
    data = response.json()
    if status_code == 201:
        assert data["telegram_id"] == 123456789
        assert data["name"] == "Test User"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token,status_code", [(settings.INTERNAL_TOKEN, 200), ("invalid_token", 401)]
)
async def test_get_current_user(
    client: TestClient, session: AsyncSession, token: str, status_code: int
):
    user = User(telegram_id=123456789, name="Test User")
    session.add(user)
    await session.commit()

    response = client.get(
        "/api/v1/users/me",
        headers={
            "X-Internal-Token": token,
            "X-Telegram-User-Id": "123456789",
        },
    )
    assert response.status_code == status_code
    data = response.json()
    if status_code == 200:
        assert data["id"] == user.id
        assert data["telegram_id"] == 123456789
        assert data["name"] == "Test User"


def test_get_user_not_found(client: TestClient):
    response = client.get(
        "/api/v1/users/me",
        headers={
            "X-Internal-Token": settings.INTERNAL_TOKEN,
            "X-Telegram-User-Id": "123456789",
        },
    )
    assert response.status_code == 404
