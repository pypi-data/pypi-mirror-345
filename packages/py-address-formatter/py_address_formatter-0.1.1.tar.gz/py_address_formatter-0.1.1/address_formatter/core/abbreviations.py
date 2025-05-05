"""
Address component abbreviation system.

This module provides functionality for abbreviating address components
according to country-specific or language-specific rules.
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Pattern


logger = logging.getLogger(__name__)


class AbbreviationEngine:
    """
    Engine for abbreviating address components.
    
    This class applies abbreviation rules to address components
    based on language and component type.
    """
    
    def __init__(self, abbreviations_path: Optional[Path] = None):
        """
        Initialize the abbreviation engine.
        
        Args:
            abbreviations_path: Path to the abbreviations JSON file
        """
        self.abbreviations: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
        self.compiled_patterns: Dict[str, Dict[str, List[Tuple[Pattern, str]]]] = {}
        
        # Load abbreviations if path provided
        if abbreviations_path:
            self.load_abbreviations(abbreviations_path)
    
    def load_abbreviations(self, path: Path) -> None:
        """
        Load abbreviation rules from a JSON file.
        
        Args:
            path: Path to the abbreviations JSON file
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.abbreviations = json.load(f)
            
            # Pre-compile regex patterns for efficiency
            self._compile_patterns()
            
            logger.info(f"Loaded abbreviations for {len(self.abbreviations)} languages from {path}")
        except FileNotFoundError:
            logger.warning(f"Abbreviations file not found: {path}")
        except json.JSONDecodeError:
            logger.error(f"Error parsing abbreviations file: {path}")
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for all abbreviation rules."""
        for lang, components in self.abbreviations.items():
            self.compiled_patterns[lang] = {}
            
            for component, replacements in components.items():
                self.compiled_patterns[lang][component] = []
                
                for replacement in replacements:
                    # Each replacement should have 'from' and 'to' keys
                    if 'from' in replacement and 'to' in replacement:
                        pattern = re.compile(
                            r'\b' + re.escape(replacement['from']) + r'\b',
                            re.IGNORECASE
                        )
                        self.compiled_patterns[lang][component].append(
                            (pattern, replacement['to'])
                        )
    
    def abbreviate(self, 
                  component_name: str, 
                  component_value: str, 
                  language: str = 'en',
                  full_components: Optional[Dict[str, Any]] = None) -> str:
        """
        Abbreviate a component value based on rules.
        
        Args:
            component_name: Name of the component (e.g., 'road', 'state')
            component_value: Value to abbreviate
            language: Language code for abbreviation rules
            full_components: Complete address components for context
            
        Returns:
            Abbreviated component value
        """
        if not component_value:
            return component_value
        
        # Skip abbreviation if the value is already short
        if len(component_value) <= 2:
            return component_value
        
        # Check if we have rules for this language and component
        if (language not in self.compiled_patterns or
            component_name not in self.compiled_patterns.get(language, {})):
            # Try 'en' as fallback if available
            if (language != 'en' and 'en' in self.compiled_patterns and 
                component_name in self.compiled_patterns.get('en', {})):
                language = 'en'
            else:
                return component_value
        
        # Apply all matching patterns
        result = component_value
        for pattern, replacement in self.compiled_patterns[language][component_name]:
            result = pattern.sub(replacement, result)
        
        return result
    
    def abbreviate_address(self, 
                         components: Dict[str, Any], 
                         language: str = 'en') -> Dict[str, Any]:
        """
        Abbreviate all components in an address.
        
        Args:
            components: Address components
            language: Language code for abbreviation rules
            
        Returns:
            Address with abbreviated components
        """
        result = components.copy()
        
        # Apply abbreviations to each component
        for component_name, component_value in components.items():
            if isinstance(component_value, str):
                result[component_name] = self.abbreviate(
                    component_name, component_value, language, components
                )
        
        return result
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of languages with abbreviation rules.
        
        Returns:
            List of language codes
        """
        return list(self.abbreviations.keys())


def load_default_abbreviations() -> AbbreviationEngine:
    """
    Load default abbreviations from the data directory.
    
    Returns:
        Initialized AbbreviationEngine
    """
    # Potential paths to check
    potential_paths = [
        Path("address_formatter/data/templates/abbreviations.json"),
        Path("data/templates/abbreviations.json"),
        Path("../data/templates/abbreviations.json"),
    ]
    
    engine = AbbreviationEngine()
    
    # Try each path
    for path in potential_paths:
        if path.exists():
            engine.load_abbreviations(path)
            return engine
    
    logger.warning("No default abbreviations file found")
    return engine 