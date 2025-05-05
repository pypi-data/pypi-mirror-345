"""
Abbreviation plugin for the address formatter.

This plugin provides additional abbreviation functionality for address components.
"""
from typing import Dict, Any

from address_formatter.plugins.interface import FormatterPlugin, PluginMetadata


class AbbreviationPlugin(FormatterPlugin):
    """
    Plugin that provides enhanced abbreviation functionality.
    
    This plugin adds additional abbreviation rules beyond the core formatter's
    capabilities, such as company name abbreviations and specialized format abbreviations.
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="abbreviation_plugin",
            version="1.0.0",
            description="Provides enhanced abbreviation functionality",
            author="Address Formatter Team",
            priority=100,
            tags=["abbreviation", "formatting"]
        )
    
    def initialize(self) -> None:
        """Initialize the plugin with abbreviation patterns."""
        # Load custom abbreviation patterns
        self.company_abbreviations = {
            "Corporation": "Corp.",
            "Incorporated": "Inc.",
            "Limited": "Ltd.",
            "Company": "Co."
        }
        
        self.specialty_abbreviations = {
            "Building": "Bldg.",
            "Department": "Dept.",
            "Government": "Govt.",
            "Institute": "Inst.",
            "University": "Univ."
        }
    
    def pre_format(self, components: Dict[str, Any], 
                  options: Dict[str, Any]) -> Dict[str, Any]:
        """Process address components before formatting to apply abbreviations."""
        # Skip if abbreviation is not enabled
        if not options.get("abbreviate", False):
            return components
        
        result = components.copy()
        
        # Apply abbreviations to organization names
        if "organization" in result:
            org_name = result["organization"]
            for full, abbrev in self.company_abbreviations.items():
                # Match at word boundaries
                pattern = r"\b" + full + r"\b"
                import re
                org_name = re.sub(pattern, abbrev, org_name)
            result["organization"] = org_name
        
        # Apply specialty abbreviations to building names
        if "building" in result:
            building = result["building"]
            for full, abbrev in self.specialty_abbreviations.items():
                pattern = r"\b" + full + r"\b"
                import re
                building = re.sub(pattern, abbrev, building)
            result["building"] = building
        
        return result
    
    def post_format(self, formatted_address: str, 
                   components: Dict[str, Any], 
                   options: Dict[str, Any]) -> str:
        """Process formatted address to apply final abbreviations."""
        # Skip if abbreviation is not enabled
        if not options.get("abbreviate", False):
            return formatted_address
        
        # Apply both sets of abbreviations to the full formatted address
        import re
        result = formatted_address
        
        for full, abbrev in {**self.company_abbreviations, **self.specialty_abbreviations}.items():
            pattern = r"\b" + full + r"\b"
            result = re.sub(pattern, abbrev, result)
        
        return result 