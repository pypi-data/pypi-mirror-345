#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentask",
    version="0.1.2",
    author="TaskFlow Team",
    author_email="example@example.com",
    description="An AI-powered task planning assistant with calendar generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/taskflow",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mistralai",
        "google-generativeai",
        "python-dotenv",
        "icalendar",
        "grpcio==1.60.1",
    ],
    entry_points={
        "console_scripts": [
            "understand=agentask.understand_main:main",
            "plan=agentask.plan_main:main",
            "generate-calendar=agentask.calendar_main:main",
        ],
    },
)
