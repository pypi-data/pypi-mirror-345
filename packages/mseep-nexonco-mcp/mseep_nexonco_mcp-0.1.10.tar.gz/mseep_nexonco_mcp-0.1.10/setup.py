
from setuptools import setup, find_packages

setup(
    name="mseep-nexonco-mcp",
    version="0.1.10",
    description="An advanced MCP Server for accessing and analyzing clinical evidence data, with flexible search options to support precision medicine and oncology research.",
    author="mseep",
    author_email="support@skydeck.ai",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['mcp[cli]>=1.6.0', 'pandas>=2.2.3', 'requests>=2.32.3', 'starlette>=0.46.1', 'uvicorn>=0.34.0'],
    keywords=["mseep"] + [],
)
