from setuptools import setup, find_packages
import os
import re

# Read version from _version.py
with open('_version.py', 'r') as f:
    version_file = f.read()
    version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    version = version_match.group(1) if version_match else '0.0.0'

setup(
    name='gspreadplusplus',
    version=version,
    author='Daniel Simanek',
    author_email='daniel.simanek@decathlon.com',
    description='Enhanced Google Sheets operations with advanced data type handling',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/daniel-simanek/gspreadplusplus',
    packages=find_packages(),
    install_requires=[
        'gspread>=5.0.0',
        'google-auth>=2.0.0',
        'pyspark>=3.0.0',
        'pandas>=1.0.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires='>=3.7',
)
