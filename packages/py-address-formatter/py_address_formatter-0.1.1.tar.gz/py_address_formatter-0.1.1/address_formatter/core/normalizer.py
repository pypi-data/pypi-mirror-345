"""
Address normalizer module.

This module contains the AddressNormalizer class that converts
address data into a standardized format for processing.
"""
from typing import Dict, Any, List, Optional, Callable, Union


class AddressNormalizer:
    """
    Normalizes address data to a standard format.
    
    Applies a series of rules to clean, standardize, and validate
    address components before formatting.
    """
    
    def __init__(self, custom_rules: Optional[Dict[str, Callable]] = None):
        """
        Initialize the address normalizer.
        
        Args:
            custom_rules: Dictionary of custom normalization rules
        """
        # Initialize the default rules
        self.rules = {
            'lowercase_keys': self._lowercase_keys,
            'remove_empty': self._remove_empty,
            'standardize_country': self._standardize_country,
            'extract_postal_code': self._extract_postal_code,
            'normalize_fields': self._normalize_field_names,
            'expand_abbreviations': self._expand_abbreviations,
            'cleanup_whitespace': self._cleanup_whitespace,
        }
        
        # Add custom rules if provided
        if custom_rules:
            self.rules.update(custom_rules)
            
        # Define the order in which rules are applied
        self.rule_order = [
            'lowercase_keys',
            'remove_empty',
            'normalize_fields',
            'standardize_country',
            'extract_postal_code',
            'expand_abbreviations',
            'cleanup_whitespace',
        ]
    
    def normalize(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize an address dictionary.
        
        Args:
            address: Input address dictionary
            
        Returns:
            Normalized address dictionary
        """
        if not address:
            return {}
            
        # Create a copy to avoid modifying the original
        normalized = address.copy()
        
        # Apply rules in order
        for rule_name in self.rule_order:
            if rule_name in self.rules:
                try:
                    normalized = self.rules[rule_name](normalized)
                except Exception as e:
                    # Log the error but continue with other rules
                    print(f"Error applying rule {rule_name}: {e}")
        
        return normalized
    
    def add_rule(self, rule_name: str, rule_func: Callable):
        """
        Add a custom normalization rule.
        
        Args:
            rule_name: Name of the rule
            rule_func: Function implementing the rule
            
        Raises:
            ValueError: If rule_name already exists
        """
        if rule_name in self.rules:
            raise ValueError(f"Rule '{rule_name}' already exists")
        
        self.rules[rule_name] = rule_func
        # Add to the end of the rule order
        self.rule_order.append(rule_name)
    
    def _lowercase_keys(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert all keys to lowercase.
        
        Args:
            address: Input address dictionary
            
        Returns:
            Address with lowercase keys
        """
        return {k.lower(): v for k, v in address.items()}
    
    def _remove_empty(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove empty or None values.
        
        Args:
            address: Input address dictionary
            
        Returns:
            Address without empty values
        """
        return {k: v for k, v in address.items() if v is not None and v != ""}
    
    def _normalize_field_names(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize field names to a common format.
        
        Args:
            address: Input address dictionary
            
        Returns:
            Address with standardized field names
        """
        # Mapping of common field variations to standard names
        field_mapping = {
            'street': 'street',
            'street1': 'street',
            'address': 'street',
            'address1': 'street',
            'addressline1': 'street',
            'address_line_1': 'street',
            'address_line1': 'street',
            
            'street2': 'street2',
            'address2': 'street2',
            'addressline2': 'street2',
            'address_line_2': 'street2',
            'address_line2': 'street2',
            
            'city': 'city',
            'town': 'city',
            'locality': 'city',
            
            'state': 'state',
            'province': 'state',
            'region': 'state',
            'county': 'state',
            'administrative_area': 'state',
            
            'zip': 'postal_code',
            'zipcode': 'postal_code',
            'zip_code': 'postal_code',
            'postcode': 'postal_code',
            'postal': 'postal_code',
            'postalcode': 'postal_code',
            'post_code': 'postal_code',
            
            'country': 'country',
            'country_name': 'country',
            
            'countrycode': 'country_code',
            'country_code': 'country_code',
            'country_iso': 'country_code',
            
            'name': 'recipient',
            'fullname': 'recipient',
            'full_name': 'recipient',
            'recipient': 'recipient',
            'recipient_name': 'recipient',
            'attention': 'recipient',
            
            'company': 'organization',
            'business': 'organization',
            'business_name': 'organization',
            'company_name': 'organization',
            'organization': 'organization',
            'organisation': 'organization',
        }
        
        result = {}
        for key, value in address.items():
            # Get the standard field name or keep the original
            standard_key = field_mapping.get(key.lower(), key.lower())
            # Don't overwrite existing standard fields
            if standard_key not in result:
                result[standard_key] = value
            # If the field already exists, keep the more specific one
            elif standard_key in result and key.lower() == standard_key:
                result[standard_key] = value
                
        return result
    
    def _standardize_country(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize country names and codes.
        
        Args:
            address: Address data dictionary
            
        Returns:
            Address with standardized country information
        """
        result = address.copy()
        
        # Country name to code mapping
        country_map = {
            'united states': 'US',
            'united states of america': 'US',
            'us': 'US',
            'usa': 'US',
            'united kingdom': 'GB',
            'great britain': 'GB',
            'uk': 'GB',
            'england': 'GB',
            'canada': 'CA',
            'australia': 'AU',
            'germany': 'DE',
            'deutschland': 'DE',
            'france': 'FR',
            'italy': 'IT',
            'italia': 'IT',
            'japan': 'JP',
            'spain': 'ES',
            'españa': 'ES',
            'mexico': 'MX',
            'méxico': 'MX',
            'brazil': 'BR',
            'brasil': 'BR',
            'russia': 'RU',
            'china': 'CN',
            'india': 'IN',
        }
        
        # Code to country name mapping
        code_to_country = {
            'US': 'United States of America',
            'GB': 'United Kingdom',
            'CA': 'Canada',
            'AU': 'Australia',
            'DE': 'Germany',
            'FR': 'France',
            'IT': 'Italy',
            'JP': 'Japan',
            'ES': 'Spain',
            'MX': 'Mexico',
            'BR': 'Brazil',
            'RU': 'Russia',
            'CN': 'China',
            'IN': 'India',
        }
        
        # Determine country code from country name
        if 'country' in result and result['country']:
            country = str(result['country']).lower().strip()
            if country in country_map:
                result['country_code'] = country_map[country]
                
        # Normalize country code if it exists
        if 'country_code' in result and result['country_code']:
            code = str(result['country_code']).upper().strip()
            result['country_code'] = code
            
            # Add full country name if we have the code
            if code in code_to_country and 'country' not in result:
                result['country'] = code_to_country[code]
        
        # If we have a country code but no country name, add the name
        if 'country_code' in result and result['country_code'] and 'country' not in result:
            code = result['country_code']
            if code in code_to_country:
                result['country'] = code_to_country[code]
        
        return result
    
    def _extract_postal_code(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and standardize postal code format.
        
        Args:
            address: Input address dictionary
            
        Returns:
            Address with standardized postal code
        """
        result = address.copy()
        
        # If postal code exists
        if 'postal_code' in result:
            postal = result['postal_code']
            
            # Standardize formats based on country code
            if 'country_code' in result:
                country_code = result['country_code'].upper()
                
                # US ZIP codes
                if country_code == 'US' and isinstance(postal, str):
                    # Format as 5-digit or ZIP+4
                    postal = postal.strip().replace(' ', '')
                    if len(postal) == 9 and postal.isdigit():
                        result['postal_code'] = f"{postal[:5]}-{postal[5:]}"
                    elif len(postal) > 5 and '-' not in postal:
                        result['postal_code'] = f"{postal[:5]}-{postal[5:]}"
                
                # UK postcodes
                elif country_code == 'GB' and isinstance(postal, str):
                    # Ensure proper spacing for UK postcodes
                    postal = postal.strip().upper().replace(' ', '')
                    if len(postal) > 3:
                        inward = postal[-3:]
                        outward = postal[:-3]
                        result['postal_code'] = f"{outward} {inward}"
                        
        return result
    
    def _expand_abbreviations(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand common address abbreviations.
        
        Args:
            address: Input address dictionary
            
        Returns:
            Address with expanded abbreviations
        """
        result = address.copy()
        
        # US state abbreviations
        us_states = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
        }
        
        # Street abbreviations
        street_abbreviations = {
            'st': 'street',
            'rd': 'road',
            'ave': 'avenue',
            'blvd': 'boulevard',
            'dr': 'drive',
            'ln': 'lane',
            'pl': 'place',
            'ct': 'court',
        }
        
        # Expand state abbreviations
        if 'state' in result and result['state'] in us_states:
            result['state'] = us_states[result['state']]
            
        # Expand street abbreviations in road name
        if 'road' in result and isinstance(result['road'], str):
            road_parts = result['road'].lower().split()
            if road_parts and road_parts[-1] in street_abbreviations:
                road_parts[-1] = street_abbreviations[road_parts[-1]]
                result['road'] = ' '.join(road_parts)
                
        return result
    
    def _rename_field(self, address: Dict[str, Any], from_field: str, to_field: str):
        """
        Rename a field in the address dictionary.
        
        Args:
            address: Address data dictionary (modified in place)
            from_field: Original field name
            to_field: New field name
        """
        if from_field in address:
            address[to_field] = address[from_field]
            del address[from_field]
    
    def _combine_fields(self, 
                        address: Dict[str, Any], 
                        source_fields: List[str], 
                        target_field: str, 
                        separator: str):
        """
        Combine multiple fields into one.
        
        Args:
            address: Address data dictionary (modified in place)
            source_fields: List of fields to combine
            target_field: Field to store the combined result
            separator: String to use between combined values
        """
        values = []
        for field in source_fields:
            if field in address and address[field]:
                values.append(str(address[field]))
                
        if values:
            address[target_field] = separator.join(values)
            
            # Optionally remove source fields
            # for field in source_fields:
            #     if field in address:
            #         del address[field]
    
    def _split_field(self, 
                     address: Dict[str, Any], 
                     field: str, 
                     target_fields: List[str], 
                     separator: str):
        """
        Split a field into multiple target fields.
        
        Args:
            address: Address data dictionary (modified in place)
            field: Field to split
            target_fields: Fields to store the split values
            separator: String that separates the values
        """
        if field in address and isinstance(address[field], str):
            values = address[field].split(separator)
            
            # Assign values to target fields
            for i, target in enumerate(target_fields):
                if i < len(values):
                    address[target] = values[i].strip()
    
    def _format_field(self, 
                      address: Dict[str, Any], 
                      field: str, 
                      format_type: str):
        """
        Format a field according to specified type.
        
        Args:
            address: Address data dictionary (modified in place)
            field: Field to format
            format_type: Type of formatting to apply
        """
        if field in address:
            value = address[field]
            
            if format_type == 'uppercase' and isinstance(value, str):
                address[field] = value.upper()
                
            elif format_type == 'lowercase' and isinstance(value, str):
                address[field] = value.lower()
                
            elif format_type == 'title' and isinstance(value, str):
                address[field] = value.title()
                
            elif format_type == 'strip' and isinstance(value, str):
                address[field] = value.strip()
                
            elif format_type == 'number':
                try:
                    address[field] = int(value)
                except (ValueError, TypeError):
                    pass  # Keep original if conversion fails
    
    def _cleanup_whitespace(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up extra whitespace in all string values.
        
        Args:
            address: Address data dictionary
            
        Returns:
            Modified address with cleaned whitespace
        """
        for key, value in address.items():
            if isinstance(value, str):
                # Replace multiple spaces with a single space and strip
                address[key] = ' '.join(value.split()).strip()
        return address
    
    def _get_default_rules(self) -> List[Dict[str, Any]]:
        """
        Get the default normalization rules.
        
        Returns:
            List of rule dictionaries
        """
        return [
            # Common field renaming
            {'type': 'rename_field', 'from_field': 'postal_code', 'to_field': 'postcode'},
            {'type': 'rename_field', 'from_field': 'zip', 'to_field': 'postcode'},
            {'type': 'rename_field', 'from_field': 'zip_code', 'to_field': 'postcode'},
            {'type': 'rename_field', 'from_field': 'street_address', 'to_field': 'street'},
            {'type': 'rename_field', 'from_field': 'address1', 'to_field': 'street'},
            {'type': 'rename_field', 'from_field': 'address2', 'to_field': 'house_number'},
            {'type': 'rename_field', 'from_field': 'state_province', 'to_field': 'state'},
            
            # Format fields
            {'type': 'format_field', 'field': 'country_code', 'format_type': 'uppercase'},
            {'type': 'format_field', 'field': 'state', 'format_type': 'uppercase'},
            {'type': 'format_field', 'field': 'postcode', 'format_type': 'uppercase'},
            
            # Combine address components if needed
            {
                'type': 'combine_fields', 
                'source_fields': ['house_number', 'street'], 
                'target_field': 'street_full',
                'separator': ' '
            }
        ] 