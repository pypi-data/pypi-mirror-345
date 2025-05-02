#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dsapi-llmclient",  # Using the prefix to avoid conflicts
    version="0.1.5",  # Incremented version number from 0.1.1 to 0.1.5
    author="Leo",
    author_email="marticle.ios@gmail.com",
    description="轻量级LLM API客户端库，支持缓存、重试和详细日志记录功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leo/dsapi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "tenacity>=8.0.0",
        "python-dotenv>=0.19.0",
        "jsonschema>=4.0.0"
    ],
)