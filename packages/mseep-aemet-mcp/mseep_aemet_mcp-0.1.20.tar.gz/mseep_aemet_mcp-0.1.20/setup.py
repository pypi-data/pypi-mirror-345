
from setuptools import setup, find_packages

setup(
    name="mseep-aemet_mcp",
    version="0.1.20",
    description="AEMET API integration with MCP (Model Context Protocol)",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.6.0'],
    keywords=["mseep"] + [],
)
