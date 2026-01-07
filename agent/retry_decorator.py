"""
Retry Mechanism Module
Provides retry decorator with exponential backoff for test functions
"""

import time
import functools
from typing import Callable, Type
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, initial_wait: float = 2.0, 
                     exceptions: tuple = (Exception,)):
    """
    Decorator that retries a function with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_wait: Initial wait time in seconds (default: 2.0)
        exceptions: Tuple of exception types to catch (default: all exceptions)
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @retry_on_failure(max_retries=3, initial_wait=2.0)
        def my_test_function():
            # Test code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait_time = initial_wait
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Try to execute the function
                    result = func(*args, **kwargs)
                    
                    # If we get here, function succeeded
                    if attempt > 0:
                        logger.info(f"✓ {func.__name__} succeeded on retry attempt {attempt}")
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"⚠ {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}: "
                            f"{type(e).__name__}: {str(e)}"
                        )
                        logger.info(f"  Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                        wait_time *= 2  # Exponential backoff
                    else:
                        logger.error(
                            f"✗ {func.__name__} failed after {max_retries + 1} attempts"
                        )
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


def retry_playwright_action(max_retries: int = 3, initial_wait: float = 2.0):
    """
    Specialized retry decorator for Playwright/Selenium actions
    Catches common test automation exceptions
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_wait: Initial wait time in seconds (default: 2.0)
    """
    # Common exceptions in browser automation
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import Error as PlaywrightError
    
    exceptions_to_catch = (
        PlaywrightTimeoutError,
        PlaywrightError,
        TimeoutError,
        Exception
    )
    
    return retry_on_failure(
        max_retries=max_retries,
        initial_wait=initial_wait,
        exceptions=exceptions_to_catch
    )


# Example usage functions
if __name__ == "__main__":
    # Example 1: Basic retry
    @retry_on_failure(max_retries=3, initial_wait=1.0)
    def flaky_function():
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise Exception("Random failure!")
        return "Success!"
    
    # Example 2: Playwright action retry
    @retry_playwright_action(max_retries=3, initial_wait=2.0)
    def click_element(page, selector):
        """Simulated Playwright click action"""
        page.click(selector, timeout=5000)
        return True
    
    # Test the retry mechanism
    print("Testing retry mechanism...")
    try:
        result = flaky_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed: {e}")
