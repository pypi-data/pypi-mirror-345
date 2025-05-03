#!/usr/bin/env python
"""
Setup configuration for Levox GDPR compliance tool.
"""
from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read long description from README
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='levox',
    version='1.5.3',  # Keep in sync with VERSION in build_levox.py
    description='GDPR Compliance Analysis and Remediation Tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Fenrix AI',
    author_email='support@fenrixai.com',
    url='https://github.com/fenrixai/levox',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'levox=levox.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    keywords='gdpr privacy compliance security scanner analysis remediation',
) 