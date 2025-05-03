
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-code-analyzer",
    version="0.1.0",
    description="A code analysis tool using Model Context Protocol",
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
    install_requires=['mcp>=1.0.0', 'astroid>=2.14.2', 'radon>=5.1.0', 'networkx>=3.0', 'chardet>=4.0.0'],
    keywords=["mseep"] + [],
)
