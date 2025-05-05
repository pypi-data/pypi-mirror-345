# GitHub Integration Guide for PyAddress

## Overview

PyAddress integrates with the ["address-formatting" GitHub repository](https://github.com/OpenCageData/address-formatting) maintained by OpenCage Data as a critical component of its address formatting pipeline. This repository contains a comprehensive collection of address templates and formatting rules for over 200 countries worldwide.

This document explains how the GitHub integration fits into the overall PyAddress architecture and provides practical guidance on using, maintaining, and troubleshooting it.

## How GitHub Integration Fits into the PyAddress Architecture

The external GitHub repository is a foundational component in the PyAddress pipeline:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GitHub Repository (address-formatting)                │
│                                                                         │
│     ┌───────────────┐      ┌───────────────┐      ┌──────────────┐     │
│     │Country Template│      │ Normalization │      │   Test       │     │
│     │     YAML      │─────▶│    Rules      │─────▶│   Cases      │     │
│     └───────────────┘      └───────────────┘      └──────────────┘     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Template Processing Layer                         │
│                                                                         │
│     ┌───────────────┐      ┌───────────────┐      ┌──────────────┐     │
│     │process_templates.py  │prepare_templates.py  │template_loader.py   │
│     └───────────────┘      └───────────────┘      └──────────────┘     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            AddressFormatter                              │
│                                                                         │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐      │
│   │  Normalizer   │───▶│ Plugin Manager │───▶│     Renderer     │      │
│   └───────────────┘    └───────────────┘    └───────────────────┘      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            Formatted Address                             │
└─────────────────────────────────────────────────────────────────────────┘
```

### Real-World Scenario

1. When a user wants to format an address for "1600 Pennsylvania Avenue, Washington DC 20500, USA":

   ```python
   from pyaddress import format_address
   
   address = {
       'house_number': '1600',
       'road': 'Pennsylvania Avenue',
       'city': 'Washington',
       'state': 'DC',
       'postcode': '20500',
       'country_code': 'US'
   }
   
   formatted_address = format_address(address)
   print(formatted_address)
   # Output:
   # 1600 Pennsylvania Avenue
   # Washington, DC 20500
   # United States
   ```

2. Behind the scenes, PyAddress:
   - Identifies the country (US)
   - Retrieves the appropriate template from the processed GitHub templates
   - Applies country-specific formatting rules derived from the GitHub repository 
   - Returns the properly formatted address

This entire process relies on the GitHub repository templates to ensure proper formatting according to regional standards.

## Integration Architecture

### Git Submodule Structure

The address-formatting repository is integrated as a Git submodule within the PyAddress project:

```
pyaddress/
├── .gitmodules                              # Defines the submodule configuration
├── address-formatting/                      # The actual submodule (external repository)
│   ├── conf/countries/                      # Country-specific YAML templates
│   │   ├── worldwide.yaml                   # Contains templates for most countries
│   │   └── [country-specific files].yaml    # Country-specific overrides
│   ├── testcases/                           # Test cases for various countries
│   └── README.md                            # Documentation of the external repository
└── address_formatter/
    ├── core/
    │   └── template_loader.py               # Loads processed templates
    └── management/
        ├── process_templates.py             # Processes GitHub templates
        └── prepare_templates.py             # Prepares templates for use
```

## Complete Workflow: From GitHub to Formatted Address

### 1. Project Setup and Template Processing

When setting up PyAddress, the GitHub repository is integrated:

```bash
# Clone the PyAddress repository
git clone https://github.com/your-org/pyaddress.git
cd pyaddress

# Initialize and update the GitHub submodule
git submodule init
git submodule update

# Install dependencies
pip install -r requirements.txt

# Process templates from GitHub repository
python -m pyaddress.address_formatter.management.process_templates
```

The `process_templates.py` script:
1. Reads YAML templates from `pyaddress/address-formatting/conf/countries/`
2. Processes them into Python dictionaries
3. Stores processed templates in `pyaddress/data/templates/processed/`

### 2. Address Formatting Pipeline

When formatting an address, the complete flow is:

```python
# In a real application
from pyaddress import AddressFormatter

# Input address components
address = {
    'house_number': '1600',
    'road': 'Pennsylvania Avenue',
    'city': 'Washington',
    'state': 'DC',
    'postcode': '20500',
    'country': 'United States',
    'country_code': 'US'
}

# Create formatter
formatter = AddressFormatter()

# Format the address - this is where the GitHub templates are used
formatted_address = formatter.format(address)

print(formatted_address)
```

At each step, the GitHub integration plays a role:

1. **Country Detection**:
   - Country-specific templates from GitHub determine which countries are supported
   - `country_code` lookup tables are derived from GitHub data

2. **Normalization**:
   - Normalization rules in the GitHub repo standardize components
   - Abbreviations and synonyms are processed

3. **Template Selection**:
   - The appropriate template is selected from processed GitHub templates
   - Fallback templates are used if needed

4. **Rendering**:
   - The template is applied to address components
   - Missing components are handled according to GitHub template rules

## Practical Usage Examples

### Example 1: Formatting International Addresses

Format addresses for different countries using templates from the GitHub repository:

```python
from pyaddress import format_address

# US address
us_address = {
    'house_number': '1600',
    'road': 'Pennsylvania Avenue',
    'city': 'Washington',
    'state': 'DC',
    'postcode': '20500',
    'country_code': 'US'
}

# UK address
uk_address = {
    'house_number': '10',
    'road': 'Downing Street',
    'city': 'London',
    'postcode': 'SW1A 2AA',
    'country_code': 'GB'
}

# Format addresses using country-specific templates from GitHub
print(format_address(us_address))
print(format_address(uk_address))

# Output:
# 1600 Pennsylvania Avenue
# Washington, DC 20500
# United States
#
# 10 Downing Street
# London
# SW1A 2AA
# United Kingdom
```

### Example 2: Checking Template Availability

Check which countries are supported by the GitHub templates:

```python
from pyaddress import AddressFormatter

formatter = AddressFormatter()
countries = formatter.get_supported_countries()

print(f"Total supported countries: {len(countries)}")
print(f"Sample countries: {', '.join(sorted(countries)[:10])}")

# Verify if a specific country is supported
country_code = "JP"
if country_code in countries:
    print(f"Templates for {country_code} are available")
    # Get the template
    template = formatter.renderer.template_loader.get_template_for_country(country_code)
    print(f"Template format: {template['format']}")
else:
    print(f"No templates available for {country_code}")
```

### Example 3: Custom Templates Based on GitHub Templates

Extend the GitHub templates with your own customizations:

```python
from pyaddress import AddressFormatter
from pyaddress.address_formatter.core.template_loader import TemplateLoader

# Load the standard US template from GitHub
loader = TemplateLoader()
us_template = loader.get_template_for_country("US")

# Create a custom template based on the GitHub template
custom_template = us_template.copy()
custom_template["format"] = "{{house_number}} {{road}}\n{{city}}, {{state}} {{postcode}}\nUSA"

# Use the custom template
formatter = AddressFormatter()
formatter.renderer.add_template("US_CUSTOM", custom_template)

# Use the custom template to format an address
address = {
    'house_number': '1600',
    'road': 'Pennsylvania Avenue',
    'city': 'Washington',
    'state': 'DC',
    'postcode': '20500',
    'country_code': 'US_CUSTOM'  # Use our custom template
}

formatted = formatter.format(address)
print(formatted)
# Output:
# 1600 Pennsylvania Avenue
# Washington, DC 20500
# USA
```

## Maintaining and Updating the Integration

### Updating the Submodule

The GitHub repository is periodically updated with new templates and improvements. To incorporate these updates:

```bash
# Navigate to the project root
cd /path/to/pyaddress

# Update the submodule to the latest version
git submodule update --remote

# Re-process templates with the updated data
python -m pyaddress.address_formatter.management.process_templates

# Run tests to ensure compatibility
python -m pytest pyaddress/tests/test_templates.py

# If tests pass, commit the changes
git add pyaddress/address-formatting
git add pyaddress/data/templates/processed
git commit -m "Update address-formatting submodule and process templates"
```

### Integration Update Workflow

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Update Submodule   │────▶│  Process Templates  │────▶│  Run Validation     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
           │                          │                           │
           ▼                          ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ git submodule update│     │process_templates.py │     │validate_templates.py│
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

## Troubleshooting Integration Issues

### Common Issues and Solutions

1. **Missing Templates After Update**:
   ```python
   # Check if templates were properly processed
   from pyaddress.address_formatter.management.process_templates import process_templates, validate_templates
   
   # Re-process templates
   process_templates()
   
   # Validate the templates
   validation_results = validate_templates()
   if validation_results['failed'] > 0:
       print(f"Found {validation_results['failed']} template validation failures")
       # Review individual failures
       for failure in validation_results['failure_details']:
           print(f"Country: {failure['country']}, Issue: {failure['reason']}")
   ```

2. **Template Format Changes in GitHub Repository**:
   If the GitHub repository changes its format, you may need to update the template processor:
   
   ```python
   # Update the template processor to handle new format
   # In pyaddress/address_formatter/management/process_templates.py
   
   def process_yaml_template(yaml_data):
       """
       Process YAML template with updated format handling
       """
       # Updated code to handle new format
       # ...
   ```

3. **Debugging Template Issues**:
   ```python
   from pyaddress.address_formatter.core.template_loader import TemplateLoader
   
   # Load templates and check for specific country
   loader = TemplateLoader(debug=True)
   
   # Get raw template for debugging
   country_code = "US"
   template = loader.get_template_for_country(country_code, raw=True)
   print(f"Raw template for {country_code}: {template}")
   
   # Compare with processed template
   processed = loader.get_template_for_country(country_code)
   print(f"Processed template: {processed}")
   ```

## Conclusion: The Role of GitHub Integration in PyAddress

The GitHub integration is a foundational component of PyAddress, providing:

1. **Standardization**: Ensures addresses are formatted according to international standards
2. **Maintainability**: Leverages community-maintained templates instead of maintaining them in-house
3. **Extensibility**: Allows for easy extension with custom templates based on standard ones
4. **Validation**: Provides test cases to validate formatting functionality

By connecting PyAddress to this external repository, users benefit from up-to-date address formatting rules without requiring frequent library updates. The architecture is designed to seamlessly incorporate template updates when they become available, ensuring addresses are always formatted according to the latest international standards.

This integration demonstrates how PyAddress leverages external resources to provide a robust, accurate, and comprehensive address formatting solution while maintaining flexibility for customization and extension. 