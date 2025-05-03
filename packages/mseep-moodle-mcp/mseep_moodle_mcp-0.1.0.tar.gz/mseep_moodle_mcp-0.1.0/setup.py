
from setuptools import setup, find_packages

setup(
    name="mseep-moodle-mcp",
    version="0.1.0",
    description="A Model Context Protocol (MCP) server implementation that provides capabilities to interact with Moodle LMS.",
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
    install_requires=['glom>=24.11.0', 'mcp[cli]>=1.6.0', 'python-dotenv>=1.1.0', 'requests>=2.32.3'],
    keywords=["mseep"] + [],
)
