from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="playwright-mcp-server",
    version="0.1.0",
    author="HA",
    author_email="ha30.coding1@gmail.com",
    description="MCP server exposing Playwright browser automation capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/playwright-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright",
        "mcp",  
        "asyncio",
        "uv",
        "mcp[cli]",
    ],
    entry_points={
        "console_scripts": [
            "playwright-mcp-server=playwright_mcp_server:run_server",
        ],
    },
)