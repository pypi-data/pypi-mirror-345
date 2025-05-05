"""
Monitoring metrics for the address formatter.

This module provides Prometheus metrics for monitoring
the address formatter's performance and error rates.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps
from typing import Callable, Any, Dict, Optional

# Define metrics
REQUEST_COUNT = Counter(
    'address_formatter_requests_total',
    'Total address formatting requests',
    ['status', 'country_code']
)

FORMAT_ERRORS = Counter(
    'address_formatter_errors_total',
    'Total address formatting errors',
    ['error_type']
)

FORMATTING_TIME = Histogram(
    'address_formatter_formatting_seconds',
    'Time spent formatting addresses',
    ['country_code'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

CACHE_SIZE = Gauge(
    'address_formatter_cache_size',
    'Current size of the address formatter cache',
    ['cache_type']
)

TEMPLATE_COUNT = Gauge(
    'address_formatter_template_count',
    'Number of loaded templates',
)

COMPONENT_FREQUENCY = Counter(
    'address_formatter_component_frequency',
    'Frequency of address components',
    ['component_name']
)

# Monitoring decorators
def monitor_formatting(country_code_key: str = 'country_code'):
    """
    Decorator for monitoring address formatting.
    
    Args:
        country_code_key: Key for the country code in the components.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(components: Dict[str, str], *args, **kwargs) -> Any:
            country_code = components.get(country_code_key, 'unknown')
            
            # Record component frequency
            for component, value in components.items():
                if value:  # Only count non-empty components
                    COMPONENT_FREQUENCY.labels(component_name=component).inc()
            
            # Record timing
            start_time = time.time()
            try:
                result = func(components, *args, **kwargs)
                REQUEST_COUNT.labels(status='success', country_code=country_code).inc()
                return result
            except Exception as e:
                REQUEST_COUNT.labels(status='error', country_code=country_code).inc()
                FORMAT_ERRORS.labels(error_type=type(e).__name__).inc()
                raise
            finally:
                FORMATTING_TIME.labels(country_code=country_code).observe(time.time() - start_time)
        
        return wrapper
    
    return decorator

def update_cache_size(cache_type: str, size: int) -> None:
    """
    Update the cache size metric.
    
    Args:
        cache_type: Type of cache.
        size: Current size of the cache.
    """
    CACHE_SIZE.labels(cache_type=cache_type).set(size)

def update_template_count(count: int) -> None:
    """
    Update the template count metric.
    
    Args:
        count: Number of loaded templates.
    """
    TEMPLATE_COUNT.set(count)

class MetricsCollector:
    """Collector for address formatter metrics."""
    
    @staticmethod
    def collect_formatter_metrics(formatter: 'AddressFormatter') -> Dict[str, Any]:
        """
        Collect metrics from the formatter.
        
        Args:
            formatter: Address formatter instance.
            
        Returns:
            Dictionary of metrics.
        """
        metrics = {
            'cache': {
                'size': len(getattr(formatter, 'cache', {})),
            },
            'templates': {
                'count': len(getattr(formatter.renderer, 'templates', {})),
            },
            'plugins': {
                'count': len(getattr(formatter, 'plugins', [])),
            },
        }
        
        # Update Prometheus metrics
        update_cache_size('formatter', metrics['cache']['size'])
        update_template_count(metrics['templates']['count'])
        
        return metrics 