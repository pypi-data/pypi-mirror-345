# `core.py` Module Documentation

This module defines the core functionality of Meowdoc, a tool designed to automatically generate documentation for Python projects using Large Language Models (LLMs) and integrate it with MkDocs. It handles file processing, documentation generation via LLMs, and MkDocs project integration.

## `MeowdocCore` Class

This class orchestrates the entire documentation generation process. It initializes with project-specific configurations, interacts with an LLM to generate documentation from Python code, manages file input and output, and prepares the generated documentation for integration into a MkDocs project.

### Initialization (`__init__`)

```python
def __init__(
    self, 
    input_path,
    mkdocs_dir,
    docs_dir,
    ignore_patterns,
    project_name,
    project_description,
    repo_url,
    llm_provider,
):
```

Initializes the `MeowdocCore` object.

**Parameters:**

*   `input_path` (str):  The path to the Python file or directory for which documentation needs to be generated.
*   `mkdocs_dir` (str): The directory where the MkDocs project resides.
*   `docs_dir` (str): The directory within the MkDocs project where the generated documentation will be stored.
*   `ignore_patterns` (list[str]): A list of filename patterns to ignore during file processing. This is for filtering out files like `.pyc`, `__pycache__`, or files in `venv` directories.
*   `project_name` (str): The name of the project, used in the generated documentation and MkDocs configuration.
*   `project_description` (str): A brief description of the project, included in the generated documentation.
*   `repo_url` (str): URL of the project's repository (e.g., GitHub).
*   `llm_provider` (LLMProvider): An instance of the LLM provider (e.g., `GeminiProvider`, `OpenAiProvider`, `OllamaProvider`) to be used for documentation generation.

**Example:**

```python
from meowdoc import core
from meowdoc import llm

# Assuming you have an LLM provider instance, such as GeminiProvider
# and your project directory structure is already set up.
#  For example:
# project_dir/
#   module1.py
#   module2.py
#   mkdocs.yml

# Example usage:

# Create an instance of the LLMProvider (replace with actual implementation)
# Make sure you have the necessary environment variables or API keys set.
config = {
    "llm": {
        "provider": "gemini",
        "api_key_file": ".secrets/gemini_api.key", # Path to your gemini api key file
        "model": "gemini-pro"
    }
}

llm_provider = llm.get_llm_provider(config)

generator = core.MeowdocCore(
    input_path="project_dir",
    mkdocs_dir="docs",
    docs_dir="docs",
    ignore_patterns=[".venv", "__pycache__"],
    project_name="MyProject",
    project_description="A sample project.",
    repo_url="https://github.com/example/myproject",
    llm_provider=llm_provider,
)
```

### `generate_docs` Method

```python
def generate_docs(self, file_path, all_file_contents):
```

Generates documentation for a single file using an LLM, incorporating context from other related files within the project.  It constructs a prompt that includes the target file's code and the code of all other files in the `all_file_contents` dictionary.  It also retrieves and appends additional guidelines from a `docguide` file, if it exists.

**Parameters:**

*   `file_path` (str): The full path to the file for which documentation is to be generated.
*   `all_file_contents` (dict[str, str]): A dictionary where keys are filenames (relative to `input_path`) and values are the corresponding file contents. This provides context to the LLM.

**Returns:**

*   `str` | `None`:  The generated documentation in Markdown format, or `None` if an error occurred during the LLM call.

**Example:**

```python
# Assuming you have populated the all_file_contents dictionary
# with the content of all relevant files, then you can call the generate_docs function.

all_file_contents = {
    "module1.py": "def my_function():\n  \"\"\"This is a dummy function\"\"\"\n  pass",
    "module2.py": "def another_function():\n  pass",
}

# Generate the documentation
documentation = generator.generate_docs("project_dir/module1.py", all_file_contents)

if documentation:
    print(documentation)
else:
    print("Documentation generation failed.")
```

**Details:**

1.  **Prompt Construction:** The method constructs a detailed prompt for the LLM.  The prompt includes:
    *   The Python code of the target file.
    *   The Python code of all other related files to provide context.
    *   Specific instructions on the desired structure and content of the documentation (module-level description, function/class descriptions with parameters/return values, interaction with other modules, example usage, docstring inference).
2.  **Docguide Integration:** It checks for a `docguide` file located in the `docguide` directory that corresponds to the current file being processed (e.g., `"docguide/module1.py.md"`). If found, the content of the docguide is appended to the prompt as "Additional Guidelines".
3.  **LLM Interaction:** It calls the `generate` method of the injected `llm_provider` with the constructed prompt to generate the documentation.
4.  **Error Handling:**  Includes error handling for scenarios where the LLM call fails, logging the exception and returning `None`.

### `create_index` Method

```python
def create_index(self, mkdocs_dir, docs_dir, readme_content):
```

Creates the `index.md` file (the main page of the MkDocs site) within the specified MkDocs directory, populating it with provided content.

**Parameters:**

*   `mkdocs_dir` (str): The root directory of the MkDocs project.
*   `docs_dir` (str): The directory within the MkDocs project where the documentation source files are stored (typically "docs").
*   `readme_content` (str):  The content to be written into the `index.md` file.  This is often the content of the project's README file.

**Example:**

```python
# Assume you have the content of your project's README file.
readme_content = """# My Project\nThis is the project's README content."""

# Create index.md file
generator.create_index("docs", "docs", readme_content)
```

### `should_ignore` Method

```python
def should_ignore(self, path, ignore_patterns):
```

Determines whether a given file or directory path should be ignored based on a list of filename patterns.  It checks not only the path itself but also all of its parent directories.

**Parameters:**

*   `path` (str): The file or directory path to check.
*   `ignore_patterns` (list[str]): A list of filename patterns to ignore (e.g., `*.pyc`, `venv`, `__pycache__`).

**Returns:**

*   `bool`: `True` if the path or any of its parent directories should be ignored; `False` otherwise.

**Example:**

```python
ignore_patterns = [".venv", "__pycache__", "*.log"]

# Check if a specific path should be ignored
should_ignore = generator.should_ignore("project_dir/.venv/module.py", ignore_patterns)
print(f"Should ignore .venv directory? {should_ignore}") # Output: True

should_ignore = generator.should_ignore("project_dir/module.log", ignore_patterns)
print(f"Should ignore module.log? {should_ignore}") # Output: True
```

**Details:**

1.  **Absolute Path Conversion:** Converts the input `path` to an absolute path for consistent comparison.
2.  **Parent Directory Traversal:** Iteratively checks each parent directory of the path against the `ignore_patterns`.
3.  **Pattern Matching:**  Uses `fnmatch.fnmatch` to perform filename pattern matching.

### `_collect_files` Method

```python
def _collect_files(self):
```

Walks the input directory and returns a list of tuples containing the full file path and the relative path from the input directory.

**Returns:**

*   `list[tuple[str, str]]`: A list of tuples, where the first element is the absolute file path and the second element is the relative path of the file with respect to the input directory.

**Example:**

```python
# Collect a list of files from the input path, respecting ignore patterns.
file_list = generator._collect_files()

for file_path, relative_path in file_list:
    print(f"File Path: {file_path}, Relative Path: {relative_path}")
```

### `process_path` Method

```python
def process_path(self):
```

The core method for processing files within the specified input path. It concurrently generates documentation for each file using a thread pool, leveraging the `generate_docs` method.

**Returns:**

*   `list[str]`: A list of file paths to the generated documentation files.

**Details:**

1.  **File Collection:** Uses `_collect_files()` to gather a list of files to process.
2.  **File Content Pre-reading:** Reads the content of all collected files into memory. This improves performance, especially when processing a large number of small files, by allowing the LLM calls to be parallelized without disk I/O contention.
3.  **Thread Pool Execution:** Uses `ThreadPoolExecutor` to parallelize the calls to `generate_docs`.
4.  **Documentation Generation and Output:**  For each file, it calls `generate_docs` to generate the documentation, and then writes the generated documentation to a Markdown file in the `mkdocs_docs` directory, mirroring the directory structure of the input path.
5.  **Error Handling:** Handles potential exceptions during file reading and documentation generation, logging errors appropriately.

**Example:**

```python
# Process all the files in the input path and generate documentation for them
generated_files = generator.process_path()

if generated_files:
    print("Generated documentation files:")
    for file_path in generated_files:
        print(file_path)
else:
    print("No documentation files were generated.")
```

### `create_project_index` Method

```python
def create_project_index(self):
```

Creates a project index page (`index.md`) that includes a project description, getting started instructions, and a "Contributing" section generated by the LLM.

**Details:**

1.  **LLM-Generated Contribution Guide:** Creates a contributing guide using the `llm_provider`.
2.  **Index Content Generation:** Creates the markdown content of the index file, including a brief getting started guide.
3.  **Index Writing:** Writes the created content into an `index.md` file, which will serve as the landing page for the documentation website.

**Example:**

```python
# Generate and create project index file
generator.create_project_index()
print("Project index created successfully.")
```

## Usage Notes

*   The `MeowdocCore` class depends on an external LLM provider for generating documentation.  You must configure the `llm_provider` with the appropriate API key and model settings.
*   The class uses logging for debugging and error reporting.  Ensure that logging is configured appropriately for your environment.
*   The `docguide` directory is used to provide additional context and guidelines to the LLM during documentation generation.  You can create `docguide` files to customize the generated documentation for specific files.
*   The `process_path` method uses a thread pool to parallelize documentation generation.  This can significantly improve performance when processing large projects.
*   Error handling is implemented to catch exceptions during file processing, LLM calls, and file writing.  Ensure that you monitor the logs for any errors.

## Interactions with Other Modules

*   **`mkdocs.py`:**  The `MeowdocCore` class integrates with the `mkdocs.py` module to create and update the MkDocs project, including creating the `mkdocs.yml` configuration file. The `update_mkdocs_nav` function from `mkdocs.py` is used to update the navigation structure of the MkDocs site based on the generated documentation files. Also, the `update_mkdocs_config_from_toml` function allows settings from a `config.toml` file to be applied to the `mkdocs.yml` file.
*   **`llm.py`:** The `MeowdocCore` class uses the `llm.py` module to interact with the chosen LLM provider.  It uses the `LLMProvider` base class and its implementations (e.g., `GeminiProvider`, `OpenAiProvider`, `OllamaProvider`) to generate documentation.
*   **`cli.py`:** The `cli.py` module orchestrates the entire documentation generation process by parsing command-line arguments, loading configuration settings, creating an instance of `MeowdocCore`, and calling the `process_path` method.
