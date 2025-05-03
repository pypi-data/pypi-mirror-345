from setuptools import setup, find_packages
import os

# Read the README.md file for the long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cdp-chrome-tabs",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    description="A Python package to interact with Chrome tabs via Chrome DevTools Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="guocity",
    author_email="your.email@example.com",
    url="https://github.com/guocity/cdp-chrome-tabs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords=["chrome", "browser", "devtools", "automation", "cdp"],
)
