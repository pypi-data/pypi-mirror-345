from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_desc = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="grebes",
    version="0.1.1",
    description="🕵️‍♂️ Grebes: lightweight, nature-inspired data auditor",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Akash Nath",
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "openpyxl>=3.0.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "grebes=grebes.cli:main",
        ],
    },
)
