"""
Popup Handler Module
Automatically handles common website popups and modals
"""

from playwright.sync_api import Page
import logging
from typing import List, Dict


logger = logging.getLogger(__name__)


def handle_common_popups(page: Page, timeout: int = 5000) -> Dict[str, bool]:
    """
    Automatically handle common website popups
    
    Args:
        page: Playwright page object
        timeout: Timeout for each popup check in milliseconds
        
    Returns:
        Dictionary with handled popup types and success status
    """
    handled_popups = {
        'cookie_consent': False,
        'notification_permission': False,
        'newsletter_modal': False,
        'app_download_prompt': False,
        'chat_widget': False,
        'age_verification': False
    }
    
    logger.info("Checking for common popups...")
    
    # Handle cookie consent banners
    handled_popups['cookie_consent'] = _handle_cookie_consent(page, timeout)
    
    # Handle notification permission popups (browser level)
    handled_popups['notification_permission'] = _handle_notification_permission(page, timeout)
    
    # Handle newsletter signup modals
    handled_popups['newsletter_modal'] = _handle_newsletter_modal(page, timeout)
    
    # Handle app download prompts
    handled_popups['app_download_prompt'] = _handle_app_download(page, timeout)
    
    # Handle chat widgets
    handled_popups['chat_widget'] = _handle_chat_widget(page, timeout)
    
    # Handle age verification
    handled_popups['age_verification'] = _handle_age_verification(page, timeout)
    
    # Log results
    handled_count = sum(1 for v in handled_popups.values() if v)
    if handled_count > 0:
        logger.info(f"✓ Handled {handled_count} popup(s)")
        for popup_type, was_handled in handled_popups.items():
            if was_handled:
                logger.info(f"  - Dismissed {popup_type}")
    else:
        logger.info("No popups detected")
    
    return handled_popups


def _handle_cookie_consent(page: Page, timeout: int) -> bool:
    """Handle cookie consent banners"""
    cookie_selectors = [
        # Common button texts
        'button:has-text("Accept")',
        'button:has-text("Accept all")',
        'button:has-text("Accept All")',
        'button:has-text("Accept cookies")',
        'button:has-text("I agree")',
        'button:has-text("I accept")',
        'button:has-text("Agree")',
        'button:has-text("OK")',
        'button:has-text("Allow")',
        'button:has-text("Allow all")',
        'button:has-text("Got it")',
        'button:has-text("Continue")',
        
        # Common class/ID patterns
        '[id*="cookie"][id*="accept"]',
        '[id*="cookie"][id*="consent"]',
        '[class*="cookie"][class*="accept"]',
        '[class*="cookie"][class*="button"]',
        '[class*="consent"][class*="accept"]',
        
        # Links
        'a:has-text("Accept")',
        'a:has-text("I agree")',
        
        # Specific frameworks
        '.cc-allow',
        '.cc-accept',
        '#cookieAcceptButton',
        '[aria-label*="Accept"]',
        '[aria-label*="cookie"]'
    ]
    
    return _try_click_selectors(page, cookie_selectors, timeout, "cookie consent")


def _handle_notification_permission(page: Page, timeout: int) -> bool:
    """Handle notification permission popups"""
    notification_selectors = [
        'button:has-text("Allow")',
        'button:has-text("Enable")',
        'button:has-text("Yes")',
        'button:has-text("Later")',
        'button:has-text("Not now")',
        'button:has-text("No thanks")',
        'button:has-text("Block")',
        'button:has-text("Dismiss")',
        '[aria-label*="notification"]',
        '[class*="notification"][class*="close"]',
        '[id*="notification"][id*="close"]'
    ]
    
    return _try_click_selectors(page, notification_selectors, timeout, "notification permission")


def _handle_newsletter_modal(page: Page, timeout: int) -> bool:
    """Handle newsletter signup modals"""
    newsletter_selectors = [
        # Close buttons
        'button[aria-label="Close"]',
        'button[aria-label="Close modal"]',
        'button.close',
        '[class*="modal"] button[class*="close"]',
        '[class*="popup"] button[class*="close"]',
        '[class*="newsletter"] button[class*="close"]',
        
        # No thanks / Skip buttons
        'button:has-text("No thanks")',
        'button:has-text("Skip")',
        'button:has-text("Maybe later")',
        'button:has-text("Not interested")',
        'button:has-text("Close")',
        
        # Common close icons
        'button:has-text("×")',
        'button:has-text("✕")',
        '[class*="icon-close"]',
        
        # Overlay clicks (sometimes clicking outside closes modal)
        '[class*="modal-backdrop"]',
        '[class*="overlay"]'
    ]
    
    return _try_click_selectors(page, newsletter_selectors, timeout, "newsletter modal")


def _handle_app_download(page: Page, timeout: int) -> bool:
    """Handle app download prompts"""
    app_selectors = [
        'button:has-text("Continue in browser")',
        'button:has-text("Continue on web")',
        'button:has-text("Not now")',
        'button:has-text("No thanks")',
        'button:has-text("Skip")',
        'button:has-text("Close")',
        'a:has-text("Continue in browser")',
        'a:has-text("Not now")',
        '[class*="app-banner"] button[class*="close"]',
        '[class*="download-app"] button[class*="dismiss"]',
        '[id*="app-banner"] button'
    ]
    
    return _try_click_selectors(page, app_selectors, timeout, "app download prompt")


def _handle_chat_widget(page: Page, timeout: int) -> bool:
    """Handle chat widgets"""
    chat_selectors = [
        # Common chat widget close buttons
        'button[aria-label*="Close chat"]',
        'button[aria-label*="Minimize chat"]',
        '[id*="chat"] button[aria-label*="Close"]',
        '[class*="chat-widget"] button[class*="close"]',
        '[class*="intercom"] button[class*="close"]',
        '[id*="drift"] button[class*="close"]',
        
        # Minimize instead of close
        'button:has-text("Minimize")',
        '[aria-label="Minimize"]'
    ]
    
    return _try_click_selectors(page, chat_selectors, timeout, "chat widget")


def _handle_age_verification(page: Page, timeout: int) -> bool:
    """Handle age verification popups"""
    age_selectors = [
        'button:has-text("Yes")',
        'button:has-text("I am 18")',
        'button:has-text("Enter")',
        'button:has-text("Continue")',
        'button:has-text("I am old enough")',
        '[id*="age"] button:has-text("Yes")',
        '[class*="age-gate"] button',
        '[id*="age-verification"] button'
    ]
    
    return _try_click_selectors(page, age_selectors, timeout, "age verification")


def _try_click_selectors(page: Page, selectors: List[str], timeout: int, 
                         popup_type: str) -> bool:
    """
    Try clicking elements matching the given selectors
    
    Args:
        page: Playwright page object
        selectors: List of CSS selectors to try
        timeout: Timeout in milliseconds
        popup_type: Name of popup type for logging
        
    Returns:
        True if any selector was clicked successfully
    """
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if element.count() > 0 and element.is_visible(timeout=timeout):
                element.click(timeout=timeout)
                logger.info(f"✓ Closed {popup_type} using selector: {selector}")
                page.wait_for_timeout(500)  # Wait for animation
                return True
        except Exception:
            continue
    
    return False


def setup_popup_blocking_context(browser):
    """
    Setup browser context with popup blocking configurations
    
    Args:
        browser: Playwright browser instance
        
    Returns:
        Browser context with popup blocking enabled
    """
    context = browser.new_context(
        # Block notification permissions automatically
        permissions=[],
        
        # Set geolocation to avoid location popups
        geolocation={'latitude': 0, 'longitude': 0},
        
        # User agent to avoid some popups
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    # Grant permission to deny notifications
    context.grant_permissions([])
    
    return context


# Example usage
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = setup_popup_blocking_context(browser)
        page = context.new_page()
        
        page.goto("https://www.example.com")
        
        # Handle popups
        result = handle_common_popups(page)
        print(f"\nHandled popups: {result}")
        
        browser.close()
