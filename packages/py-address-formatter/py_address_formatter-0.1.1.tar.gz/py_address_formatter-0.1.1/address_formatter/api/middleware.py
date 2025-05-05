"""
Middleware for the address formatter API.

This module provides middleware for the FastAPI application,
including metrics collection and error handling.
"""

from fastapi import Request, Response
from prometheus_client import Counter, Histogram
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Define API metrics
API_REQUEST_COUNT = Counter(
    'address_formatter_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

API_REQUEST_LATENCY = Histogram(
    'address_formatter_api_request_latency_seconds',
    'API request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting API metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract method and path for metrics
        method = request.method
        endpoint = request.url.path
        
        # Process the request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            # Record metrics
            API_REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            API_REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""
    
    def __init__(self, app: ASGIApp, rate_limit: int = 100):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Simple token bucket rate limiting
        if client_ip in self.clients:
            last_request, tokens = self.clients[client_ip]
            time_passed = time.time() - last_request
            tokens = min(self.rate_limit, tokens + time_passed * (self.rate_limit / 60.0))
            
            if tokens < 1:
                return Response(
                    content="Rate limit exceeded",
                    status_code=429
                )
            
            tokens -= 1
        else:
            tokens = self.rate_limit - 1
        
        self.clients[client_ip] = (time.time(), tokens)
        
        return await call_next(request) 