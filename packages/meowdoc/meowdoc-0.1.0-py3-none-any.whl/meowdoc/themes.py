import subprocess

THEMES = {
    "default": {"package_name": "", "mkdocs_name": ""},
    "dracula": {"package_name": "mkdocs-dracula-theme", "mkdocs_name": "dracula"},
    "material": {"package_name": "mkdocs-material", "mkdocs_name": "material"},
}


def enable_theme(theme="dracula"):
    subprocess.run(
        ["pip", "install", THEMES[theme]["package_name"]],
        check=True,
        capture_output=True,
        text=True,
    )
    pass
