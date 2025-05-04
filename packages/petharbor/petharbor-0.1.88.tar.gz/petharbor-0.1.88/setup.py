from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="petharbor",
    version="0.1.88",
    author="Sean Farrell",
    author_email="sean.farrell2@durham.ac.uk",
    description="PetHarbor is a Python package designed for anonymizing datasets using either a pre-trained model or a hash-based approach.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seanfarr788/petharbor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "accelerate",
        "backports.tarfile",
        "colorlog",
        "datasets",
        "transformers",
        "importlib-metadata",
        "jaraco.collections",
        "pandas",
        "protobuf",
        "pysocks",
        "sentencepiece",
        "tomli",
        "torch",  # Added for petharbor[advance]
        "spacy",  # Added for petharbor[lite]
    ],
    extras_require={
        "advance": [
            "torch",
            "transformers",
            "accelerate"
        ],
        "lite": [
            "datasets",
            "spacy",
        ],
    },
)