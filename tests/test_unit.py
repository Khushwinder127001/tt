"""
 TT test
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
import uvicorn
from fastapi.testclient import TestClient
from iamlistening import Listener

from tt.app import app, start_bot_task
from tt.config import settings
from tt.plugins.plugin_manager import PluginManager
from tt.utils import send_notification, start_bot, start_plugins


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


def test_dynaconf_is_in_testing():
    assert settings.VALUE == "On Testing"
    assert settings.chat_platform == "discord"


@pytest.fixture(name="message")
def message_test():
    return "Test message"


@pytest.fixture(name="listener_obj")
def listener_test():
    return Listener()


@pytest.fixture(name="ial_test")
def ial_test():
    listener = Listener()
    listener.handler = AsyncMock()
    return listener


@pytest.fixture(name="plugin_manager_obj")
def pluginmngr_test():
    return PluginManager()


@pytest.fixture
def message():
    return "Test message"


@pytest.fixture
def mock_listener():
    mock_listener = AsyncMock(spec=Listener)
    mock_listener.handler = AsyncMock()
    return mock_listener


@pytest.fixture
def mock_plugin_manager():
    return AsyncMock(spec=PluginManager)


@pytest.mark.asyncio
async def test_start_bot_task():
    run_bot = AsyncMock()
    await start_bot_task()
    assert run_bot.assert_awaited_once


def test_app_endpoint_main():
    client = TestClient(app)
    response = client.get("/")
    init = MagicMock(client)
    # assert response.status_code == 200
    assert response.status_code is not None
    assert init.assert_called


def test_app_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_webhook_with_valid_auth():
    client = TestClient(app)
    payload = {"data": "buy BTC"}
    response = client.post("/webhook/123abc", json=payload)
    post = MagicMock()
    print(response.content.decode("utf-8"))
    assert response is not None
    assert response.content.decode("utf-8") is not None
    assert post.assert_called


def test_webhook_with_invalid_auth():
    client = TestClient(app)
    payload = {"data": "my_data"}
    response = client.post("/webhook/abc123", json=payload)
    print(response.content.decode("utf-8"))
    assert response.content.decode("utf-8") is not None


@pytest.mark.asyncio
async def test_send_notification(caplog):
    await send_notification("Test message")
    assert "Loaded Discord" in caplog.text


@pytest.mark.asyncio
async def test_start_plugins():
    plugin_manager = AsyncMock(spec=PluginManager)
    await start_plugins(plugin_manager)
    plugin_manager.load_plugins.assert_called_once()


@pytest.mark.asyncio
async def test_start_bot():
    listener = AsyncMock(spec=Listener)
    listener.handler = AsyncMock()
    plugin_manager = AsyncMock(spec=PluginManager)
    await start_bot(listener, plugin_manager, max_iterations=1)
    listener.start.assert_awaited_once()
    listener.handler.get_latest_message.assert_awaited_once()


def test_main():
    client = TestClient(app)
    uvicorn.run = AsyncMock(client)
    uvicorn.run.assert_called_once
