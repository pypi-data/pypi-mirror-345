from setuptools import setup, find_packages

setup(
    name="logdash",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "colorama",
    ],
    author="LogDash",
    author_email="info@logdash.io",
    description="Python SDK for LogDash logging and metrics service",
    keywords="logging, metrics, monitoring",
    url="https://logdash.io",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 