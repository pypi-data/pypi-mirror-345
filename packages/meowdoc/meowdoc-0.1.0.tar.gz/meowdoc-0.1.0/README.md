# Meowdoc

Meowdoc is a tool to generate documentation so that you don't have to :3. Read the documentation to find more!

## Getting Started

This section provides a quick overview of how to get started with meowdoc.

### Installation

```bash
pip install meowdoc
```

## Usage

make a config.toml file.

```toml
[main]
mkdocs_dir = "docs"
docs_dir_name = "docs"
input_path = "meowdoc" # or any directory such as `src/`
create_mkdocs = false

[project]
name = "Meowdoc"
description = "Meow! Meowdoc is a tool to generate documentation so that you don't have to :3. Read the documentation to find more!"
repo_url = "https://github.com/re-masashi/meowdoc"

[ignore]
patterns = [
    ".venv",
    "venv",
    "node_modules",
    ".git",
    "__pycache__",
    ".env",
    "requirements.txt"
]

[llm]
provider = "gemini"  # Options: gemini, openai, ollama, etc.
api_key_file = "secrets/gemini_api_key.txt"  # Path to the file containing the API key
# base_url = "http://localhost:11434"  # Required for Ollama
model = "gemini-2.0-flash-exp"  # Model name
```

Then run

```bash
python -m meowdoc.cli
```

You should see your docs succesfully created
Then, run

```bash
cd docs # or the folder of ur docs
mkdocs serve
```

## Contributing to Meowdoc

We welcome contributions to Meowdoc! Whether you're fixing a bug, adding a new feature, improving documentation, or suggesting ideas, we appreciate your help. Please take a moment to review this guide before contributing.

### How to Contribute

Here are several ways you can contribute to Meowdoc:

- **Report Bugs:** If you find a bug, please open an issue on its GitHub issue tracker. Be as descriptive as possible, including steps to reproduce the bug, the expected behavior, and the actual behavior.

- **Suggest Features:** Have an idea for a new feature? Open an issue on its GitHub issue tracker and describe your suggestion in detail. Explain why you think this feature would be valuable and how it could be implemented.

- **Improve Documentation:** Good documentation is crucial. If you find errors, omissions, or areas where the documentation could be improved, please submit a pull request with your suggested changes.

- **Submit Code:** We encourage you to submit code contributions to fix bugs or add new features. Please follow the guidelines below.

### Coding Style

We adhere to the following coding style guidelines:

- **Python:** We follow the PEP 8 style guide. Use `flake8` and `black` to format your code. Pre-commit should catch most style violations.
- **[Other Languages/Frameworks Used]:** (Describe coding style for other relevant languages or frameworks)

### Conventional Commits

We use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for commit messages. This helps us automate releases and generate changelogs.

A commit message should be structured as follows:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Examples:

- `feat(ui): add dark mode toggle`
- `fix(auth): prevent unauthorized access`
- `docs: update contributing guidelines`
- `chore: update dependencies`
- `test: add unit tests for parser`
- `ci: configure github actions`
