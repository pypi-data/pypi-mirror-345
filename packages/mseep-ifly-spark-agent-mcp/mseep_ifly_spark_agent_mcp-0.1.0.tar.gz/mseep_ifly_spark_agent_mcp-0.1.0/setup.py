
from setuptools import setup, find_packages

setup(
    name="mseep-ifly-spark-agent-mcp",
    version="0.1.0",
    description="This is a simple example of using MCP Server to invoke the task chain of the iFlytek SparkAgent Platform.",
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
    install_requires=['httpx>=0.28.1', 'requests>=2.32.3', 'mcp>=1.6.0', 'websocket-client==1.8.0', 'python-dotenv==1.0.1', 'anyio>=4.5', 'click>=8.1.0'],
    keywords=["mseep"] + ['mcp', 'llm', 'automation', 'web', 'sparkagent'],
)
