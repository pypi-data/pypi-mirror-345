from setuptools import setup, find_packages

setup(
    name="askharsha",
    version="0.1.3",
    description="A lightweight chatbot module that uses a modern language model API to generate intelligent, clean, and readable responses. Designed for developers who want plain-text replies without markdown clutter.",
    author="Alapati Sree Harsha",
    author_email="sreeharshaalapati@gmail.com",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.6",
)
