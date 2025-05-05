import os
from dotenv import load_dotenv
import google.generativeai as genai
import argparse
import logging
import pathlib
import fnmatch
import subprocess
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file
load_dotenv()

# Set your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_docs(filepath, output_path, model="gemini-pro"):
    """Generates documentation for a Python file using Gemini."""
    logging.info(f"Generating docs for: {filepath} -> {output_path}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return None
    except Exception as e:
        logging.exception(f"Error reading file: {e}")
        return None

    prompt = f"""
    Generate comprehensive documentation in Markdown format for the following Python file:

    ```python
    {code}
    ```

    Include:

    *   A concise module-level description (if present).
    *   Descriptions of each function and class, including parameters, return values, and docstrings.
    *   Use clear headings and subheadings (e.g., ##, ###).
    *   Provide example usage where possible.
    *   If there are no docstrings, try to infer the purpose of the code based on its structure and variable names.
    """

    try:
        model = genai.GenerativeModel(model_name=model)
        response = model.generate_content(prompt)
        docs = response.text
    except Exception as e:
        logging.exception(f"Error calling Gemini API: {e}")
        return None

    try:
        pathlib.Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.write(docs)
        logging.info(f"Documentation written to: {output_path}")
        return output_path
    except Exception as e:
        logging.exception(f"Error writing to output file: {e}")
        return None


def should_ignore(path, ignore_patterns):
    """Checks if a path or any of its parent directories should be ignored."""
    path = os.path.abspath(path)  # Convert to absolute path for consistent comparison
    while path:
        base_name = os.path.basename(path)
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(base_name, pattern):
                logging.info(f"Ignoring {path} because it matches pattern: {pattern}")
                return True
        path = os.path.dirname(path)  # Move up to the parent directory
        if path == os.path.dirname(path):  # check for root
            break
    return False


def process_path(input_path, mkdocs_dir, docs_dir_name, model, ignore_patterns=None):
    """Processes a single file or directory, ignoring specified patterns and the docs directory."""
    logging.info(f"Processing path: {input_path}")
    generated_files = []

    if ignore_patterns is None:
        ignore_patterns = []

    if should_ignore(input_path, ignore_patterns):
        logging.info(f"Ignoring path (matches pattern): {input_path}")
        return []

    if os.path.abspath(input_path) == os.path.abspath(mkdocs_dir):
        logging.info(f"Ignoring the mkdocs directory: {input_path}")
        return []

    docs_dir = os.path.join(mkdocs_dir, docs_dir_name)

    if os.path.isfile(input_path):
        logging.info(f"Input is a file: {input_path}")
        output_filename = os.path.splitext(os.path.basename(input_path))[0] + ".md"
        output_path = os.path.join(docs_dir, output_filename)
        doc_path = generate_docs(input_path, output_path, model)
        if doc_path:
            generated_files.append(doc_path)
    elif os.path.isdir(input_path):
        logging.info(f"Input is a directory: {input_path}")
        for item in os.listdir(input_path):
            item_path = os.path.join(input_path, item)
            if not should_ignore(item_path, ignore_patterns) and not os.path.samefile(
                item_path, docs_dir
            ):
                generated_files.extend(
                    process_path(
                        item_path, mkdocs_dir, docs_dir_name, model, ignore_patterns
                    )
                )
            elif os.path.samefile(item_path, docs_dir):
                logging.info(f"Ignoring the docs directory: {item_path}")
            else:
                logging.info(
                    f"Ignoring item within directory (matches pattern): {item_path}"
                )
    else:
        logging.warning(f"Skipping invalid path: {input_path}")
    return generated_files


def update_mkdocs_nav(generated_files, is_input_dir, mkdocs_dir, docs_dir_name):
    mkdocs_config_path = os.path.join(mkdocs_dir, "mkdocs.yml")
    logging.info(f"Updating mkdocs.yml: {mkdocs_config_path}")

    try:
        with open(mkdocs_config_path, "r") as f:
            mkdocs_config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"mkdocs.yml not found. Please create a mkdocs project first.")
        return
    except yaml.YAMLError as e:
        logging.error(f"Error parsing mkdocs.yml: {e}")
        return

    if "nav" not in mkdocs_config:
        mkdocs_config["nav"] = []

    nav = mkdocs_config["nav"]

    if is_input_dir:
        api_section_exists = False
        for item in nav:
            if isinstance(item, dict) and "API" in item:
                api_section = item["API"]
                api_section_exists = True
                break
        if not api_section_exists:
            nav.append({"API": []})
            api_section = nav[-1]["API"]
        else:
            api_section = item["API"]

        for file in generated_files:
            filename = os.path.splitext(os.path.basename(file))[0]
            relative_path = os.path.relpath(
                file, os.path.join(mkdocs_dir, docs_dir_name)
            )
            nav_entry = {filename: relative_path}
            if nav_entry not in api_section:
                api_section.append(nav_entry)

    else:  # single file
        file = generated_files[0]
        filename = os.path.splitext(os.path.basename(file))[0]
        relative_path = os.path.relpath(file, mkdocs_dir)
        nav_entry = {filename: relative_path}
        if nav_entry not in nav:
            nav.append(nav_entry)

    try:
        with open(mkdocs_config_path, "w") as f:
            yaml.dump(mkdocs_config, f, indent=2)  # Use indent for better formatting
        logging.info("mkdocs.yml updated")
    except Exception as e:
        logging.error(f"Error writing to mkdocs.yml: {e}")


def create_mkdocs_project(project_dir, docs_dir_name):
    """Creates a new MkDocs project if one doesn't exist."""
    mkdocs_config_path = os.path.join(project_dir, "mkdocs.yml")
    if not os.path.exists(mkdocs_config_path):
        logging.info(f"Creating new MkDocs project in: {project_dir}")
        try:
            subprocess.run(
                ["mkdocs", "new", project_dir],
                check=True,
                capture_output=True,
                text=True,
            )
            # Add a default nav to the created mkdocs.yml
            with open(mkdocs_config_path, "r") as f:
                mkdocs_config = yaml.safe_load(f)
            mkdocs_config["nav"] = [{"Home": "index.md"}]
            with open(mkdocs_config_path, "w") as f:
                yaml.dump(mkdocs_config, f)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to create MkDocs project: {e}")
            logging.error(f"Stdout: {e.stdout}")
            logging.error(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            logging.exception(f"An unexpected error occurred: {e}")
            return False
        return True
    else:
        logging.info(f"MkDocs project already exists in: {project_dir}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation for Python files using Gemini and MkDocs."
    )
    parser.add_argument("input_path", help="Path to the Python file or directory.")
    parser.add_argument(
        "-m",
        "--model",
        help="Gemini model to use (default: gemini-pro)",
        default="gemini-pro",
    )
    parser.add_argument(
        "--create-mkdocs",
        help="Create mkdocs project if it doesnt exist",
        action="store_true",
    )
    parser.add_argument(
        "--mkdocs-dir",
        help="Directory for the mkdocs project (default: docs)",
        default="docs",
    )
    parser.add_argument(
        "--docs-dir-name",
        help="Name of the docs directory inside the mkdocs project (default: docs)",
        default="docs",
    )
    parser.add_argument(
        "--interactive", help="Run in interactive mode", action="store_true"
    )
    parser.add_argument(
        "--ignore",
        nargs="+",
        help="Ignore patterns (e.g., .venv venv node_modules).",
        default=[
            ".venv",
            "venv",
            "node_modules",
            ".git",
            "__pycache__",
            ".env",
            "requirements.txt",
        ],
    )
    args = parser.parse_args()

    logging.info(f"Input path: {args.input_path}")
    logging.info(f"Model: {args.model}")
    logging.info(f"MkDocs Directory: {args.mkdocs_dir}")
    logging.info(f"Docs Directory Name: {args.docs_dir_name}")

    if args.interactive:
        logging.info("Running in interactive mode.")
        if not args.input_path:
            args.input_path = input("Enter the input path (file or directory): ")
        if not args.model:
            args.model = (
                input("Enter the Gemini model to use (default: gemini-pro): ")
                or "gemini-pro"
            )
        create_mkdocs = input(
            "Create MkDocs project if it doesn't exist? (y/N): "
        ).lower()
        args.create_mkdocs = create_mkdocs == "y"
        if not args.mkdocs_dir:
            args.mkdocs_dir = (
                input("Enter the MkDocs project directory (default: docs): ") or "docs"
            )
        if not args.docs_dir_name:
            args.docs_dir_name = (
                input("Enter the docs directory name (default: docs): ") or "docs"
            )
        ignore_input = input(
            "Enter ignore patterns separated by spaces (or press Enter for defaults): "
        )
        if ignore_input:
            args.ignore = ignore_input.split()
    elif not args.input_path:
        parser.print_help()
        exit(1)

    if args.create_mkdocs:
        if not create_mkdocs_project(args.mkdocs_dir, args.docs_dir_name):
            exit(1)

    docs_dir = os.path.join(args.mkdocs_dir, args.docs_dir_name)
    is_input_dir = os.path.isdir(args.input_path)
    generated_files = process_path(
        args.input_path,
        args.mkdocs_dir,
        args.docs_dir_name,
        args.model,
        args.ignore,
    )

    if generated_files:
        update_mkdocs_nav(
            generated_files, is_input_dir, args.mkdocs_dir, args.docs_dir_name
        )
    logging.info("Finished.")


if __name__ == "__main__":
    main()
