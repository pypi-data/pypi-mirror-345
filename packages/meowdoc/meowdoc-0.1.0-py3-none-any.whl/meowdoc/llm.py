from abc import ABC, abstractmethod
import google.generativeai as genai
import openai
import requests
import logging

class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        pass


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

def read_api_key(path):
    content = ""
    with open(path) as f:
        content = f.read()
    return content