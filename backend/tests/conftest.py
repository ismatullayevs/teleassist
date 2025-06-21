import pytest
import pytest_asyncio
from core.db import create_async_engine, Base, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.pool import StaticPool


@pytest_asyncio.fixture(name="session")
async def session_fixture():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    

@pytest.fixture(name="client")
def client_fixture(session: AsyncSession):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override  

    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()