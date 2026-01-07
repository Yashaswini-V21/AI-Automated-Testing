"""
Smart Element Finder Module
Provides robust element finding with multiple fallback strategies
"""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import logging
import time
from typing import Optional, List


logger = logging.getLogger(__name__)


class ElementNotFoundError(Exception):
    """Custom exception for element not found after all strategies"""
    pass


def find_element_robust(page: Page, 
                       primary_selector: str,
                       fallback_selectors: Optional[List[str]] = None,
                       timeout: int = 10000,
                       screenshot_on_failure: bool = True,
                       screenshot_path: str = "static/screenshots/element_not_found.png") -> Optional[any]:
    """
    Robust element finder with multiple fallback strategies
    
    Strategies:
    1. Try CSS selector
    2. Try XPath selector  
    3. Try text content matching
    4. Scroll page and retry steps 1-3
    5. Take screenshot and raise exception
    
    Args:
        page: Playwright page object
        primary_selector: Primary CSS selector to try first
        fallback_selectors: Optional list of fallback selectors (CSS or XPath)
        timeout: Maximum wait time in milliseconds (default: 10000)
        screenshot_on_failure: Whether to take screenshot on failure
        screenshot_path: Path to save screenshot
        
    Returns:
        Element locator if found, None if not found
        
    Raises:
        ElementNotFoundError: If element not found after all strategies
    """
    
    strategies_tried = []
    start_time = time.time()
    timeout_seconds = timeout / 1000
    
    # Strategy 1: Try primary CSS selector
    try:
        logger.info(f"Strategy 1: Trying CSS selector: {primary_selector}")
        element = page.locator(primary_selector)
        element.wait_for(timeout=timeout, state='visible')
        logger.info(f"✓ Found element using CSS selector: {primary_selector}")
        return element
    except (PlaywrightTimeoutError, Exception) as e:
        strategies_tried.append(f"CSS selector '{primary_selector}': {type(e).__name__}")
        logger.warning(f"Strategy 1 failed: {type(e).__name__}")
    
    # Check if we still have time
    elapsed = time.time() - start_time
    if elapsed >= timeout_seconds:
        logger.error("Timeout reached before trying other strategies")
        if screenshot_on_failure:
            _take_screenshot(page, screenshot_path)
        raise ElementNotFoundError(f"Element not found. Strategies tried: {strategies_tried}")
    
    # Strategy 2: Try fallback selectors (CSS or XPath)
    if fallback_selectors:
        for selector in fallback_selectors:
            if elapsed >= timeout_seconds:
                break
                
            try:
                logger.info(f"Strategy 2: Trying fallback selector: {selector}")
                
                # Detect if XPath or CSS
                if selector.startswith('//') or selector.startswith('(//'):
                    element = page.locator(f"xpath={selector}")
                else:
                    element = page.locator(selector)
                
                remaining_timeout = int((timeout_seconds - elapsed) * 1000)
                element.wait_for(timeout=max(1000, remaining_timeout), state='visible')
                logger.info(f"✓ Found element using fallback selector: {selector}")
                return element
            except (PlaywrightTimeoutError, Exception) as e:
                strategies_tried.append(f"Fallback '{selector}': {type(e).__name__}")
                logger.warning(f"Strategy 2 failed for {selector}: {type(e).__name__}")
            
            elapsed = time.time() - start_time
    
    # Strategy 3: Try finding by text content
    if elapsed < timeout_seconds:
        try:
            logger.info(f"Strategy 3: Trying to find by text content")
            # Extract text if selector contains text
            text_to_find = primary_selector.split('text=')[-1].strip('"').strip("'") if 'text=' in primary_selector else None
            
            if text_to_find:
                element = page.get_by_text(text_to_find, exact=False)
                remaining_timeout = int((timeout_seconds - elapsed) * 1000)
                element.wait_for(timeout=max(1000, remaining_timeout), state='visible')
                logger.info(f"✓ Found element by text: {text_to_find}")
                return element
        except (PlaywrightTimeoutError, Exception) as e:
            strategies_tried.append(f"Text content search: {type(e).__name__}")
            logger.warning(f"Strategy 3 failed: {type(e).__name__}")
        
        elapsed = time.time() - start_time
    
    # Strategy 4: Scroll page and retry
    if elapsed < timeout_seconds:
        try:
            logger.info("Strategy 4: Scrolling page and retrying")
            
            # Scroll down the page in steps
            for scroll_step in range(3):
                page.evaluate(f"window.scrollBy(0, {300 * (scroll_step + 1)})")
                page.wait_for_timeout(500)
                
                # Retry primary selector after scroll
                try:
                    element = page.locator(primary_selector)
                    element.wait_for(timeout=2000, state='visible')
                    logger.info(f"✓ Found element after scrolling: {primary_selector}")
                    return element
                except:
                    continue
            
            strategies_tried.append("Scroll and retry: Element not visible after scrolling")
        except Exception as e:
            strategies_tried.append(f"Scroll strategy: {type(e).__name__}")
            logger.warning(f"Strategy 4 failed: {type(e).__name__}")
    
    # Strategy 5: All strategies failed - take screenshot and raise exception
    logger.error(f"All strategies failed to find element")
    
    if screenshot_on_failure:
        screenshot_path = _take_screenshot(page, screenshot_path)
        logger.info(f"Screenshot saved to: {screenshot_path}")
    
    error_msg = f"Element not found after trying all strategies.\nStrategies attempted:\n"
    for i, strategy in enumerate(strategies_tried, 1):
        error_msg += f"  {i}. {strategy}\n"
    
    raise ElementNotFoundError(error_msg)


def _take_screenshot(page: Page, path: str) -> str:
    """Take a screenshot and return the path"""
    try:
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        page.screenshot(path=path, full_page=True)
        return path
    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")
        return None


# Convenience functions for common patterns
def find_button_robust(page: Page, text: str, timeout: int = 10000):
    """Find button by text with fallback strategies"""
    return find_element_robust(
        page,
        f"button:has-text('{text}')",
        fallback_selectors=[
            f"input[type='button'][value*='{text}']",
            f"input[type='submit'][value*='{text}']",
            f"a:has-text('{text}')",
            f"//*[contains(text(), '{text}')]"
        ],
        timeout=timeout
    )


def find_input_robust(page: Page, name: str = None, placeholder: str = None, timeout: int = 10000):
    """Find input field by name or placeholder with fallback strategies"""
    primary = f"input[name='{name}']" if name else f"input[placeholder*='{placeholder}']"
    fallbacks = []
    
    if name:
        fallbacks.extend([
            f"input#{name}",
            f"textarea[name='{name}']",
            f"//input[@name='{name}']"
        ])
    
    if placeholder:
        fallbacks.extend([
            f"textarea[placeholder*='{placeholder}']",
            f"//input[@placeholder='{placeholder}']"
        ])
    
    return find_element_robust(page, primary, fallback_selectors=fallbacks, timeout=timeout)


def find_link_robust(page: Page, text: str, timeout: int = 10000):
    """Find link by text with fallback strategies"""
    return find_element_robust(
        page,
        f"a:has-text('{text}')",
        fallback_selectors=[
            f"//a[contains(text(), '{text}')]",
            f"[href]:has-text('{text}')"
        ],
        timeout=timeout
    )
