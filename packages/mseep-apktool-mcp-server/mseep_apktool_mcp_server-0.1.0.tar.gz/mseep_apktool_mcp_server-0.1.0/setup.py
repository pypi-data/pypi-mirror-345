
from setuptools import setup, find_packages

setup(
    name="mseep-apktool-mcp-server",
    version="0.1.0",
    description="Add your description here",
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
    install_requires=['fastmcp>=2.2.0', 'logging>=0.4.9.6'],
    keywords=["mseep"] + [],
)
