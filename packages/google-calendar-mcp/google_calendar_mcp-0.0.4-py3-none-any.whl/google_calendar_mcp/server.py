#!/usr/bin/env python3
"""
Google Calendar MCP Server entry point
"""

import asyncio
import logging
import os
import pathlib
import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Dict, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from mcp.server.fastmcp import FastMCP, Context

# calendar_tools のインポートはそのまま
from .calendar_tools import (
    create_event,
    delete_event,
    list_calendars,
    list_colors,
    list_events,
    search_events,
    update_event,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("google-calendar-mcp")

# --- Lifespan Context ---
@dataclass
class AppContext:
    calendar_service: Optional[Resource] = None

# --- Lifespan Management ---
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    context = AppContext()
    try:
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            logger.error(
                "GOOGLE_APPLICATION_CREDENTIALS environment variable not set. "
                "Please set it to the path of your service account JSON file."
            )
            yield context # 初期化失敗時は None のまま yield
            return

        # パスの先頭が~や相対パスの場合も展開する
        credentials_path = str(pathlib.Path(credentials_path).expanduser().resolve())

        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )
        context.calendar_service = build("calendar", "v3", credentials=credentials)
        logger.info("Successfully initialized Google Calendar service")
        yield context # 初期化成功時は service を含む context を yield
    except Exception as e:
        logger.error(f"Failed to initialize Google Calendar service: {e}")
        yield context # 例外発生時も None のまま yield
    finally:
        # Cleanup (もし必要なら)
        logger.info("Shutting down Google Calendar MCP server")


# --- MCP Server Initialization ---
mcp = FastMCP(
    "google-calendar",
    version="1.0.0",
    description="Google Calendar MCP Server with Service Account authentication",
    lifespan=app_lifespan
)

# --- Tool Definitions ---

@mcp.tool()
async def list_calendars_tool(ctx: Context) -> Any:
    """List all available calendars"""
    app_context: AppContext = ctx.request_context.lifespan_context
    if not app_context.calendar_service:
        return "Error: Google Calendar service not initialized."
    try:
        # calendar_tools.list_calendars は引数なしと仮定
        return await list_calendars(app_context.calendar_service)
    except Exception as e:
        logger.error(f"Error in list_calendars_tool: {e}")
        return f"Error executing list-calendars: {str(e)}"

@mcp.tool(name="list-events") # MCP ツール名を指定
async def list_events_tool(
    calendarId: str,
    timeMin: Optional[str] = None,
    timeMax: Optional[str] = None,
    maxResults: Optional[int] = None,
    ctx: Context = None
) -> Any:
    """List events from a calendar"""
    app_context: AppContext = ctx.request_context.lifespan_context
    if not app_context.calendar_service:
        return "Error: Google Calendar service not initialized."
    args = {
        "calendarId": calendarId,
        "timeMin": timeMin,
        "timeMax": timeMax,
        "maxResults": maxResults,
    }
    args = {k: v for k, v in args.items() if v is not None}
    try:
        return await list_events(app_context.calendar_service, args)
    except Exception as e:
        logger.error(f"Error in list_events_tool: {e}")
        return f"Error executing list-events: {str(e)}"

@mcp.tool(name="search-events") # MCP ツール名を指定
async def search_events_tool(
    calendarId: str,
    query: str,
    timeMin: Optional[str] = None,
    timeMax: Optional[str] = None,
    maxResults: Optional[int] = None,
    ctx: Context = None
) -> Any:
    """Search for events in a calendar by text query"""
    app_context: AppContext = ctx.request_context.lifespan_context
    if not app_context.calendar_service:
        return "Error: Google Calendar service not initialized."
    args = {
        "calendarId": calendarId,
        "query": query,
        "timeMin": timeMin,
        "timeMax": timeMax,
        "maxResults": maxResults,
    }
    args = {k: v for k, v in args.items() if v is not None}
    try:
        return await search_events(app_context.calendar_service, args)
    except Exception as e:
        logger.error(f"Error in search_events_tool: {e}")
        return f"Error executing search-events: {str(e)}"

@mcp.tool(name="list-colors") # MCP ツール名を指定
async def list_colors_tool(ctx: Context) -> Any:
    """List available color IDs and their meanings for calendar events"""
    app_context: AppContext = ctx.request_context.lifespan_context
    if not app_context.calendar_service:
        return "Error: Google Calendar service not initialized."
    try:
        # calendar_tools.list_colors は引数なしと仮定
        return await list_colors(app_context.calendar_service)
    except Exception as e:
        logger.error(f"Error in list_colors_tool: {e}")
        return f"Error executing list-colors: {str(e)}"

@mcp.tool(name="create-event") # MCP ツール名を指定
async def create_event_tool(
    calendarId: str,
    summary: str,
    start: str, # RFC3339 or YYYY-MM-DD
    end: str,   # RFC3339 or YYYY-MM-DD
    timeZone: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    colorId: Optional[str] = None,
    ctx: Context = None
) -> Any:
    """Create a new calendar event"""
    app_context: AppContext = ctx.request_context.lifespan_context
    if not app_context.calendar_service:
        return "Error: Google Calendar service not initialized."

    event_body = {'summary': summary, 'start': {}, 'end': {}}
    if 'T' in start:
        event_body['start']['dateTime'] = start
        event_body['start']['timeZone'] = timeZone
    else:
        event_body['start']['date'] = start
    if 'T' in end:
        event_body['end']['dateTime'] = end
        event_body['end']['timeZone'] = timeZone
    else:
        event_body['end']['date'] = end

    if description: event_body['description'] = description
    if location: event_body['location'] = location
    if colorId: event_body['colorId'] = colorId

    args = {"calendarId": calendarId, "body": event_body}
    try:
        # calendar_tools.create_event が calendar_service と args を受け取ると仮定
        return await create_event(app_context.calendar_service, args)
    except Exception as e:
        logger.error(f"Error in create_event_tool: {e}")
        return f"Error executing create-event: {str(e)}"

@mcp.tool(name="update-event") # MCP ツール名を指定
async def update_event_tool(
    calendarId: str,
    eventId: str,
    # timeZone は API body に含めるため、ツール引数からは削除
    summary: Optional[str] = None,
    description: Optional[str] = None,
    start: Optional[str] = None, # RFC3339 or YYYY-MM-DD
    end: Optional[str] = None,   # RFC3339 or YYYY-MM-DD
    timeZone: Optional[str] = None, # start/end が dateTime の場合に必要
    location: Optional[str] = None,
    colorId: Optional[str] = None,
    ctx: Context = None
) -> Any:
    """Update an existing calendar event"""
    app_context: AppContext = ctx.request_context.lifespan_context
    if not app_context.calendar_service:
        return "Error: Google Calendar service not initialized."

    update_body = {}
    if summary is not None: update_body['summary'] = summary
    if description is not None: update_body['description'] = description
    if location is not None: update_body['location'] = location
    if colorId is not None: update_body['colorId'] = colorId

    if start:
        update_body['start'] = {}
        if 'T' in start:
            if not timeZone: return "Error: timeZone is required when updating start dateTime."
            update_body['start']['dateTime'] = start
            update_body['start']['timeZone'] = timeZone
        else:
            update_body['start']['date'] = start
    if end:
        update_body['end'] = {}
        if 'T' in end:
            if not timeZone: return "Error: timeZone is required when updating end dateTime."
            update_body['end']['dateTime'] = end
            update_body['end']['timeZone'] = timeZone
        else:
            update_body['end']['date'] = end

    if not update_body:
        return "Error: No fields provided for update."

    args = {"calendarId": calendarId, "eventId": eventId, "body": update_body}
    try:
        # calendar_tools.update_event が calendar_service と args を受け取ると仮定
        return await update_event(app_context.calendar_service, args)
    except Exception as e:
        logger.error(f"Error in update_event_tool: {e}")
        return f"Error executing update-event: {str(e)}"

@mcp.tool(name="delete-event") # MCP ツール名を指定
async def delete_event_tool(
    calendarId: str,
    eventId: str,
    ctx: Context = None
) -> Any:
    """Delete a calendar event"""
    app_context: AppContext = ctx.request_context.lifespan_context
    if not app_context.calendar_service:
        return "Error: Google Calendar service not initialized."
    args = {"calendarId": calendarId, "eventId": eventId}
    try:
        # calendar_tools.delete_event が calendar_service と args を受け取ると仮定
        return await delete_event(app_context.calendar_service, args)
    except Exception as e:
        logger.error(f"Error in delete_event_tool: {e}")
        return f"Error executing delete-event: {str(e)}"


# --- Main Execution ---
def main() -> None:
    """Entry point for the MCP server"""
    try:
        mcp.run() # FastMCP インスタンスを実行
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Unhandled exception during server run: {e}")
        sys.exit(1)

# スクリプトとして直接実行された場合にも main を呼び出す
if __name__ == "__main__":
    main()