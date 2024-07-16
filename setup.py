"""
Setup script for the auto_battler package.

This script uses setuptools to define the package metadata and dependencies
for the auto_battler project.

Attributes:
    name (str): The name of the package.
    version (str): The version of the package.
    packages (list): List of all Python import packages that should be included.
    python_requires (str): The required Python version for this package.
    install_requires (list): List of dependencies to be installed along with the package.
"""

from setuptools import setup, find_packages

setup(
    name='auto_battler',
    version='1.3.1',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'numpy==1.23.4',
        'pygame==2.1.2',
        'pandas==2.0.0'
    ],
)