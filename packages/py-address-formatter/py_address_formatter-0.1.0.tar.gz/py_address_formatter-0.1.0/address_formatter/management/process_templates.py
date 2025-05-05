"""
Template processing script.

This script converts OpenCageData YAML templates to JSON format
and prepares them for use in the address formatter.
"""
import os
import json
import yaml
from pathlib import Path
import shutil
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("template_processor")

class TemplateProcessor:
    """Process OpenCageData templates into JSON format."""

    def __init__(self, source_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        """
        Initialize the template processor.

        Args:
            source_dir: Path to OpenCageData templates
            output_dir: Output directory for processed templates
        """
        # Get the script directory
        script_dir = Path(__file__).parent.absolute()
        pyaddress_dir = script_dir.parent.parent

        # Default paths relative to the pyaddress directory
        self.source_dir = source_dir or (pyaddress_dir / "address-formatting")
        self.output_dir = output_dir or (pyaddress_dir / "address_formatter/data/templates")

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        logger.info(f"Script directory: {script_dir}")
        logger.info(f"PyAddress directory: {pyaddress_dir}")
        logger.info(f"Source directory: {self.source_dir}")
        logger.info(f"Output directory: {self.output_dir}")

    def process_all(self) -> None:
        """Process all templates and configuration files."""
        logger.info("Starting template processing...")

        # Validate source directory
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")

        # Process worldwide template
        self._process_worldwide()

        # Process country-specific templates
        self._process_country_templates()

        # Process component aliases
        self._process_component_aliases()

        # Process address formatting configuration
        self._process_formatting_config()

        logger.info("Template processing completed successfully.")

    def _process_worldwide(self) -> None:
        """Process the worldwide template."""
        worldwide_path = self.source_dir / "conf/countries/worldwide.yaml"

        if not worldwide_path.exists():
            raise FileNotFoundError(f"Worldwide template not found: {worldwide_path}")

        logger.info(f"Processing worldwide template from {worldwide_path}")

        with open(worldwide_path, 'r', encoding='utf-8') as f:
            worldwide = yaml.safe_load(f)

        # Save as JSON
        output_path = self.output_dir / "worldwide.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"default": worldwide}, f, ensure_ascii=False, indent=2)

        logger.info(f"Worldwide template saved to {output_path}")

    def _process_country_templates(self) -> None:
        """Process country-specific templates."""
        countries_dir = self.source_dir / "conf/countries"

        if not countries_dir.exists():
            raise FileNotFoundError(f"Countries directory not found: {countries_dir}")

        logger.info(f"Processing country templates from {countries_dir}")

        country_templates = {}
        country_count = 0

        # First, check for individual country files
        for country_file in countries_dir.glob("*.yaml"):
            # Skip worldwide template as we'll process it differently
            if country_file.name == "worldwide.yaml":
                continue

            # Extract country code from filename (e.g., "us.yaml" -> "US")
            country_code = country_file.stem.upper()

            logger.debug(f"Processing country template: {country_code}")

            # Load YAML data
            with open(country_file, 'r', encoding='utf-8') as f:
                template = yaml.safe_load(f)

            # Add to country templates dictionary
            country_templates[country_code] = template
            country_count += 1

        # Now process the worldwide.yaml file which contains all country templates
        worldwide_path = countries_dir / "worldwide.yaml"
        if worldwide_path.exists():
            logger.info(f"Processing country templates from worldwide file: {worldwide_path}")

            with open(worldwide_path, 'r', encoding='utf-8') as f:
                worldwide_data = yaml.safe_load(f)

            # Extract country-specific templates
            for key, value in worldwide_data.items():
                # Check if the key is a 2-letter country code (e.g., "US:", "GB:")
                if len(key) == 2 and key.isalpha():
                    country_code = key.upper()
                    logger.debug(f"Extracting country template from worldwide file: {country_code}")

                    # Add to country templates dictionary
                    country_templates[country_code] = value
                    country_count += 1

        # Save all country templates as a single JSON file
        output_path = self.output_dir / "countries.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(country_templates, f, ensure_ascii=False, indent=2)

        logger.info(f"Processed {country_count} country templates to {output_path}")

    def _process_component_aliases(self) -> None:
        """Process component aliases from OpenCageData."""
        components_path = self.source_dir / "conf/components.yaml"

        if not components_path.exists():
            raise FileNotFoundError(f"Components file not found: {components_path}")

        logger.info(f"Processing component aliases from {components_path}")

        # Load YAML data
        with open(components_path, 'r', encoding='utf-8') as f:
            components_data = list(yaml.safe_load_all(f))

        aliases = []
        components_count = 0
        aliases_count = 0

        # Process each component
        for component in components_data:
            component_name = component.get('name')
            component_aliases = component.get('aliases', [])

            if not component_name:
                continue

            components_count += 1

            # Add component name as an alias to itself
            aliases.append({
                'name': component_name,
                'alias': component_name
            })

            # Process aliases
            for alias in component_aliases:
                aliases.append({
                    'name': component_name,
                    'alias': alias
                })
                aliases_count += 1

        # Save aliases as JSON
        output_path = self.output_dir / "aliases.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(aliases, f, ensure_ascii=False, indent=2)

        logger.info(f"Processed {components_count} components with {aliases_count} aliases to {output_path}")

    def _process_formatting_config(self) -> None:
        """Process address formatting configuration."""
        conf_path = self.source_dir / "conf/abbreviations"

        if not conf_path.exists():
            logger.warning(f"Abbreviations directory not found: {conf_path}")
            return

        logger.info(f"Processing formatting configuration from {conf_path}")

        abbreviations = {}

        # Process each abbreviation file
        for abbr_file in conf_path.glob("*.yaml"):
            # Extract language code from filename
            lang_code = abbr_file.stem

            # Load YAML data
            with open(abbr_file, 'r', encoding='utf-8') as f:
                abbr_data = yaml.safe_load(f)

            # Add to abbreviations dictionary
            abbreviations[lang_code] = abbr_data

        # Save abbreviations as JSON
        output_path = self.output_dir / "abbreviations.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(abbreviations, f, ensure_ascii=False, indent=2)

        logger.info(f"Processed abbreviations for {len(abbreviations)} languages to {output_path}")


def main():
    """Execute template processing."""
    try:
        processor = TemplateProcessor()
        processor.process_all()
    except Exception as e:
        logger.error(f"Error processing templates: {str(e)}")
        raise


if __name__ == "__main__":
    main()