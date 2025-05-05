# `llm.py` Documentation

This module defines an abstract base class for LLM providers and concrete implementations for Google Gemini, OpenAI, and Ollama (a local LLM). It also includes utility functions for initializing LLM providers based on configuration and reading API keys from files. This module is a core component of Meowdoc, enabling the generation of documentation from source code by leveraging large language models.

## Table of Contents

1.  [Module Overview](#module-overview)
2.  [Classes](#classes)
    *   [LLMProvider](#llmprovider)
    *   [GeminiProvider](#geminiprovider)
    *   [OpenAiProvider](#openaiprovider)
    *   [OllamaProvider](#ollamaprovider)
3.  [Functions](#functions)
    *   [get\_llm\_provider](#get_llm_provider)
    *   [read\_api\_key](#read_api_key)

## Module Overview

The `llm.py` module provides a flexible and extensible way to integrate different LLM providers into the Meowdoc documentation generation process.  It utilizes an abstract base class (`LLMProvider`) to define a common interface for all providers, allowing for easy swapping and addition of new LLM services. Concrete implementations are provided for Gemini, OpenAI, and Ollama.  A factory function (`get_llm_provider`) is used to instantiate the appropriate provider based on a configuration dictionary. This module handles authentication and error handling for interacting with the LLM APIs, providing a simplified interface for the rest of the Meowdoc application.

The `llm.py` module interacts with other modules within Meowdoc, primarily `core.py` and `cli.py`.

*   `core.py`: Uses the `LLMProvider` interface and its implementations (e.g., `GeminiProvider`) to generate documentation from code. The `MeowdocCore` class in `core.py` takes an `LLMProvider` instance as input during initialization.
*   `cli.py`: Uses the `get_llm_provider` function to instantiate an `LLMProvider` based on configuration settings loaded from a TOML file or command-line arguments. The `main` function in `cli.py` retrieves the LLM provider instance and passes it to the `MeowdocCore` class.

## Classes

### LLMProvider

```python
class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        pass
```

**Description:**

The `LLMProvider` class is an abstract base class that defines the interface for all LLM provider implementations.  It ensures that all concrete providers have a `generate` method that takes a prompt string as input and returns a string containing the generated response.

**Methods:**

*   `generate(prompt: str) -> str`:
    *   **Description:**  Abstract method that generates a response based on the given prompt.  Must be implemented by concrete subclasses.
    *   **Parameters:**
        *   `prompt` (str): The prompt string to be sent to the LLM.
    *   **Returns:**
        *   str: The generated response from the LLM.

### GeminiProvider

```python
class GeminiProvider(LLMProvider):
    """LLM provider for Google Gemini."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        try:
            response = genai.GenerativeModel(model_name=self.model).generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            return ""
```

**Description:**

The `GeminiProvider` class implements the `LLMProvider` interface for Google's Gemini LLM.  It handles authentication with the Gemini API and generates responses based on the provided prompt.

**Attributes:**

*   `api_key` (str): The API key for accessing the Gemini API.
*   `model` (str): The name of the Gemini model to use.

**Methods:**

*   `__init__(api_key: str, model: str)`:
    *   **Description:** Initializes a new instance of the `GeminiProvider` class.
    *   **Parameters:**
        *   `api_key` (str): The API key for accessing the Gemini API.
        *   `model` (str): The name of the Gemini model to use.
    *   **Returns:**
        *   None
*   `generate(prompt: str) -> str`:
    *   **Description:** Generates a response using the Gemini API based on the given prompt.
    *   **Parameters:**
        *   `prompt` (str): The prompt string to be sent to the Gemini API.
    *   **Returns:**
        *   str: The generated response from the Gemini API, or an empty string if an error occurred.

**Error Handling:**

The `generate` method includes a `try...except` block to catch potential exceptions when calling the Gemini API.  If an error occurs, it logs the error message and returns an empty string.

### OpenAiProvider

```python
class OpenAiProvider(LLMProvider):
    """LLM provider for OpenAI."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def generate(self, prompt: str) -> str:
        try:
            response = openai.Completion.create(
                model=self.model,
                prompt=prompt,
                max_tokens=500
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {e}")
            return ""
```

**Description:**

The `OpenAiProvider` class implements the `LLMProvider` interface for OpenAI's LLM models.  It handles authentication with the OpenAI API and generates responses based on the provided prompt.

**Attributes:**

*   `api_key` (str): The API key for accessing the OpenAI API.
*   `model` (str): The name of the OpenAI model to use.

**Methods:**

*   `__init__(api_key: str, model: str)`:
    *   **Description:** Initializes a new instance of the `OpenAiProvider` class.
    *   **Parameters:**
        *   `api_key` (str): The API key for accessing the OpenAI API.
        *   `model` (str): The name of the OpenAI model to use.
    *   **Returns:**
        *   None
*   `generate(prompt: str) -> str`:
    *   **Description:** Generates a response using the OpenAI API based on the given prompt.
    *   **Parameters:**
        *   `prompt` (str): The prompt string to be sent to the OpenAI API.
    *   **Returns:**
        *   str: The generated response from the OpenAI API, or an empty string if an error occurred.

**Error Handling:**

The `generate` method includes a `try...except` block to catch potential exceptions when calling the OpenAI API.  If an error occurs, it logs the error message and returns an empty string.

### OllamaProvider

```python
class OllamaProvider(LLMProvider):
    """LLM provider for Ollama (local LLM)."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_ctx": 4096
                    }
                }
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logging.error(f"Error calling Ollama API: {e}")
            return ""
```

**Description:**

The `OllamaProvider` class implements the `LLMProvider` interface for Ollama, which allows running LLMs locally.  It communicates with the Ollama API via HTTP requests to generate responses.

**Attributes:**

*   `base_url` (str): The base URL of the Ollama API.
*   `model` (str): The name of the Ollama model to use.

**Methods:**

*   `__init__(base_url: str, model: str)`:
    *   **Description:** Initializes a new instance of the `OllamaProvider` class.
    *   **Parameters:**
        *   `base_url` (str): The base URL of the Ollama API.
        *   `model` (str): The name of the Ollama model to use.
    *   **Returns:**
        *   None
*   `generate(prompt: str) -> str`:
    *   **Description:** Generates a response using the Ollama API based on the given prompt.
    *   **Parameters:**
        *   `prompt` (str): The prompt string to be sent to the Ollama API.
    *   **Returns:**
        *   str: The generated response from the Ollama API, or an empty string if an error occurred.

**Error Handling:**

The `generate` method includes a `try...except` block to catch potential exceptions when calling the Ollama API.  If an error occurs, it logs the error message and returns an empty string. The `response.raise_for_status()` method is used to raise an exception for bad HTTP status codes (e.g., 404, 500).

## Functions

### get\_llm\_provider

```python
def get_llm_provider(config: dict) -> LLMProvider:
    """Initialize the LLM provider based on the configuration.

    Args:
        config (dict): Configuration dictionary containing LLM settings.

    Returns:
        LLMProvider: An instance of the specified LLM provider.

    Raises:
        ValueError: If the configuration is invalid or missing required fields.
    """
    provider = config["llm"]["provider"]
    api_key_file = config["llm"].get("api_key_file")
    base_url = config["llm"].get("base_url")
    model = config["llm"].get("model")

    if provider == "gemini":
        if not api_key_file:
            raise ValueError("API key file path is required for Gemini.")
        api_key = read_api_key(api_key_file)
        return GeminiProvider(api_key=api_key, model=model)
    elif provider == "openai":
        if not api_key_file:
            raise ValueError("API key file path is required for OpenAI.")
        api_key = read_api_key(api_key_file)
        return OpenAiProvider(api_key=api_key, model=model)
    elif provider == "ollama":
        if not base_url:
            raise ValueError("Base URL is required for Ollama.")
        return OllamaProvider(base_url=base_url, model=model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
```

**Description:**

The `get_llm_provider` function acts as a factory for creating `LLMProvider` instances based on the provided configuration.  It reads the provider type from the configuration dictionary and instantiates the appropriate provider class (Gemini, OpenAI, or Ollama).  It also handles reading API keys from files and validates that required configuration parameters are present.

**Parameters:**

*   `config` (dict): A dictionary containing the configuration for the LLM provider.  This dictionary should have a `"llm"` key containing a sub-dictionary with the following keys:
    *   `"provider"` (str):  The name of the LLM provider (e.g., `"gemini"`, `"openai"`, `"ollama"`).
    *   `"api_key_file"` (str, optional): The path to the file containing the API key (required for Gemini and OpenAI).
    *   `"base_url"` (str, optional): The base URL of the Ollama API (required for Ollama).
    *   `"model"` (str): The name of the LLM model to use.

**Returns:**

*   `LLMProvider`: An instance of the specified `LLMProvider` class.

**Raises:**

*   `ValueError`: If the configuration is invalid or missing required fields.  Specifically, a `ValueError` is raised if:
    *   The `"provider"` key is not found in the configuration.
    *   The specified provider is not supported.
    *   The `"api_key_file"` is missing when using the Gemini or OpenAI provider.
    *   The `"base_url"` is missing when using the Ollama provider.

**Example:**

```python
config = {
    "llm": {
        "provider": "gemini",
        "api_key_file": "path/to/gemini_api_key.txt",
        "model": "gemini-pro"
    }
}
provider = get_llm_provider(config) # Returns a GeminiProvider instance
```

### read\_api\_key

```python
def read_api_key(path):
    content = ""
    with open(path) as f:
        content = f.read()
    return content
```

**Description:**

The `read_api_key` function reads the API key from the file specified by the given path.

**Parameters:**

*   `path` (str): The path to the file containing the API key.

**Returns:**

*   `str`: The API key read from the file.

**Error Handling:**

The function does not explicitly handle file-related exceptions. Any `FileNotFoundError` or `IOError` will be raised and need to be handled by the caller.

**Example:**

```python
api_key = read_api_key("path/to/api_key.txt")
print(api_key)
```
