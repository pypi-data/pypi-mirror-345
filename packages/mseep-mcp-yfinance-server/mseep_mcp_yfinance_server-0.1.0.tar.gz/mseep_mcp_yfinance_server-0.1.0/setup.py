
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-yfinance-server",
    version="0.1.0",
    description="A Yfinance Server project",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.6.0', 'yfinance>=0.2.55', 'pandas>=2.0.0', 'numpy>=1.24.0', 'typing-extensions>=4.5.0', 'textblob>=0.19.0', 'matplotlib>=3.10.1', 'ipython>=9.1.0'],
    keywords=["mseep"] + [],
)
