import os
from setuptools import setup, find_packages

# Get current directory
here = os.path.abspath(os.path.dirname(__file__))

# Read README.md
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements.txt
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="mcp-proxy-adapter",
    version="2.1.0",
    description="Adapter for exposing Command Registry commands as tools for AI models via MCP Proxy.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vasilyvz/mcp-proxy-adapter",
    author="Vasiliy VZ",
    author_email="vasilyvz@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="openai, llm, ai, proxy, tools",
    # package_dir={"": "src"},
    packages=find_packages(),
    python_requires=">=3.9, <4",
    install_requires=requirements,
    project_urls={
        "Bug Reports": "https://github.com/vasilyvz/mcp-proxy-adapter/issues",
        "Source": "https://github.com/vasilyvz/mcp-proxy-adapter",
    },
    include_package_data=True,
    package_data={
        "examples": ["*.py", "*.json"],
    },
) 