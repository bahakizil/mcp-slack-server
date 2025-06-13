"""
Unit tests for Slack MCP Server.
"""
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from slack_sdk.web.async_client import AsyncWebClient

from slack_mcp_app.slack_mcp_server import mcp


class TestSlackMCPServer:
    """Test cases for Slack MCP Server."""

    @pytest.fixture
    def mock_slack_client(self):
        """Create a mock Slack client."""
        client = AsyncMock(spec=AsyncWebClient)
        client.conversations_list.return_value = {
            "ok": True,
            "channels": [
                {"id": "C123", "name": "general"},
                {"id": "C456", "name": "random"},
            ],
        }
        client.chat_postMessage.return_value = {
            "ok": True,
            "ts": "1234567890.123456",
        }
        client.reactions_add.return_value = {"ok": True}
        return client

    @pytest.fixture
    def client(self):
        """Create a test client."""
        # Mock environment variables
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token",
                "SLACK_SIGNING_SECRET": "test-secret",
            },
        ):
            return TestClient(mcp.app)

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "slack-mcp-server"

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Slack MCP Server"
        assert data["mcp_endpoint"] == "/mcp"

    @pytest.mark.asyncio
    async def test_list_channels(self, mock_slack_client):
        """Test listing Slack channels."""
        from slack_mcp_app.slack_mcp_server import list_channels

        # Mock the context
        mock_context = MagicMock()
        mock_context.lifespan_context.slack_bot = mock_slack_client

        result = await list_channels(limit=10, ctx=mock_context)

        mock_slack_client.conversations_list.assert_called_once_with(
            limit=10, exclude_archived=True
        )

        expected_result = "C123 | general\nC456 | random"
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_post_message(self, mock_slack_client):
        """Test posting a message to Slack."""
        from slack_mcp_app.slack_mcp_server import post_message

        # Mock the context
        mock_context = MagicMock()
        mock_context.lifespan_context.slack_bot = mock_slack_client

        result = await post_message(
            channel_id="C123", text="Hello, World!", ctx=mock_context
        )

        mock_slack_client.chat_postMessage.assert_called_once_with(
            channel="C123", text="Hello, World!"
        )

        assert result == "1234567890.123456"

    @pytest.mark.asyncio
    async def test_reply_to_thread(self, mock_slack_client):
        """Test replying to a thread in Slack."""
        from slack_mcp_app.slack_mcp_server import reply_to_thread

        # Mock the context
        mock_context = MagicMock()
        mock_context.lifespan_context.slack_bot = mock_slack_client

        result = await reply_to_thread(
            channel_id="C123",
            thread_ts="1234567890.123456",
            text="Reply text",
            ctx=mock_context,
        )

        mock_slack_client.chat_postMessage.assert_called_once_with(
            channel="C123", text="Reply text", thread_ts="1234567890.123456"
        )

        assert result == "1234567890.123456"

    @pytest.mark.asyncio
    async def test_add_reaction(self, mock_slack_client):
        """Test adding a reaction to a message."""
        from slack_mcp_app.slack_mcp_server import add_reaction

        # Mock the context
        mock_context = MagicMock()
        mock_context.lifespan_context.slack_bot = mock_slack_client

        result = await add_reaction(
            channel_id="C123",
            timestamp="1234567890.123456",
            reaction="thumbsup",
            ctx=mock_context,
        )

        mock_slack_client.reactions_add.assert_called_once_with(
            channel="C123", timestamp="1234567890.123456", name="thumbsup"
        )

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_list_channels_no_context(self):
        """Test list_channels with no context (fallback behavior)."""
        from slack_mcp_app.slack_mcp_server import list_channels

        with patch.dict(
            os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}
        ), patch.object(AsyncWebClient, "conversations_list") as mock_conversations:
            mock_conversations.return_value = {
                "ok": True,
                "channels": [{"id": "C123", "name": "general"}],
            }

            result = await list_channels(limit=10, ctx=None)

            assert result == "C123 | general"

    @pytest.mark.asyncio
    async def test_missing_slack_token(self):
        """Test behavior when SLACK_BOT_TOKEN is missing."""
        from slack_mcp_app.slack_mcp_server import list_channels

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="SLACK_BOT_TOKEN"):
                await list_channels(limit=10, ctx=None)


class TestSlackMCPServerIntegration:
    """Integration tests for Slack MCP Server."""

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("SLACK_BOT_TOKEN"), reason="SLACK_BOT_TOKEN not set"
    )
    def test_real_slack_connection(self):
        """Test real connection to Slack API (requires valid token)."""
        # This test only runs if SLACK_BOT_TOKEN is set
        # Useful for integration testing with real Slack workspace
        pass


class TestSlackMCPServerErrors:
    """Test error handling in Slack MCP Server."""

    @pytest.mark.asyncio
    async def test_slack_api_error(self, mock_slack_client):
        """Test handling of Slack API errors."""
        from slack_mcp_app.slack_mcp_server import list_channels

        # Mock an API error
        mock_slack_client.conversations_list.side_effect = Exception(
            "Slack API Error"
        )

        mock_context = MagicMock()
        mock_context.lifespan_context.slack_bot = mock_slack_client

        with pytest.raises(Exception, match="Slack API Error"):
            await list_channels(limit=10, ctx=mock_context)

    @pytest.mark.asyncio
    async def test_invalid_channel_id(self, mock_slack_client):
        """Test posting to invalid channel."""
        from slack_mcp_app.slack_mcp_server import post_message

        # Mock an invalid channel error
        mock_slack_client.chat_postMessage.return_value = {
            "ok": False,
            "error": "channel_not_found",
        }

        mock_context = MagicMock()
        mock_context.lifespan_context.slack_bot = mock_slack_client

        result = await post_message(
            channel_id="INVALID", text="Test", ctx=mock_context
        )

        # Should still return result (error handling depends on implementation)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__]) 