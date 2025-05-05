"""
Plugin manager for the address formatter.

This module provides functionality for loading, managing, and
executing formatter plugins.
"""
import importlib
import importlib.util
import inspect
import logging
import os
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, Tuple

from .interface import FormatterPlugin, PluginMetadata


class PluginManager:
    """
    Manager for formatter plugins.
    
    The PluginManager handles plugin discovery, loading, and execution
    during the address formatting process.
    """
    
    def __init__(self):
        """Initialize the plugin manager with empty plugin lists."""
        self.plugins: List[FormatterPlugin] = []
        self._logger = logging.getLogger(__name__)
        
        # Automatically load built-in plugins
        self._load_builtin_plugins()
    
    def _load_builtin_plugins(self):
        """
        Load built-in plugins from the builtins package.
        
        This method is called automatically during initialization.
        """
        try:
            # Try to import the builtins module using the current package structure
            from address_formatter.plugins import builtins
            
            # Check if builtins module has plugin instances
            for attr_name in dir(builtins):
                attr = getattr(builtins, attr_name)
                if isinstance(attr, FormatterPlugin):
                    # The plugin is already instantiated in __init__.py
                    self.plugins.append(attr)
                    self._logger.info(f"Loaded built-in plugin: {attr.metadata.name}")
            
            # If no plugins were found, discover them
            if not self.plugins:
                builtin_plugin_dir = os.path.join(os.path.dirname(__file__), "builtins")
                self.discover_plugins(builtin_plugin_dir)
        except ImportError as e:
            self._logger.warning(f"Could not import built-in plugins: {e}")
        except Exception as e:
            self._logger.error(f"Error loading built-in plugins: {e}")
    
    def discover_plugins(self, plugin_dir: Optional[str] = None) -> List[str]:
        """
        Discover plugins in the specified directory.
        
        Args:
            plugin_dir: The directory to search for plugins (default: built-in plugins)
            
        Returns:
            List of discovered plugin module paths
        """
        discovered = []
        
        # Use the default plugin directory if none specified
        if plugin_dir is None:
            plugin_dir = os.path.join(os.path.dirname(__file__), "builtins")
        
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            self._logger.warning(f"Plugin directory {plugin_dir} does not exist")
            return discovered
        
        # Add plugin directory to path if not already there
        if str(plugin_path.absolute()) not in sys.path:
            sys.path.append(str(plugin_path.absolute()))
        
        # Discover modules in the plugin directory
        try:
            for _, name, is_pkg in pkgutil.iter_modules([str(plugin_path)]):
                if not is_pkg:  # Only consider Python modules, not packages
                    discovered.append(name)
        except Exception as e:
            self._logger.error(f"Error discovering plugins: {str(e)}")
        
        return discovered
    
    def load_plugin(self, plugin_module: str) -> bool:
        """
        Load a plugin from a module path.
        
        Args:
            plugin_module: The module path of the plugin
            
        Returns:
            True if the plugin was loaded successfully, False otherwise
        """
        try:
            # Try different ways to import the module
            module = None
            import_errors = []
            
            # Try direct import
            try:
                module = importlib.import_module(plugin_module)
            except ImportError as e:
                import_errors.append(str(e))
                
                # Try as a relative import within the plugins package
                try:
                    module = importlib.import_module(f".builtins.{plugin_module}", __package__)
                except ImportError as e2:
                    import_errors.append(str(e2))
                    
                    # Try from the current directory
                    try:
                        if plugin_module.endswith(".py"):
                            plugin_path = plugin_module
                        else:
                            plugin_path = f"{plugin_module}.py"
                        
                        if os.path.exists(plugin_path):
                            return self.load_plugin_from_path(plugin_path)
                    except Exception as e3:
                        import_errors.append(str(e3))
            
            # If we failed to import the module, log the errors and return False
            if module is None:
                self._logger.error(f"Error loading plugin {plugin_module}: {'; '.join(import_errors)}")
                return False
            
            # Find plugin classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, FormatterPlugin) and 
                    obj is not FormatterPlugin):
                    
                    # Create an instance of the plugin
                    plugin = obj()
                    
                    # Initialize the plugin
                    plugin.initialize()
                    
                    # Add to the plugin list
                    self.plugins.append(plugin)
                    self._logger.info(f"Loaded plugin: {plugin.metadata}")
                    return True
            
            self._logger.warning(f"No plugin classes found in module {plugin_module}")
            return False
            
        except Exception as e:
            self._logger.error(f"Error loading plugin {plugin_module}: {str(e)}")
            return False
    
    def load_plugin_from_path(self, plugin_path: str) -> bool:
        """
        Load a plugin from a file path.
        
        Args:
            plugin_path: The file path of the plugin
            
        Returns:
            True if the plugin was loaded successfully, False otherwise
        """
        try:
            # Create a unique module name
            module_name = f"plugin_{Path(plugin_path).stem}"
            
            # Load the module from the file path
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None or spec.loader is None:
                self._logger.error(f"Could not load plugin from {plugin_path}")
                return False
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, FormatterPlugin) and 
                    obj is not FormatterPlugin):
                    
                    # Create an instance of the plugin
                    plugin = obj()
                    
                    # Initialize the plugin
                    plugin.initialize()
                    
                    # Add to the plugin list
                    self.plugins.append(plugin)
                    self._logger.info(f"Loaded plugin: {plugin.metadata}")
                    return True
            
            self._logger.warning(f"No plugin classes found in {plugin_path}")
            return False
            
        except Exception as e:
            self._logger.error(f"Error loading plugin from {plugin_path}: {str(e)}")
            return False
    
    def get_plugins(self) -> List[FormatterPlugin]:
        """
        Get all loaded plugins.
        
        Returns:
            List of loaded plugins
        """
        return sorted(self.plugins, key=lambda p: p.metadata.priority, reverse=True)
    
    def get_plugin_by_name(self, name: str) -> Optional[FormatterPlugin]:
        """
        Get a plugin by name.
        
        Args:
            name: The name of the plugin
            
        Returns:
            The plugin with the specified name, or None if not found
        """
        for plugin in self.plugins:
            if plugin.metadata.name.lower() == name.lower():
                return plugin
        return None
    
    def get_available_plugins(self) -> List[str]:
        """
        Get a list of names of all available plugins.
        
        Returns:
            List of plugin names
        """
        return [plugin.metadata.name for plugin in self.plugins]
    
    def apply_plugin(self, plugin_name: str, address: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a specific plugin to the address.
        
        Args:
            plugin_name: Name of the plugin to apply
            address: Address components dictionary
            options: Formatting options
            
        Returns:
            Modified address components
        """
        plugin = self.get_plugin_by_name(plugin_name)
        if plugin is None:
            self._logger.warning(f"Plugin {plugin_name} not found")
            return address
            
        try:
            # Ensure address is a dictionary
            if not isinstance(address, dict):
                self._logger.warning(f"Plugin {plugin_name} received non-dictionary address: {address}")
                return address
                
            # Ensure options is a dictionary
            if not isinstance(options, dict):
                options = {}
                
            return plugin.process(address, options)
        except Exception as e:
            self._logger.error(f"Error applying plugin {plugin_name}: {str(e)}")
            return address
    
    def apply_plugins(self, address: Dict[str, Any], country_code: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all appropriate plugins to an address.
        
        Args:
            address: Address components dictionary
            country_code: Country code for country-specific plugins
            options: Formatting options
            
        Returns:
            Modified address components
        """
        processed = address.copy()
        
        # Add country code to the processed address if not already present
        if country_code and 'country_code' not in processed:
            processed['country_code'] = country_code
            
        # Apply pre-format plugins
        processed = self.apply_plugins_pre_format(processed, options)
        
        # Apply plugins based on options
        for option_name, option_value in options.items():
            if option_value and option_name in self.get_available_plugins():
                try:
                    self._logger.info(f"Applying plugin {option_name} based on option")
                    processed = self.apply_plugin(option_name, processed, options)
                except Exception as e:
                    self._logger.error(f"Error applying plugin {option_name}: {str(e)}")
        
        return processed
    
    def apply_plugins_pre_format(self, 
                                components: Dict[str, Any], 
                                options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all loaded plugins to address components before formatting.
        
        Args:
            components: The address components to process
            options: Formatting options
            
        Returns:
            Processed address components
        """
        processed = components.copy()
        
        for plugin in self.get_plugins():
            try:
                processed = plugin.pre_format(processed, options)
            except Exception as e:
                self._logger.error(f"Error in plugin {plugin.metadata.name} (pre_format): {str(e)}")
        
        return processed
    
    def apply_plugins_post_format(self, 
                                 formatted_address: str, 
                                 components: Dict[str, Any], 
                                 options: Dict[str, Any]) -> str:
        """
        Apply all loaded plugins to a formatted address after formatting.
        
        Args:
            formatted_address: The formatted address
            components: The address components used for formatting
            options: Formatting options
            
        Returns:
            Processed formatted address
        """
        processed = formatted_address
        
        for plugin in self.get_plugins():
            try:
                processed = plugin.post_format(processed, components, options)
            except Exception as e:
                self._logger.error(f"Error in plugin {plugin.metadata.name} (post_format): {str(e)}")
        
        return processed
    
    def unload_all_plugins(self) -> None:
        """Unload all plugins."""
        for plugin in self.plugins:
            try:
                plugin.shutdown()
            except Exception as e:
                self._logger.error(f"Error shutting down plugin {plugin.metadata.name}: {str(e)}")
        
        self.plugins = []
    
    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin by name.
        
        Args:
            name: The name of the plugin to unload
            
        Returns:
            True if the plugin was unloaded, False otherwise
        """
        plugin = self.get_plugin_by_name(name)
        if plugin is None:
            return False
        
        try:
            plugin.shutdown()
            self.plugins.remove(plugin)
            return True
        except Exception as e:
            self._logger.error(f"Error unloading plugin {name}: {str(e)}")
            return False


# Create a singleton instance of the plugin manager
manager = PluginManager() 