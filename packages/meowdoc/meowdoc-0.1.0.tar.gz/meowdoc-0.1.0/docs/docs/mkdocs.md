# `mkdocs.py` Documentation

This module contains functions to manage and update MkDocs projects and their configurations. It allows for the creation of new MkDocs projects, updating the navigation structure in `mkdocs.yml` based on generated documentation files, and merging configurations from a TOML file. It also handles setting the MkDocs theme. MkDocs is a static site generator geared towards building project documentation from Markdown files.

## Module Overview

The `mkdocs.py` file provides the following functionality:

*   Creating a new MkDocs project.
*   Updating the `mkdocs.yml` configuration file to include links to generated documentation.
*   Merging configurations from a TOML file into `mkdocs.yml`.
*   Deduplicating API Elements in navigation
*   Setting the active MkDocs theme.

This module is a crucial part of the `meowdoc` documentation generation process, acting as the bridge between the generated Markdown files and the MkDocs static site generator. It integrates with `core.py`, `cli.py`, and `themes.py` to create and manage the documentation website.

## Function Documentation

### `update_mkdocs_nav(generated_files, is_input_dir, mkdocs_dir, docs_dir_name, name, description, theme="material")`

Updates the navigation structure in the `mkdocs.yml` file based on the generated documentation files. This function handles both single file and directory-based documentation generation.

**Parameters:**

*   `generated_files` (list): A list of file paths to the generated documentation files.
*   `is_input_dir` (bool): A boolean indicating whether the input was a directory (True) or a single file (False).
*   `mkdocs_dir` (str): The path to the MkDocs project directory.
*   `docs_dir_name` (str): The name of the directory where the documentation files are stored within the MkDocs project.
*   `name` (str): The name of the site, used for the `site_name` in `mkdocs.yml`.
*   `description` (str): The description of the site, not currently used, but reserved for future use.
*   `theme` (str, optional): The MkDocs theme to use. Defaults to "material".

**Functionality:**

1.  **Loads the `mkdocs.yml` file:** Reads the existing `mkdocs.yml` file.  If the file does not exist, an error is logged and the function returns. If there is an error parsing the YAML, an error is logged and the function returns.
2.  **Updates site name and theme:** Sets the `site_name` and `theme` in the `mkdocs.yml` configuration.
3.  **Handles directory input:**
    *   If `is_input_dir` is True, the function creates a nested navigation structure under an "API" section in the `mkdocs.yml` file based on the directory structure of the input files.
    *   It constructs a nested dictionary representing the directory structure, and then converts it into the format required by MkDocs for navigation.
4.  **Handles single file input:**
    *   If `is_input_dir` is False, the function adds a simple navigation entry for the single generated file to the `mkdocs.yml` file.
5.  **Writes the updated `mkdocs.yml` file:** Writes the updated configuration to the `mkdocs.yml` file, using indentation for readability.
6.  **Enables the specified theme:** Calls `themes.enable_theme` to install the selected theme.

**Example Usage:**

```python
generated_files = ["docs/module1.md", "docs/module2.md"]
update_mkdocs_nav(
    generated_files=generated_files,
    is_input_dir=True,
    mkdocs_dir="docs",
    docs_dir_name="docs",
    name="My Project",
    description="My project description",
    theme="material",
)
```

**Error Handling:**

*   Logs an error if the `mkdocs.yml` file is not found.
*   Logs an error if there is an issue parsing the `mkdocs.yml` file.
*   Logs an error if there is an issue writing to the `mkdocs.yml` file.

**Interactions with other modules:**

*   Reads and writes to `mkdocs.yml` in the MkDocs project directory.
*   Uses `themes.enable_theme` from `themes.py` to enable the selected theme.

### `create_mkdocs_project(project_dir, docs_dir_name)`

Creates a new MkDocs project in the specified directory if one does not already exist.

**Parameters:**

*   `project_dir` (str): The directory where the MkDocs project should be created.
*   `docs_dir_name` (str): The name of the documentation directory, usually "docs".

**Functionality:**

1.  **Checks for existing project:** Checks if an `mkdocs.yml` file already exists in the specified directory.
2.  **Creates new project:** If no existing project is found, it uses the `mkdocs new` command to create a new MkDocs project in the specified directory. It redirects stdout and stderr for better error handling and reporting.
3.  **Sets a default navigation:** It modifies the default `mkdocs.yml` after creation to include a basic "Home" navigation item.

**Returns:**

*   `bool`: Returns `True` if the project was created successfully or if it already existed. Returns `False` if there was an error creating the project.

**Example Usage:**

```python
if mkdocs.create_mkdocs_project(project_dir="docs", docs_dir_name="docs"):
    print("MkDocs project created or already exists.")
else:
    print("Failed to create MkDocs project.")
```

**Error Handling:**

*   Logs an error if the `mkdocs new` command fails.

**Interactions with other modules:**

*   Uses the `subprocess` module to execute the `mkdocs new` command.

### `merge_dicts(existing, new)`

Recursively merges two dictionaries. The `new` dictionary values take precedence, but nested dictionaries are merged intelligently.

**Parameters:**

*   `existing` (dict): The existing dictionary to merge into. This dictionary will be modified in place.
*   `new` (dict): The new dictionary whose values will be merged into the existing dictionary.

**Functionality:**

1.  **Iterates through new dictionary:** Loops through each key-value pair in the `new` dictionary.
2.  **Handles nested dictionaries:** If both the current value in the `new` dictionary and the corresponding value in the `existing` dictionary are dictionaries, the function recursively calls itself to merge the nested dictionaries.
3.  **Overwrites or adds values:** If the value in the `new` dictionary is not a dictionary or the corresponding value in the `existing` dictionary is not a dictionary, the value from the `new` dictionary overwrites the value in the `existing` dictionary. If the key does not exist in the `existing` dictionary, it is added.

**Returns:**

*   `dict`: Returns the modified `existing` dictionary, which now contains the merged values from both dictionaries.

**Example Usage:**

```python
existing_config = {"site_name": "My Site", "theme": {"name": "material"}}
new_config = {"site_name": "New Site Name", "plugins": ["search"]}
merged_config = merge_dicts(existing_config, new_config)
print(merged_config)
# Expected output: {'site_name': 'New Site Name', 'theme': {'name': 'material'}, 'plugins': ['search']}
```

**Interactions with other modules:**

*   Used by `update_mkdocs_config_from_toml` to merge settings from the TOML configuration file into the `mkdocs.yml` file.

### `finalize(mkdocs_config)`

Finalizes the mkdocs configuration.

**Parameters:**

*   `mkdocs_config` (dict): The mkdocs configuration dictionary.

**Functionality:**
1. Deduplicates "API" elements.

**Returns:**

*   `dict`: The finalized mkdocs configuration dictionary.

**Interactions with other modules:**

*   Called by `update_mkdocs_config_from_toml` to finalize the mkdocs config after toml values have been merged.

### `_dedupe_API_elem(elem)`

Deduplicates the elements within the "API" section of the MkDocs navigation. This function ensures that there are no duplicate entries in the generated documentation navigation.

**Parameters:**

*   `elem` (dict): A dictionary representing a navigation element in the MkDocs configuration.

**Functionality:**

1.  **Checks for "API" key:** Determines if the input dictionary has a key called "API".
2.  **Deduplicates elements:** If the "API" key exists, the function converts each dictionary within the "API" list to a JSON string (using `json.dumps` with `sort_keys=True` for consistent ordering), and tracks the seen JSON strings in a set. This allows identification of duplicate dictionaries regardless of key order.
3.  **Maintains order of original dict:** Appends the original dictionary to `deduplicated_data` array
4.  **Updates the "API" list:** The function replaces the original "API" list with the deduplicated list.

**Returns:**

*   `dict`: The modified element, where the "API" list is deduplicated, if it exists. Otherwise, the original element.

**Example Usage:**

```python
elem = {"API": [{"key1": "value1"}, {"key2": "value2"}, {"key1": "value1"}]}
deduplicated_elem = _dedupe_API_elem(elem)
print(deduplicated_elem)
# Expected Output: {'API': [{'key1': 'value1'}, {'key2': 'value2'}]}
```

**Interactions with other modules:**

*   Called by `finalize` to ensure uniqueness of API elements in mkdocs.yml navigation section.

### `update_mkdocs_config_from_toml(config, mkdocs_dir)`

Updates the `mkdocs.yml` configuration file with settings from a TOML configuration file.

**Parameters:**

*   `config` (dict): A dictionary representing the TOML configuration.
*   `mkdocs_dir` (str): The path to the MkDocs project directory.

**Functionality:**

1.  **Loads `mkdocs.yml`:** Loads the existing `mkdocs.yml` file.
2.  **Merges configurations:** Uses the `merge_dicts` function to merge the settings from the TOML configuration file into the `mkdocs.yml` configuration.  The settings from the TOML file take precedence.
3.  **Finalizes mkdocs config:** Deduplicates API elements
4.  **Writes updated `mkdocs.yml`:** Writes the updated configuration to the `mkdocs.yml` file.

**Example Usage:**

```python
config = {"mkdocs": {"site_name": "My New Site"}}
update_mkdocs_config_from_toml(config, "docs")
```

**Error Handling:**

*   Logs an error if the `mkdocs.yml` file is not found.
*   Logs an error if there is an issue parsing the `mkdocs.yml` file.
*   Logs an error if there is an issue writing to the `mkdocs.yml` file.

**Interactions with other modules:**

*   Uses the `merge_dicts` function to merge the configurations.
*   Reads and writes to the `mkdocs.yml` file.
*   Uses `finalize` to dedupe the "API" navigation section.

## Example Usage (Overall)

This example demonstrates how the functions in `mkdocs.py` might be used within the `meowdoc` application to create and manage a MkDocs project.

```python
import os
from meowdoc import mkdocs

# Configuration
project_dir = "my_project_docs"
docs_dir_name = "docs"
project_name = "MyProject"
project_description = "Documentation for MyProject"
generated_files = [os.path.join(project_dir, docs_dir_name, "module1.md"), os.path.join(project_dir, docs_dir_name, "module2.md")]
config = {"mkdocs": {"theme": {"name": "material"}}}

# Create a new MkDocs project if it doesn't exist
mkdocs.create_mkdocs_project(project_dir, docs_dir_name)

# Update the mkdocs.yml file with the generated files
mkdocs.update_mkdocs_nav(generated_files, True, project_dir, docs_dir_name, project_name, project_description)

# Update the mkdocs.yml file with settings from a TOML file
mkdocs.update_mkdocs_config_from_toml(config, project_dir)
```

## Relationships with Other Modules

*   **`core.py`:** The `mkdocs.py` module is called from `core.py` after documentation has been generated. Specifically, `core.py` utilizes `mkdocs.update_mkdocs_nav` to update the MkDocs navigation with the newly generated files and their structure.
*   **`cli.py`:** The `cli.py` module uses `mkdocs.py` to create a MkDocs project (`mkdocs.create_mkdocs_project`) if needed and to update the MkDocs navigation (`mkdocs.update_mkdocs_nav`) and config file (`mkdocs.update_mkdocs_config_from_toml`) after documentation generation. The CLI passes configuration information to `mkdocs.py`.
*   **`themes.py`:** The `mkdocs.update_mkdocs_nav` function calls `themes.enable_theme` to ensure the specified theme is installed.
*   **`llm.py`:** While `mkdocs.py` doesn't directly interact with `llm.py`, the generated documentation content (which `mkdocs.py` helps integrate into the MkDocs site) is created using the LLM providers defined in `llm.py`.
