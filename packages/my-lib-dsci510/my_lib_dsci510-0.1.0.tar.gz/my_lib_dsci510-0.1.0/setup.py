# codes in setup.py
from setuptools import setup, find_packages

setup(
    name='my_lib_dsci510',
    version='0.1.0',
    description='A simple demo library with an attention function',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.20.0'  # Add any version you depend on
    ],
    python_requires='>=3.6',
)