from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="askharsha",
    version="0.1.5",
    description="A lightweight chatbot module that uses a modern language model API to generate intelligent, clean, and readable responses. Designed for developers who want plain-text replies without markdown clutter.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alapati Sree Harsha",
    author_email="sreeharshaalapati@gmail.com",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.6",
)

