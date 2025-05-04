
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-sentry",
    version="0.6.2",
    description="MCP server for retrieving issues from sentry.io",
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
    install_requires=['mcp>=1.0.0'],
    keywords=["mseep"] + [],
)
