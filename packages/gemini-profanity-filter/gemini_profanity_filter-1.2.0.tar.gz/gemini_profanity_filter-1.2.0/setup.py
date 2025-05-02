from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gemini-profanity-filter",
    version="1.2.0",
    author="Mark",
    author_email="firi8228@gmail.com",
    description="A Python module for detecting and filtering profanity using Google's Gemini API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "google-generativeai>=0.3.0",
    ],
)