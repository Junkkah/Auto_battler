from setuptools import setup, find_packages

setup(
    name='auto_battler',
    version='1.1',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'numpy==1.24.2',
        'pygame==2.3.0',
        'pandas==2.0.0'
    ],
)