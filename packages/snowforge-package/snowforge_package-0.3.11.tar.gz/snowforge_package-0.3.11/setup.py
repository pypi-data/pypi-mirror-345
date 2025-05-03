# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="snowforge-package",
    version="0.3.11",  # Change this for new releases
    author="Andreas Heggelund",
    author_email="andreasheggelund@gmail.com",
    description="A Python package for supporting migration from on-prem to cloud",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Snowforge",  # Replace with your GitHub repo
    packages=find_packages(),
    install_requires=[
        "boto3",
        "snowflake-connector-python",
        "coloredlogs",
        "colored",
        "tqdm",
        "toml",
        "argparse"        
    ],
    python_requires=">=3.12",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
