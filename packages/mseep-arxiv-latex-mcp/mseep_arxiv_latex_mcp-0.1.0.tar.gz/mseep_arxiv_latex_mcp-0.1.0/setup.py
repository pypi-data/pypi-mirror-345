
from setuptools import setup, find_packages

setup(
    name="mseep-arxiv-latex-mcp",
    version="0.1.0",
    description="An MCP server that fetches and processes arXiv papers using LaTeX source for accurate equation handling",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.6.0', 'arxiv-to-prompt>=0.1.1'],
    keywords=["mseep"] + [],
)
