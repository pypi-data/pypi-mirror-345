
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-reddit",
    version="0.1.0",
    description="A Reddit client using PRAW",
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
    install_requires=['aiohttp>=3.11.18', 'fastmcp>=2.2.0', 'mcp[cli]>=1.6.0', 'praw>=7.7.1', 'python-dotenv>=1.0.0', 'rich>=13.7.0'],
    keywords=["mseep"] + [],
)
