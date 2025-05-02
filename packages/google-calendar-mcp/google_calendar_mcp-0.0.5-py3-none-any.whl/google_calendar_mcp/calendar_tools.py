"""
Google Calendar API tool implementations
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import Resource

logger = logging.getLogger("google-calendar-mcp.tools")


async def list_calendars(service: Resource) -> str:
    """
    List all available calendars
    
    Args:
        service: Google Calendar API service instance
        
    Returns:
        Formatted string with calendar information
    """
    try:
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get("items", [])
        
        if not calendars:
            return "No calendars found."
        
        result = []
        for calendar in calendars:
            result.append(f"{calendar.get('summary', 'Untitled')} ({calendar.get('id', 'no-id')})")
        
        return "\n".join(result)
    except Exception as e:
        logger.error(f"Error listing calendars: {e}")
        raise


async def list_events(service: Resource, args: Dict[str, Any]) -> str:
    """
    List events from a calendar
    
    Args:
        service: Google Calendar API service instance
        args: Dictionary containing calendarId and optional parameters
        
    Returns:
        Formatted string with event information
    """
    try:
        calendar_id = args.get("calendarId", "primary")
        time_min = args.get("timeMin")
        time_max = args.get("timeMax")
        max_results = args.get("maxResults", 10)
        
        # Build request parameters
        params = {
            "calendarId": calendar_id,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        
        events_result = service.events().list(**params).execute()
        events = events_result.get("items", [])
        
        if not events:
            return f"No events found for calendar {calendar_id}."
        
        return format_event_list(events)
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise


async def search_events(service: Resource, args: Dict[str, Any]) -> str:
    """
    Search for events in a calendar by text query
    
    Args:
        service: Google Calendar API service instance
        args: Dictionary containing calendarId, query and optional parameters
        
    Returns:
        Formatted string with event information
    """
    try:
        calendar_id = args.get("calendarId", "primary")
        query = args.get("query", "")
        time_min = args.get("timeMin")
        time_max = args.get("timeMax")
        max_results = args.get("maxResults", 10)
        
        # Build request parameters
        params = {
            "calendarId": calendar_id,
            "q": query,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        
        events_result = service.events().list(**params).execute()
        events = events_result.get("items", [])
        
        if not events:
            return f"No events found matching '{query}' in calendar {calendar_id}."
        
        return format_event_list(events)
    except Exception as e:
        logger.error(f"Error searching events: {e}")
        raise


async def list_colors(service: Resource) -> str:
    """
    List available color IDs and their meanings for calendar events
    
    Args:
        service: Google Calendar API service instance
        
    Returns:
        Formatted string with color information
    """
    try:
        colors_result = service.colors().get().execute()
        event_colors = colors_result.get("event", {})
        
        if not event_colors:
            return "No color information available."
        
        result = ["Available event colors:"]
        for color_id, color_info in event_colors.items():
            result.append(
                f"Color ID: {color_id} - {color_info.get('background')} (background) / "
                f"{color_info.get('foreground')} (foreground)"
            )
        
        return "\n".join(result)
    except Exception as e:
        logger.error(f"Error listing colors: {e}")
        raise


async def create_event(service: Resource, args: Dict[str, Any]) -> str:
    """
    Create a new calendar event
    
    Args:
        service: Google Calendar API service instance
        args: Dictionary containing event details
        
    Returns:
        Formatted string with created event information
    """
    try:
        calendar_id = args.get("calendarId", "primary")
        summary = args.get("summary")
        description = args.get("description")
        start_time = args.get("start")
        end_time = args.get("end")
        time_zone = args.get("timeZone")
        location = args.get("location")
        color_id = args.get("colorId")
        
        # Create event body
        event_body = {
            "summary": summary,
            "location": location,
            "description": description,
            "colorId": color_id,
        }
        
        # Clean up None values
        event_body = {k: v for k, v in event_body.items() if v is not None}
        
        # Handle start and end times
        if "T" in start_time:  # It's a datetime
            event_body["start"] = {"dateTime": start_time, "timeZone": time_zone}
        else:  # It's a date
            event_body["start"] = {"date": start_time}
            
        if "T" in end_time:  # It's a datetime
            event_body["end"] = {"dateTime": end_time, "timeZone": time_zone}
        else:  # It's a date
            event_body["end"] = {"date": end_time}
        
        # Create the event
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        
        return f"Event created: {event.get('summary')} ({event.get('id')})"
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise


async def update_event(service: Resource, args: Dict[str, Any]) -> str:
    """
    Update an existing calendar event
    
    Args:
        service: Google Calendar API service instance
        args: Dictionary containing event details to update
        
    Returns:
        Formatted string with updated event information
    """
    try:
        calendar_id = args.get("calendarId", "primary")
        event_id = args.get("eventId")
        summary = args.get("summary")
        description = args.get("description")
        start_time = args.get("start")
        end_time = args.get("end")
        time_zone = args.get("timeZone")
        location = args.get("location")
        color_id = args.get("colorId")
        
        # Create event body with only the fields to update
        event_body = {}
        
        if summary is not None:
            event_body["summary"] = summary
        if description is not None:
            event_body["description"] = description
        if location is not None:
            event_body["location"] = location
        if color_id is not None:
            event_body["colorId"] = color_id
            
        # Handle start and end times if provided
        time_changed = start_time is not None or end_time is not None
        
        if start_time is not None:
            if "T" in start_time:  # It's a datetime
                event_body["start"] = {"dateTime": start_time, "timeZone": time_zone}
            else:  # It's a date
                event_body["start"] = {"date": start_time}
                
        if end_time is not None:
            if "T" in end_time:  # It's a datetime
                event_body["end"] = {"dateTime": end_time, "timeZone": time_zone}
            else:  # It's a date
                event_body["end"] = {"date": end_time}
                
        # If only timeZone was changed but not start/end, we need to get the current event first
        if not time_changed and time_zone is not None:
            current_event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            
            if "dateTime" in current_event.get("start", {}):
                event_body["start"] = {
                    "dateTime": current_event["start"]["dateTime"],
                    "timeZone": time_zone
                }
                
            if "dateTime" in current_event.get("end", {}):
                event_body["end"] = {
                    "dateTime": current_event["end"]["dateTime"],
                    "timeZone": time_zone
                }
        
        # Update the event
        updated_event = service.events().patch(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_body
        ).execute()
        
        return f"Event updated: {updated_event.get('summary')} ({updated_event.get('id')})"
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        raise


async def delete_event(service: Resource, args: Dict[str, Any]) -> str:
    """
    Delete a calendar event
    
    Args:
        service: Google Calendar API service instance
        args: Dictionary containing calendarId and eventId
        
    Returns:
        Confirmation message
    """
    try:
        calendar_id = args.get("calendarId", "primary")
        event_id = args.get("eventId")
        
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        
        return f"Event {event_id} deleted from calendar {calendar_id}."
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise


def format_event_list(events: List[Dict[str, Any]]) -> str:
    """
    Format a list of events into a user-friendly string
    
    Args:
        events: List of event dictionaries from Google Calendar API
        
    Returns:
        Formatted string with event information
    """
    result = []
    
    for event in events:
        # Basic event info
        event_id = event.get("id", "no-id")
        summary = event.get("summary", "Untitled")
        
        # Start and end times
        start = event.get("start", {})
        end = event.get("end", {})
        start_time = start.get("dateTime", start.get("date", "unspecified"))
        end_time = end.get("dateTime", end.get("date", "unspecified"))
        
        # Optional fields
        location_info = f"\nLocation: {event.get('location')}" if event.get("location") else ""
        color_info = f"\nColor ID: {event.get('colorId')}" if event.get("colorId") else ""
        
        # Attendees
        attendee_list = ""
        if event.get("attendees"):
            attendees = []
            for attendee in event.get("attendees", []):
                email = attendee.get("email", "no-email")
                status = attendee.get("responseStatus", "unknown")
                attendees.append(f"{email} ({status})")
            attendee_list = f"\nAttendees: {', '.join(attendees)}"
        
        # Reminders
        reminder_info = ""
        if event.get("reminders"):
            reminders = event.get("reminders", {})
            if reminders.get("useDefault"):
                reminder_info = "\nReminders: Using default"
            elif reminders.get("overrides"):
                reminder_details = []
                for reminder in reminders.get("overrides", []):
                    method = reminder.get("method", "unknown")
                    minutes = reminder.get("minutes", "unknown")
                    reminder_details.append(f"{method} {minutes} minutes before")
                reminder_info = f"\nReminders: {', '.join(reminder_details)}"
            else:
                reminder_info = "\nReminders: None"
        
        # Combine all information
        event_info = (
            f"{summary} ({event_id}){location_info}\n"
            f"Start: {start_time}\n"
            f"End: {end_time}{attendee_list}{color_info}{reminder_info}\n"
        )
        
        result.append(event_info)
    
    return "\n".join(result)