from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
with open(os.path.join('swift_parser_py', '__init__.py'), encoding='utf-8') as f:
    version = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", f.read()).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="swift-parser-py",
    version=version,
    author="Solchos",
    author_email="solchos@gmail.com",
    description="Python-based metadata-driven parser for SWIFT/ISO 15022 messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/solchos/swift-parser",
    packages=find_packages(include=['swift_parser_py', 'swift_parser_py.*'], exclude=['*.tests', '*.tests.*']),
    include_package_data=True,
    package_data={
        "swift_parser_py": ["metadata/*.json"],
        "swift_parser_py.utils": ["field_parser_fix.py"],
    },
    install_requires=[
        "typing>=3.7.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="swift, iso15022, finance, banking, parser",
    python_requires=">=3.8",
    project_urls={
        "Bug Tracker": "https://github.com/solchos/swift-parser/issues",
    },
)