"""
Script de instalação do Fotix.
"""

from setuptools import setup, find_packages

setup(
    name="fotix",
    version="0.1.0",
    package_dir={"": "fotix/src"},
    packages=find_packages(where="fotix/src"),
    python_requires=">=3.10",
    install_requires=[],
)
