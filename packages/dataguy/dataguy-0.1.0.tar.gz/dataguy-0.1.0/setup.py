from setuptools import setup, find_packages

setup(
    name="dataguy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "claudette",
        "pandas",
        "matplotlib",
        "numpy",
        "scikit-learn",
        "anthropic",
    ],
    author="István Magyary; Sára Viemann; Kristóf Bálint",
    author_email="magistak@gmail.com",
    description="A Python package for automated data science using LLMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/magistak/llm-data",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
