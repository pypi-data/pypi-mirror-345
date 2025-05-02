from setuptools import setup, find_packages
import os
import sys

# Make sure the Levox directory is available to setup
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Read requirements from the Levox folder
with open(os.path.join("Levox", "requirements.txt")) as f:
    requirements = f.read().splitlines()

# Read long description from README.md if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="levox",
    version="1.5.2",  # Match the version in main.py
    description="GDPR, PII and Data Flow Compliance Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levox Team",
    author_email="info@levox.io",
    url="https://github.com/levox/gdpr-compliance",
    package_dir={"levox": "Levox/levox"},
    packages=["levox"] + ["levox." + p for p in find_packages("Levox/levox")],
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "levox=levox.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    keywords="gdpr, compliance, security, privacy, pii, data-protection",
) 