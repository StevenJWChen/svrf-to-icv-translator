#!/usr/bin/env python3
"""
Setup script for SVRF to ICV Translator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="svrf-to-icv-translator",
    version="1.0.0",
    description="Comprehensive Python toolkit for translating Calibre SVRF design rule files to Synopsys IC Validator (ICV) format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SVRF DRC Tools Development Team",
    author_email="developer@example.com",
    url="https://github.com/StevenJWChen/svrf-to-icv-translator",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="SVRF ICV DRC EDA semiconductor design rules translation calibre synopsys",
    python_requires=">=3.8",
    py_modules=[
        "simple_svrf_parser",
        "svrf_to_icv_translator", 
        "final_enhanced_translator",
        "enhanced_svrf_parser",
        "enhanced_svrf_to_icv_translator",
        "demo_parser",
        "demo_translator"
    ],
    install_requires=[
        # Core functionality has no dependencies - uses only Python standard library
    ],
    extras_require={
        "stock": requirements,  # Optional TSMC stock tracker dependencies
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0", 
            "flake8>=4.0.0",
            "mypy>=0.990"
        ],
    },
    entry_points={
        "console_scripts": [
            "svrf-parse=simple_svrf_parser:main",
            "svrf-to-icv=svrf_to_icv_translator:main",
            "svrf-translate=final_enhanced_translator:main",
        ],
    },
    package_data={
        "": [
            "*.svrf",
            "*.icv", 
            "*.md",
            "LICENSE",
            "requirements.txt"
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/StevenJWChen/svrf-to-icv-translator/issues",
        "Source": "https://github.com/StevenJWChen/svrf-to-icv-translator",
        "Documentation": "https://github.com/StevenJWChen/svrf-to-icv-translator/blob/main/README.md",
    },
)