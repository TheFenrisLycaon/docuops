"""
Setup script for docuops package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="docuops",
    version="0.1.0",
    author="Rishabh Anand",
    author_email="rishabhanandxz@gmail.com",
    description="A small Python toolkit for PDF and DOCX operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/docuops",  # Replace with your actual GitHub repository URL
    packages=find_packages(),
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    tests_require=[
        "pytest",
    ],
    entry_points={
        "console_scripts": [
            "docuops=docuops.cli:main",
        ],
    },
    keywords="pdf docx document processing compression conversion",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/docuops/issues",  # Update with your GitHub username
        "Source": "https://github.com/yourusername/docuops",  # Update with your GitHub username
    },
)