
from setuptools import setup, find_packages

setup(
    name="mseep-malloryai-mcp-server",
    version="0.1.0",
    description="MalloryAI Intelligence MCP Server",
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
    install_requires=['malloryai-sdk>=0.3.2', 'python-dotenv>=1.1.0', 'pydantic>=2.11.0', 'mcp[cli]>=1.6.0'],
    keywords=["mseep"] + [],
)
