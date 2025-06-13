import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional

from mcp.server.fastmcp import FastMCP, Context
from slack_sdk.web.async_client import AsyncWebClient

__all__ = ["mcp"]

SLACK_BOT_TOKEN_ENV = "SLACK_BOT_TOKEN"
SLACK_USER_TOKEN_ENV = "SLACK_USER_TOKEN"  # Add user token support


@dataclass
class AppContext:
    """Application lifecycle context."""

    slack_bot: AsyncWebClient
    slack_user: Optional[AsyncWebClient] = None  # Optional user token client


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
    dependencies=["slack_sdk"],  # helpful for mcp install
)

# Add health check endpoint directly to FastMCP app
from fastapi import FastAPI

# Add custom endpoints to FastMCP app
def add_health_endpoints(mcp_instance):
    """Add health check endpoints to FastMCP app."""
    app = mcp_instance.app
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint for AWS App Runner load balancer."""
        return {"status": "healthy", "service": "slack-mcp-server", "version": "1.0.0"}

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"service": "Slack MCP Server", "version": "1.0.0", "mcp_endpoint": "/mcp", "health": "/health"}

# Call after mcp creation
add_health_endpoints(mcp)


def _get_slack_bot(ctx: Context) -> AsyncWebClient:
    """Helper to retrieve the Bot Slack client from the lifespan context."""
    
    if ctx is None or ctx.lifespan_context is None:
        # Fallback to create a new client if context is not available
        token = os.getenv(SLACK_BOT_TOKEN_ENV)
        if not token:
            raise RuntimeError(f"{SLACK_BOT_TOKEN_ENV} environment variable must be set")
        return AsyncWebClient(token=token)
    
    return ctx.lifespan_context.slack_bot


def _get_slack_user(ctx: Context) -> AsyncWebClient:
    """Helper to retrieve the User Slack client from the lifespan context."""
    
    if ctx is None or ctx.lifespan_context is None or ctx.lifespan_context.slack_user is None:
        # Fallback to create a new client if context is not available
        token = os.getenv(SLACK_USER_TOKEN_ENV)
        if not token:
            raise RuntimeError(f"{SLACK_USER_TOKEN_ENV} environment variable must be set for user operations")
        return AsyncWebClient(token=token)
    
    return ctx.lifespan_context.slack_user


@mcp.tool(
    description="List public Slack channels that the bot has access to.",
)
async def list_channels(limit: int = 100, ctx: Context | None = None) -> str:  # noqa: D401
    """Return a newline-separated list of channel IDs and names.

    Parameters
    ----------
    limit: int, optional
        Maximum number of channels to return. Defaults to 100.
    ctx: Context, optional
        Injected automatically by FastMCP. Gives access to the Slack client.
    """

    slack = _get_slack_bot(ctx)
    response = await slack.conversations_list(limit=limit, exclude_archived=True)
    channels = response.get("channels", [])
    lines = [f"{c['id']} | {c['name']}" for c in channels]
    return "\n".join(lines)


@mcp.tool(
    description="Post a message to a Slack channel.",
)
async def post_message(channel_id: str, text: str, ctx: Context | None = None) -> str:  # noqa: D401
    """Send *text* to *channel_id* and return the resulting timestamp."""

    slack = _get_slack_bot(ctx)
    resp = await slack.chat_postMessage(channel=channel_id, text=text)
    return resp.get("ts", "")


@mcp.tool(
    description="Reply to a specific thread in a Slack channel.",
)
async def reply_to_thread(
    channel_id: str,
    thread_ts: str,
    text: str,
    ctx: Context | None = None,
) -> str:  # noqa: D401
    """Reply with *text* in *channel_id* under the thread specified by *thread_ts*."""

    slack = _get_slack_bot(ctx)
    resp = await slack.chat_postMessage(channel=channel_id, text=text, thread_ts=thread_ts)
    return resp.get("ts", "")


@mcp.tool(
    description="Add a reaction emoji to a message in Slack.",
)
async def add_reaction(
    channel_id: str,
    timestamp: str,
    reaction: str,
    ctx: Context | None = None,
) -> str:  # noqa: D401
    """Add *reaction* (emoji name without colons) to the message at *timestamp*."""

    slack = _get_slack_bot(ctx)
    await slack.reactions_add(channel=channel_id, timestamp=timestamp, name=reaction)
    return "ok"


@mcp.tool(
    description="Search for messages across Slack workspace (requires user token).",
)
async def search_messages_user(
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
    ctx: Context | None = None,
) -> str:  # noqa: D401
    """Search for messages with user token."""
    
    slack = _get_slack_user(ctx)
    resp = await slack.search_messages(query=query, sort=sort, sort_dir=sort_dir, count=count)
    
    if resp.get("ok"):
        messages = resp.get("messages", {}).get("matches", [])
        result = []
        for msg in messages:
            result.append(f"Channel: {msg.get('channel', {}).get('name', 'unknown')}")
            result.append(f"User: {msg.get('user', 'unknown')}")
            result.append(f"Text: {msg.get('text', '')}")
            result.append("---")
        return "\n".join(result)
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


@mcp.tool(
    description="Set user status (requires user token).",
)
async def set_user_status_user(
    status_text: str,
    status_emoji: str = "",
    status_expiration: int = 0,
    ctx: Context | None = None,
) -> str:  # noqa: D401
    """Set the current user's status with user token."""
    
    slack = _get_slack_user(ctx)
    profile = {
        "status_text": status_text,
        "status_emoji": status_emoji,
    }
    if status_expiration > 0:
        profile["status_expiration"] = status_expiration
        
    resp = await slack.users_profile_set(profile=profile)
    
    if resp.get("ok"):
        return "Status updated successfully"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


@mcp.tool(
    description="Create a reminder (requires user token).",
)
async def create_reminder_user(
    text: str,
    time: str,
    user: str = "",
    ctx: Context | None = None,
) -> str:  # noqa: D401
    """Create a reminder with user token."""
    
    slack = _get_slack_user(ctx)
    resp = await slack.reminders_add(text=text, time=time, user=user if user else None)
    
    if resp.get("ok"):
        reminder = resp.get("reminder", {})
        return f"Reminder created with ID: {reminder.get('id', 'unknown')}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


@mcp.tool(
    description="Join a channel with the bot (requires bot to be invited first).",
)
async def join_channel(
    channel_id: str,
    ctx: Context | None = None,
) -> str:  # noqa: D401
    """Join a channel with the bot."""
    
    slack = _get_slack_bot(ctx)
    resp = await slack.conversations_join(channel=channel_id)
    
    if resp.get("ok"):
        return f"Successfully joined channel {channel_id}"
    else:
        return f"Error joining channel: {resp.get('error', 'unknown error')}"


if __name__ == "__main__":
    # By default run a production-grade streamable HTTP server. This can be
    # changed to "sse" or omitted for stdio if desired.
    mcp.run(transport="streamable-http") 