import os
from dotenv import load_dotenv
import logging
import argparse
import toml
from meowdoc import core, mkdocs, llm
import google.generativeai as genai

def main():
    """Main function to run MeowDoc."""

    logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()  # Load environment variables
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    parser = argparse.ArgumentParser(description="Generate documentation using LLMs and MkDocs.")
    add_parser_args(parser)
    args = parser.parse_args()

    config = load_config(args.config)  # Load and validate configuration
    if config is None:
        exit(1)

    config = override_config_with_args(config, args)  # Override with CLI args

    llm_provider = get_llm_provider(config)  # Get LLM provider
    if llm_provider is None:
        exit(1)

    config = handle_interactive_mode(config, args)  # Handle interactive mode if enabled

    validate_main_config(config, parser)  # Validate main config

    # Extract config values (using helper function for defaults)
    input_path = config["main"]["input_path"]
    mkdocs_dir = config["main"].get("mkdocs_dir", "docs")
    docs_dir_name = config["main"].get("docs_dir_name", "docs")
    create_mkdocs = config["main"].get("create_mkdocs", False)
    ignore_patterns = config["ignore"]["patterns"]
    project_name = config["project"].get("name", "")
    description = config["project"].get("description", "")
    repo_url = config["project"].get("repo_url", "")

    log_configuration(config)  # Log the configuration

    generator = core.MeowdocCore(
        input_path,
        mkdocs_dir,
        docs_dir_name,
        ignore_patterns,
        project_name,
        description,
        repo_url,
        llm_provider,
    )

    print("checking for existing mkdocs project...")
    handle_mkdocs_setup(mkdocs_dir, docs_dir_name, create_mkdocs)  # Create mkdocs if needed

    print("processing input path...")
    generated_files = generator.process_path()
    
    generator.create_project_index()
    print("creating project index")

    if generated_files:
        is_input_dir = os.path.isdir(input_path)
        mkdocs.update_mkdocs_nav(generated_files, is_input_dir, mkdocs_dir, docs_dir_name, project_name, description)
        mkdocs.update_mkdocs_config_from_toml(config, mkdocs_dir)
        print("All docs generated")

    logging.info("Finished.")

def load_config(config_path):
    """Loads and validates the TOML configuration."""
    try:
        with open(config_path, "r") as f:
            config = toml.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        return None
    except toml.TomlDecodeError as e:
        logging.error(f"Error parsing TOML file: {e}")
        return None

    # Basic validation (you can add more checks)
    if "main" not in config or "ignore" not in config or "project" not in config or "llm" not in config:
        logging.error("Invalid config file structure.")
        return None

    return config


def override_config_with_args(config, args):
    """Overrides config values with command-line arguments."""

    if args.provider:
        config["llm"]["provider"] = args.provider
    if args.api_key:
        config["llm"]["api_key"] = args.api_key
    if args.base_url:
        config["llm"]["base_url"] = args.base_url
    if args.model:
        config["llm"]["model"] = args.model

    args_overrides = {k: v for k, v in vars(args).items() if v is not None and k not in ["config", "interactive", "create_mkdocs"]}
    if "ignore" in args_overrides and args_overrides["ignore"]:
        config["ignore"]["patterns"] = args_overrides.pop("ignore") # Remove "ignore" from args_overrides to prevent it from being added to main section
    config["main"].update(args_overrides) # Update only the main section with other overrides

    return config


def get_llm_provider(config):
    """Gets the LLM provider instance."""
    try:
        return llm.get_llm_provider(config)
    except ValueError as e:
        logging.error(e)
        return None


def handle_interactive_mode(config, args):
    """Handles interactive mode input."""
    if args.interactive:
        logging.info("Running in interactive mode.")

        def prompt_for_config(section, option, prompt_message, default=None):
            value = input(prompt_message) or default
            config[section][option] = value
        
        prompt_for_config("main", "input_path", "Enter the input path (file or directory): ")
        prompt_for_config("llm", "model", "Enter the Gemini model to use (default: gemini-pro): ", "gemini-pro")

        create_mkdocs = input("Create MkDocs project if it doesn't exist? (y/N): ").lower()
        config["main"]["create_mkdocs"] = create_mkdocs == "y"

        prompt_for_config("main", "mkdocs_dir", "Enter the MkDocs project directory (default: docs): ", "docs")
        prompt_for_config("main", "docs_dir_name", "Enter the docs directory name (default: docs): ", "docs")

        ignore_input = input("Enter ignore patterns separated by commas (or press Enter for defaults): ")
        config["ignore"]["patterns"] = ignore_input.split(",") if ignore_input else [".venv", "venv", "node_modules", ".git", "__pycache__", ".env", "requirements.txt"]
    return config

def validate_main_config(config, parser):
    """Validates the main configuration."""
    if not config["main"].get("input_path"):
        parser.print_help()
        exit(1)

    if "ignore" not in config or "patterns" not in config["ignore"]:
        config["ignore"] = {"patterns": [".venv", "venv", "node_modules", ".git", "__pycache__", ".env", "requirements.txt"]}


def handle_mkdocs_setup(mkdocs_dir, docs_dir_name, create_mkdocs):
    """Handles MkDocs project creation."""
    if create_mkdocs:
        if not mkdocs.create_mkdocs_project(mkdocs_dir, docs_dir_name):
            exit(1)
    elif not os.path.exists(mkdocs_dir) or not os.path.exists(os.path.join(mkdocs_dir, docs_dir_name)):
        if not mkdocs.create_mkdocs_project(mkdocs_dir, docs_dir_name):
            exit(1)

def log_configuration(config):
    """Logs the current configuration."""
    logging.info(f"Input path: {config['main']['input_path']}")
    logging.info(f"Model: {config['llm']['model']}")
    logging.info(f"MkDocs Directory: {config['main']['mkdocs_dir']}")
    logging.info(f"Docs Directory Name: {config['main']['docs_dir_name']}")
    logging.info(f"Ignore Patterns: {config['ignore']['patterns']}")
    logging.info(f"Project name: {config['project'].get('name', '')}")

def add_parser_args(parser):
    parser.add_argument(
        "-c",
        "--config",
        help="Path to the configuration file (default: config.toml)",
        default="config.toml",
    )
    parser.add_argument(
        "input_path", nargs="?", help="Path to the Python file or directory."
    )
    parser.add_argument(
        "--create-mkdocs",
        help="Create mkdocs project if it doesn't exist",
        action="store_true",
    )
    parser.add_argument(
        "--mkdocs-dir", help="Directory for the mkdocs project.", default=None
    )
    parser.add_argument(
        "--docs-dir-name",
        help="Name of the docs directory inside the mkdocs project.",
        default=None,
    )
    parser.add_argument(
        "--interactive", help="Run in interactive mode", action="store_true"
    )
    parser.add_argument(
        "--ignore",
        nargs="+",
        help="Ignore patterns (e.g., .venv venv node_modules).",
        default=None,
    )
    parser.add_argument("--provider", help="LLM provider (gemini, openai, ollama).")
    parser.add_argument("--api-key", help="API key for the LLM provider.")
    parser.add_argument("--base-url", help="Base URL for local LLMs like Ollama.")
    parser.add_argument("--model", help="Model name for the LLM provider.")

if __name__ == "__main__":
    main()
