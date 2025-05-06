
from setuptools import setup, find_packages

setup(
    name="mseep-norman-mcp-server",
    version="0.1.4",
    description="A Model Context Protocol (MCP) server for Norman Finance API",
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
    install_requires=['mcp>=0.3.0', 'mcp[cli]>=1.7.0', 'mcp[sse]>=1.7.0', 'requests>=2.25.0', 'python-dotenv>=0.19.0', 'pyyaml>=6.0.1', 'httpx>=0.24.0', 'jinja2>=3.0.0'],
    keywords=["mseep"] + [],
)
