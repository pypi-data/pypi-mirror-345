"""
Monitoring package for the address formatter.

This package provides functionality for monitoring the
address formatter's performance and error rates.
"""

from .metrics import (
    monitor_formatting,
    update_cache_size,
    update_template_count,
    MetricsCollector,
    REQUEST_COUNT,
    FORMAT_ERRORS,
    FORMATTING_TIME,
    CACHE_SIZE,
    TEMPLATE_COUNT,
    COMPONENT_FREQUENCY
)

__all__ = [
    "monitor_formatting",
    "update_cache_size",
    "update_template_count",
    "MetricsCollector",
    "REQUEST_COUNT",
    "FORMAT_ERRORS",
    "FORMATTING_TIME",
    "CACHE_SIZE",
    "TEMPLATE_COUNT",
    "COMPONENT_FREQUENCY"
] 