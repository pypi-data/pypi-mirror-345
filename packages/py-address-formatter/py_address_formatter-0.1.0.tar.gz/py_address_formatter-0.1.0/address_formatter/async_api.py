"""
Asynchronous API for the address formatter.

This module provides an asynchronous API for the address formatter,
allowing for concurrent processing of multiple addresses.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Union, Any, Optional, Tuple

from .formatter import AddressFormatter, format_address
from .config import settings
from .types import AddressComponent, FormattingOptions

# Create a thread pool for async operations
_thread_pool = ThreadPoolExecutor(max_workers=settings.thread_pool_size)

class AsyncAddressFormatter:
    """
    Asynchronous address formatter.
    
    This class provides asynchronous methods for formatting addresses,
    allowing for concurrent processing of multiple addresses.
    """
    
    def __init__(self):
        """Initialize the asynchronous address formatter."""
        self.formatter = AddressFormatter()
    
    async def format(
        self,
        components: Dict[str, str],
        options: Optional[Dict[str, Any]] = None
    ) -> Union[str, List[str]]:
        """
        Format an address asynchronously.
        
        Args:
            components: Address components to format.
            options: Formatting options.
            
        Returns:
            Formatted address.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _thread_pool,
            lambda: format_address(components, options or {})
        )
    
    async def format_batch(
        self,
        batch: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None
    ) -> List[Union[str, List[str]]]:
        """
        Format multiple addresses asynchronously.
        
        Args:
            batch: List of address components to format.
            options: Formatting options.
            
        Returns:
            List of formatted addresses.
        """
        tasks = [self.format(components, options) for components in batch]
        return await asyncio.gather(*tasks)

async def format_address_async(
    components: Dict[str, str],
    options: Optional[Dict[str, Any]] = None
) -> Union[str, List[str]]:
    """
    Format an address asynchronously.
    
    Args:
        components: Address components to format.
        options: Formatting options.
        
    Returns:
        Formatted address.
    """
    formatter = AsyncAddressFormatter()
    return await formatter.format(components, options)

async def format_batch_async(
    batch: List[Dict[str, str]],
    options: Optional[Dict[str, Any]] = None
) -> List[Union[str, List[str]]]:
    """
    Format multiple addresses asynchronously.
    
    Args:
        batch: List of address components to format.
        options: Formatting options.
        
    Returns:
        List of formatted addresses.
    """
    formatter = AsyncAddressFormatter()
    return await formatter.format_batch(batch, options) 