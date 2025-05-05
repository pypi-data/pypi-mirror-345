from setuptools import setup, find_packages
import os

# Get the long description from the README file
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vectordbcloud",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=1.10.0",
        "python-jose>=3.3.0",
        "typing-extensions>=4.0.0",
    ],
    author="VectorDBCloud Team",
    author_email="support@vectordbcloud.com",
    description="Official Python SDK for VectorDBCloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VectorDBCloud/vectordbcloud-python",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
