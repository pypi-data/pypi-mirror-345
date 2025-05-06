from setuptools import setup, find_packages
import pathlib

# Get the directory containing this file
here = pathlib.Path(__file__).parent.resolve()

# Read the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="dxflow",  
    author="DiPhyx Team",  
    author_email="info@diphyx.com",  
    description="A Python SDK for the DiPhyx cloud computing platform, designed to streamline scientific discovery.", 
    long_description=long_description,  
    long_description_content_type="text/markdown",  
    url="https://dxflow.ai", 
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
    keywords="cloud computing, scientific discovery, SDK",  
    packages=find_packages(),  
    python_requires=">=3.6, <4",
    install_requires=[
        "requests",
        "tuspy",
        "PyYAML",
    ],
    # project_urls={  
    #     "Bug Reports": "https://dxflow.ai/issues",
    #     "Source": "https://github.com/diphyx/dxflow_sdk",
    # },
)
