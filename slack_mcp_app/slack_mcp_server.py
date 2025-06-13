import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Optional

from slack_sdk.web.async_client import AsyncWebClient

from mcp.server.fastmcp import Context, FastMCP
from . import tools

__all__ = ["mcp"]

SLACK_BOT_TOKEN_ENV = "SLACK_BOT_TOKEN"
SLACK_USER_TOKEN_ENV = "SLACK_USER_TOKEN"


@dataclass
class AppContext:
    """Application lifecycle context."""

    slack_bot: AsyncWebClient
    slack_user: Optional[AsyncWebClient] = None


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialise and clean up shared resources for the server.

    Loads the Slack bot token from the environment and instantiates an
    async Slack WebClient that is shared between all tool calls. The
    client is closed gracefully on application shutdown.
    """

    bot_token = os.getenv(SLACK_BOT_TOKEN_ENV)
    if not bot_token:
        raise RuntimeError(
            f"{SLACK_BOT_TOKEN_ENV} environment variable must be set to run the Slack MCP server"
        )

    user_token = os.getenv(SLACK_USER_TOKEN_ENV)

    slack_bot_client = AsyncWebClient(token=bot_token)
    slack_user_client = AsyncWebClient(token=user_token) if user_token else None

    try:
        yield AppContext(slack_bot=slack_bot_client, slack_user=slack_user_client)
    finally:
        # AsyncWebClient doesn't have a close() method, it's handled automatically
        pass


mcp = FastMCP(
    name="Slack MCP Server",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=["slack_sdk"],
)


# Auto-register all tools from the tools module
tool_registry = [
    # Channel & User Management
    ("list_channels", "List public Slack channels that the bot has access to.", tools.list_channels),
    ("list_users", "List users in the Slack workspace.", tools.list_users),
    ("get_user_info", "Get detailed information about a user.", tools.get_user_info),
    ("find_user_by_email", "Find a user by their email address.", tools.find_user_by_email),
    
    # Messaging
    ("send_message", "Send a message to a Slack channel.", tools.send_message),
    ("reply_to_message", "Reply to a specific thread in a Slack channel.", tools.reply_to_message),
    ("delete_message", "Delete a message from a Slack channel.", tools.delete_message),
    ("schedule_message", "Schedule a message for later delivery.", tools.schedule_message),
    
    # Reactions & Interactions
    ("add_reaction", "Add a reaction emoji to a message in Slack.", tools.add_reaction),
    ("pin_message", "Pin a message to a channel.", tools.pin_message),
    ("unpin_message", "Unpin a message from a channel.", tools.unpin_message),
    
    # File Operations
    ("upload_file", "Upload a file to Slack channels.", tools.upload_file),
    ("list_files", "List files in the workspace.", tools.list_files),
    
    # Conversation & History
    ("get_conversation_history", "Get conversation history from a channel.", tools.get_conversation_history),
    ("get_thread_replies", "Get replies in a message thread.", tools.get_thread_replies),
    
    # Search (User Token Required)
    ("search_messages", "Search for messages across Slack workspace (requires user token).", tools.search_messages),
    
    # User Status & Reminders (User Token Required)
    ("set_user_status", "Set user status (requires user token).", tools.set_user_status),
    ("create_reminder", "Create a reminder (requires user token).", tools.create_reminder),
    
    # Channel Management
    ("create_channel", "Create a new channel.", tools.create_channel),
    ("archive_channel", "Archive a channel.", tools.archive_channel),
    ("set_channel_topic", "Set a channel's topic.", tools.set_channel_topic),
    ("set_channel_description", "Set a channel's description/purpose.", tools.set_channel_description),
    ("join_channel", "Join a channel with the bot (requires bot to be invited first).", tools.join_channel),
    
    # Workspace Info
    ("get_team_info", "Get information about the team/workspace.", tools.get_team_info),
    ("list_emojis", "List custom emojis in the workspace.", tools.list_emojis),
]

# Register all tools dynamically
for tool_name, description, tool_func in tool_registry:
    mcp.tool(description=description)(tool_func)


if __name__ == "__main__":
    # By default run a production-grade streamable HTTP server
    mcp.run(transport="streamable-http")
