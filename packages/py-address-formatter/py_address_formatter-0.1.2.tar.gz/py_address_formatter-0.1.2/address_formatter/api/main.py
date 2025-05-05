"""
Main API implementation for the address formatter.

This module provides a FastAPI application with endpoints for
formatting addresses, validating address components, and accessing
metrics.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union

from ..formatter import AddressFormatter, format_address
from ..async_api import format_address_async, format_batch_async
from ..config import settings
from .. import __version__
from ..monitoring import MetricsCollector
from .middleware import MetricsMiddleware, RateLimitMiddleware

# Initialize the FastAPI application
app = FastAPI(
    title="Address Formatter API",
    description="API for formatting addresses according to country-specific rules",
    version=__version__,
)

# Add middleware
app.add_middleware(MetricsMiddleware)
app.add_middleware(RateLimitMiddleware, rate_limit=settings.api_rate_limit)

# Initialize the formatter
formatter = AddressFormatter()

# Define request and response models
class AddressRequest(BaseModel):
    """Request model for address formatting."""
    components: Dict[str, str] = Field(..., description="Address components to format")
    options: Optional[Dict[str, Any]] = Field(
        default={}, description="Formatting options"
    )

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

class BatchRequest(BaseModel):
    """Request model for batch address formatting."""
    addresses: List[Dict[str, str]] = Field(..., description="List of address components to format")
    options: Optional[Dict[str, Any]] = Field(
        default={}, description="Formatting options applied to all addresses"
    )

    class Config:
        schema_extra = {
            "example": {
                "addresses": [
                    {
                        "houseNumber": "123",
                        "road": "Main St",
                        "city": "Anytown",
                        "state": "CA",
                        "countryCode": "US",
                        "postcode": "12345"
                    },
                    {
                        "houseNumber": "456",
                        "road": "High St",
                        "city": "Othertown",
                        "state": "NY",
                        "countryCode": "US",
                        "postcode": "67890"
                    }
                ],
                "options": {
                    "abbreviate": True,
                    "appendCountry": False
                }
            }
        }

class FormatResponse(BaseModel):
    """Response model for formatted addresses."""
    formatted: Union[str, List[str]] = Field(..., description="Formatted address")
    components: Dict[str, str] = Field(..., description="Normalized address components")

class BatchResponse(BaseModel):
    """Response model for batch formatted addresses."""
    results: List[Union[str, List[str]]] = Field(..., description="List of formatted addresses")
    
class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")

class HealthResponse(BaseModel):
    """Response model for health checks."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")

# Define API endpoints
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check the health of the service."""
    return {
        "status": "healthy",
        "version": __version__
    }

@app.get("/metrics", tags=["System"])
async def metrics():
    """Get Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/stats", tags=["System"])
async def stats():
    """Get formatter statistics."""
    return MetricsCollector.collect_formatter_metrics(formatter)

@app.post("/format", response_model=FormatResponse, tags=["Formatting"])
async def format_address_endpoint(request: AddressRequest):
    """Format an address according to country-specific rules."""
    try:
        # Format the address
        if settings.enable_async:
            formatted = await format_address_async(request.components, request.options)
        else:
            formatted = format_address(request.components, request.options)
        
        # Get the normalized components
        normalized = formatter.normalizer.normalize(request.components)
        
        return {
            "formatted": formatted,
            "components": normalized
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to format address", "details": str(e)}
        )

@app.post("/batch", response_model=BatchResponse, tags=["Formatting"])
async def batch_format_endpoint(request: BatchRequest):
    """Format multiple addresses in a single request."""
    try:
        # Check batch limits
        if len(request.addresses) > 100:
            raise HTTPException(
                status_code=400,
                detail={"error": "Batch size exceeds limit", "max_size": 100}
            )
        
        # Process the batch
        if settings.enable_async:
            results = await format_batch_async(request.addresses, request.options)
        else:
            # Fallback to synchronous processing
            results = [format_address(addr, request.options) for addr in request.addresses]
        
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to process batch", "details": str(e)}
        )

@app.post("/validate", tags=["Validation"])
async def validate_address(request: AddressRequest):
    """Validate address components."""
    try:
        # Validate the components
        normalized = formatter.normalizer.normalize(request.components)
        country_code = normalized.get("country_code", "")
        
        # Check if we have a template for this country
        template = formatter.renderer.template_loader.get_template(country_code)
        
        required_components = ["road", "city"]
        missing = [comp for comp in required_components if comp not in normalized]
        
        return {
            "valid": len(missing) == 0,
            "missing_required": missing if missing else None,
            "country_support": {"supported": bool(template), "country_code": country_code}
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to validate address", "details": str(e)}
        )

# Exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    ) 