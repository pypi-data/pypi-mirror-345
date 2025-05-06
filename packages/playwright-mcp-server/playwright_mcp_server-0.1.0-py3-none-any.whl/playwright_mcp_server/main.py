import sys
import traceback
from mcp.server.fastmcp import FastMCP
from playwrightHandler import PlaywrightHandler as ph, logger

mcp = FastMCP('playwright-python-server')

logger.info("Starting MCP Playwright server")

@mcp.tool()
def launch_page(webPageURL: str) -> str:
    """
    Launch a new page with the given URL and return the page id.
    """
    logger.info(f"Tool launch_page called with URL: {webPageURL}")
    try:
        page_id = ph.launch_page(webPageURL)
        logger.info(f"Tool launch_page successful, returned page_id: {page_id}")
        return page_id
    except Exception as e:
        logger.error(f"Error executing tool launch_page: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error: {str(e)}"

@mcp.tool()
def close_page(page_id: str) -> bool:
    """
    Close the page with the given id.
    """
    logger.info(f"Tool close_page called with page_id: {page_id}")
    try:
        ph.close_page(page_id)
        logger.info(f"Page {page_id} closed successfully")
        return True
    except Exception as e:
        logger.error(f"Error executing tool close_page: {str(e)}")
        logger.error(traceback.format_exc())
        return False

@mcp.tool()
def take_screenshot(page_id: str, screenshotPath: str) -> bool:
    """
    Take a screenshot of the page with the given id and save it to the given file path.
    Runs with a 20 second timeout to prevent hanging.
    """
    logger.info(f"Tool take_screenshot called with page_id: {page_id}, path: {screenshotPath}")
    try:
        # Add timeout handling at the tool level
        import threading
        import time
        
        result = {"success": False, "error": None}
        
        def screenshot_thread():
            try:
                ph.take_screenshot(page_id, screenshotPath)
                result["success"] = True
            except Exception as e:
                result["error"] = str(e)
        
        # Start screenshot in thread with timeout
        thread = threading.Thread(target=screenshot_thread)
        thread.daemon = True
        thread.start()
        
        # Wait with timeout
        thread.join(timeout=20)
        
        if thread.is_alive():
            logger.error(f"Screenshot operation timed out after 20 seconds")
            return False
        
        if result["success"]:
            logger.info(f"Screenshot of page {page_id} saved to {screenshotPath}")
            return True
        else:
            logger.error(f"Error in screenshot thread: {result['error']}")
            return False
            
    except Exception as e:
        logger.error(f"Error executing tool take_screenshot: {str(e)}")
        logger.error(traceback.format_exc())
        return False

@mcp.tool()
def cleanup() -> bool:
    """
    Clean up all Playwright resources.
    """
    logger.info("Tool cleanup called")
    try:
        ph.cleanup()
        logger.info("Cleanup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error executing tool cleanup: {str(e)}")
        logger.error(traceback.format_exc())
        return False

@mcp.tool()
def get_active_pages() -> dict:
    """
    Get information about all active pages.
    """
    logger.info("Tool get_active_pages called")
    try:
        pages_info = {page_id: str(page) for page_id, page in ph._pages.items()}
        logger.info(f"Active pages: {len(pages_info)}")
        logger.debug(f"Active pages info: {pages_info}")
        return pages_info
    except Exception as e:
        logger.error(f"Error executing tool get_active_pages: {str(e)}")
        logger.error(traceback.format_exc())
        return {}

# Add new tool to get current page title
@mcp.tool()
def get_page_title(page_id: str) -> str:
    """
    Get the title of the page with the given id.
    """
    logger.info(f"Tool get_page_title called with page_id: {page_id}")
    try:
        # Helper function to get title asynchronously
        async def get_title_async(page):
            return await page.title()
        
        with ph._lock:
            page = ph._pages.get(page_id, None)
            if page is None:
                error_msg = f"Page with id {page_id} not found"
                logger.error(error_msg)
                return f"Error: {error_msg}"
        
        title = ph._run_async(get_title_async(page))
        logger.info(f"Got title for page {page_id}: {title}")
        return title
    except Exception as e:
        logger.error(f"Error executing tool get_page_title: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error: {str(e)}"

if __name__ == "__main__":
    try:
        logger.info("Starting MCP server")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopping due to keyboard interrupt")
        ph.cleanup()
        logger.info("Exiting")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        logger.error(traceback.format_exc())
        ph.cleanup()
        logger.info("Exiting with error")
        sys.exit(1)