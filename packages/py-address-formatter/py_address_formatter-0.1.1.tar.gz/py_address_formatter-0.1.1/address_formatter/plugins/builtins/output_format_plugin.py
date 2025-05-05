"""
Output format plugin for the address formatter.

This plugin handles converting addresses to different output formats.
"""
from typing import Dict, Any, List

from address_formatter.plugins.interface import FormatterPlugin, PluginMetadata


class OutputFormatPlugin(FormatterPlugin):
    """
    Plugin that handles different output formats for addresses.
    
    This plugin can convert formatted addresses to different formats:
    - array: Split the address into an array of lines
    - html: Convert line breaks to <br> tags
    - json: Format address components as JSON
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="output_format",
            version="1.0.0",
            description="Provides different output formats for addresses",
            author="Address Formatter Team",
            priority=800,  # Run last as it affects final output
            tags=["output", "formatting"]
        )
    
    def pre_format(self, components: Dict[str, Any], 
                  options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process address components before formatting.
        
        This plugin doesn't modify components in pre-format stage.
        """
        # No pre-processing needed for this plugin
        return components
    
    def post_format(self, formatted_address: str, 
                   components: Dict[str, Any], 
                   options: Dict[str, Any]) -> str:
        """
        Process the formatted address to convert to the requested output format.
        """
        output_format = options.get("output_format", None)
        
        if not output_format:
            return formatted_address
            
        if output_format == "array":
            # Simply return as a list of lines
            return formatted_address.split("\n")
            
        elif output_format == "html":
            # Convert newlines to HTML line breaks
            return formatted_address.replace("\n", "<br>\n")
            
        elif output_format == "json":
            # Create a structured JSON representation
            import json
            lines = formatted_address.split("\n")
            result = {
                "formatted": formatted_address,
                "lines": lines
            }
            return json.dumps(result)
            
        # Default to the original format if unknown format requested
        return formatted_address 