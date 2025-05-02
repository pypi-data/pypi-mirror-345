#!/usr/bin/env python3
"""
Google Calendar MCP Server with Service Account authentication
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from modelcontextprotocol.server import Server
from modelcontextprotocol.server.stdio import StdioServerTransport
from modelcontextprotocol.types import (
    CallToolRequest,
    CallToolResponse,
    Content,
    ListToolsRequest,
    ListToolsResponse,
    Tool,
)

from tools.calendar_tools import (
    create_event,
    delete_event,
    list_calendars,
    list_colors,
    list_events,
    search_events,
    update_event,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("google-calendar-mcp")


class GoogleCalendarMCPServer:
    """Google Calendar MCP Server implementation using Service Account authentication"""

    def __init__(self) -> None:
        """Initialize the MCP server and Google Calendar service"""
        self.server = Server(
            name="google-calendar",
            version="1.0.0",
            description="Google Calendar MCP Server with Service Account authentication",
        )
        self.calendar_service = None

    async def initialize(self) -> bool:
        """Initialize the Google Calendar service with Service Account authentication"""
        try:
            # Get the path to the service account JSON file from environment variable
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if not credentials_path:
                logger.error(
                    "GOOGLE_APPLICATION_CREDENTIALS environment variable not set. "
                    "Please set it to the path of your service account JSON file."
                )
                return False

            # Create credentials from the service account file
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/calendar"],
            )

            # Build the Google Calendar service
            self.calendar_service = build("calendar", "v3", credentials=credentials)
            logger.info("Successfully initialized Google Calendar service")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            return False

    def register_handlers(self) -> None:
        """Register request handlers for the MCP server"""
        # Register the ListTools handler
        self.server.set_request_handler(
            ListToolsRequest, self.handle_list_tools_request
        )

        # Register the CallTool handler
        self.server.set_request_handler(
            CallToolRequest, self.handle_call_tool_request
        )

    async def handle_list_tools_request(
        self, _: ListToolsRequest
    ) -> ListToolsResponse:
        """Handle ListTools request by returning the list of available tools"""
        tools = [
            Tool(
                name="list-calendars",
                description="List all available calendars",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="list-events",
                description="List events from a calendar",
                input_schema={
                    "type": "object",
                    "properties": {
                        "calendarId": {
                            "type": "string",
                            "description": "ID of the calendar to list events from (use 'primary' for the main calendar)",
                        },
                        "timeMin": {
                            "type": "string",
                            "description": "Start time of the interval (RFC3339 timestamp)",
                        },
                        "timeMax": {
                            "type": "string",
                            "description": "End time of the interval (RFC3339 timestamp)",
                        },
                        "maxResults": {
                            "type": "integer",
                            "description": "Maximum number of events to return",
                        },
                    },
                    "required": ["calendarId"],
                },
            ),
            Tool(
                name="search-events",
                description="Search for events in a calendar by text query",
                input_schema={
                    "type": "object",
                    "properties": {
                        "calendarId": {
                            "type": "string",
                            "description": "ID of the calendar to search events in (use 'primary' for the main calendar)",
                        },
                        "query": {
                            "type": "string",
                            "description": "Free text search terms to find events that match",
                        },
                        "timeMin": {
                            "type": "string",
                            "description": "Start time of the interval (RFC3339 timestamp)",
                        },
                        "timeMax": {
                            "type": "string",
                            "description": "End time of the interval (RFC3339 timestamp)",
                        },
                        "maxResults": {
                            "type": "integer",
                            "description": "Maximum number of events to return",
                        },
                    },
                    "required": ["calendarId", "query"],
                },
            ),
            Tool(
                name="list-colors",
                description="List available color IDs and their meanings for calendar events",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="create-event",
                description="Create a new calendar event",
                input_schema={
                    "type": "object",
                    "properties": {
                        "calendarId": {
                            "type": "string",
                            "description": "ID of the calendar to create the event in (use 'primary' for the main calendar)",
                        },
                        "summary": {
                            "type": "string",
                            "description": "Title of the event",
                        },
                        "description": {
                            "type": "string",
                            "description": "Description/notes for the event (optional)",
                        },
                        "start": {
                            "type": "string",
                            "description": "Start time (RFC3339 timestamp) or date (YYYY-MM-DD)",
                        },
                        "end": {
                            "type": "string",
                            "description": "End time (RFC3339 timestamp) or date (YYYY-MM-DD)",
                        },
                        "timeZone": {
                            "type": "string",
                            "description": "Timezone of the event start/end times (e.g., America/Los_Angeles)",
                        },
                        "location": {
                            "type": "string",
                            "description": "Location of the event (optional)",
                        },
                        "colorId": {
                            "type": "string",
                            "description": "Color ID for the event (optional, use list-colors to see available IDs)",
                        },
                    },
                    "required": ["calendarId", "summary", "start", "end", "timeZone"],
                },
            ),
            Tool(
                name="update-event",
                description="Update an existing calendar event",
                input_schema={
                    "type": "object",
                    "properties": {
                        "calendarId": {
                            "type": "string",
                            "description": "ID of the calendar containing the event",
                        },
                        "eventId": {
                            "type": "string",
                            "description": "ID of the event to update",
                        },
                        "summary": {
                            "type": "string",
                            "description": "New title for the event (optional)",
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the event (optional)",
                        },
                        "start": {
                            "type": "string",
                            "description": "New start time (RFC3339 timestamp) or date (YYYY-MM-DD) (optional)",
                        },
                        "end": {
                            "type": "string",
                            "description": "New end time (RFC3339 timestamp) or date (YYYY-MM-DD) (optional)",
                        },
                        "timeZone": {
                            "type": "string",
                            "description": "Timezone for the start/end times (IANA format, e.g., America/Los_Angeles)",
                        },
                        "location": {
                            "type": "string",
                            "description": "New location for the event (optional)",
                        },
                        "colorId": {
                            "type": "string",
                            "description": "New color ID for the event (optional)",
                        },
                    },
                    "required": ["calendarId", "eventId", "timeZone"],
                },
            ),
            Tool(
                name="delete-event",
                description="Delete a calendar event",
                input_schema={
                    "type": "object",
                    "properties": {
                        "calendarId": {
                            "type": "string",
                            "description": "ID of the calendar containing the event",
                        },
                        "eventId": {
                            "type": "string",
                            "description": "ID of the event to delete",
                        },
                    },
                    "required": ["calendarId", "eventId"],
                },
            ),
        ]
        return ListToolsResponse(tools=tools)

    async def handle_call_tool_request(
        self, request: CallToolRequest
    ) -> CallToolResponse:
        """Handle CallTool request by executing the requested tool"""
        if not self.calendar_service:
            return CallToolResponse(
                content=[
                    Content(
                        type="text",
                        text="Google Calendar service is not initialized. Please check your service account credentials.",
                    )
                ]
            )

        tool_name = request.params.name
        args = request.params.arguments

        try:
            if tool_name == "list-calendars":
                result = await list_calendars(self.calendar_service)
            elif tool_name == "list-events":
                result = await list_events(self.calendar_service, args)
            elif tool_name == "search-events":
                result = await search_events(self.calendar_service, args)
            elif tool_name == "list-colors":
                result = await list_colors(self.calendar_service)
            elif tool_name == "create-event":
                result = await create_event(self.calendar_service, args)
            elif tool_name == "update-event":
                result = await update_event(self.calendar_service, args)
            elif tool_name == "delete-event":
                result = await delete_event(self.calendar_service, args)
            else:
                return CallToolResponse(
                    content=[
                        Content(
                            type="text",
                            text=f"Unknown tool: {tool_name}",
                        )
                    ]
                )

            return CallToolResponse(
                content=[
                    Content(
                        type="text",
                        text=result,
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return CallToolResponse(
                content=[
                    Content(
                        type="text",
                        text=f"Error executing tool {tool_name}: {str(e)}",
                    )
                ]
            )

    async def start(self) -> None:
        """Start the MCP server"""
        # Initialize the Google Calendar service
        if not await self.initialize():
            logger.error("Failed to initialize. Exiting.")
            return

        # Register request handlers
        self.register_handlers()

        # Connect to the transport
        transport = StdioServerTransport()
        await self.server.connect(transport)
        logger.info("Server started and connected to transport")


async def main() -> None:
    """Main entry point for the MCP server"""
    server = GoogleCalendarMCPServer()
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)