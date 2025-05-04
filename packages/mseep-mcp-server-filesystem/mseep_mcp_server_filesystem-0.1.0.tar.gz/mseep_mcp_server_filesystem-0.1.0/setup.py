
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-filesystem",
    version="0.1.0",
    description="A simple Model Context Protocol (MCP) server with file operation tools",
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
    install_requires=['pathspec>=0.12.1', 'igittigitt>=2.1.5', 'mcp>=1.3.0', 'mcp[server]>=1.3.0', 'mcp[cli]>=1.3.0', 'structlog>=25.2.0', 'python-json-logger>=3.3.0'],
    keywords=["mseep"] + ['mcp', 'server', 'filesystem', 'claude', 'ai', 'assistant', 'file-operations'],
)
