from setuptools import find_packages, setup

setup(
    name="crf_api_client",  # Package name
    version="0.0.3",  # Package version
    packages=find_packages(),  # Automatically finds `mypackage`
    install_requires=[],  # List dependencies if any
    author="CRF",
    description="A client for the CRF API",
    python_requires=">=3.11",  # Minimum Python version
)
