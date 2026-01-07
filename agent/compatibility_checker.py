"""
Website Compatibility Checker Module
Checks website compatibility and calculates robustness score
"""

from playwright.sync_api import sync_playwright, Page
from typing import Dict, List
import logging


logger = logging.getLogger(__name__)


def check_website_compatibility(url: str, browser_type: str = 'chromium', 
                                headless: bool = True) -> Dict:
    """
    Check website compatibility and detect potential issues
    
    Args:
        url: URL of the website to check
        browser_type: Browser to use (chromium, firefox, webkit)
        headless: Run in headless mode
        
    Returns:
        Dictionary with compatibility report including warnings and robustness score
    """
    report = {
        'url': url,
        'status_code': None,
        'is_accessible': False,
        'has_captcha': False,
        'requires_login': False,
        'uses_heavy_javascript': False,
        'uses_react': False,
        'uses_angular': False,
        'uses_vue': False,
        'has_iframes': False,
        'has_shadow_dom': False,
        'warnings': [],
        'suggestions': [],
        'robustness_score': 0
    }
    
    with sync_playwright() as p:
        try:
            # Launch browser
            if browser_type == 'firefox':
                browser = p.firefox.launch(headless=headless)
            elif browser_type == 'webkit':
                browser = p.webkit.launch(headless=headless)
            else:
                browser = p.chromium.launch(headless=headless)
            
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate to the page and capture response
            response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Check status code
            if response:
                report['status_code'] = response.status
                report['is_accessible'] = 200 <= response.status < 300
                
                if not report['is_accessible']:
                    report['warnings'].append(f"Non-successful status code: {response.status}")
            
            # Wait for page to load
            page.wait_for_load_state('networkidle', timeout=10000)
            
            # Check for CAPTCHA
            report['has_captcha'] = _check_for_captcha(page)
            if report['has_captcha']:
                report['warnings'].append("CAPTCHA detected - automation may be blocked")
                report['suggestions'].append("Consider using CAPTCHA solving services or manual intervention")
            
            # Check if login is required
            report['requires_login'] = _check_for_login(page)
            if report['requires_login']:
                report['warnings'].append("Login form detected - may require authentication")
                report['suggestions'].append("Provide login credentials or handle authentication")
            
            # Check for JavaScript frameworks
            report['uses_react'] = _check_for_react(page)
            report['uses_angular'] = _check_for_angular(page)
            report['uses_vue'] = _check_for_vue(page)
            
            report['uses_heavy_javascript'] = any([
                report['uses_react'],
                report['uses_angular'],
                report['uses_vue']
            ])
            
            if report['uses_heavy_javascript']:
                frameworks = []
                if report['uses_react']:
                    frameworks.append("React")
                if report['uses_angular']:
                    frameworks.append("Angular")
                if report['uses_vue']:
                    frameworks.append("Vue")
                
                report['warnings'].append(f"Heavy JavaScript framework detected: {', '.join(frameworks)}")
                report['suggestions'].append("Use longer wait times and wait for network idle")
            
            # Check for iframes
            report['has_iframes'] = _check_for_iframes(page)
            if report['has_iframes']:
                report['warnings'].append("Iframes detected - may require special handling")
                report['suggestions'].append("Use frame_locator() to interact with iframe content")
            
            # Check for Shadow DOM
            report['has_shadow_dom'] = _check_for_shadow_dom(page)
            if report['has_shadow_dom']:
                report['warnings'].append("Shadow DOM detected - standard selectors may not work")
                report['suggestions'].append("Use Playwright's shadow DOM piercing or special selectors")
            
            # Calculate robustness score (0-100)
            report['robustness_score'] = _calculate_robustness_score(report)
            
            browser.close()
            
        except Exception as e:
            report['warnings'].append(f"Error during compatibility check: {str(e)}")
            report['suggestions'].append("Website may be unstable or unreachable")
            logger.error(f"Compatibility check failed: {e}")
    
    return report


def _check_for_captcha(page: Page) -> bool:
    """Check if CAPTCHA is present on the page"""
    captcha_keywords = [
        'recaptcha', 'captcha', 'hcaptcha', 'g-recaptcha',
        'challenge', 'verification', 'robot check'
    ]
    
    try:
        page_content = page.content().lower()
        return any(keyword in page_content for keyword in captcha_keywords)
    except:
        return False


def _check_for_login(page: Page) -> bool:
    """Check if login form is present"""
    try:
        # Look for common login form indicators
        login_selectors = [
            'input[type="password"]',
            'input[name*="password"]',
            'input[name*="login"]',
            'input[name*="username"]',
            'input[name*="email"][type="email"]',
            'form[name*="login"]',
            'form[id*="login"]'
        ]
        
        for selector in login_selectors:
            if page.locator(selector).count() > 0:
                return True
        
        # Check for login-related text
        page_content = page.content().lower()
        login_keywords = ['sign in', 'log in', 'login', 'sign up']
        
        return any(keyword in page_content for keyword in login_keywords)
    except:
        return False


def _check_for_react(page: Page) -> bool:
    """Check if React is used"""
    try:
        has_react = page.evaluate("""() => {
            return !!(window.React || 
                     document.querySelector('[data-reactroot]') ||
                     document.querySelector('[data-reactid]') ||
                     window.__REACT_DEVTOOLS_GLOBAL_HOOK__);
        }""")
        return has_react
    except:
        return False


def _check_for_angular(page: Page) -> bool:
    """Check if Angular is used"""
    try:
        has_angular = page.evaluate("""() => {
            return !!(window.angular || 
                     window.ng || 
                     document.querySelector('[ng-app]') ||
                     document.querySelector('[ng-controller]'));
        }""")
        return has_angular
    except:
        return False


def _check_for_vue(page: Page) -> bool:
    """Check if Vue is used"""
    try:
        has_vue = page.evaluate("""() => {
            return !!(window.Vue || 
                     document.querySelector('[data-v-]') ||
                     document.querySelector('[v-cloak]'));
        }""")
        return has_vue
    except:
        return False


def _check_for_iframes(page: Page) -> bool:
    """Check if iframes are present"""
    try:
        return page.locator('iframe').count() > 0
    except:
        return False


def _check_for_shadow_dom(page: Page) -> bool:
    """Check if Shadow DOM is used"""
    try:
        has_shadow = page.evaluate("""() => {
            const elements = document.querySelectorAll('*');
            for (let el of elements) {
                if (el.shadowRoot) return true;
            }
            return false;
        }""")
        return has_shadow
    except:
        return False


def _calculate_robustness_score(report: Dict) -> int:
    """
    Calculate robustness score (0-100) based on compatibility checks
    Higher score = more robust/easier to automate
    """
    score = 100
    
    # Deduct points for issues
    if not report['is_accessible']:
        score -= 40  # Major issue
    
    if report['has_captcha']:
        score -= 30  # Major issue
    
    if report['requires_login']:
        score -= 10  # Moderate issue
    
    if report['uses_heavy_javascript']:
        score -= 15  # Moderate issue
    
    if report['has_iframes']:
        score -= 10  # Moderate issue
    
    if report['has_shadow_dom']:
        score -= 15  # Moderate issue
    
    return max(0, score)


def print_compatibility_report(report: Dict):
    """Print compatibility report to console"""
    print("\n" + "="*70)
    print(" "*20 + "WEBSITE COMPATIBILITY REPORT")
    print("="*70)
    print(f"\nURL: {report['url']}")
    print(f"Status Code: {report['status_code']}")
    print(f"Accessible: {'✓ Yes' if report['is_accessible'] else '✗ No'}")
    
    print("\n" + "-"*70)
    print("Detected Features:")
    print(f"  CAPTCHA: {'✗ Yes' if report['has_captcha'] else '✓ No'}")
    print(f"  Login Required: {'⚠ Yes' if report['requires_login'] else '✓ No'}")
    print(f"  Heavy JavaScript: {'⚠ Yes' if report['uses_heavy_javascript'] else '✓ No'}")
    
    if report['uses_heavy_javascript']:
        frameworks = []
        if report['uses_react']:
            frameworks.append("React")
        if report['uses_angular']:
            frameworks.append("Angular")
        if report['uses_vue']:
            frameworks.append("Vue")
        print(f"    Frameworks: {', '.join(frameworks)}")
    
    print(f"  Iframes: {'⚠ Yes' if report['has_iframes'] else '✓ No'}")
    print(f"  Shadow DOM: {'⚠ Yes' if report['has_shadow_dom'] else '✓ No'}")
    
    print("\n" + "-"*70)
    print(f"Robustness Score: {report['robustness_score']}/100")
    
    if report['robustness_score'] >= 80:
        print("Rating: ✓ Excellent - Easy to automate")
    elif report['robustness_score'] >= 60:
        print("Rating: ⚠ Good - Manageable with proper handling")
    elif report['robustness_score'] >= 40:
        print("Rating: ⚠ Fair - Requires careful implementation")
    else:
        print("Rating: ✗ Poor - Difficult to automate")
    
    if report['warnings']:
        print("\n" + "-"*70)
        print("Warnings:")
        for warning in report['warnings']:
            print(f"  ⚠ {warning}")
    
    if report['suggestions']:
        print("\n" + "-"*70)
        print("Suggestions:")
        for suggestion in report['suggestions']:
            print(f"  💡 {suggestion}")
    
    print("="*70 + "\n")


# Example usage
if __name__ == "__main__":
    report = check_website_compatibility("https://www.google.com")
    print_compatibility_report(report)
