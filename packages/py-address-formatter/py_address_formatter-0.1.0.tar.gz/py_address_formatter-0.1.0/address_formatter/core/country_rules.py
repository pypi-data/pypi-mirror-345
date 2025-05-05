"""
Country-specific rules for address formatting.

This module provides special case handlers and country-specific
formatting rules for different countries.
"""
from typing import Dict, Any, Optional, Callable


class CountryRules:
    """
    Handles country-specific address formatting rules.
    
    This class applies special formatting rules for specific
    countries that require custom handling beyond templates.
    """
    
    def __init__(self):
        """Initialize the country rules handler."""
        # Mapping of country codes to special case handlers
        self.special_cases: Dict[str, Callable] = {
            'NL': self._handle_netherlands,
            'US': self._handle_us,
            'GB': self._handle_uk,
            'CA': self._handle_canada,
            'AU': self._handle_australia,
            'JP': self._handle_japan,
            'KR': self._handle_korea,
            'CN': self._handle_china,
            'TW': self._handle_taiwan,
            'HK': self._handle_hong_kong,
            'SG': self._handle_singapore,
        }
    
    def apply_rules(self, country_code: str, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply country-specific rules to address components.
        
        Args:
            country_code: ISO country code
            components: Address components
            
        Returns:
            Updated address components
        """
        # Skip if no country code
        if not country_code:
            return components
        
        # Normalize country code
        country_code = country_code.upper()
        
        # Apply special case handler if available
        handler = self.special_cases.get(country_code)
        if handler:
            return handler(components)
        
        # Return unmodified components if no special handling needed
        return components
    
    def _handle_netherlands(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle special cases for Netherlands (NL).
        
        - Special handling for Caribbean islands (Curaçao, Aruba, etc.)
        - Postcode formatting (#### XX)
        
        Args:
            components: Address components
            
        Returns:
            Updated address components
        """
        result = components.copy()
        
        # Handle Caribbean islands that are countries in their own right
        state = result.get('state', '')
        if state:
            # Handle Curaçao
            if state.lower() == 'curaçao' or state.lower() == 'curacao':
                result['country_code'] = 'CW'
                result['country'] = 'Curaçao'
                result.pop('state', None)
            
            # Handle Aruba
            elif state.lower() == 'aruba':
                result['country_code'] = 'AW'
                result['country'] = 'Aruba'
                result.pop('state', None)
            
            # Handle Sint Maarten
            elif state.lower() == 'sint maarten' or state.lower() == 'saint martin':
                result['country_code'] = 'SX'
                result['country'] = 'Sint Maarten'
                result.pop('state', None)
        
        # Format postcode (if present)
        postcode = result.get('postcode', '')
        if postcode and len(postcode) >= 6:
            # Ensure format #### XX
            digits = ''.join(c for c in postcode if c.isdigit())
            letters = ''.join(c for c in postcode if c.isalpha())
            
            if len(digits) >= 4 and len(letters) >= 2:
                result['postcode'] = f"{digits[:4]} {letters[:2].upper()}"
        
        return result
    
    def _handle_us(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle special cases for United States (US).
        
        - State code standardization
        - ZIP code formatting
        - Special territories handling
        
        Args:
            components: Address components
            
        Returns:
            Updated address components
        """
        result = components.copy()
        
        # State code standardization
        state = result.get('state', '')
        if state:
            # Map of state names to standard codes
            state_codes = {
                'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
                'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
                'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
                'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
                'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
                'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
                'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
                'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
                'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
                'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
                'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
                'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
                'wisconsin': 'WI', 'wyoming': 'WY',
                'district of columbia': 'DC', 'washington dc': 'DC', 'washington d.c.': 'DC',
                'puerto rico': 'PR', 'american samoa': 'AS', 'guam': 'GU',
                'northern mariana islands': 'MP', 'virgin islands': 'VI',
            }
            
            # If state is a full name, convert to code
            if state.lower() in state_codes:
                result['state'] = state_codes[state.lower()]
            # If state is already a code, standardize to uppercase
            elif len(state) == 2:
                result['state'] = state.upper()
        
        # ZIP code formatting
        postcode = result.get('postcode', '')
        if postcode:
            # Keep only digits
            digits = ''.join(c for c in postcode if c.isdigit())
            
            # Format as ZIP or ZIP+4
            if len(digits) >= 9:
                result['postcode'] = f"{digits[:5]}-{digits[5:9]}"
            elif len(digits) >= 5:
                result['postcode'] = digits[:5]
            else:
                result['postcode'] = digits
        
        # Special territories handling
        if result.get('state') in ['PR', 'GU', 'VI', 'AS', 'MP']:
            # Set special territory flag
            result['territory'] = True
        
        return result
    
    def _handle_uk(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle special cases for United Kingdom (GB).
        
        - Postcode formatting
        - County standardization
        - Special regions handling
        
        Args:
            components: Address components
            
        Returns:
            Updated address components
        """
        result = components.copy()
        
        # Format postcode (if present)
        postcode = result.get('postcode', '')
        if postcode:
            # Remove all spaces
            postcode = ''.join(postcode.split())
            
            # Format based on standard UK postcode patterns
            if len(postcode) >= 5:
                if len(postcode) >= 7:
                    # Format as AA## #AA
                    outward = postcode[:-3]
                    inward = postcode[-3:]
                    result['postcode'] = f"{outward} {inward}"
                else:
                    # Format as AA# #AA
                    outward = postcode[:-3]
                    inward = postcode[-3:]
                    result['postcode'] = f"{outward} {inward}"
        
        # Special case for countries within the UK
        state = result.get('state', '')
        if state:
            uk_countries = {
                'england': {'country_part': 'England'},
                'scotland': {'country_part': 'Scotland'},
                'wales': {'country_part': 'Wales', 'welsh_name': 'Cymru'},
                'northern ireland': {'country_part': 'Northern Ireland'},
            }
            
            if state.lower() in uk_countries:
                result['country_part'] = uk_countries[state.lower()]['country_part']
                
                # Special case for Wales - add Welsh name
                if state.lower() == 'wales' and 'welsh_name' in uk_countries[state.lower()]:
                    result['country_part_local'] = uk_countries[state.lower()]['welsh_name']
        
        return result
    
    def _handle_canada(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases for Canada (CA)."""
        result = components.copy()
        
        # Province code standardization
        province = result.get('state', '')
        if province:
            # Map of province names to standard codes
            province_codes = {
                'alberta': 'AB', 'british columbia': 'BC', 'manitoba': 'MB',
                'new brunswick': 'NB', 'newfoundland and labrador': 'NL',
                'newfoundland': 'NL', 'labrador': 'NL',
                'northwest territories': 'NT', 'nova scotia': 'NS',
                'nunavut': 'NU', 'ontario': 'ON', 'prince edward island': 'PE',
                'quebec': 'QC', 'saskatchewan': 'SK', 'yukon': 'YT',
            }
            
            # If province is a full name, convert to code
            if province.lower() in province_codes:
                result['state'] = province_codes[province.lower()]
            # If province is already a code, standardize to uppercase
            elif len(province) == 2:
                result['state'] = province.upper()
        
        # Format postal code
        postcode = result.get('postcode', '')
        if postcode:
            # Remove all spaces and non-alphanumeric characters
            clean_postcode = ''.join(c for c in postcode if c.isalnum())
            
            # Format as A#A #A#
            if len(clean_postcode) >= 6:
                result['postcode'] = f"{clean_postcode[:3]} {clean_postcode[3:6]}".upper()
        
        return result
    
    def _handle_australia(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases for Australia (AU)."""
        result = components.copy()
        
        # State code standardization
        state = result.get('state', '')
        if state:
            # Map of state/territory names to standard codes
            state_codes = {
                'australian capital territory': 'ACT', 'new south wales': 'NSW',
                'northern territory': 'NT', 'queensland': 'QLD',
                'south australia': 'SA', 'tasmania': 'TAS',
                'victoria': 'VIC', 'western australia': 'WA',
            }
            
            # If state is a full name, convert to code
            if state.lower() in state_codes:
                result['state'] = state_codes[state.lower()]
            # If state is already a code, standardize to uppercase
            elif len(state) <= 3 or state.upper() in state_codes.values():
                result['state'] = state.upper()
        
        # Format postcode (should be 4 digits)
        postcode = result.get('postcode', '')
        if postcode:
            # Keep only digits
            digits = ''.join(c for c in postcode if c.isdigit())
            
            if digits:
                result['postcode'] = digits[:4]
        
        return result
    
    def _handle_japan(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases for Japan (JP)."""
        result = components.copy()
        
        # Format postcode
        postcode = result.get('postcode', '')
        if postcode:
            # Keep only digits
            digits = ''.join(c for c in postcode if c.isdigit())
            
            # Format as ###-####
            if len(digits) >= 7:
                result['postcode'] = f"{digits[:3]}-{digits[3:7]}"
        
        return result
    
    def _handle_korea(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases for South Korea (KR)."""
        return components
    
    def _handle_china(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases for China (CN)."""
        return components
    
    def _handle_taiwan(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases for Taiwan (TW)."""
        return components
    
    def _handle_hong_kong(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases for Hong Kong (HK)."""
        return components
    
    def _handle_singapore(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases for Singapore (SG)."""
        return components 