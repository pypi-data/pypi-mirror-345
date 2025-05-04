
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-sleep",
    version="0.1.1",
    description="Tool that allows you to wait a certain time to continue the execution of an agent.",
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
    install_requires=['click>=8.1.8', 'dotenv>=0.9.9', 'mcp>=1.5.0'],
    keywords=["mseep"] + [],
)
