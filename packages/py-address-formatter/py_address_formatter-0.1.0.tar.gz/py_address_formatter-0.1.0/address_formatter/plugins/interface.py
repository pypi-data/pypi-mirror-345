"""
Plugin interface for the address formatter.

This module defines the interface for plugins that can be used
to extend the functionality of the address formatter.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Protocol, Tuple


@dataclass
class PluginMetadata:
    """
    Metadata for a formatter plugin.
    
    This class describes a plugin, including its name,
    version, description, and other metadata.
    """
    name: str
    version: str
    description: str
    author: str
    priority: int = 100  # Higher priority plugins are executed first
    tags: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.name} v{self.version} ({self.author})"


class FormatterPlugin(ABC):
    """
    Base class for all formatter plugins.
    
    Plugins can modify address components before or after formatting,
    or perform other tasks during the formatting process.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        Get metadata for this plugin.
        
        Returns:
            Plugin metadata
        """
        pass
    
    def process(self, components: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process address components.
        
        This is the main entry point for plugin processing, called by the plugin manager.
        By default, it simply calls pre_format.
        
        Args:
            components: The address components to process
            options: Formatting options
            
        Returns:
            Processed address components
        """
        return self.pre_format(components, options)
    
    @abstractmethod
    def pre_format(self, components: Dict[str, Any], 
                  options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process address components before formatting.
        
        Args:
            components: The address components to process
            options: Formatting options
            
        Returns:
            Processed address components
        """
        pass
    
    @abstractmethod
    def post_format(self, formatted_address: str, 
                   components: Dict[str, Any], 
                   options: Dict[str, Any]) -> str:
        """
        Process the formatted address after formatting.
        
        Args:
            formatted_address: The formatted address
            components: The address components used for formatting
            options: Formatting options
            
        Returns:
            Processed formatted address
        """
        pass
    
    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method is called when the plugin is loaded.
        Can be overridden to provide initialization logic.
        """
        pass
    
    def shutdown(self) -> None:
        """
        Shutdown the plugin.
        
        This method is called when the plugin is unloaded.
        Can be overridden to provide cleanup logic.
        """
        pass 