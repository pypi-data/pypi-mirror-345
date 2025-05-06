# Playwright MCP Server

A microservice that exposes Playwright browser automation capabilities through the MCP (Microservice Communication Protocol) interface.

## Features

- Launch browser pages with specified URLs
- Take screenshots of web pages
- Manage multiple browser instances
- Clean browser resources efficiently
- Get page titles and other information

## Installation

### From PyPI

```bash
pip install playwright-mcp-server
```

### From Source

```bash
git clone https://github.com/yourusername/playwright-mcp-server.git
cd playwright-mcp-server
pip install -e .
```

After installation, you'll need to install the Playwright browser binaries:

```bash
playwright install
```

## Usage

### As a Command Line Tool

After installation, you can run the server directly from the command line:

```bash
playwright-mcp-server
```

### As a Library

```python
from playwright_mcp_server import run_server

# Start the server
run_server()
```

## Available Tools

The MCP server exposes the following tools:

- **launch_page(webPageURL)**: Launch a new page with the given URL
- **close_page(page_id)**: Close the page with the given ID
- **take_screenshot(page_id, screenshotPath)**: Take a screenshot of the page
- **get_page_title(page_id)**: Get the title of the page
- **get_active_pages()**: Get information about all active pages
- **cleanup()**: Clean up all Playwright resources

## Project Structure

```
playwright-mcp-server/
├── playwright_mcp_server/
│   ├── __init__.py
│   ├── main.py
│   └── playwrightHandler.py
├── setup.py
└── README.md
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


<!-- playwright_mcp_server/
├── playwright_mcp_server/
│   ├── __init__.py         # Package initialization
│   ├── main.py             # MCP server implementation
│   └── playwrightHandler.py # Playwright interface
├── tests/
│   ├── __init__.py
│   └── test_server.py      # Test cases for server functionality
├── setup.py                # Package configuration
├── MANIFEST.in             # Additional files to include
├── README.md               # Project documentation
└── LICENSE                 # License file -->