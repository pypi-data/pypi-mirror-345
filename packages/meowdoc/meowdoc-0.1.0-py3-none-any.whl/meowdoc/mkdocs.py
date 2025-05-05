import os
import logging
import yaml
import subprocess
from meowdoc import themes
import json

from pprint import pprint

def update_mkdocs_nav(
    generated_files,
    is_input_dir,
    mkdocs_dir,
    docs_dir_name,
    name,
    description,
    theme="material",
):
    mkdocs_config_path = os.path.join(mkdocs_dir, "mkdocs.yml")
    logging.info(f"Updating mkdocs.yml: {mkdocs_config_path}")

    try:
        with open(mkdocs_config_path, "r") as f:
            mkdocs_config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("mkdocs.yml not found. Please create a mkdocs project first.")
        return
    except yaml.YAMLError as e:
        logging.error(f"Error parsing mkdocs.yml: {e}")
        return

    if "nav" not in mkdocs_config:
        mkdocs_config["nav"] = []

    mkdocs_config["site_name"] = name
    mkdocs_config["theme"] = {"name": themes.THEMES[theme]["mkdocs_name"]}
    nav = mkdocs_config["nav"]
    # nav = []

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

        file_nav_structure = {}  # Dictionary to build nested nav

        for file in generated_files:
            relative_path = os.path.relpath(file, os.path.join(mkdocs_dir, docs_dir_name))
            parts = relative_path.split(os.sep)  # Split into path parts
            filename = os.path.splitext(parts[-1])[0]  # Filename without extension

            current_level = file_nav_structure
            for part in parts[:-1]:  # Iterate through directory parts
                if part not in current_level:
                    current_level[part] = {}  # Create nested dict if needed
                current_level = current_level[part]

            current_level[filename] = relative_path # Add the file at the end

        # Convert the nested dictionary to a list of dictionaries for mkdocs
        def convert_to_mkdocs_nav(data):
            mkdocs_nav = []
            for key, value in data.items():
                if isinstance(value, dict):
                    mkdocs_nav.append({key: convert_to_mkdocs_nav(value)})
                else:
                    mkdocs_nav.append({key: value})
            return mkdocs_nav

        api_section.extend(convert_to_mkdocs_nav(file_nav_structure)) # Extend the api section with the new structure

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

    themes.enable_theme(theme)


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

    print("Created mkdocs project")

def merge_dicts(existing, new):
    """
    Recursively merge two dictionaries. The `new` dictionary values take precedence,
    but nested dictionaries are merged intelligently.
    """
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(existing.get(key), dict):
            merge_dicts(existing[key], value)  # Recursively merge nested dictionaries
        else:
            existing[key] = value  # Overwrite or add the new value
    return existing

def finalize(mkdocs_config):
    if mkdocs_config.get("nav") is None:
        return mkdocs_config
    matches = list(map(_dedupe_API_elem, mkdocs_config["nav"]))
    mkdocs_config["nav"] = matches
    return mkdocs_config

def _dedupe_API_elem(elem):
    if elem.get("API") is not None:        
        data = elem["API"]
        pprint(data)
        seen_json = set()
        deduplicated_data = []

        for d in data:
            # Convert the dictionary to a JSON string with sorted keys
            # sort_keys=True is essential to ensure consistent string representation
            # for dictionaries with the same content but different key order.
            d_json = json.dumps(d, sort_keys=True)

            if d_json not in seen_json:
                seen_json.add(d_json)
                deduplicated_data.append(d) # Append the original dictionary

        elem["API"] = deduplicated_data
        pprint(deduplicated_data)
    return elem

def update_mkdocs_config_from_toml(config, mkdocs_dir):
    mkdocs_settings = config.get("mkdocs", {})  # Get the mkdocs section

    mkdocs_config_path = os.path.join(mkdocs_dir, "mkdocs.yml")
    logging.info(f"Updating mkdocs.yml: {mkdocs_config_path}")

    try:
        with open(mkdocs_config_path, "r") as f:
            mkdocs_config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        logging.error("mkdocs.yml not found. Please create a mkdocs project first.")
        return
    except yaml.YAMLError as e:
        logging.error(f"Error parsing mkdocs.yml: {e}")
        return

    # Merge mkdocs.yml with settings from config.toml
    mkdocs_config = merge_dicts(mkdocs_config, mkdocs_settings)
    mkdocs_config = finalize(mkdocs_config)

    try:
        with open(mkdocs_config_path, "w") as f:
            yaml.dump(mkdocs_config, f, indent=2)
        logging.info("mkdocs.yml updated with settings from config.toml")
    except Exception as e:
        logging.error(f"Error writing to mkdocs.yml: {e}")