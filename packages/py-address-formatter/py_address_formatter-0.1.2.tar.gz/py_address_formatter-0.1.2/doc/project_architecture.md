# PyAddress Project Architecture

## Overview

PyAddress is a comprehensive address formatting library that formats address components according to country-specific rules. The system includes components for normalization, formatting, rendering, as well as an extensible plugin architecture and machine learning capabilities.

This document outlines the architecture, component interactions, and data flow of the PyAddress library.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                             PyAddress Library                            │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            AddressFormatter                              │
│                                                                         │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐      │
│   │  Normalizer   │───▶│ Plugin Manager │───▶│     Renderer     │      │
│   └───────────────┘    └───────────────┘    └───────────────────┘      │
│           │                    │                      │                 │
│           ▼                    ▼                      ▼                 │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐      │
│   │Normalization  │    │    Plugins    │    │    Templates      │      │
│   │    Rules      │    │               │    │                   │      │
│   └───────────────┘    └───────────────┘    └───────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Extension Components                           │
│                                                                         │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐      │
│   │ REST API      │    │ ML Components │    │Command Line Tools │      │
│   └───────────────┘    └───────────────┘    └───────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       External Data & Integration                        │
│                                                                         │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐      │
│   │address-       │    │   External    │    │ Validation Data   │      │
│   │formatting repo│    │  Data Sources │    │     Sources       │      │
│   └───────────────┘    └───────────────┘    └───────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. AddressFormatter

**Location**: `pyaddress/address_formatter/formatter.py`

The central class that coordinates the address formatting pipeline:

1. Normalizes address data
2. Applies plugins 
3. Renders formatted addresses

**Key Methods**:
- `format(address, country_code, options)`: The main method that processes and formats an address
- `_determine_country_code(address)`: Helper method to extract or determine the country code
- `register_plugin(plugin)`: Registers a custom plugin with the formatter

**Dependencies**:
- `AddressNormalizer`: Normalizes address components
- `AddressRenderer`: Renders formatted addresses using templates
- `PluginManager`: Manages plugins and their lifecycle

### 2. AddressNormalizer

**Location**: `pyaddress/address_formatter/core/normalizer.py`

Normalizes address components according to rules.

**Key Methods**:
- `normalize(address)`: Normalizes address components
- `set_normalization_rules(rules)`: Sets custom normalization rules

### 3. AddressRenderer

**Location**: `pyaddress/address_formatter/core/renderer.py`

Renders normalized address data using country-specific templates.

**Key Methods**:
- `render(address, country_code)`: Renders an address
- `_apply_template(address, template)`: Applies a template to address data
- `get_supported_countries()`: Returns a list of supported country codes

**Dependencies**:
- `TemplateLoader`: Loads address formatting templates

### 4. TemplateLoader

**Location**: `pyaddress/address_formatter/core/template_loader.py`

Loads and manages templates for different countries.

**Key Methods**:
- `get_template_for_country(country_code)`: Gets the template for a specific country
- `_load_templates()`: Loads templates from disk

## Plugin System

### 1. PluginManager

**Location**: `pyaddress/address_formatter/plugins/manager.py`

Manages the lifecycle of formatter plugins.

**Key Methods**:
- `load_plugin(plugin_module)`: Loads a plugin from a module path
- `apply_plugins(address, country_code, options)`: Applies all plugins to address data
- `register_plugin(plugin)`: Registers a new plugin

### 2. FormatterPlugin Interface

**Location**: `pyaddress/address_formatter/plugins/interface.py`

Base class for all formatter plugins.

**Key Methods**:
- `pre_format(components, options)`: Processes address components before formatting
- `post_format(formatted_address, components, options)`: Processes the formatted address
- `initialize()`: Initializes the plugin
- `shutdown()`: Cleans up when the plugin is unloaded

### 3. Built-in Plugins

**Location**: `pyaddress/address_formatter/plugins/builtins/`

- **AbbreviationPlugin**: Provides abbreviation functionality
- **AddCountryPlugin**: Adds country information to addresses
- **OutputFormatPlugin**: Handles different output formats
- **MLIntegrationPlugin**: Integrates machine learning capabilities

## Machine Learning Components

**Location**: `pyaddress/ml/`

### 1. MLPredictor

**Location**: `pyaddress/ml/predictor.py`

Predicts missing address components using machine learning.

**Key Methods**:
- `predict_components(address_text)`: Predicts structured components from text
- `extract_components(address_text)`: Extracts components from unstructured text

### 2. MLTrainer

**Location**: `pyaddress/ml/trainer.py`

Trains machine learning models for address prediction.

**Key Methods**:
- `train(training_data)`: Trains a model with training data
- `evaluate(test_data)`: Evaluates model performance

## API and CLI Components

### 1. REST API

**Location**: `pyaddress/address_formatter/api/`

Provides a RESTful API for address formatting.

**Key Files**:
- `main.py`: FastAPI application
- `middleware.py`: API middleware
- `server.py`: Server configuration

### 2. Command Line Interface

**Location**: `pyaddress/address_formatter/cli.py`

Provides a command-line interface.

**Key Commands**:
- `format`: Formats addresses
- `validate`: Validates addresses
- `export`: Exports address data

## External Integration - GitHub Repository

**Location**: `pyaddress/address-formatting/` (Git submodule)

### 1. Address Formatting Repository Integration

The PyAddress system integrates with the ["address-formatting" GitHub repository](https://github.com/OpenCageData/address-formatting) as a Git submodule, which provides a comprehensive set of address templates and formatting rules for countries worldwide.

**Setup Connection**:
- Located at `.gitmodules` in the project root
- Referenced via the Git submodule system

**Purpose and Usage**:
- Provides standardized address formatting templates for 200+ countries
- Offers validation rules and test cases for address formats
- Serves as the source of truth for country-specific formatting conventions

**Integration Points**:
- `TemplateLoader` uses the YAML templates from this repository
- The normalization rules are derived from patterns in these templates
- Test data from this repository is used to validate the formatter's behavior

**Sync Process**:
- The module is initialized during project setup with `git submodule init` and `git submodule update`
- Templates are periodically synchronized when the upstream repository is updated
- The PyAddress system converts the YAML templates into its internal format during loading

### 2. Template Processing

**Location**: `pyaddress/address_formatter/management/process_templates.py`

This component processes the templates from the GitHub repository and converts them into the format used by PyAddress.

**Key Methods**:
- `process_templates()`: Processes all templates from the repository
- `update_templates()`: Updates templates when the repository is updated
- `validate_templates()`: Validates templates against test cases

### 3. Integration Workflow

1. External address formatting standards are maintained in the GitHub repository
2. These standards are imported as a Git submodule
3. The template processor converts these into the internal format
4. The address formatter uses the processed templates for formatting
5. Updates to the external repository can be incorporated by updating the submodule

## Data Flow

### Address Formatting Flow

1. User provides address components to the `format_address()` function or `AddressFormatter.format()` method
2. Address components are normalized by `AddressNormalizer`
3. Plugins are applied in order of priority via `PluginManager`
4. Address is rendered using templates via `AddressRenderer`
5. Formatted address is returned to the user

### Plugin Processing Flow

1. Plugins are loaded at initialization or registered at runtime
2. For each address formatting request:
   - Each plugin's `pre_format()` method is called before rendering
   - The address is rendered
   - Each plugin's `post_format()` method is called after rendering

### ML Integration Flow

1. `MLIntegrationPlugin` connects the core formatter to ML capabilities
2. When ML is enabled:
   - Address components are pre-processed before formatting
   - Missing components may be predicted using the ML models
   - Components are post-processed for final output

### GitHub Repository Integration Flow

1. Address format definitions are maintained in the external GitHub repository
2. These definitions are pulled into the project as a Git submodule
3. During build or runtime initialization:
   - Templates are loaded from the submodule
   - Templates are processed and converted to the internal format
   - Templates are cached for performance
4. The formatter uses these templates when rendering addresses
5. When the GitHub repository is updated:
   - The submodule is updated with `git submodule update`
   - Templates are reprocessed and the cache is invalidated
   - The formatter uses the updated templates

## Configuration

**Location**: `pyaddress/address_formatter/config.py`

Manages configuration for the address formatter:

- Template paths
- Plugin directories
- Machine learning settings
- API configuration

## Extension Points

The system is designed to be extensible in several ways:

1. **Custom Plugins**: Create classes that implement the `FormatterPlugin` interface
2. **Custom Templates**: Add new templates to support additional countries
3. **Custom Normalization Rules**: Add or modify normalization rules
4. **ML Model Extension**: Train and use custom ML models for component prediction

## Testing Infrastructure

**Location**: `pyaddress/tests/`

Includes unit tests, integration tests, and end-to-end tests:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test the complete system

## Deployment Options

The system can be deployed in several ways:

1. **Library**: Use as a Python library in other applications
2. **CLI Tool**: Use the command-line interface
3. **REST API**: Deploy as a REST API service
4. **Docker Container**: Deploy using the provided Dockerfile

## Performance Considerations

- Template caching improves rendering performance
- Plugin prioritization allows control over processing order
- ML integration can be disabled for performance-critical applications
- GitHub repository templates are processed once and cached for efficiency

## Future Expansion Areas

- Additional country format support
- Enhanced ML capabilities for address parsing
- Performance optimizations for high-volume processing
- Additional output formats and localization options
- Automated syncing with the GitHub repository for template updates 