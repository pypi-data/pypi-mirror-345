"""
Predefined event types for the address formatter.

This module defines specific event types that are used
throughout the address formatter system.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .bus import Event


@dataclass
class FormatStartEvent(Event):
    """Event fired when address formatting begins."""
    
    source: str = ""
    components: Dict[str, Any] = field(default_factory=dict)
    
    def __init__(self, source: str, components: Dict[str, Any]):
        super().__init__(
            event_type="format.start",
            source=source,
            payload={"components": components}
        )
        self.source = source
        self.components = components


@dataclass
class FormatCompleteEvent(Event):
    """Event fired when address formatting completes."""
    
    source: str = ""
    components: Dict[str, Any] = field(default_factory=dict)
    formatted_address: str = ""
    
    def __init__(self, source: str, components: Dict[str, Any], formatted_address: str):
        super().__init__(
            event_type="format.complete",
            source=source,
            payload={
                "components": components,
                "formatted_address": formatted_address
            }
        )
        self.source = source
        self.components = components
        self.formatted_address = formatted_address


@dataclass
class ComponentNormalizedEvent(Event):
    """Event fired when an address component is normalized."""
    
    source: str = ""
    original_component: str = ""
    normalized_component: str = ""
    
    def __init__(self, source: str, original: str, normalized: str):
        super().__init__(
            event_type="component.normalized",
            source=source,
            payload={
                "original": original,
                "normalized": normalized
            }
        )
        self.source = source
        self.original_component = original
        self.normalized_component = normalized


@dataclass
class TemplateSelectedEvent(Event):
    """Event fired when a template is selected for an address."""
    
    source: str = ""
    country_code: str = ""
    template_id: str = ""
    
    def __init__(self, source: str, country_code: str, template_id: str):
        super().__init__(
            event_type="template.selected",
            source=source,
            payload={
                "country_code": country_code,
                "template_id": template_id
            }
        )
        self.source = source
        self.country_code = country_code
        self.template_id = template_id


@dataclass
class RenderCompleteEvent(Event):
    """Event fired when template rendering completes."""
    
    source: str = ""
    template_id: str = ""
    rendered_text: str = ""
    
    def __init__(self, source: str, template_id: str, rendered_text: str):
        super().__init__(
            event_type="render.complete",
            source=source,
            payload={
                "template_id": template_id,
                "rendered_text": rendered_text
            }
        )
        self.source = source
        self.template_id = template_id
        self.rendered_text = rendered_text


@dataclass
class ErrorEvent(Event):
    """Event fired when an error occurs during formatting."""
    
    source: str = ""
    error_type: str = ""
    message: str = ""
    exception: Optional[Exception] = None
    
    def __init__(self, source: str, error_type: str, message: str, 
                 exception: Optional[Exception] = None):
        super().__init__(
            event_type="error",
            source=source,
            payload={
                "error_type": error_type,
                "message": message,
                "exception": str(exception) if exception else None
            }
        )
        self.source = source
        self.error_type = error_type
        self.message = message
        self.exception = exception 