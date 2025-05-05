"""
Address formatter core module.

This module contains the main AddressFormatter class responsible
for normalizing and rendering addresses.
"""
from typing import Dict, Any, List, Optional, Union, Callable
import os
from pathlib import Path

# Import core components with proper paths
from address_formatter.core.normalizer import AddressNormalizer
from address_formatter.core.template_loader import TemplateLoader
from address_formatter.core.renderer import AddressRenderer
from address_formatter.core.country_rules import CountryRules
from address_formatter.plugins.manager import PluginManager

class AddressFormatter:
    """
    Main address formatter class.
    
    Combines address normalization, plugin processing, and rendering
    to format addresses according to country-specific standards.
    """
    
    def __init__(self, 
                 template_paths: Optional[List[str]] = None,
                 custom_rules: Optional[Dict[str, Any]] = None,
                 enable_plugins: bool = True):
        """
        Initialize the address formatter.
        
        Args:
            template_paths: List of paths to template files or directories
            custom_rules: Custom normalization rules
            enable_plugins: Whether to use plugins for address processing
        """
        self.normalizer = AddressNormalizer(custom_rules=custom_rules)
        self.renderer = AddressRenderer(template_paths=template_paths)
        self.plugin_manager = PluginManager() if enable_plugins else None
        self.plugins_enabled = enable_plugins
    
    def format(self, 
               address: Dict[str, Any], 
               country_code: Optional[str] = None,
               options: Optional[Dict[str, Any]] = None) -> str:
        """
        Format an address.
        
        Args:
            address: Address dictionary
            country_code: ISO country code (optional if in address)
            options: Formatting options dictionary
            
        Returns:
            Formatted address string
            
        Raises:
            ValueError: If country code cannot be determined
        """
        # Normalize address
        normalized = self.normalizer.normalize(address)
        
        # Ensure options is a dictionary
        if options is None:
            options = {}
        
        # Apply plugins if enabled
        if self.plugins_enabled and self.plugin_manager:
            # Apply plugins
            for plugin_name in self.plugin_manager.get_available_plugins():
                try:
                    normalized = self.plugin_manager.apply_plugin(
                        plugin_name, normalized, options
                    )
                except Exception as e:
                    # Log the error but continue with other plugins
                    print(f"Error applying plugin {plugin_name}: {e}")
        
        # Determine country code
        if not country_code:
            country_code = normalized.get('country_code')
        
        # Render the address
        return self.renderer.render(normalized, country_code)
    
    def batch_format(self, 
                     addresses: List[Dict[str, Any]], 
                     country_code: Optional[str] = None,
                     plugins: Optional[List[str]] = None) -> List[str]:
        """
        Format multiple addresses.
        
        Args:
            addresses: List of address dictionaries
            country_code: Default ISO country code (optional)
            plugins: List of plugin names to apply (optional)
            
        Returns:
            List of formatted address strings
        """
        return [self.format(addr, country_code, plugins) for addr in addresses]
    
    def get_supported_countries(self) -> List[str]:
        """
        Get a list of supported country codes.
        
        Returns:
            List of country codes with templates
        """
        return self.renderer.get_supported_countries()
    
    def add_template(self, country_code: str, template: Dict[str, Any]):
        """
        Add or update a template for a specific country.
        
        Args:
            country_code: Country code (e.g., 'US', 'GB')
            template: Template dictionary
        """
        self.renderer.add_template(country_code, template)
    
    def add_normalization_rule(self, rule_name: str, rule_func: callable):
        """
        Add a custom normalization rule.
        
        Args:
            rule_name: Name of the rule
            rule_func: Function implementing the rule
        """
        self.normalizer.add_rule(rule_name, rule_func)
    
    def get_available_plugins(self) -> List[str]:
        """
        Get a list of available plugins.
        
        Returns:
            List of plugin names
        """
        if not self.plugins_enabled or not self.plugin_manager:
            return []
        return self.plugin_manager.get_available_plugins()
    
    def enable_plugins(self, enabled: bool = True):
        """
        Enable or disable plugins.
        
        Args:
            enabled: Whether plugins should be enabled
        """
        self.plugins_enabled = enabled
        if enabled and not self.plugin_manager:
            self.plugin_manager = PluginManager()
    
    def reload_plugins(self):
        """
        Reload all plugins.
        """
        if self.plugins_enabled and self.plugin_manager:
            self.plugin_manager.reload_plugins() 