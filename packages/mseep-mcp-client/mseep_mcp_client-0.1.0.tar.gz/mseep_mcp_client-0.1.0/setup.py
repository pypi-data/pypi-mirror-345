
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-client",
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
    install_requires=['aiohttp>=3.11.16', 'boto3>=1.37.29', 'botocore>=1.37.29', 'fastapi>=0.115.6', 'mcp>=1.6.0', 'openai>=1.75.0', 'pandas>=2.2.3', 'python-dotenv>=1.0.1', 'requests>=2.32.3', 'streamlit>=1.41.1', 'streamlit-cookies-controller>=0.0.4', 'streamlit-local-storage>=0.0.25', 'tzdata>=2024.2', 'uvicorn>=0.34.0'],
    keywords=["mseep"] + [],
)
