
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-mistral-ocr",
    version="1.0.0",
    description="MCP Server for OCR processing using Mistral AI",
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
    install_requires=['mistralai>=1.5.1', 'aiohttp', 'mcp[cli]', 'python-dotenv'],
    keywords=["mseep"] + [],
)
