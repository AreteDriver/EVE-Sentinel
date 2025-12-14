"""Setup configuration for Sentinel."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eve-sentinel",
    version="0.1.0",
    author="James C. Young",
    description="Read-only intelligence analysis engine for EVE Online recruitment vetting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AreteDriver/Sentinel-",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "networkx>=3.0",
        "matplotlib>=3.5.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dateutil>=2.8.0",
    ],
)
