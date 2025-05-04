
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-telegram",
    version="0.1.2",
    description="MCP server to work with Telegram through MTProto",
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
    install_requires=['mcp>=1.1.0', 'telethon>=1.23.0', 'pydantic>=2.0.0', 'pydantic-settings>=2.6.0', 'typer>=0.15.0', 'xdg-base-dirs>=6.0.0'],
    keywords=["mseep"] + [],
)
