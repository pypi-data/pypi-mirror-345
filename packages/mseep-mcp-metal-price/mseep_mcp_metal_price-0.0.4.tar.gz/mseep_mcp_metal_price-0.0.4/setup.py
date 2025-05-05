
from setuptools import setup, find_packages

setup(
    name="mseep-mcp_metal_price",
    version="0.0.4",
    description="An MCP server for metal price information",
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
    install_requires=['mcp>=1.0.0', 'requests>=2.31.0'],
    keywords=["mseep"] + [],
)
