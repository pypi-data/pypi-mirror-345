from setuptools import setup, find_packages
from pathlib import Path

def read_requirements():
    reqs_path = Path(__file__).parent / 'requirements.txt'
    if reqs_path.is_file():
        with reqs_path.open() as reqs_file:
            return reqs_file.read().splitlines()
    return []

readme_path = Path(__file__).parent / 'flexiconc/docs/pypi-description.md'

setup(
    name="FlexiConc",
    version="0.1.8",
    author="RC21 (Nathan Dykes, Stephanie Evert, Michaela Mahlberg, Alexander Piperski @ Friedrich-Alexander-Universität Erlangen-Nürnberg)",
    author_email="aleksandr.piperski@fau.de",
    description="A Python package to assist concordance reading",
    long_description=readme_path.read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/fau-klue/flexiconc",
    project_urls={
        "Documentation": "https://fau-klue.github.io/flexiconc-docs/",
        # "Source": "https://github.com/fau-klue/flexiconc"
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=read_requirements(),
    package_data={
        "": ["*.ini", "*.txt", "*.tsv", "*.json"],
    },
)
