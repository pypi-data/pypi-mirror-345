import asyncio 
from playwright.async_api import async_playwright, Page
import threading
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S', filename='mcp.log', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Add console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

class PlaywrightHandler:
    # Store active playwright instances and pages
    _playwright = None
    _pages = {}
    _lock = threading.Lock()
    
    # Thread pool for running async operations
    _executor = ThreadPoolExecutor(max_workers=4)
    
    # Shared event loop for async operations
    _loop = None
    _loop_thread = None

    @staticmethod
    def _ensure_event_loop():
        """
        Ensure that a shared event loop is running in a background thread
        """
        with PlaywrightHandler._lock:
            if PlaywrightHandler._loop is None:
                def run_event_loop():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    PlaywrightHandler._loop = loop
                    logger.debug("Started shared event loop")
                    loop.run_forever()
                
                PlaywrightHandler._loop_thread = threading.Thread(
                    target=run_event_loop, daemon=True)
                PlaywrightHandler._loop_thread.start()
                # Give time for loop to initialize
                time.sleep(0.1)

    @staticmethod
    def _run_async(coro):
        """
        Run a coroutine in the shared event loop and return its result
        """
        PlaywrightHandler._ensure_event_loop()
        future = asyncio.run_coroutine_threadsafe(coro, PlaywrightHandler._loop)
        return future.result()

    @staticmethod
    async def _get_playwright():
        """
        Get or create a playwright instance.
        """
        logger.debug("Getting playwright instance")
        if PlaywrightHandler._playwright is None:
            logger.info("Initializing new playwright instance")
            PlaywrightHandler._playwright = await async_playwright().start()
            logger.debug("Playwright instance started successfully")
        return PlaywrightHandler._playwright
    
    @staticmethod
    async def launch_page_async(webPageURL: str) -> Page:
        """
        Launch a new browser page and navigate to the given URL.
        Returns the page object.
        """
        logger.info(f"Launching page with URL: {webPageURL}")
        try:
            playwright = await PlaywrightHandler._get_playwright()
            logger.debug("Starting browser")
            browser = await playwright.chromium.launch(headless=True)  # Changed to headless mode for better performance
            logger.debug("Creating browser context")
            context = await browser.new_context()
            logger.debug("Creating new page")
            page = await context.new_page()
            logger.info(f"Navigating to {webPageURL}")
            await page.goto(webPageURL)
            logger.info(f"Successfully navigated to {webPageURL}")
            return page
        except Exception as e:
            logger.error(f"Error in launch_page_async: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def launch_page(webPageURL: str) -> str:
        """
        Synchronous wrapper for launch_page_async.
        Returns the page ID as a string.
        """
        logger.info(f"Running launch_page with URL: {webPageURL}")
        
        # Ensure URL has proper format
        if not webPageURL.startswith(("http://", "https://")):
            original_url = webPageURL
            webPageURL = "https://" + webPageURL.lstrip("/")
            logger.info(f"URL modified from {original_url} to: {webPageURL}")
        
        try:
            page = PlaywrightHandler._run_async(
                PlaywrightHandler.launch_page_async(webPageURL))
            
            page_id = str(id(page))
            with PlaywrightHandler._lock:
                PlaywrightHandler._pages[page_id] = page
            
            logger.info(f"Page launched successfully with ID: {page_id}")
            return page_id
        except Exception as e:
            error_msg = f"Failed to launch page: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    @staticmethod
    async def close_page_async(page: Page) -> None:
        """
        Close the given page and its browser context.
        """
        try:
            logger.debug(f"Closing page with object ID: {id(page)}")
            context = page.context
            browser = context.browser
            
            logger.debug("Closing page")
            await page.close()
            
            logger.debug("Closing context")
            await context.close()
            
            logger.debug("Closing browser")
            await browser.close()
            
            logger.info("Page, context, and browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing page: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def close_page(page_id: str) -> None:
        """
        Synchronous wrapper for close_page_async.
        """
        logger.info(f"Closing page with ID: {page_id}")
        
        with PlaywrightHandler._lock:
            page = PlaywrightHandler._pages.get(page_id, None)
            if page is None:
                error_msg = f"Page with id {page_id} not found"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Remove page from registry before closing to prevent race conditions
            del PlaywrightHandler._pages[page_id]
        
        try:
            PlaywrightHandler._run_async(
                PlaywrightHandler.close_page_async(page))
            logger.info(f"Page {page_id} closed successfully")
        except Exception as e:
            error_msg = f"Failed to close page: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    @staticmethod
    async def take_screenshot_async(page: Page, screenshotPath: str) -> None:
        """
        Take a screenshot of the given page and save it to the given file path.
        """
        try:
            logger.debug(f"Taking screenshot of page {id(page)} to path: {screenshotPath}")
            # Set a timeout for screenshot operation
            await asyncio.wait_for(
                page.screenshot(
                    path=screenshotPath,
                    full_page=False,  # Only capture viewport, not full page
                    timeout=10000     # 10 second timeout
                ), 
                timeout=15.0  # Overall timeout
            )
            logger.info(f"Screenshot saved successfully to {screenshotPath}")
        except asyncio.TimeoutError:
            logger.error("Screenshot operation timed out")
            raise TimeoutError("Screenshot operation timed out after 15 seconds")
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def take_screenshot(page_id: str, screenshotPath: str) -> None:
        """
        Synchronous wrapper for take_screenshot_async.
        """
        logger.info(f"Taking screenshot of page {page_id} to path: {screenshotPath}")
        
        with PlaywrightHandler._lock:
            page = PlaywrightHandler._pages.get(page_id, None)
            if page is None:
                error_msg = f"Page with id {page_id} not found"
                logger.error(error_msg)
                raise ValueError(error_msg)
            elif page.is_closed():
                error_msg = f"Page with id {page_id} is closed"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Using a separate lock for the screenshot operation to avoid blocking other operations
        try:
            PlaywrightHandler._run_async(
                PlaywrightHandler.take_screenshot_async(page, screenshotPath))
            logger.debug(f"Screenshot of page {page_id} completed")
        except Exception as e:
            error_msg = f"Failed to take screenshot: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    @staticmethod
    async def _cleanup_async() -> None:
        """
        Cleanup the playwright instance asynchronously.
        """
        if PlaywrightHandler._playwright:
            logger.debug("Stopping playwright instance")
            try:
                await PlaywrightHandler._playwright.stop()
                logger.info("Playwright instance stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping playwright: {str(e)}", exc_info=True)
            finally:
                PlaywrightHandler._playwright = None
    
    @staticmethod
    def cleanup() -> None:
        """
        Cleanup the playwright instance and all browsers.
        """
        logger.info("Starting cleanup of all PlaywrightHandler resources")
        
        # Clear pages dictionary first
        with PlaywrightHandler._lock:
            page_count = len(PlaywrightHandler._pages)
            PlaywrightHandler._pages.clear()
            logger.info(f"Cleared {page_count} page references")
        
        try:
            # Cleanup playwright
            if PlaywrightHandler._loop is not None:
                PlaywrightHandler._run_async(PlaywrightHandler._cleanup_async())
            
            # Shutdown event loop
            if PlaywrightHandler._loop is not None:
                PlaywrightHandler._loop.call_soon_threadsafe(PlaywrightHandler._loop.stop)
                if PlaywrightHandler._loop_thread is not None:
                    PlaywrightHandler._loop_thread.join(timeout=5.0)
                PlaywrightHandler._loop = None
                PlaywrightHandler._loop_thread = None
            
            # Shutdown thread pool
            PlaywrightHandler._executor.shutdown(wait=True)
            
            logger.info("Cleanup completed successfully")
        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)