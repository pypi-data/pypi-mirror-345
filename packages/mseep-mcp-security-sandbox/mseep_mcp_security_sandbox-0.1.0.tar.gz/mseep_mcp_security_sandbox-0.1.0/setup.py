
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-security-sandbox",
    version="0.1.0",
    description="An experimental sandbox and a lab to explore mcp hosts, mcp clients, and mcp servers. Perform attacks agaisnt mcp servers and abuse LLMs",
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
    install_requires=['bs4>=0.0.2', 'html2text>=2024.2.26', 'mcp[cli]>=1.6.0', 'ollama>=0.4.7', 'pydantic-ai>=0.0.55', 'requests>=2.32.3', 'streamlit>=1.44.1', 'torch>=2.6.0'],
    keywords=["mseep"] + [],
)
