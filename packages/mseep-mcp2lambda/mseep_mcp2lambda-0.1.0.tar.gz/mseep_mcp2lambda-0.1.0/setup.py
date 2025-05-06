
from setuptools import setup, find_packages

setup(
    name="mseep-mcp2lambda",
    version="0.1.0",
    description="MCP2Lambda - A bridge between MCP clients and AWS Lambda functions",
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
    install_requires=['boto3>=1.37.0', 'mcp==1.3.0'],
    keywords=["mseep"] + [],
)
