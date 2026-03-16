#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="todo-tui",
    version="1.0.0",
    description="Terminal Todo App with Jira sync support",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "textual>=0.40.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "todo=todo_tui.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
