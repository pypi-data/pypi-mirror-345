# `cli.py` Documentation

This module provides a command-line interface (CLI) for the MeowDoc documentation generator. It handles argument parsing, configuration loading and validation, LLM provider selection, and orchestrates the documentation generation process.

## Overview

The `cli.py` script serves as the entry point for the MeowDoc application. It uses the `argparse` module to define command-line arguments, loads configuration from a TOML file, and uses the configuration to set up the LLM provider.  It then calls the core Meowdoc functionality to generate documentation and update an MkDocs project.

## Functions

### `main()`

```python
def main():
    """Main function to run MeowDoc."""
```

The main function is the entry point of the `cli.py` script. It orchestrates the entire documentation generation process.

**Functionality:**

1.  **Logging Setup**: Initializes basic logging to the console.
2.  **Environment Variable Loading**: Loads environment variables from a `.dotenv` file using `load_dotenv()`.
3.  **LLM API Key Configuration**: Configures the Google Generative AI API key using `os.getenv("GOOGLE_API_KEY")`.
4.  **Argument Parsing**: Uses `argparse` to parse command-line arguments.
5.  **Configuration Loading**: Loads configuration from a TOML file using `load_config()`.
6.  **Configuration Overriding**: Overrides configuration values with command-line arguments using `override_config_with_args()`.
7.  **LLM Provider Selection**: Gets the LLM provider instance using `get_llm_provider()`.
8.  **Interactive Mode Handling**:  Handles interactive mode using `handle_interactive_mode()`.
9.  **Configuration Validation**: Validates the main configuration using `validate_main_config()`.
10. **Extract Config Values:** Extracts configuration values from config.
11. **Logging Configuration:** Logs the configuration using `log_configuration()`.
12. **MeowdocCore Instantiation**: Creates an instance of `core.MeowdocCore`.
13. **MkDocs Setup**: Creates or updates the MkDocs project using `handle_mkdocs_setup()`.
14. **Documentation Generation**: Processes the input path using `generator.process_path()` to generate documentation.
15. **MkDocs Navigation Update**: Updates the MkDocs navigation based on the generated files using `mkdocs.update_mkdocs_nav()`.
16. **MkDocs Config Update:** Updates the mkdocs configuration based on the toml file, using `mkdocs.update_mkdocs_config_from_toml`
17. **Completion Message**: Prints a completion message.

### `load_config(config_path)`

```python
def load_config(config_path):
    """Loads and validates the TOML configuration."""
```

Loads the configuration from a TOML file.

**Parameters:**

*   `config_path` (str): The path to the TOML configuration file.

**Returns:**

*   `dict`: The configuration dictionary if successful, `None` otherwise.

**Errors:**

*   Logs an error and returns `None` if the file is not found or if there is an error parsing the TOML file.
*   Logs an error and returns `None` if the config file structure is invalid.

### `override_config_with_args(config, args)`

```python
def override_config_with_args(config, args):
    """Overrides config values with command-line arguments."""
```

Overrides configuration values with command-line arguments. This allows users to customize the documentation generation process using command-line flags.

**Parameters:**

*   `config` (dict): The configuration dictionary.
*   `args` (`argparse.Namespace`): The parsed command-line arguments.

**Returns:**

*   `dict`: The updated configuration dictionary.

### `get_llm_provider(config)`

```python
def get_llm_provider(config):
    """Gets the LLM provider instance."""
```

Gets the LLM provider instance based on the configuration.

**Parameters:**

*   `config` (dict): The configuration dictionary containing LLM provider settings.

**Returns:**

*   `llm.LLMProvider`: An instance of the LLM provider if successful, `None` otherwise.

**Errors:**

*   Logs an error and returns `None` if the LLM provider cannot be initialized.

### `handle_interactive_mode(config, args)`

```python
def handle_interactive_mode(config, args):
    """Handles interactive mode input."""
```

Handles interactive mode input, prompting the user for configuration values.

**Parameters:**

*   `config` (dict): The configuration dictionary.
*   `args` (`argparse.Namespace`): The parsed command-line arguments.

**Returns:**

*   `dict`: The updated configuration dictionary.

**Functionality:**

If interactive mode is enabled via the `--interactive` flag, this function prompts the user for the following configuration values:

*   Input path (file or directory).
*   Gemini model to use.
*   Whether to create an MkDocs project if one doesn't exist.
*   MkDocs project directory.
*   Docs directory name.
*   Ignore patterns (comma-separated).

### `validate_main_config(config, parser)`

```python
def validate_main_config(config, parser):
    """Validates the main configuration."""
```

Validates the main configuration, ensuring that required parameters are present.

**Parameters:**

*   `config` (dict): The configuration dictionary.
*   `parser` (`argparse.ArgumentParser`): The argument parser.

**Functionality:**

*   Checks if the `input_path` is present in the configuration. If not, it prints the help message and exits.
*   If the `ignore` patterns are not specified, set them to defaults.

### `handle_mkdocs_setup(mkdocs_dir, docs_dir_name, create_mkdocs)`

```python
def handle_mkdocs_setup(mkdocs_dir, docs_dir_name, create_mkdocs):
    """Handles MkDocs project creation."""
```

Handles the creation of the MkDocs project.

**Parameters:**

*   `mkdocs_dir` (str): The directory for the MkDocs project.
*   `docs_dir_name` (str): The name of the docs directory inside the MkDocs project.
*   `create_mkdocs` (bool): Whether to create the MkDocs project if it doesn't exist.

**Functionality:**

*   If `create_mkdocs` is True, creates the MkDocs project if it doesn't exist using `mkdocs.create_mkdocs_project()`.
*   If `create_mkdocs` is False, checks if the MkDocs project exists. If it doesn't, it creates the MkDocs project.

### `log_configuration(config)`

```python
def log_configuration(config):
    """Logs the current configuration."""
```

Logs the current configuration settings to the console at the INFO level.  This helps in debugging and verifying the configuration.

**Parameters:**

*   `config` (dict): The configuration dictionary.

### `add_parser_args(parser)`

```python
def add_parser_args(parser):
    """Adds command-line arguments to the argument parser."""
```

Adds command-line arguments to the argument parser.

**Parameters:**

*   `parser` (`argparse.ArgumentParser`): The argument parser.

**Arguments:**

*   `-c`, `--config`: Path to the configuration file (default: `config.toml`).
*   `input_path`: Path to the Python file or directory.
*   `--create-mkdocs`: Create mkdocs project if it doesn't exist.
*   `--mkdocs-dir`: Directory for the mkdocs project.
*   `--docs-dir-name`: Name of the docs directory inside the mkdocs project.
*   `--interactive`: Run in interactive mode.
*   `--ignore`: Ignore patterns (e.g., `.venv venv node_modules`).
*   `--provider`: LLM provider (gemini, openai, ollama).
*   `--api-key`: API key for the LLM provider.
*   `--base-url`: Base URL for local LLMs like Ollama.
    `--model`: Model name for the LLM provider.

## Usage

To use the `cli.py` script, run it from the command line with the desired arguments.  For example:

```bash
python cli.py -c config.toml my_project/
```

This will generate documentation for the `my_project/` directory using the configuration specified in `config.toml`.

## Configuration

The configuration is loaded from a TOML file. The file should contain the following sections:

*   `main`: Main configuration settings, including `input_path`, `mkdocs_dir`, and `docs_dir_name`.
*   `ignore`: Ignore patterns for files and directories.
*   `project`: Project-related information such as the project name and description.
*   `llm`: LLM provider settings, including the provider name and API key.
*   `mkdocs`: Overrides for the MkDocs configuration file (`mkdocs.yml`).

Example `config.toml`:

```toml
[main]
input_path = "my_project/"
mkdocs_dir = "mkdocs/"
docs_dir_name = "docs/"
create_mkdocs = false

[ignore]
patterns = [".venv", "venv", "node_modules", ".git", "__pycache__"]

[project]
name = "My Project"
description = "A brief description of my project."

[llm]
provider = "gemini"
api_key_file = "path/to/your/api_key.txt"
model = "gemini-pro"

[mkdocs]
site_description = "My awesome project"
```

## Dependencies

*   `os`
*   `dotenv`
*   `logging`
*   `argparse`
*   `toml`
*   `meowdoc.core`
*   `meowdoc.mkdocs`
*   `google.generativeai`

## Related Files

*   `mkdocs.py`: Handles MkDocs project creation and navigation updating.
*   `core.py`: Contains the core documentation generation logic.
*   `llm.py`: Defines the LLM provider interface and implementations.
*   `themes.py`:  Manages the MkDocs theme.
