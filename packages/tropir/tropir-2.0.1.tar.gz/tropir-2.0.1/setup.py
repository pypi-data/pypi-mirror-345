from setuptools import setup, find_packages

setup(
    name="tropir",
    version="2.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tropir=tropir.cli:main",
        ],
    },
    author="Tropir",
    author_email="founders@tropir.com",
    description="A thin client for tracing LLM calls",
    long_description=open("README.md").read() if open("README.md", "a").close() or True else "",
    long_description_content_type="text/markdown",
    url="https://tropir.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 