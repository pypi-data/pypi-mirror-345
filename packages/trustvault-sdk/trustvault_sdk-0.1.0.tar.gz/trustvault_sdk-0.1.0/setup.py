import io
from setuptools import setup, find_packages

# Read the long description from README.md
with io.open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="trustvault-sdk",
    version="0.1.0",
    author="sanjay",
    author_email="sanju.skm@gmail.com",
    description="Lightweight Python SDK for application observability (TrustVault)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sanjuskm/trustvault",
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)