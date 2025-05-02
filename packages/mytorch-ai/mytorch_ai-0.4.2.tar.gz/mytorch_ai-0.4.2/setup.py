# This is the setup.py file for the mytorch_client package.
# It is used to install the package for local development.
# It is not used to install the package for production.
#
# To install the package for local development, run the following command:
# pip install -e .
#

from setuptools import setup, find_packages

setup(
    name="mytorch_client",
    version="0.4.2",
    packages=find_packages(),
    install_requires=[
        "grpcio>=1.71.0",
        "grpcio-tools>=1.71.0",
        "numpy",
        "requests",
        "pillow",
        "tqdm",
        "matplotlib",
        "scikit-learn",
        "setuptools",
        "typing_extensions",
    ]
) 
