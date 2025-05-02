from setuptools import setup, find_packages

setup(
    name="ampa_sdk",
    version="0.1.0",
    description="Python SDK for the AMPA API",
    author="the37lab",
    packages=find_packages(where="."),
    package_dir={"": "src"},
    install_requires=["requests"],
    python_requires=">=3.7",
)