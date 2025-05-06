import os
import unittest
import tempfile
from playwright_mcp_server import PlaywrightHandler

class TestPlaywrightHandler(unittest.TestCase):
    def setUp(self):
        # This will be called before each test
        PlaywrightHandler._ensure_event_loop()
    
    def tearDown(self):
        # This will be called after each test
        PlaywrightHandler.cleanup()
    
    def test_launch_page(self):
        # Test that we can launch a page successfully
        page_id = PlaywrightHandler.launch_page("https://example.com")
        self.assertIsNotNone(page_id)
        self.assertIn(page_id, PlaywrightHandler._pages)
    
    def test_take_screenshot(self):
        # Test that we can take a screenshot
        page_id = PlaywrightHandler.launch_page("https://example.com")
        
        # Create a temporary file for the screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            screenshot_path = tmp.name
        
        try:
            # Take screenshot
            PlaywrightHandler.take_screenshot(page_id, screenshot_path)
            
            # Check that the file exists and is not empty
            self.assertTrue(os.path.exists(screenshot_path))
            self.assertGreater(os.path.getsize(screenshot_path), 0)
        finally:
            # Clean up
            if os.path.exists(screenshot_path):
                os.unlink(screenshot_path)
    
    def test_close_page(self):
        # Test that we can close a page
        page_id = PlaywrightHandler.launch_page("https://example.com")
        self.assertIn(page_id, PlaywrightHandler._pages)
        
        PlaywrightHandler.close_page(page_id)
        self.assertNotIn(page_id, PlaywrightHandler._pages)

if __name__ == "__main__":
    unittest.main()