from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="olostep-sdk",
    version="0.1.2",
    author="Mohammad Ehsan Ansari",
    author_email="mdehsan873@gmail.com",
    description="Official Python SDK for Olostep Web Scraping API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",  # update if needed
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
)
