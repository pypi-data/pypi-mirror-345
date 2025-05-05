"""
Address renderer module.

This module contains the renderer class used for formatting
normalized address data using templates.
"""
import json
import os
from typing import Dict, Any, List, Optional

class AddressRenderer:
    """
    Renders normalized address data using country-specific templates.
    
    The renderer uses a template system to format addresses according to
    country-specific conventions and formats.
    """
    
    def __init__(self, template_paths: Optional[List[str]] = None):
        """
        Initialize the renderer with template paths.
        
        Args:
            template_paths: List of paths to template files or directories
        """
        self.templates = {}
        self.template_paths = template_paths or []
        
        # Default template path within the package
        default_template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data', 'templates', 'templates.json'
        )
        
        if os.path.exists(default_template_path):
            self.template_paths.append(default_template_path)
            
        self._load_templates()
    
    def render(self, address: Dict[str, Any], country_code: str = None) -> str:
        """
        Render an address using the appropriate template.
        
        Args:
            address: Normalized address dictionary
            country_code: Optional country code (if not in address)
                         If explicitly None, no country will be included
            
        Returns:
            Formatted address string
            
        Raises:
            ValueError: If country code cannot be determined
        """
        # Check for empty address
        if not address:
            return ""
            
        # Copy address to avoid modifying the original
        address_copy = address.copy()
        
        # If country_code is explicitly None, remove country from address
        if country_code is None:
            # Remove country from address data to ensure it's not rendered
            for field in ['country', 'country_code', 'country_name']:
                if field in address_copy:
                    del address_copy[field]
            # Use default template but without country
            country_code = "default"
            
        # Determine country code if not provided
        elif not country_code:
            country_code = address_copy.get('country_code')
            
            if not country_code:
                # Try to find a country name and map to code
                country = address_copy.get('country')
                if country:
                    country_code = self._country_name_to_code(country)
                    
            if not country_code:
                # If no country code, use default
                country_code = "default"
            
        # Get the template for this country
        template = self._get_template_for_country(country_code)
        
        # Apply template to address
        return self._apply_template(address_copy, template)
    
    def _apply_template(self, address: Dict[str, Any], template: Dict[str, Any]) -> str:
        """
        Apply a template to an address.
        
        Args:
            address: Normalized address dictionary
            template: Template dictionary with format instructions
            
        Returns:
            Formatted address string
        """
        # Make sure postcode is in the address if it exists under a different name
        address_copy = address.copy()
        
        # Check if the address is empty
        if not address_copy:
            return ""
            
        # Handle postcode variations
        if 'postcode' not in address_copy:
            for field in ['postal_code', 'zip', 'zip_code']:
                if field in address_copy and address_copy[field]:
                    address_copy['postcode'] = address_copy[field]
                    break
        
        # Get the format string
        format_str = template.get('format', '')
        
        # Process required fields
        required_fields = template.get('required_fields', [])
        missing_required = False
        for field in required_fields:
            if field not in address_copy or not address_copy[field]:
                # If a required field is missing, apply fallback logic
                missing_required = True
                break
                
        if missing_required:
            format_str = template.get('fallback_format', format_str)
            
            # If still missing critical information, use simple format
            if not any(field in address_copy and address_copy[field] for field in ['street', 'city']):
                return self._simple_format(address_copy)
        
        # Format the address
        try:
            # First replace fields that exist in the address
            result = format_str
            for key, value in address_copy.items():
                placeholder = '{' + key + '}'
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
            
            # Clean up any unused placeholders
            import re
            result = re.sub(r'\{[^}]+\}', '', result)
            
            # Clean up extra whitespace, commas, and line breaks
            result = re.sub(r',\s*,', ',', result)
            result = re.sub(r'\n\s*\n', '\n', result)
            result = re.sub(r'^\s+|\s+$', '', result, flags=re.MULTILINE)
            result = re.sub(r'^\s*,\s*', '', result, flags=re.MULTILINE)
            result = re.sub(r'\s*,\s*$', '', result, flags=re.MULTILINE)
            result = re.sub(r'\n+', '\n', result)
            
            return result.strip()
        except Exception as e:
            # Fallback to simple concatenation if template fails
            return self._simple_format(address_copy)
    
    def _simple_format(self, address: Dict[str, Any]) -> str:
        """
        Simple address formatting as fallback.
        
        Args:
            address: Normalized address dictionary
            
        Returns:
            Basic formatted address string
        """
        # Define a basic order of address components
        basic_order = [
            'name', 'organization', 
            'street', 'street2', 
            'city', 'state', 'postcode',
            'country'
        ]
        
        lines = []
        for field in basic_order:
            if field in address and address[field]:
                lines.append(str(address[field]))
                
        return '\n'.join(lines)
    
    def _get_template_for_country(self, country_code: str) -> Dict[str, Any]:
        """
        Get the template for a specific country.
        
        Args:
            country_code: Country code to get template for
            
        Returns:
            Template dictionary
        """
        # Handle None or empty string
        if not country_code:
            country_code = "default"
        else:
            # Normalize country code
            country_code = country_code.upper().strip()
        
        # Create country-specific templates if they don't exist
        if not self.templates:
            # Add basic templates for common countries
            self._add_default_templates()
        
        # Return country-specific template if it exists
        if country_code in self.templates:
            return self.templates[country_code]
        
        # Fallback to default template
        if 'default' in self.templates:
            return self.templates['default']
        
        # Last resort fallback - create a basic template on the fly
        return {
            'format': '{street}\n{city}, {state} {postcode}\n{country}',
            'required_fields': ['street'],
            'fallback_format': '{street}\n{city}\n{country}'
        }
    
    def _add_default_templates(self):
        """Add default templates for common countries."""
        # United States
        self.templates['US'] = {
            'format': '{name}\n{organization}\n{house_number} {street}\n{city}, {state} {postcode}\n{country}',
            'required_fields': ['street', 'city'],
            'fallback_format': '{name}\n{organization}\n{street}\n{city}, {state}\n{country}'
        }
        
        # United Kingdom
        self.templates['GB'] = {
            'format': '{name}\n{organization}\n{house_number} {street}\n{city}\n{postcode}\n{country}',
            'required_fields': ['street', 'city'],
            'fallback_format': '{name}\n{organization}\n{street}\n{city}\n{country}'
        }
        
        # Germany
        self.templates['DE'] = {
            'format': '{name}\n{organization}\n{street} {house_number}\n{postcode} {city}\n{country}',
            'required_fields': ['street', 'city'],
            'fallback_format': '{name}\n{organization}\n{street}\n{city}\n{country}'
        }
        
        # France
        self.templates['FR'] = {
            'format': '{name}\n{organization}\n{house_number} {street}\n{postcode} {city}\n{country}',
            'required_fields': ['street', 'city'],
            'fallback_format': '{name}\n{organization}\n{street}\n{city}\n{country}'
        }
        
        # Default template
        self.templates['default'] = {
            'format': '{name}\n{organization}\n{house_number} {street}\n{city}, {state} {postcode}\n{country}',
            'required_fields': ['street', 'city'],
            'fallback_format': '{name}\n{organization}\n{street}\n{city}\n{country}'
        }
    
    def _load_templates(self):
        """
        Load address templates from all template paths.
        """
        for path in self.template_paths:
            self._load_template_from_path(path)
    
    def _load_template_from_path(self, path: str):
        """
        Load templates from a file or directory.
        
        Args:
            path: Path to template file or directory
        """
        if not os.path.exists(path):
            return
            
        if os.path.isdir(path):
            # Load all JSON files in the directory
            for filename in os.listdir(path):
                if filename.endswith('.json'):
                    file_path = os.path.join(path, filename)
                    self._load_template_from_file(file_path)
        else:
            # Load a single template file
            self._load_template_from_file(path)
    
    def _load_template_from_file(self, file_path: str):
        """
        Load templates from a JSON file.
        
        Args:
            file_path: Path to template JSON file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
                
            # Merge templates
            self.templates.update(templates)
        except Exception as e:
            # Log error but continue
            print(f"Error loading template file {file_path}: {e}")
    
    def add_template(self, country_code: str, template: Dict[str, Any]):
        """
        Add or update a template for a specific country.
        
        Args:
            country_code: Country code (e.g., 'US', 'GB')
            template: Template dictionary
        """
        self.templates[country_code.upper()] = template
    
    def get_supported_countries(self) -> List[str]:
        """
        Get a list of countries with available templates.
        
        Returns:
            List of country codes
        """
        return [code for code in self.templates.keys() if code != 'default']
    
    def _country_name_to_code(self, country_name: str) -> Optional[str]:
        """
        Convert a country name to a country code.
        
        Args:
            country_name: Name of the country
            
        Returns:
            Country code or None if not found
        """
        # This is a simplified mapping
        # In a real implementation, this would be more comprehensive
        country_map = {
            'united states': 'US',
            'usa': 'US',
            'united states of america': 'US',
            'united kingdom': 'GB',
            'uk': 'GB',
            'great britain': 'GB',
            'canada': 'CA',
            'australia': 'AU',
            'germany': 'DE',
            'deutschland': 'DE',
            'france': 'FR',
            'japan': 'JP',
            'china': 'CN',
            'india': 'IN',
            'brazil': 'BR',
            'russia': 'RU',
            'italy': 'IT',
            'spain': 'ES',
            'mexico': 'MX',
            'netherlands': 'NL',
            'holland': 'NL',
            'belgium': 'BE',
            'sweden': 'SE',
            'switzerland': 'CH',
            'austria': 'AT',
            'ireland': 'IE',
            'new zealand': 'NZ',
            'south korea': 'KR',
            'korea': 'KR',
            'singapore': 'SG'
        }
        
        return country_map.get(country_name.lower()) 