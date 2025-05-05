import os
import logging
import fnmatch
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

class MeowdocCore:
    """A class to generate documentation for Python files using LLM and MkDocs."""

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
#         model="gemini-2.0-flash-exp",
    ):
        """Initialize the DocumentationGenerator with a specified AI model."""
        self.input_path=input_path
        self.mkdocs_dir=mkdocs_dir
        self.docs_dir=docs_dir
        self.ignore_patterns=ignore_patterns
        self.project_name=project_name
        self.project_description=project_description
        self.repo_url=repo_url
        self.llm_provider = llm_provider
#        self.model = model
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def generate_docs(self, file_path, all_file_contents):
        """Generates documentation for a single file with context from all related files."""
        filename = os.path.basename(file_path)
        relative_filename = os.path.relpath(file_path, self.input_path) # Get the relative path
        filename = relative_filename

        try:
            code = all_file_contents[filename]
        except KeyError:
            logging.error(f"File content not found for {file_path}")
            return None
        finally:
            logging.info(f"File content found for {file_path}")

        prompt = "Generate comprehensive documentation in Markdown format for the following Python file (do not give the Markdown in backticks.), considering the context of related files:\n\n"
        prompt += f"File: {filename}\n```python\n{code}\n```\n\n"

        prompt += "Context from related files:\n\n"
        for other_filename, other_code in all_file_contents.items():
            if other_filename != filename:
                prompt += f"File: {other_filename}\n```python\n{other_code}\n```\n\n"

        prompt += """
        Include:
        *   A concise Module-level description.
        *   Descriptions of functions and classes, including parameters, return values, and docstrings.
        *   Clearly indicate how this file interacts with other modules (using examples).
        *   Provide example usage.
        *   Descriptions of each function and class, including parameters, return values, and docstrings.
        *   Use clear headings and subheadings (e.g., ##, ###).
        *   Provide example usage where possible.
        *   If there are no docstrings, try to infer the purpose of the code based on its structure and variable names.
        """

        # Read docguide content if it exists
        docguide_path = os.path.join("docguide", file_path + ".md")
        if os.path.exists(docguide_path):
            logging.info(f"Docguide content found for {file_path}")
            with open(docguide_path, "r", encoding="utf-8") as guide_file:
                guide_content = guide_file.read()
                # Append guide content to the prompt
                prompt += f"\n\n### Additional Guidelines:\n{guide_content}\n"

        try:
            # response = genai.GenerativeModel(model_name=self.model).generate_content(
            #     prompt
            # )
            response = self.llm_provider.generate(prompt)
            print(f"generated content for `{filename}`")
            return response
        except Exception as e:
            logging.exception(f"Error calling LLM: {e}")
            return None

    def create_index(self, mkdocs_dir, docs_dir, readme_content):
        """Creates the index.md file with the provided content."""
        index_path = os.path.join(mkdocs_dir, docs_dir, "index.md")
        with open(index_path, "w", encoding="utf-8") as outfile:
            outfile.write(readme_content)
        print(f"README written to: {index_path}")

    def should_ignore(self, path, ignore_patterns):
        """Checks if a path or any of its parent directories should be ignored."""
        path = os.path.abspath(
            path
        )  # Convert to absolute path for consistent comparison
        while path:
            base_name = os.path.basename(path)
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(base_name, pattern):
                    # logging.info(
                    #     f"Ignoring {path} because it matches pattern: {pattern}"
                    # )
                    return True
            path = os.path.dirname(path)  # Move up to the parent directory
            if path == os.path.dirname(path):  # Check for root
                break
        return False

    # def process_path(self, input_path=None):
    #     if input_path is None:
    #         input_path = self.input_path

    #     mkdocs_dir = self.mkdocs_dir
    #     docs_dir_name = self.docs_dir
    #     ignore_patterns = self.ignore_patterns
    #     logging.info(f"Processing path: {input_path}")
    #     generated_files = []

    #     if ignore_patterns is None:
    #         ignore_patterns = []

    #     if self.should_ignore(input_path, ignore_patterns):
    #         logging.info(f"Ignoring path (matches pattern): {input_path}")
    #         return []

    #     if os.path.abspath(input_path) == os.path.abspath(mkdocs_dir):
    #         logging.info(f"Ignoring the mkdocs directory: {input_path}")
    #         return []

    #     docs_dir = os.path.join(mkdocs_dir, docs_dir_name)

    #     if os.path.isfile(input_path):
    #         logging.info(f"Input is a file: {input_path}")
    #         if True:
    #             with open(input_path, "r", encoding="utf-8") as f:
    #                 all_file_contents = {}
    #                 all_file_contents[os.path.basename(input_path)] = f.read()
    #             result = self.generate_docs(input_path, all_file_contents)
    #             if result is not None:
    #                 docs = result
    #                 output_filename = os.path.splitext(os.path.basename(input_path))[0] + ".md"
    #                 output_path = os.path.join(docs_dir, output_filename)
    #                 pathlib.Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    #                 with open(output_path, "w", encoding="utf-8") as outfile:
    #                     outfile.write(docs)
    #                 generated_files.append(output_path)
    #             else:
    #                 logging.error("Error generating documentation for %s", input_path)
    #     elif os.path.isdir(input_path):
    #         logging.info(f"Input is a directory: {input_path}")
    #         all_file_contents = {}  # Initialize OUTSIDE

    #         for root, _, files in os.walk(input_path):
    #             for file in files:
    #                 file_path = os.path.join(root, file)
    #                 relative_file_path = os.path.relpath(file_path, input_path)

    #                 if self.should_ignore(file_path, ignore_patterns):
    #                     logging.info(f"Ignoring file (matches pattern): {file_path}")
    #                     continue

    #                 if os.path.samefile(file_path, os.path.join(mkdocs_dir, docs_dir_name)):
    #                     logging.info(f"Ignoring the mkdocs directory: {file_path}")
    #                     continue

    #                 if True:
    #                     try:
    #                         with open(file_path, "r", encoding="utf-8") as f:
    #                             all_file_contents[relative_file_path] = f.read()  # KEY CHANGE: Relative path as key
    #                     except Exception as e:
    #                         logging.error(f"Error reading file {file_path}: {e}")
    #                         continue

    #                     docs = self.generate_docs(file_path, all_file_contents)  # Full path for generate_docs
    #                     if docs:
    #                         output_dir = os.path.join(docs_dir, os.path.dirname(relative_file_path))
    #                         output_filename = os.path.splitext(os.path.basename(relative_file_path))[0] + ".md"
    #                         output_path = os.path.join(output_dir, output_filename)

    #                         pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)  # Create all dirs

    #                         with open(output_path, "w", encoding="utf-8") as outfile:
    #                             outfile.write(docs)
    #                         generated_files.append(output_path)
    #                     else:
    #                         logging.error(f"Error generating docs for {file_path}")

    #     else:
    #         logging.warning(f"Skipping invalid path: {input_path}")

    #     print(generated_files)

    #     return generated_files

    def _collect_files(self):
        """Walk input_path and return list of (file_path, relative_path)."""
        file_list = []
        for root, _, files in os.walk(self.input_path):
            if self.should_ignore(root, self.ignore_patterns):
                continue
            for fname in files:
                fp = os.path.join(root, fname)
                if self.should_ignore(fp, self.ignore_patterns):
                    continue
                rel = os.path.relpath(fp, self.input_path)
                file_list.append((fp, rel))
        return file_list

    def process_path(self):
        """Concurrent version of the old process_path; returns list of generated docs."""
        files = self._collect_files()
        all_contents = {}
        # Pre‑read all files into memory (so reading itself can be parallelized too)
        for fp, rel in files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    all_contents[rel] = f.read()
            except Exception as e:
                logging.error(f"Failed reading {fp}: {e}")

        mkdocs_docs = os.path.join(self.mkdocs_dir, self.docs_dir)
        pathlib.Path(mkdocs_docs).mkdir(parents=True, exist_ok=True)

        results = []
        # Use ThreadPoolExecutor for I/O-bound work
        with ThreadPoolExecutor() as exe:
            future_to_file = {
                exe.submit(self.generate_docs, fp, all_contents): (fp, rel)
                for fp, rel in files
            }
            for fut in as_completed(future_to_file):
                fp, rel = future_to_file[fut]
                docs = fut.result()
                if docs:
                    out_fname = os.path.splitext(os.path.basename(rel))[0] + '.md'
                    out_path = os.path.join(mkdocs_docs, os.path.dirname(rel), out_fname)
                    pathlib.Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
                    with open(out_path, 'w', encoding='utf-8') as out:
                        out.write(docs)
                    results.append(out_path)
                else:
                    logging.error(f"No docs for {fp}")
        return results

    def create_project_index(
        self,
    ):
        mkdocs_dir=self.mkdocs_dir
        docs_dir=self.docs_dir
        project_name=self.project_name
        project_description=self.project_description

        project_name = project_name.lower().replace("_", "-")

        # Generate AI-based description
        def generate_ai_description(prompt):
            try:
                response = self.llm_provider.generate(prompt)
                print("generated description")
                return response
            except Exception as e:
                logging.error(f"Error calling Gemini API: {e}")
                return "AI-generated content could not be loaded."

        contributing_prompt = f"""
        Generate a 'Contributing' section for a project named {project_name} in markdown. Do not give the response in backticks. 
        Include guidelines for contributing, such as setting up the development environment and submitting pull requests.
        """
        contributing_description = generate_ai_description(contributing_prompt)

        # Create the index content
        index_content = f"""# {project_name}

{project_description}

## Getting Started

This section provides a quick overview of how to get started with {project_name}.

### Installation

```bash
pip install {project_name}
```
Contributing

{contributing_description}
License

MIT License
Repository

GitHub
"""
        # Write the content to index.md
        index_path = os.path.join(mkdocs_dir, docs_dir, "index.md")
        with open(index_path, "w", encoding="utf-8") as outfile:
            outfile.write(index_content)
            print(f"index.md written to: {index_path}")
