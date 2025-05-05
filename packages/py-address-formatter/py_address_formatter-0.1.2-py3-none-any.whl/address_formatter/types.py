"""
Type definitions for the address formatter.

This module provides type definitions for the address formatter,
including address components, formatting options, and templates.
"""

from typing import Dict, List, Union, Optional, Callable, TypedDict, Literal, Protocol, Any
from enum import Enum
from pydantic import Field, BaseModel

# Basic types
CountryCode = str
LanguageCode = str
ComponentName = str
ComponentValue = str

# Component types
class AddressComponentRequired(TypedDict, total=False):
    """Required address components dictionary type."""
    country_code: str

class AddressComponent(AddressComponentRequired, total=False):
    """Address component dictionary type."""
    # Primary components
    city: str
    country: str
    postcode: str
    road: str
    house_number: str
    state: str
    
    # Secondary components
    suburb: str
    county: str
    district: str
    neighbourhood: str
    state_district: str
    
    # Additional components
    building: str
    floor: str
    unit: str
    po_box: str
    
    # Attention and organization
    attention: str
    organization: str
    
    # Metadata
    language: str

# Formatting options
class FormattingOptions(TypedDict, total=False):
    """Formatting options dictionary type."""
    abbreviate: bool
    append_country: bool
    output: Literal["string", "array"]
    language: str
    
    # Advanced options
    use_template: str
    add_attention: bool
    add_country_code: bool
    extract_from_text: bool
    predict_missing: bool

# Template types
class TemplateData(TypedDict):
    """Template data dictionary type."""
    name: str
    description: str
    template: str
    fallback: Optional[str]
    replace: List[Dict[str, str]]

# Renderer protocol
class AddressRendererProtocol(Protocol):
    """Protocol for address renderers."""
    def render(self, components: AddressComponent, options: FormattingOptions) -> str:
        """Render address components using a template."""
        ...

# Normalizer protocol
class AddressNormalizerProtocol(Protocol):
    """Protocol for address normalizers."""
    def normalize(self, components: Dict[str, str]) -> AddressComponent:
        """Normalize address components."""
        ...

# Formatter protocol
class AddressFormatterProtocol(Protocol):
    """Protocol for address formatters."""
    def format(self, components: Dict[str, str], options: Optional[Dict[str, Any]] = None) -> Union[str, List[str]]:
        """Format address components."""
        ...

# Event types
class EventType(str, Enum):
    """Event types for the address formatter."""
    FORMAT_START = "format.start"
    FORMAT_COMPLETE = "format.complete"
    COMPONENT_NORMALIZED = "component.normalized"
    TEMPLATE_SELECTED = "template.selected"
    RENDER_COMPLETE = "render.complete"
    ERROR = "error"

# Pydantic models for API
class AddressRequestModel(BaseModel):
    """API request model for address formatting."""
    components: Dict[str, str] = Field(..., description="Address components to format")
    options: Optional[Dict[str, Any]] = Field(default={}, description="Formatting options")
    
    class Config:
        schema_extra = {
            "example": {
                "components": {
                    "houseNumber": "123",
                    "road": "Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "country": "United States",
                    "countryCode": "US",
                    "postcode": "12345"
                },
                "options": {
                    "abbreviate": True,
                    "appendCountry": False
                }
            }
        }

class AddressResponseModel(BaseModel):
    """API response model for formatted addresses."""
    formatted: Union[str, List[str]] = Field(..., description="Formatted address")
    components: Dict[str, str] = Field(..., description="Normalized address components")

# Template mapping type
TemplateMapping = Dict[CountryCode, TemplateData]

# Component alias mapping type
AliasMapping = Dict[str, str]

# Event handler type
EventHandler = Callable[[Dict[str, Any]], None]

# Plugin types
class PluginMetadata(BaseModel):
    """Plugin metadata model."""
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")

class PluginProtocol(Protocol):
    """Protocol for address formatter plugins."""
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        ...
    
    def pre_format(self, components: AddressComponent, options: FormattingOptions) -> AddressComponent:
        """Pre-process address components before formatting."""
        ...
    
    def post_format(self, formatted: Union[str, List[str]], components: AddressComponent, options: FormattingOptions) -> Union[str, List[str]]:
        """Post-process formatted address."""
        ... 