"""
Event system for the address formatter.

This module provides an event-driven architecture for the address formatter,
allowing components to communicate and react to various formatting events.
"""

from .bus import EventBus, EventSubscriber, Event, event_bus
from .types import (
    FormatStartEvent,
    FormatCompleteEvent,
    ComponentNormalizedEvent,
    TemplateSelectedEvent,
    RenderCompleteEvent,
    ErrorEvent
)

__all__ = [
    'EventBus', 
    'EventSubscriber', 
    'Event', 
    'event_bus',
    'FormatStartEvent',
    'FormatCompleteEvent',
    'ComponentNormalizedEvent',
    'TemplateSelectedEvent',
    'RenderCompleteEvent',
    'ErrorEvent'
] 