"""
Event bus implementation for the address formatter.

This module provides the core event system functionality,
including the EventBus class for event publishing and subscription.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Protocol, Optional, TypeVar, Generic, Type


@dataclass
class Event:
    """
    Base class for all events in the system.
    
    All events should inherit from this class and add specific
    properties relevant to the event type.
    """
    event_type: str
    source: str
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    payload: Dict[str, Any] = field(default_factory=dict)


class EventSubscriber(Protocol):
    """
    Protocol for event subscribers.
    
    Any callable that matches this signature can be used as an event subscriber.
    """
    def __call__(self, event: Event) -> None:
        """
        Handle an event.
        
        Args:
            event: The event to handle
        """
        ...


T = TypeVar('T', bound=Event)


class EventBus:
    """
    Event bus for publishing and subscribing to events.
    
    The EventBus manages event subscriptions and dispatches events
    to appropriate subscribers when they are published.
    """
    
    def __init__(self):
        """Initialize the event bus with empty subscriber lists."""
        self._subscribers: Dict[str, List[EventSubscriber]] = {}
        self._subscribers_by_type: Dict[Type[Event], List[EventSubscriber]] = {}
    
    def subscribe(self, 
                 event_type: str, 
                 subscriber: EventSubscriber) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The event type to subscribe to
            subscriber: The subscriber function to call when an event is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(subscriber)
    
    def subscribe_to_type(self, 
                         event_class: Type[T], 
                         subscriber: Callable[[T], None]) -> None:
        """
        Subscribe to events of a specific class.
        
        This allows for type-safe event handling with proper type checking.
        
        Args:
            event_class: The event class to subscribe to
            subscriber: The subscriber function to call when an event is published
        """
        if event_class not in self._subscribers_by_type:
            self._subscribers_by_type[event_class] = []
        self._subscribers_by_type[event_class].append(subscriber)
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish
        """
        # Notify subscribers by event type string
        for subscriber in self._subscribers.get(event.event_type, []):
            subscriber(event)
        
        # Notify subscribers by event class
        for event_class, subscribers in self._subscribers_by_type.items():
            if isinstance(event, event_class):
                for subscriber in subscribers:
                    subscriber(event)
    
    def unsubscribe(self, 
                   event_type: str, 
                   subscriber: Optional[EventSubscriber] = None) -> None:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: The event type to unsubscribe from
            subscriber: The subscriber to remove (if None, removes all subscribers)
        """
        if event_type in self._subscribers:
            if subscriber is None:
                self._subscribers[event_type] = []
            else:
                self._subscribers[event_type] = [
                    s for s in self._subscribers[event_type] if s != subscriber
                ]
    
    def unsubscribe_from_type(self, 
                             event_class: Type[Event], 
                             subscriber: Optional[Callable[[Any], None]] = None) -> None:
        """
        Unsubscribe from events of a specific class.
        
        Args:
            event_class: The event class to unsubscribe from
            subscriber: The subscriber to remove (if None, removes all subscribers)
        """
        if event_class in self._subscribers_by_type:
            if subscriber is None:
                self._subscribers_by_type[event_class] = []
            else:
                self._subscribers_by_type[event_class] = [
                    s for s in self._subscribers_by_type[event_class] if s != subscriber
                ]
    
    def clear(self) -> None:
        """Clear all subscriptions."""
        self._subscribers = {}
        self._subscribers_by_type = {}


# Create a singleton instance of the event bus
event_bus = EventBus() 