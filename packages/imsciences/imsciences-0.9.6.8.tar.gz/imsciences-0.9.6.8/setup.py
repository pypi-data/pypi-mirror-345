from setuptools import setup, find_packages
import os

# Function to read the contents of the README file
def read_md(file_name):
    if os.path.isfile(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

VERSION = '0.9.6.8'
DESCRIPTION = 'IMS Data Processing Package'
LONG_DESCRIPTION = read_md('README.md') 

# Setting up
setup(
    name="imsciences",
    version=VERSION,
    author="IMS",   
    author_email='cam@im-sciences.com',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "pandas", "plotly", "numpy", "fredapi", "xgboost", "scikit-learn",
        "bs4", "yfinance", "holidays", "google-analytics-data", "geopandas", "geopy"
    ],
    keywords=['data processing', 'apis', 'data analysis', 'data visualization', 'machine learning'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
