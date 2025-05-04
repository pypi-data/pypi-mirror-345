
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-gemini-image-generator",
    version="0.1.0",
    description="",
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
    install_requires=['fastmcp>=0.4.1', 'google>=3.0.0', 'google-genai>=1.7.0', 'pillow>=11.1.0'],
    keywords=["mseep"] + ['http', 'mcp', 'llm', 'automation'],
)
