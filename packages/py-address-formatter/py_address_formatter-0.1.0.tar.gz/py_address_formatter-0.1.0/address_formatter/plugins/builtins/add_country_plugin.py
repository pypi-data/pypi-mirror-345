"""
Add country plugin for the address formatter.

This plugin ensures country information is added to addresses.
"""
from typing import Dict, Any

from address_formatter.plugins.interface import FormatterPlugin, PluginMetadata


class AddCountryPlugin(FormatterPlugin):
    """
    Plugin that controls whether country names are included in formatted addresses.
    
    This plugin can be used to:
    - Include the country name in the formatted address
    - Exclude the country name from the formatted address
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="add_country",
            version="1.0.0",
            description="Controls whether country names are included in formatting",
            author="Address Formatter Team",
            priority=300,
            tags=["country", "formatting"]
        )
    
    def pre_format(self, components: Dict[str, Any], 
                  options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process address components before formatting.
        
        If add_country is False, this method removes country-related fields.
        """
        # Check if we should include the country
        if options.get("add_country", True) is False:
            result = components.copy()
            
            # Remove country-related fields
            for field in ['country', 'country_code', 'country_name']:
                if field in result:
                    del result[field]
                    
            return result
        
        return components
    
    def post_format(self, formatted_address: str, 
                   components: Dict[str, Any], 
                   options: Dict[str, Any]) -> str:
        """
        Process the formatted address to manage country inclusion.
        
        If needed, this could remove country lines from already formatted addresses.
        """
        # Most of the work is done in pre_format, but if needed we could:
        # - Remove the country from a formatted address (more complex)
        # - Add a country if components were modified after pre_format
        
        # This is a simplified implementation
        return formatted_address 