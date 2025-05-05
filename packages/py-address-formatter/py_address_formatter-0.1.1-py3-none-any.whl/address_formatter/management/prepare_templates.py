"""
Template management utility.

This module processes address formatting templates from YAML to JSON format
and prepares them for use in the address formatter.
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class TemplateProcessor:
    """
    Processes address formatting templates from YAML to JSON format.
    
    This class is responsible for:
    - Loading YAML templates from OpenCageData
    - Converting templates to JSON format
    - Extracting component aliases
    - Generating template files
    """
    
    def __init__(self, source_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        """
        Initialize the template processor.
        
        Args:
            source_dir: Directory containing source YAML templates. 
                        If None, uses default OpenCageData submodule path.
            output_dir: Directory to output processed JSON templates.
                        If None, uses default data/templates path.
        """
        # Set default paths if not provided
        self.source_dir = source_dir or Path("address-formatting")
        self.output_dir = output_dir or Path("address_formatter/data/templates")
        
    def process_all(self) -> None:
        """
        Process all templates from YAML to JSON.
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Process worldwide template
        self._process_worldwide()
        
        # Process country-specific templates
        self._process_country_specific()
        
        # Generate aliases
        self._generate_aliases()
        
    def _process_worldwide(self) -> None:
        """
        Process the worldwide template.
        """
        worldwide_path = self.source_dir / "conf/countries/worldwide.yaml"
        if not worldwide_path.exists():
            raise FileNotFoundError(f"Worldwide template not found at: {worldwide_path}")
        
        # Load YAML
        with open(worldwide_path, 'r', encoding='utf-8') as f:
            worldwide = yaml.safe_load(f)
        
        # Save as JSON
        output_path = self.output_dir / "worldwide.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"default": worldwide}, f, ensure_ascii=False, indent=2)
    
    def _process_country_specific(self) -> None:
        """
        Process country-specific templates.
        """
        countries_dir = self.source_dir / "conf/countries"
        if not countries_dir.exists():
            raise FileNotFoundError(f"Countries directory not found at: {countries_dir}")
        
        country_templates = {}
        
        # Process each country YAML file
        for country_file in countries_dir.glob("*.yaml"):
            # Skip worldwide template as it's processed separately
            if country_file.name == "worldwide.yaml":
                continue
            
            # Extract country code from filename
            country_code = country_file.stem.upper()
            
            # Load YAML
            with open(country_file, 'r', encoding='utf-8') as f:
                template = yaml.safe_load(f)
            
            # Add to country templates
            country_templates[country_code] = template
        
        # Save country templates as JSON
        output_path = self.output_dir / "countries.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(country_templates, f, ensure_ascii=False, indent=2)
    
    def _generate_aliases(self) -> None:
        """
        Generate component aliases from OpenCageData.
        """
        components_path = self.source_dir / "conf/components.yaml"
        if not components_path.exists():
            raise FileNotFoundError(f"Components file not found at: {components_path}")
        
        aliases = []
        
        # Load components YAML
        with open(components_path, 'r', encoding='utf-8') as f:
            components = yaml.safe_load_all(f)
            
            # Process each component
            for component in components:
                component_name = component.get('name')
                component_aliases = component.get('aliases', [])
                
                # Skip components without name
                if not component_name:
                    continue
                
                # Add the component name itself as an alias
                aliases.append({
                    'name': component_name,
                    'alias': component_name
                })
                
                # Add component aliases
                for alias in component_aliases:
                    aliases.append({
                        'name': component_name,
                        'alias': alias
                    })
        
        # Save aliases as JSON
        output_path = self.output_dir / "aliases.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(aliases, f, ensure_ascii=False, indent=2)


def main():
    """
    Main entry point for template processing.
    """
    processor = TemplateProcessor()
    processor.process_all()
    print("Templates processed successfully.")


if __name__ == "__main__":
    main() 