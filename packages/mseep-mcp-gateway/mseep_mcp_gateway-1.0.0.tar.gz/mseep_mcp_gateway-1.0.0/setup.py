
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-gateway",
    version="1.0.0",
    description="A gateway for MCP servers",
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
    install_requires=['mcp[cli]>=1.6.0'],
    keywords=["mseep"] + [],
)
