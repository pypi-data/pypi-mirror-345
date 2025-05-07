import setuptools 
from pathlib import Path


setuptools.setup(
    name="zxppackage",  # Replace with your package name
    version="0.0.1",
    author="Abyss",
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"]),
)