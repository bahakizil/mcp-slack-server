"""
Slack MCP Tools
All MCP tool implementations for Slack operations.
"""

import os
from mcp.server.fastmcp import Context
from slack_sdk.web.async_client import AsyncWebClient

# Environment variable names
SLACK_BOT_TOKEN_ENV = "SLACK_BOT_TOKEN"
SLACK_USER_TOKEN_ENV = "SLACK_USER_TOKEN"


def _get_slack_bot(ctx: Context) -> AsyncWebClient:
    """Helper to retrieve the Bot Slack client from the lifespan context."""
    if ctx is None or ctx.lifespan_context is None:
        # Fallback to create a new client if context is not available
        token = os.getenv(SLACK_BOT_TOKEN_ENV)
        if not token:
            raise RuntimeError(
                f"{SLACK_BOT_TOKEN_ENV} environment variable must be set"
            )
        return AsyncWebClient(token=token)

    return ctx.lifespan_context.slack_bot


def _get_slack_user(ctx: Context) -> AsyncWebClient:
    """Helper to retrieve the User Slack client from the lifespan context."""
    if (
        ctx is None
        or ctx.lifespan_context is None
        or ctx.lifespan_context.slack_user is None
    ):
        # Fallback to create a new client if context is not available
        token = os.getenv(SLACK_USER_TOKEN_ENV)
        if not token:
            raise RuntimeError(
                f"{SLACK_USER_TOKEN_ENV} environment variable must be set for user operations"
            )
        return AsyncWebClient(token=token)

    return ctx.lifespan_context.slack_user


# =============================================================================
# CHANNEL & USER MANAGEMENT TOOLS
# =============================================================================

async def list_channels(
    limit: int = 100, ctx: Context | None = None
) -> str:
    """List public Slack channels that the bot has access to."""
    slack = _get_slack_bot(ctx)
    response = await slack.conversations_list(limit=limit, exclude_archived=True)
    channels = response.get("channels", [])
    lines = [f"{c['id']} | {c['name']}" for c in channels]
    return "\n".join(lines)


async def list_users(
    limit: int = 100, ctx: Context | None = None
) -> str:
    """List users in the Slack workspace."""
    slack = _get_slack_bot(ctx)
    response = await slack.users_list(limit=limit)
    users = response.get("members", [])
    lines = []
    for user in users:
        if not user.get("deleted", False):
            name = user.get("real_name", user.get("name", "Unknown"))
            lines.append(f"{user['id']} | {name}")
    return "\n".join(lines)


async def get_user_info(
    user_id: str, ctx: Context | None = None
) -> str:
    """Get detailed information about a user."""
    slack = _get_slack_bot(ctx)
    response = await slack.users_info(user=user_id)
    
    if response.get("ok"):
        user = response.get("user", {})
        profile = user.get("profile", {})
        
        info = []
        info.append(f"ID: {user.get('id', 'N/A')}")
        info.append(f"Name: {user.get('name', 'N/A')}")
        info.append(f"Real Name: {profile.get('real_name', 'N/A')}")
        info.append(f"Email: {profile.get('email', 'N/A')}")
        info.append(f"Title: {profile.get('title', 'N/A')}")
        info.append(f"Status: {profile.get('status_text', 'N/A')}")
        info.append(f"Timezone: {user.get('tz', 'N/A')}")
        
        return "\n".join(info)
    else:
        return f"Error: {response.get('error', 'unknown error')}"


async def find_user_by_email(
    email: str, ctx: Context | None = None
) -> str:
    """Find a user by their email address."""
    slack = _get_slack_bot(ctx)
    response = await slack.users_lookupByEmail(email=email)
    
    if response.get("ok"):
        user = response.get("user", {})
        return f"User found: {user.get('id')} | {user.get('name')} | {user.get('real_name', '')}"
    else:
        return f"Error: {response.get('error', 'user not found')}"


# =============================================================================
# MESSAGING TOOLS
# =============================================================================

async def send_message(
    channel: str, text: str, ctx: Context | None = None
) -> str:
    """Send a message to a Slack channel."""
    slack = _get_slack_bot(ctx)
    resp = await slack.chat_postMessage(channel=channel, text=text)
    
    if resp.get("ok"):
        return f"Message sent successfully. Timestamp: {resp.get('ts', '')}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def reply_to_message(
    channel: str, thread_ts: str, text: str, ctx: Context | None = None
) -> str:
    """Reply to a specific thread in a Slack channel."""
    slack = _get_slack_bot(ctx)
    resp = await slack.chat_postMessage(
        channel=channel, text=text, thread_ts=thread_ts
    )
    
    if resp.get("ok"):
        return f"Reply sent successfully. Timestamp: {resp.get('ts', '')}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def delete_message(
    channel: str, ts: str, ctx: Context | None = None
) -> str:
    """Delete a message from a Slack channel."""
    slack = _get_slack_bot(ctx)
    resp = await slack.chat_delete(channel=channel, ts=ts)
    
    if resp.get("ok"):
        return "Message deleted successfully"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def schedule_message(
    channel: str, text: str, post_at: int, ctx: Context | None = None
) -> str:
    """Schedule a message for later delivery."""
    slack = _get_slack_bot(ctx)
    resp = await slack.chat_scheduleMessage(
        channel=channel, text=text, post_at=post_at
    )
    
    if resp.get("ok"):
        return f"Message scheduled successfully. ID: {resp.get('scheduled_message_id', '')}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


# =============================================================================
# REACTION & INTERACTION TOOLS
# =============================================================================

async def add_reaction(
    channel: str, timestamp: str, name: str, ctx: Context | None = None
) -> str:
    """Add a reaction emoji to a message in Slack."""
    slack = _get_slack_bot(ctx)
    resp = await slack.reactions_add(channel=channel, timestamp=timestamp, name=name)
    
    if resp.get("ok"):
        return "Reaction added successfully"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def pin_message(
    channel: str, timestamp: str, ctx: Context | None = None
) -> str:
    """Pin a message to a channel."""
    slack = _get_slack_bot(ctx)
    resp = await slack.pins_add(channel=channel, timestamp=timestamp)
    
    if resp.get("ok"):
        return "Message pinned successfully"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def unpin_message(
    channel: str, timestamp: str, ctx: Context | None = None
) -> str:
    """Unpin a message from a channel."""
    slack = _get_slack_bot(ctx)
    resp = await slack.pins_remove(channel=channel, timestamp=timestamp)
    
    if resp.get("ok"):
        return "Message unpinned successfully"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


# =============================================================================
# FILE OPERATIONS
# =============================================================================

async def upload_file(
    channels: str, 
    file_path: str = None, 
    content: str = None,
    filename: str = None,
    title: str = None,
    initial_comment: str = None,
    ctx: Context | None = None
) -> str:
    """Upload a file to Slack channels."""
    slack = _get_slack_bot(ctx)
    
    kwargs = {"channels": channels}
    if file_path:
        kwargs["file"] = file_path
    if content:
        kwargs["content"] = content
    if filename:
        kwargs["filename"] = filename
    if title:
        kwargs["title"] = title
    if initial_comment:
        kwargs["initial_comment"] = initial_comment
    
    resp = await slack.files_upload(**kwargs)
    
    if resp.get("ok"):
        file_info = resp.get("file", {})
        return f"File uploaded successfully. ID: {file_info.get('id', '')}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def list_files(
    user: str = None, 
    channel: str = None, 
    types: str = "all", 
    count: int = 100,
    ctx: Context | None = None
) -> str:
    """List files in the workspace."""
    slack = _get_slack_bot(ctx)
    
    kwargs = {"types": types, "count": count}
    if user:
        kwargs["user"] = user
    if channel:
        kwargs["channel"] = channel
    
    resp = await slack.files_list(**kwargs)
    
    if resp.get("ok"):
        files = resp.get("files", [])
        lines = []
        for file in files:
            lines.append(f"ID: {file.get('id')} | Name: {file.get('name', 'N/A')} | Type: {file.get('filetype', 'N/A')}")
        return "\n".join(lines) if lines else "No files found"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


# =============================================================================
# CONVERSATION & HISTORY TOOLS
# =============================================================================

async def get_conversation_history(
    channel: str, 
    limit: int = 100, 
    oldest: str = None, 
    latest: str = None,
    ctx: Context | None = None
) -> str:
    """Get conversation history from a channel."""
    slack = _get_slack_bot(ctx)
    
    kwargs = {"channel": channel, "limit": limit}
    if oldest:
        kwargs["oldest"] = oldest
    if latest:
        kwargs["latest"] = latest
    
    resp = await slack.conversations_history(**kwargs)
    
    if resp.get("ok"):
        messages = resp.get("messages", [])
        lines = []
        for msg in messages:
            user = msg.get("user", "unknown")
            text = msg.get("text", "")
            ts = msg.get("ts", "")
            lines.append(f"[{ts}] {user}: {text}")
        return "\n".join(lines) if lines else "No messages found"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def get_thread_replies(
    channel: str, ts: str, limit: int = 100, ctx: Context | None = None
) -> str:
    """Get replies in a message thread."""
    slack = _get_slack_bot(ctx)
    resp = await slack.conversations_replies(channel=channel, ts=ts, limit=limit)
    
    if resp.get("ok"):
        messages = resp.get("messages", [])
        lines = []
        for msg in messages:
            user = msg.get("user", "unknown")
            text = msg.get("text", "")
            thread_ts = msg.get("thread_ts", "")
            lines.append(f"[{thread_ts}] {user}: {text}")
        return "\n".join(lines) if lines else "No replies found"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


# =============================================================================
# SEARCH TOOLS (USER TOKEN REQUIRED)
# =============================================================================

async def search_messages(
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
    ctx: Context | None = None,
) -> str:
    """Search for messages across Slack workspace (requires user token)."""
    slack = _get_slack_user(ctx)
    resp = await slack.search_messages(
        query=query, sort=sort, sort_dir=sort_dir, count=count
    )

    if resp.get("ok"):
        messages = resp.get("messages", {}).get("matches", [])
        result = []
        for msg in messages:
            result.append(f"Channel: {msg.get('channel', {}).get('name', 'unknown')}")
            result.append(f"User: {msg.get('user', 'unknown')}")
            result.append(f"Text: {msg.get('text', '')}")
            result.append("---")
        return "\n".join(result) if result else "No messages found"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


# =============================================================================
# USER STATUS & REMINDER TOOLS (USER TOKEN REQUIRED)
# =============================================================================

async def set_user_status(
    status_text: str,
    status_emoji: str = "",
    status_expiration: int = 0,
    ctx: Context | None = None,
) -> str:
    """Set user status (requires user token)."""
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


async def create_reminder(
    text: str,
    time: str,
    user: str = "",
    ctx: Context | None = None,
) -> str:
    """Create a reminder (requires user token)."""
    slack = _get_slack_user(ctx)
    resp = await slack.reminders_add(text=text, time=time, user=user if user else None)

    if resp.get("ok"):
        reminder = resp.get("reminder", {})
        return f"Reminder created with ID: {reminder.get('id', 'unknown')}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


# =============================================================================
# CHANNEL MANAGEMENT TOOLS
# =============================================================================

async def create_channel(
    name: str, is_private: bool = False, ctx: Context | None = None
) -> str:
    """Create a new channel."""
    slack = _get_slack_bot(ctx)
    resp = await slack.conversations_create(name=name, is_private=is_private)
    
    if resp.get("ok"):
        channel = resp.get("channel", {})
        return f"Channel created successfully. ID: {channel.get('id')} | Name: #{channel.get('name')}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def archive_channel(
    channel: str, ctx: Context | None = None
) -> str:
    """Archive a channel."""
    slack = _get_slack_bot(ctx)
    resp = await slack.conversations_archive(channel=channel)
    
    if resp.get("ok"):
        return f"Channel {channel} archived successfully"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def set_channel_topic(
    channel: str, topic: str, ctx: Context | None = None
) -> str:
    """Set a channel's topic."""
    slack = _get_slack_bot(ctx)
    resp = await slack.conversations_setTopic(channel=channel, topic=topic)
    
    if resp.get("ok"):
        return f"Topic set successfully for {channel}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def set_channel_description(
    channel: str, purpose: str, ctx: Context | None = None
) -> str:
    """Set a channel's description/purpose."""
    slack = _get_slack_bot(ctx)
    resp = await slack.conversations_setPurpose(channel=channel, purpose=purpose)
    
    if resp.get("ok"):
        return f"Description set successfully for {channel}"
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def join_channel(
    channel: str, ctx: Context | None = None
) -> str:
    """Join a channel with the bot (requires bot to be invited first)."""
    slack = _get_slack_bot(ctx)
    resp = await slack.conversations_join(channel=channel)

    if resp.get("ok"):
        return f"Successfully joined channel {channel}"
    else:
        return f"Error joining channel: {resp.get('error', 'unknown error')}"


# =============================================================================
# WORKSPACE INFO TOOLS
# =============================================================================

async def get_team_info(ctx: Context | None = None) -> str:
    """Get information about the team/workspace."""
    slack = _get_slack_bot(ctx)
    resp = await slack.team_info()
    
    if resp.get("ok"):
        team = resp.get("team", {})
        info = []
        info.append(f"Name: {team.get('name', 'N/A')}")
        info.append(f"Domain: {team.get('domain', 'N/A')}")
        info.append(f"Email Domain: {team.get('email_domain', 'N/A')}")
        return "\n".join(info)
    else:
        return f"Error: {resp.get('error', 'unknown error')}"


async def list_emojis(ctx: Context | None = None) -> str:
    """List custom emojis in the workspace."""
    slack = _get_slack_bot(ctx)
    resp = await slack.emoji_list()
    
    if resp.get("ok"):
        emojis = resp.get("emoji", {})
        lines = [f":{name}: - {url}" for name, url in emojis.items()]
        return "\n".join(lines) if lines else "No custom emojis found"
    else:
        return f"Error: {resp.get('error', 'unknown error')}" 