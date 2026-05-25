import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

# This way tests never need a real Postgres or Redis running
with patch("app.database.get_pool", new_callable=AsyncMock), \
     patch("app.cache.get_redis", return_value=MagicMock()):
    from app.main import app

client = TestClient(app)


def test_health_check():
    """Health endpoint should always respond — even with mocked deps."""
    with patch("app.routes.notes.get_pool", new_callable=AsyncMock), \
         patch("app.routes.notes.get_redis") as mock_redis:
        mock_redis.return_value.ping = AsyncMock(return_value=True)
        mock_redis.return_value.get = AsyncMock(return_value=None)
        response = client.get("/health")
    assert response.status_code == 200


def test_create_note_schema():
    """POST /notes must reject empty content."""
    response = client.post("/notes", json={})
    assert response.status_code == 422   # Pydantic validation error


def test_root_not_found():
    """There is no route at root — should 404."""
    response = client.get("/")
    assert response.status_code == 404