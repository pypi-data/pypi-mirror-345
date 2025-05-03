
from setuptools import setup, find_packages

setup(
    name="mseep-axiom-mcp",
    version="0.1.3",
    description="🚀 MCP framework that unlocks truly scalable AI systems with zero friction",
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
    install_requires=['mcp>=1.0.0,<2.0.0', 'pydantic-settings>=2.6.1', 'pydantic>=2.5.3,<3.0.0', 'typer>=0.9.0', 'python-dotenv>=1.0.1', 'aiofiles>=23.2.1', 'aiohttp>=3.8.0', 'cachetools>=5.3.2', 'aiosqlite>=0.21.0', 'opentelemetry-api>=1.21.0', 'opentelemetry-sdk>=1.21.0', 'watchdog>=6.0.0', 'jsonschema>=4.23.0'],
    keywords=["mseep"] + ['ai', 'mcp', 'model-context-protocol', 'llm', 'machine-learning', 'axiom'],
)
