
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-any-openapi",
    version="0.1.0",
    description="MCP server for Any OpenAPI resources",
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
    install_requires=['mcp', 'pydantic', 'requests', 'pytz', 'pyyaml', 'faiss-cpu', 'numpy', 'sentence-transformers', 'fastapi', 'uvicorn', 'huggingface-hub'],
    keywords=["mseep"] + [],
)
