from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simpledht",
    version="0.1.1",
    author="Dhruvkumar Patel",
    author_email="dhruv.ldrp9@gmail.com",
    description="A simple distributed hash table implementation",
    long_description="A simple distributed hash table implementation",
    long_description_content_type="text/markdown",
    url="https://github.com/dhruvldrp9/simpledht",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.1",
        "click>=8.0.1",
    ],
    entry_points={
        "console_scripts": [
            "simpledht=simpledht.cli:main",
        ],
    },
) 