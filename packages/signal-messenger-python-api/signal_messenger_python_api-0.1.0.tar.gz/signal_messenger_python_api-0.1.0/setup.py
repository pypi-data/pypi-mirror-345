from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="signal-messenger-python-api",
    version="0.1.0",
    author="pcko1",
    author_email="hi@pankotsias.com",
    description="Asynchronous Python wrapper for the Signal CLI REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pcko1/signal-messenger-python-api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.9",
    install_requires=[
        "aiohttp>=3.7.4",
        "pydantic>=1.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.14.0",
            "pytest-cov>=2.10.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "mypy>=0.812",
            "flake8>=3.9.2",
        ],
    },
)
