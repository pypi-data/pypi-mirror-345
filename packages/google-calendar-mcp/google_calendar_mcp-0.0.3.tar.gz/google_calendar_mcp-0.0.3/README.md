# Google Calendar MCP

Google Calendar MCP is a Model Context Protocol (MCP) server implementation in Python with Service Account authentication.

[日本語 README はこちら](README_ja.md)

## Overview

This project implements the Google Calendar API as an MCP server in Python. It is a port from the original TypeScript version, with authentication changed from OAuth 2.0 to Service Account.

## Features

- Python 3.13 support
- MCP (Model Context Protocol) server implementation
- Google Calendar API integration
- Service Account authentication
- Dependency management with uv

## Requirements

- Python 3.13 or higher
- A Google Cloud Platform project and a valid Service Account
- The Service Account must have access to the Google Calendar API

## Installation

```bash
# Clone the repository
git clone https://github.com/youyo/google-calendar-mcp.git
cd google-calendar-mcp

# Install dependencies
uv pip install -r requirements.txt
```

## Configuration

1. Create a project in Google Cloud Platform and enable the Google Calendar API.
2. Create a Service Account and download the JSON key file.
3. Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of the JSON key file.

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Example: MCP configuration file

To use this server with an MCP client, add the following to your MCP configuration file:

```json
{
  "mcpServers": {
    "google-calendar-mcp": {
      "command": "uvx",
      "args": ["google-calendar-mcp@latest"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json"
      }
    }
  }
}
```

## Usage

```bash
# Start the server
uvx google-calendar-mcp
```

## Available Tools

- `list-calendars`: List all available calendars
- `list-events`: List events from a calendar
- `search-events`: Search for events in a calendar by text query
- `list-colors`: List available color IDs and their meanings for calendar events
- `create-event`: Create a new calendar event
- `update-event`: Update an existing calendar event
- `delete-event`: Delete a calendar event

## License

MIT
