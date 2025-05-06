
from setuptools import setup, find_packages

setup(
    name="mseep-qiniu-mcp-server",
    version="1.2.1",
    description="A MCP server project of Qiniu.",
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
    install_requires=['aioboto3>=13.2.0', 'fastjsonschema>=2.21.1', 'httpx>=0.28.1', 'mcp[cli]>=1.0.0', 'openai>=1.66.3', 'pip>=25.0.1', 'python-dotenv>=1.0.1', 'qiniu>=7.16.0'],
    keywords=["mseep"] + ['qiniu', 'mcp', 'llm'],
)
