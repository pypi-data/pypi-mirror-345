from setuptools import setup, find_packages

setup(
    name="notebook_validator",
    version="0.1.0",
    author="Your Name",
    description="Python notebook validator for Microsoft Fabric",
    long_description="A library to validate Python notebooks in Microsoft Fabric against coding standards and naming conventions.",
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "nbformat",
        "ipykernel"
    ]
)