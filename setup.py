from setuptools import setup, find_packages

setup(
    name='auto_battler',
    version='1.1',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'numpy==1.23.4',
        'pygame==2.1.2',
        'pandas==2.0.0'
    ],
)