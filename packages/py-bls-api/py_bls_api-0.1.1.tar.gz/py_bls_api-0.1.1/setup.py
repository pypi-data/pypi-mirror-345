from setuptools import setup, find_packages

# Read the contents of your README file to use it for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-bls-api",
    version="0.1.1",
    author="Chris Morris",
    description="A Python wrapper for the U.S. Bureau of Labor Statistics (BLS) API",
    long_description=long_description,
    long_description_content_type="text/markdown", 
    url="https://github.com/coding-with-chris/py-bls-api",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pandas>=1.3.0",
        "requests>=2.25.0",
    ],    
    python_requires=">=3.6",
    license="Proprietary"
)
