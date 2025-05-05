"""
Template loader for address formatting

This module provides functionality to load and manage address formatting templates
for different countries and regions.
"""
from typing import Dict, Any, Optional, List
import os
import json
from pathlib import Path


class TemplateLoader:
    """
    Loads and manages address formatting templates for different countries.

    This class handles:
    - Loading templates from a file system
    - Providing default templates
    - Selecting appropriate templates based on country codes
    """

    def __init__(self, templates_path: Optional[str] = None):
        """
        Initialize the template loader.

        Args:
            templates_path: Path to templates directory. If None, uses default templates.
        """
        if templates_path:
            self.templates_path = Path(templates_path)
        else:
            # Default path is relative to this file
            self.templates_path = Path(__file__).resolve().parent.parent / "data" / "templates"

        self.templates = self._load_templates()
        self.default_template = self._get_default_template()

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load templates from the template directory or use defaults.

        Returns:
            Dictionary mapping country codes to template configurations
        """
        templates = {}

        # Try to load templates.json file specifically first
        templates_file = self.templates_path / "templates.json"

        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                print(f"Loaded templates from {templates_file}")
                return templates
            except Exception as e:
                print(f"Error loading templates.json: {e}")

        # If templates.json not found or had an error, fall back to the original loading logic
        if self.templates_path and os.path.exists(self.templates_path):
            try:
                template_files = Path(self.templates_path).glob("*.json")

                for template_file in template_files:
                    try:
                        with open(template_file, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)

                            # Extract country code from filename or template data
                            country_code = template_file.stem.upper()
                            if 'country_code' in template_data:
                                country_code = template_data['country_code'].upper()

                            templates[country_code] = template_data
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Skip invalid template files
                        continue
            except Exception:
                # Fallback to default templates on any error
                pass

        # If no custom templates were loaded, use defaults
        if not templates:
            templates = self._get_default_templates()

        return templates

    def _get_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Provide default templates for common countries.

        Returns:
            Dictionary of default templates
        """
        return {
            'US': {
                'format': "{name}\n{street} {house_number}\n{city}, {state} {postal_code}\n{country}",
                'required': ['street', 'city', 'postal_code'],
                'abbreviate': ['state'],
                'uppercase': ['postal_code'],
                'replace': {
                    'state': {
                        'alabama': 'AL',
                        'alaska': 'AK',
                        'arizona': 'AZ',
                        'arkansas': 'AR',
                        'california': 'CA',
                        'colorado': 'CO',
                        'connecticut': 'CT',
                        'delaware': 'DE',
                        'florida': 'FL',
                        'georgia': 'GA',
                        'hawaii': 'HI',
                        'idaho': 'ID',
                        'illinois': 'IL',
                        'indiana': 'IN',
                        'iowa': 'IA',
                        'kansas': 'KS',
                        'kentucky': 'KY',
                        'louisiana': 'LA',
                        'maine': 'ME',
                        'maryland': 'MD',
                        'massachusetts': 'MA',
                        'michigan': 'MI',
                        'minnesota': 'MN',
                        'mississippi': 'MS',
                        'missouri': 'MO',
                        'montana': 'MT',
                        'nebraska': 'NE',
                        'nevada': 'NV',
                        'new hampshire': 'NH',
                        'new jersey': 'NJ',
                        'new mexico': 'NM',
                        'new york': 'NY',
                        'north carolina': 'NC',
                        'north dakota': 'ND',
                        'ohio': 'OH',
                        'oklahoma': 'OK',
                        'oregon': 'OR',
                        'pennsylvania': 'PA',
                        'rhode island': 'RI',
                        'south carolina': 'SC',
                        'south dakota': 'SD',
                        'tennessee': 'TN',
                        'texas': 'TX',
                        'utah': 'UT',
                        'vermont': 'VT',
                        'virginia': 'VA',
                        'washington': 'WA',
                        'west virginia': 'WV',
                        'wisconsin': 'WI',
                        'wyoming': 'WY'
                    }
                }
            },
            'GB': {
                'format': "{name}\n{house_number} {street}\n{city}\n{state}\n{postal_code}\n{country}",
                'required': ['street', 'city', 'postal_code'],
                'uppercase': ['postal_code']
            },
            'CA': {
                'format': "{name}\n{street} {house_number}\n{city} {state} {postal_code}\n{country}",
                'required': ['street', 'city', 'postal_code'],
                'abbreviate': ['state'],
                'uppercase': ['postal_code'],
                'replace': {
                    'state': {
                        'alberta': 'AB',
                        'british columbia': 'BC',
                        'manitoba': 'MB',
                        'new brunswick': 'NB',
                        'newfoundland and labrador': 'NL',
                        'northwest territories': 'NT',
                        'nova scotia': 'NS',
                        'nunavut': 'NU',
                        'ontario': 'ON',
                        'prince edward island': 'PE',
                        'quebec': 'QC',
                        'saskatchewan': 'SK',
                        'yukon': 'YT'
                    }
                }
            },
            'DE': {
                'format': "{name}\n{street} {house_number}\n{postal_code} {city}\n{country}",
                'required': ['street', 'city', 'postal_code']
            },
            'FR': {
                'format': "{name}\n{house_number} {street}\n{postal_code} {city}\n{country}",
                'required': ['street', 'city', 'postal_code']
            },
            'JP': {
                'format': "{name}\n{house_number}-{building}\n{street}, {district}\n{city}, {state} {postal_code}\n{country}",
                'required': ['city', 'postal_code']
            },
            'AU': {
                'format': "{name}\n{house_number} {street}\n{city} {state} {postal_code}\n{country}",
                'required': ['street', 'city', 'postal_code'],
                'abbreviate': ['state'],
                'replace': {
                    'state': {
                        'australian capital territory': 'ACT',
                        'new south wales': 'NSW',
                        'northern territory': 'NT',
                        'queensland': 'QLD',
                        'south australia': 'SA',
                        'tasmania': 'TAS',
                        'victoria': 'VIC',
                        'western australia': 'WA'
                    }
                }
            }
        }

    def _get_default_template(self) -> Dict[str, Any]:
        """
        Provide a default template for when country is unknown.

        Returns:
            Default template dictionary
        """
        return {
            'format': "{name}\n{house_number} {street}\n{district}\n{city} {state} {postal_code}\n{country}",
            'required': ['city']
        }

    def get_template(self, country_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the formatting template for the specified country.

        Args:
            country_code: ISO country code (2-letter)

        Returns:
            Template dictionary for the country, or default template if not found
        """
        if not country_code:
            return self.default_template

        country_code = country_code.upper()

        # Try to find an exact match for the country code
        if country_code in self.templates:
            return self.templates[country_code]

        # Fall back to default template
        return self.default_template