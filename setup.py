from setuptools import setup, find_packages

setup(
    name='auto_battle',
    version='1.0',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'numpy==1.24.2',
        'pygame==2.3.0'
    ],
)