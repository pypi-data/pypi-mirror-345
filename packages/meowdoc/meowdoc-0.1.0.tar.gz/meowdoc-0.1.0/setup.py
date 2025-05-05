from setuptools import setup, find_packages

setup(
    name="meowdoc",  # Replace with actual package name
    version="0.1.0",  # Replace with actual version
    packages=find_packages(),  # Automatically find packages
    install_requires=[
        "google-generativeai",
        "mkdocs",
        "python-dotenv",
        "mkdocs-material",
    ],
    entry_points={
        "console_scripts": [
            "meowdoc = cli:main",  # Replace cli:main with your actual entry point
        ],
    },
    author="Nafi (re-masashi)",
    author_email="nafines007@gmail.com",  # Replace with your email
    description="A documentation generator using Gemini and MkDocs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/re-masashi/meowdoc",  # Replace with your repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
