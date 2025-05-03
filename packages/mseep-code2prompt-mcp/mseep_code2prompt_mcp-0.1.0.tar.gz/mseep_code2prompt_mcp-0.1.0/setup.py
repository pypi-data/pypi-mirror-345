
from setuptools import setup, find_packages

setup(
    name="mseep-code2prompt-mcp",
    version="0.1.0",
    description="MCP server for Code2Prompt",
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
    install_requires=['mcp>=1.4.1', 'httpx>=0.28.1', 'dotenv>=0.9.9', 'colorlog>=6.9.0', 'code2prompt-rs>=3.2.1'],
    keywords=["mseep"] + [],
)
