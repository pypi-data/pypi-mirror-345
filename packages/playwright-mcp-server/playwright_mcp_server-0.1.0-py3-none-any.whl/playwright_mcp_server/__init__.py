"""
Playwright MCP Server - A microservice for controlling web browsers via MCP protocol.

This package provides a server that exposes Playwright browser automation capabilities
through the MCP (Microservice Communication Protocol) interface.
"""

import logging
from .playwrightHandler import PlaywrightHandler, logger
from .main import launch_page, close_page, take_screenshot, cleanup, get_active_pages, get_page_title

__version__ = '0.1.0'
__all__ = [
    'PlaywrightHandler',
    'launch_page',
    'close_page',
    'take_screenshot',
    'cleanup',
    'get_active_pages',
    'get_page_title',
    'logger',
    'run_server'
]

def run_server():
    """
    Run the MCP Playwright server.
    This is the main entry point for the package when used as a command line application.
    """
    from .main import mcp
    logging.info("Starting MCP Playwright server via package entry point")
    try:
        mcp.run()
    except KeyboardInterrupt:
        logging.info("Server stopping due to keyboard interrupt")
        PlaywrightHandler.cleanup()
    except Exception as e:
        logging.error(f"Error running server: {str(e)}")
        PlaywrightHandler.cleanup()
        raise