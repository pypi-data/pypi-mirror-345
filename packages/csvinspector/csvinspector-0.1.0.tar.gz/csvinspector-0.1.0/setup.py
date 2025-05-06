from setuptools import setup, find_packages

setup(
    name="csvinspector",
    version="0.1.0",
    author="Abhi Bhimani",
    author_email="abhibhimani14758@gmail.com",
    description="A simple library for preprocessing and EDA on CSV files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/abhii14758/csvinspector",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "missingno>=0.5.0",
        "numpy>=1.21.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
