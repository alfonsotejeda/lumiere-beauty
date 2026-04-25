import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

os.environ["MONGO_DB"] = "lumiere_test"
os.environ["ADMIN_TOKEN"] = "test-token"
os.environ["WHATSAPP_NUMBER"] = "+1234567890"
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["VALKEY_URL"] = "redis://localhost:6379"

from app.main import app
from app.db import connect_db, get_db
from app.cache import connect_cache, close_cache


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_services():
    await connect_db()
    await connect_cache()
    yield
    # Best-effort teardown; event loop may already be closing at session end
    try:
        await close_cache()
    except Exception:
        pass


@pytest_asyncio.fixture(autouse=True)
async def clean_collections():
    yield
    db = get_db()
    await db.products.drop()
    await db.orders.drop()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
