from setuptools import setup, find_packages

setup(
    name="ttmoc",
    version="0.1.1",
    packages=find_packages(include=["ttmoc", "ttmoc.*"]),
    install_requires=[
        "requests",
        "pydantic",
        "python-dotenv",
        "mcp",
        "httpx",
        "azure-identity",
        "click"
    ],
    entry_points={
        "console_scripts": [
            "ttmoc=ttmoc.cli:main",
        ],
    },
    python_requires=">=3.8",
    description="Talk To My Org Chart - MCP Server for employee directory lookup",
    author="ttthree",
    author_email="ttthree@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
