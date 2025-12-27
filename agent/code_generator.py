"""
Code Generator Module
Generates executable Playwright Python scripts from structured actions
"""

from typing import List, Dict
import os

class CodeGenerator:
    """Generates Playwright test code from parsed actions"""
    
    def generate(self, actions: List[Dict], target_url: str, browser_type: str = "chromium", headless: bool = True) -> str:
        """
        Generate Playwright Python script from actions
        
        Args:
            actions: List of parsed action dictionaries
            target_url: Base URL for the test
            browser_type: Browser to use (chromium, firefox, msedge, webkit)
            headless: Whether to run in headless mode
            
        Returns:
            Complete Python script as string
        """
        slow_mo_delay = 800 if not headless else 0
        
        mode_text = 'visible' if not headless else 'headless'
        
        # Map browser names to Playwright browser types
        browser_mapping = {
            'chromium': 'chromium',
            'chrome': 'chromium',
            'firefox': 'firefox',
            'msedge': 'chromium',  # Edge uses chromium channel
            'edge': 'chromium',
            'webkit': 'webkit',
            'brave': 'chromium',   # Brave uses chromium
            'opera': 'chromium'    # Opera uses chromium
        }
        
        playwright_browser = browser_mapping.get(browser_type.lower(), 'chromium')
        browser_display_name = {
            'chromium': 'Google Chrome',
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'msedge': 'Microsoft Edge',
            'edge': 'Microsoft Edge',
            'webkit': 'Safari (WebKit)',
            'brave': 'Brave Browser',
            'opera': 'Opera Browser'
        }.get(browser_type.lower(), browser_type)
        
        # For Edge, Brave, Opera we need to specify the channel
        channel_param = ""
        if browser_type.lower() in ['msedge', 'edge']:
            channel_param = ", channel='msedge'"
        elif browser_type.lower() == 'brave':
            # Note: Brave requires the browser to be installed and will use system Brave
            channel_param = ", channel='chrome', executable_path='C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe'"
        elif browser_type.lower() == 'opera':
            # Opera also uses chromium
            channel_param = ", channel='chrome'"
        
        script_lines = [
            "from playwright.sync_api import sync_playwright",
            "import sys",
            "import json",
            "import time",
            "import os",
            "from datetime import datetime",
            "",
            "def run_test():",
            "    results = {",
            "        'passed': [],",
            "        'failed': [],",
            "        'screenshots': [],",
<<<<<<< HEAD
            "        'steps': []",
            "    }",
            "    ",
=======
            "        'steps': [],",
            "        'start_time': None,",
            "        'end_time': None,",
            "        'execution_time': 0,",
            "        'browser': None,",
            "        'url': None",
            "    }",
            "    ",
            "    # Record start time",
            "    results['start_time'] = datetime.now().isoformat()",
            "    start_timestamp = datetime.now()",
            "    ",
>>>>>>> Yashaswini-branch
            "    # Create screenshots directory",
            "    screenshots_dir = os.path.join('static', 'screenshots')",
            "    os.makedirs(screenshots_dir, exist_ok=True)",
            "    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')",
            "    ",
            "    with sync_playwright() as p:",
            f"        # Launch {browser_display_name} browser in {mode_text} mode",
            f"        browser = p.{playwright_browser}.launch(headless={headless}, slow_mo={slow_mo_delay}{channel_param})",
<<<<<<< HEAD
            "        context = browser.new_context(",
            "            viewport={'width': 1920, 'height': 1080},",
            "            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'",
            "        )",
            "        ",
            "        page = context.new_page()",
            "        ",
            "        # Set longer timeouts for better reliability",
            "        page.set_default_timeout(60000)  # 60 seconds",
            "        page.set_default_navigation_timeout(60000)  # 60 seconds for navigation",
            "        ",
            f"        print('{browser_display_name} browser launched in {mode_text} mode', file=sys.stderr)",
            "        ",
=======
            "        context = browser.new_context(viewport={'width': 1920, 'height': 1080})",
            "        page = context.new_page()",
            "        page.set_default_timeout(30000)",
            "        ",
            f"        print('{browser_display_name} browser launched in {mode_text} mode', file=sys.stderr)",
            "        ",
            f"        # Record browser info",
            f"        results['browser'] = '{browser_display_name}'",
            f"        results['url'] = '{target_url}'",
            "        ",
>>>>>>> Yashaswini-branch
            "        try:"
        ]
        
        # Generate code for each action
        for i, action in enumerate(actions):
            step_code = self._generate_action_code(action, i, target_url)
            script_lines.extend([f"            {line}" for line in step_code.split('\n')])
        
        # Add cleanup code with extended wait for visible mode
        script_lines.extend([
            "            ",
<<<<<<< HEAD
            "            # Mark test as complete",
            "            results['status'] = 'completed'",
            "            ",
            "        except Exception as e:",
            "            results['failed'].append({",
            "                'step': 'execution',",
            "                'error': str(e)",
            "            })",
            "            results['status'] = 'error'",
            "        finally:",
            "            ",
=======
            "            # Mark test as complete with timing",
            "            results['status'] = 'completed'",
            "            results['end_time'] = datetime.now().isoformat()",
            "            execution_duration = (datetime.now() - start_timestamp).total_seconds()",
            "            results['execution_time'] = round(execution_duration, 2)",
            "            ",
            "        except Exception as e:",
            "            # Enhanced error tracking",
            "            import traceback",
            "            error_details = {",
            "                'step': 'execution',",
            "                'error': str(e),",
            "                'error_type': type(e).__name__,",
            "                'traceback': traceback.format_exc()",
            "            }",
            "            results['failed'].append(error_details)",
            "            results['status'] = 'error'",
            "            results['end_time'] = datetime.now().isoformat()",
            "            execution_duration = (datetime.now() - start_timestamp).total_seconds()",
            "            results['execution_time'] = round(execution_duration, 2)",
            "            print(f'Test execution error: {str(e)}', file=sys.stderr)",
            "        finally:",
>>>>>>> Yashaswini-branch
            f"            # In visible mode, keep browser open for viewing",
            f"            if not {headless}:",
            "                print('\\n' + '='*70, file=sys.stderr)",
            "                print('   TEST EXECUTION COMPLETED!', file=sys.stderr)",
            "                print('   Browser will stay open for 60 seconds so you can see the results.', file=sys.stderr)",
            "                print('   You can close it manually anytime.', file=sys.stderr)",
            "                print('='*70 + '\\n', file=sys.stderr)",
            "                try:",
            "                    page.wait_for_timeout(60000)  # 60 seconds (1 minute)",
            "                except:",
            "                    pass",
            "            browser.close()",
            "            print('Browser closed.', file=sys.stderr)",
            "        ",
            "        return results",
            "",
            "if __name__ == '__main__':",
            "    result = run_test()",
            "    print(json.dumps(result))"
        ])
        
        return '\n'.join(script_lines)
    
    def _generate_action_code(self, action: Dict, step_num: int, base_url: str) -> str:
        """Generate code for a single action"""
        action_type = action.get('type', '')
        target = action.get('target', '')
        value = action.get('value', '')
        description = action.get('description', f'Step {step_num + 1}')
        
        code = f"# Step {step_num + 1}: {description}\n"
        code += "try:\n"
        
        if action_type == 'navigate':
            url = target if target.startswith('http') else base_url
<<<<<<< HEAD
            code += f"    # Navigate to {url}\n"
            code += f"    print('Navigating to {url}...', file=sys.stderr)\n"
            code += f"    try:\n"
            code += f"        page.goto('{url}', wait_until='domcontentloaded', timeout=60000)\n"
            code += f"        print('Page loaded, waiting for network...', file=sys.stderr)\n"
            code += f"        page.wait_for_load_state('networkidle', timeout=30000)\n"
            code += f"    except Exception as nav_error:\n"
            code += f"        print(f'Navigation timeout/error (continuing anyway): {{nav_error}}', file=sys.stderr)\n"
            code += f"        # Continue even if networkidle fails - page might be loaded\n"
            code += f"        page.wait_for_timeout(3000)  # Give it 3 more seconds\n"
=======
            code += f"    # Navigate with retry logic\n"
            code += f"    max_retries = 3\n"
            code += f"    for attempt in range(max_retries):\n"
            code += f"        try:\n"
            code += f"            page.goto('{url}', timeout=60000)\n"
            code += f"            page.wait_for_load_state('networkidle', timeout=30000)\n"
            code += f"            print(f'Navigation successful on attempt {{attempt + 1}}', file=sys.stderr)\n"
            code += f"            break\n"
            code += f"        except Exception as nav_err:\n"
            code += f"            if attempt < max_retries - 1:\n"
            code += f"                print(f'Navigation attempt {{attempt + 1}} failed, retrying...', file=sys.stderr)\n"
            code += f"                page.wait_for_timeout(2000)\n"
            code += f"            else:\n"
            code += f"                raise Exception(f'Navigation failed after {{max_retries}} attempts: {{nav_err}}')\n"
>>>>>>> Yashaswini-branch
            code += f"    # Take screenshot after navigation\n"
            code += f"    screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png')\n"
            code += f"    page.screenshot(path=screenshot_path, full_page=True)\n"
            code += f"    results['screenshots'].append(screenshot_path)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'navigate', 'description': '{description}', 'screenshot': screenshot_path}})\n"
<<<<<<< HEAD
            code += f"    print('Navigation completed successfully', file=sys.stderr)\n"
        
        elif action_type == 'click':
            selector = self._smart_selector(target)
            code += f"    # Click on: {target}\n"
            code += f"    print('Clicking on: {target}', file=sys.stderr)\n"
            code += f"    page.wait_for_timeout(1500)  # Wait for page to stabilize\n"
            code += f"    try:\n"
            code += f"        element = page.locator(\"{selector}\").first\n"
            code += f"        element.wait_for(state='visible', timeout=20000)\n"
            code += f"        element.scroll_into_view_if_needed()\n"
            code += f"        page.wait_for_timeout(800)\n"
            code += f"        print('Element found and visible, clicking...', file=sys.stderr)\n"
            code += f"        element.click(timeout=10000)\n"
            code += f"        page.wait_for_timeout(2500)  # Wait after click\n"
            code += f"        print('Click successful', file=sys.stderr)\n"
            code += f"    except Exception as click_error:\n"
            code += f"        print(f'Click error: {{click_error}}, trying force click...', file=sys.stderr)\n"
            code += f"        # Try force click as fallback\n"
            code += f"        element = page.locator(\"{selector}\").first\n"
            code += f"        element.click(force=True, timeout=10000)\n"
            code += f"        page.wait_for_timeout(2500)\n"
            code += f"    # Take screenshot after click\n"
            code += f"    screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png')\n"
            code += f"    page.screenshot(path=screenshot_path, full_page=True)\n"
            code += f"    results['screenshots'].append(screenshot_path)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'click', 'description': '{description}', 'screenshot': screenshot_path}})\n"
        
        elif action_type == 'search':
            # Enhanced search with better timeout handling and more selectors
            code += f"    # Search with multiple strategies\n"
            code += f"    print('Searching for: {value}', file=sys.stderr)\n"
=======
        
        elif action_type == 'click':
            selector = self._smart_selector(target)
            code += f"    # Click with retry and multiple strategies\n"
            code += f"    click_success = False\n"
            code += f"    max_retries = 2\n"
            code += f"    for attempt in range(max_retries):\n"
            code += f"        try:\n"
            code += f"            element = page.locator(\"{selector}\").first\n"
            code += f"            element.wait_for(state='visible', timeout=20000)\n"
            code += f"            element.scroll_into_view_if_needed()\n"
            code += f"            page.wait_for_timeout(500)\n"
            code += f"            element.click(timeout=10000)\n"
            code += f"            click_success = True\n"
            code += f"            print(f'Click successful on attempt {{attempt + 1}}', file=sys.stderr)\n"
            code += f"            break\n"
            code += f"        except Exception as click_err:\n"
            code += f"            if attempt < max_retries - 1:\n"
            code += f"                print(f'Click attempt {{attempt + 1}} failed, retrying with force...', file=sys.stderr)\n"
            code += f"                try:\n"
            code += f"                    page.locator(\"{selector}\").first.click(force=True, timeout=5000)\n"
            code += f"                    click_success = True\n"
            code += f"                    break\n"
            code += f"                except:\n"
            code += f"                    page.wait_for_timeout(1000)\n"
            code += f"            else:\n"
            code += f"                raise Exception(f'Click failed after {{max_retries}} attempts: {{click_err}}')\n"
            code += f"    if click_success:\n"
            code += f"        page.wait_for_timeout(1000)\n"
            code += f"        # Take screenshot after click\n"
            code += f"        screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png')\n"
            code += f"        page.screenshot(path=screenshot_path, full_page=True)\n"
            code += f"        results['screenshots'].append(screenshot_path)\n"
            code += f"        results['passed'].append({{'step': {step_num + 1}, 'action': 'click', 'description': '{description}', 'screenshot': screenshot_path}})\n"
        
        elif action_type == 'search':
            # Enhanced search with better timeout handling
            code += f"    # Search with multiple strategies\n"
>>>>>>> Yashaswini-branch
            code += f"    search_found = False\n"
            code += f"    search_selectors = [\n"
            code += f"        'textarea[name=\"q\"]',  # Google's new search (textarea)\n"
            code += f"        'input[name=\"q\"]',     # Classic Google search\n"
            code += f"        'input[type=\"search\"]', # Generic search\n"
<<<<<<< HEAD
            code += f"        'input[aria-label*=\"Search\" i]',  # ARIA search (case insensitive)\n"
            code += f"        'input[placeholder*=\"Search\" i]', # Placeholder search\n"
            code += f"        'input#twotabsearchtextbox',  # Amazon search\n"
            code += f"        '[data-testid*=\"search\"] input',  # Modern apps\n"
            code += f"        '#search', '.search-input', '[role=\"searchbox\"]',\n"
            code += f"        'input[name=\"search\"]', 'input.search'\n"
=======
            code += f"        'input[aria-label*=\"Search\"]',  # ARIA search\n"
            code += f"        'input[placeholder*=\"Search\"]', # Placeholder search\n"
            code += f"        '#search', '.search-input', '[role=\"searchbox\"]'\n"
>>>>>>> Yashaswini-branch
            code += f"    ]\n"
            code += f"    for selector in search_selectors:\n"
            code += f"        try:\n"
            code += f"            elements = page.locator(selector)\n"
            code += f"            count = elements.count()\n"
            code += f"            if count > 0:\n"
<<<<<<< HEAD
            code += f"                print(f'Found search box with selector: {{selector}}', file=sys.stderr)\n"
            code += f"                element = elements.first\n"
            code += f"                element.wait_for(state='visible', timeout=5000)\n"
            code += f"                element.scroll_into_view_if_needed()\n"
            code += f"                element.click()\n"
            code += f"                page.wait_for_timeout(500)\n"
            code += f"                element.fill('{value}')\n"
            code += f"                page.wait_for_timeout(1000)\n"
            code += f"                print('Pressing Enter...', file=sys.stderr)\n"
            code += f"                page.keyboard.press('Enter')\n"
            code += f"                page.wait_for_timeout(3000)  # Wait for results\n"
=======
            code += f"                element = elements.first\n"
            code += f"                element.wait_for(state='visible', timeout=3000)\n"
            code += f"                element.click()\n"
            code += f"                page.wait_for_timeout(500)\n"
            code += f"                element.fill('{value}')\n"
            code += f"                page.wait_for_timeout(800)\n"
            code += f"                page.keyboard.press('Enter')\n"
            code += f"                page.wait_for_timeout(2000)\n"
>>>>>>> Yashaswini-branch
            code += f"                # Take screenshot after search\n"
            code += f"                screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png')\n"
            code += f"                page.screenshot(path=screenshot_path, full_page=True)\n"
            code += f"                results['screenshots'].append(screenshot_path)\n"
            code += f"                search_found = True\n"
            code += f"                break\n"
            code += f"        except Exception as sel_err:\n"
<<<<<<< HEAD
            code += f"            print(f'Selector {{selector}} failed: {{sel_err}}', file=sys.stderr)\n"
            code += f"            continue\n"
            code += f"    if search_found:\n"
            code += f"        results['passed'].append({{'step': {step_num + 1}, 'action': 'search', 'description': '{description}', 'value': '{value}', 'screenshot': screenshot_path}})\n"
            code += f"        print('Search completed successfully', file=sys.stderr)\n"
=======
            code += f"            continue\n"
            code += f"    if search_found:\n"
            code += f"        screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png') if screenshot_path else 'N/A'\n"
            code += f"        results['passed'].append({{'step': {step_num + 1}, 'action': 'search', 'description': '{description}', 'value': '{value}', 'screenshot': screenshot_path}})\n"
>>>>>>> Yashaswini-branch
            code += f"    else:\n"
            code += f"        raise Exception('Could not find search box with any selector')\n"
        
        elif action_type == 'fill':
            selector = self._smart_selector(target)
            code += f"    # Try multiple selectors for: {target}\n"
            code += f"    element = page.locator(\"{selector}\").first\n"
            code += f"    element.wait_for(state='visible', timeout=10000)\n"
            code += f"    element.click()\n"
            code += f"    element.fill('{value}')\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'fill', 'description': '{description}', 'value': '{value}'}})\n"
        
        elif action_type == 'assert_text':
            code += f"    page_content = page.content()\n"
            code += f"    if '{value}' in page_content:\n"
            code += f"        results['passed'].append({{'step': {step_num + 1}, 'action': 'assert_text', 'description': '{description}', 'expected': '{value}'}})\n"
            code += f"    else:\n"
            code += f"        results['failed'].append({{'step': {step_num + 1}, 'action': 'assert_text', 'description': '{description}', 'expected': '{value}', 'error': 'Text not found'}})\n"
        
        elif action_type == 'assert_url':
            code += f"    current_url = page.url\n"
            code += f"    if '{value}' in current_url:\n"
            code += f"        results['passed'].append({{'step': {step_num + 1}, 'action': 'assert_url', 'description': '{description}', 'expected': '{value}'}})\n"
            code += f"    else:\n"
            code += f"        results['failed'].append({{'step': {step_num + 1}, 'action': 'assert_url', 'description': '{description}', 'expected': '{value}', 'actual': current_url}})\n"
        
        elif action_type == 'wait':
            timeout = int(value) * 1000 if value else 1000
            code += f"    page.wait_for_timeout({timeout})\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'wait', 'description': '{description}'}})\n"
        
<<<<<<< HEAD
        elif action_type == 'scroll':
            direction = value if value else 'down'
            scroll_amount = '500' if direction == 'down' else '-500'
            code += f"    # Scroll {direction}\n"
            code += f"    page.evaluate('window.scrollBy(0, {scroll_amount})')\n"
            code += f"    page.wait_for_timeout(500)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'scroll', 'description': '{description}'}})\n"
        
        elif action_type == 'hover':
            selector = self._smart_selector(target)
            code += f"    # Hover over: {target}\n"
            code += f"    element = page.locator(\"{selector}\").first\n"
            code += f"    element.wait_for(state='visible', timeout=10000)\n"
            code += f"    element.scroll_into_view_if_needed()\n"
            code += f"    element.hover()\n"
            code += f"    page.wait_for_timeout(1000)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'hover', 'description': '{description}'}})\n"
        
        elif action_type == 'select':
            selector = self._smart_selector(target)
            code += f"    # Select from dropdown: {target}\n"
            code += f"    dropdown = page.locator(\"{selector}\").first\n"
            code += f"    dropdown.wait_for(state='visible', timeout=10000)\n"
            code += f"    dropdown.select_option(label='{value}')\n"
            code += f"    page.wait_for_timeout(500)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'select', 'description': '{description}', 'value': '{value}'}})\n"
        
        elif action_type == 'screenshot':
            code += f"    # Take screenshot\n"
            code += f"    screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png')\n"
            code += f"    page.screenshot(path=screenshot_path, full_page=True)\n"
            code += f"    results['screenshots'].append(screenshot_path)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'screenshot', 'description': '{description}', 'screenshot': screenshot_path}})\n"
        
        elif action_type == 'refresh':
            code += f"    # Refresh page\n"
            code += f"    page.reload()\n"
            code += f"    page.wait_for_load_state('networkidle')\n"
            code += f"    page.wait_for_timeout(1000)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'refresh', 'description': '{description}'}})\n"
        
        elif action_type == 'back':
            code += f"    # Go back\n"
            code += f"    page.go_back()\n"
            code += f"    page.wait_for_load_state('networkidle')\n"
            code += f"    page.wait_for_timeout(1000)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'back', 'description': '{description}'}})\n"
        
=======
>>>>>>> Yashaswini-branch
        else:
            code += f"    # Unknown action type: {action_type}\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'unknown', 'description': '{description}'}})\n"
        
        code += "except Exception as e:\n"
<<<<<<< HEAD
        code += f"    results['failed'].append({{'step': {step_num + 1}, 'action': '{action_type}', 'description': '{description}', 'error': str(e)}})\n"
=======
        code += f"    import traceback\\n"
        code += f"    error_info = {{\\n"
        code += f"        'step': {step_num + 1},\\n"
        code += f"        'action': '{action_type}',\\n"
        code += f"        'description': '{description}',\\n"
        code += f"        'error': str(e),\\n"
        code += f"        'error_type': type(e).__name__\\n"
        code += f"    }}\\n"
        code += f"    results['failed'].append(error_info)\\n"
        code += f"    print(f'Step {step_num + 1} failed - {{type(e).__name__}}: {{str(e)}}', file=sys.stderr)\\n"
>>>>>>> Yashaswini-branch
        
        return code
    
    def _smart_selector(self, target: str) -> str:
        """
<<<<<<< HEAD
        Ultra-robust intelligent selector generator for ANY website
        Handles Amazon, Netflix, Spotify, YouTube, and all modern websites
=======
        Generate intelligent CSS/Playwright selector from target description
>>>>>>> Yashaswini-branch
        """
        target_lower = target.lower()
        
        # If it's already a CSS selector, return it
        if any(char in target for char in ['#', '.', '[', '>']):
            return target
        
<<<<<<< HEAD
        # ========== E-COMMERCE PATTERNS (Amazon, eBay, Walmart, etc.) ==========
        
        # Add to Cart - comprehensive patterns
        if 'add to cart' in target_lower or 'add to basket' in target_lower:
            return "#add-to-cart-button, input[name='submit.add-to-cart'], button[name='submit.add-to-cart'], #add-to-cart, [data-action='add-to-cart'], button:has-text('Add to Cart'), button:has-text('Add to Basket'), .add-to-cart, [class*='addToCart'], [id*='addToCart']"
        
        # Product selection patterns
        if 'first product' in target_lower or 'first result' in target_lower or 'first item' in target_lower:
            return "[data-component-type='s-search-result']:first-child a.a-link-normal, .s-result-item:first-child h2 a, [data-index='0'] h2 a, div[data-cel-widget*='search_result']:first-child a.a-link-normal, .product-item:first-child a, .search-result:first-child a, [class*='product']:first-child a, [class*='item']:first-child a"
        
        if 'second product' in target_lower or 'second result' in target_lower:
            return "[data-component-type='s-search-result']:nth-child(2) a.a-link-normal, .s-result-item:nth-child(2) h2 a, [data-index='1'] h2 a, .product-item:nth-child(2) a, .search-result:nth-child(2) a"
        
        if 'third product' in target_lower or 'third result' in target_lower:
            return "[data-component-type='s-search-result']:nth-child(3) a.a-link-normal, .s-result-item:nth-child(3) h2 a, [data-index='2'] h2 a, .product-item:nth-child(3) a, .search-result:nth-child(3) a"
        
        if 'last product' in target_lower or 'last result' in target_lower:
            return "[data-component-type='s-search-result']:last-child a.a-link-normal, .s-result-item:last-child h2 a, .product-item:last-child a, .search-result:last-child a"
        
        # Buy Now button
        if any(word in target_lower for word in ['buy now', 'buy', 'purchase']):
            return "input[name='submit.buy-now'], #buy-now-button, button:has-text('Buy Now'), [data-action='buy-now'], .buy-now, [class*='buyNow']"
        
        # Checkout button
        if 'checkout' in target_lower:
            return "button:has-text('Checkout'), a:has-text('Checkout'), [name='proceedToCheckout'], #sc-buy-box-ptc-button, .checkout-button, [class*='checkout']"
        
        # ========== STREAMING SERVICES (Netflix, Spotify, YouTube) ==========
        
        # Play/Watch/Listen buttons
        if any(word in target_lower for word in ['play', 'watch', 'listen']):
            return f"button:has-text('{target}'), [aria-label*='Play'], [data-uia='play'], .play-button, [role='button']:has-text('{target}'), a:has-text('{target}'), [class*='play'], [id*='play']"
        
        # Profile/Account menu
        if any(word in target_lower for word in ['profile', 'account', 'user']):
            return f"button[aria-label*='Account'], [data-uia='account-menu'], .account-dropdown-button, a:has-text('{target}'), [aria-label*='Profile'], [class*='profile'], [class*='account'], [id*='account-menu']"
        
        # Browse/Categories (Netflix)
        if any(word in target_lower for word in ['browse', 'categories', 'genres', 'menu']):
            return f"a:has-text('{target}'), button:has-text('{target}'), [role='navigation'] a:has-text('{target}'), [data-uia*='menu'], nav a:has-text('{target}')"
        
        # ========== SOCIAL MEDIA (Facebook, Twitter, Instagram, LinkedIn) ==========
        
        # Post/Tweet/Share
        if any(word in target_lower for word in ['post', 'tweet', 'share', 'publish']):
            return f"button:has-text('{target}'), [data-testid*='post'], [data-testid*='tweet'], [aria-label*='Post'], [aria-label*='Tweet'], [aria-label*='Share'], [role='button']:has-text('{target}')"
        
        # Like/Heart
        if any(word in target_lower for word in ['like', 'heart', 'favorite']):
            return f"button:has-text('{target}'), [data-testid*='like'], [aria-label*='Like'], [aria-label*='Favorite'], [class*='like'], [class*='heart']"
        
        # Follow/Subscribe
        if any(word in target_lower for word in ['follow', 'subscribe']):
            return f"button:has-text('{target}'), [aria-label*='Follow'], [aria-label*='Subscribe'], [data-testid*='follow'], [data-testid*='subscribe']"
        
        # ========== FORMS & INPUTS ==========
        
        # Search box - comprehensive patterns
        if 'search' in target_lower:
            return "input[name='q'], input[name='search'], input[type='search'], input[aria-label*='Search'], input[placeholder*='Search'], textarea[name='q'], [data-testid*='search'], [role='searchbox'], input#twotabsearchtextbox, [class*='search'] input, #search-input, .search-input"
        
        # Email field
        if 'email' in target_lower:
            return "input[type='email'], input[name*='email'], input[id*='email'], input[autocomplete='email'], [data-testid*='email'], input[placeholder*='email' i]"
        
        # Password field
        if 'password' in target_lower:
            return "input[type='password'], input[name*='password'], input[id*='password'], input[autocomplete*='password'], [data-testid*='password'], input[placeholder*='password' i]"
        
        # Username field
        if 'username' in target_lower or 'user' in target_lower:
            return "input[name*='user'], input[id*='user'], input[placeholder*='user' i], input[autocomplete='username'], [data-testid*='username']"
        
        # Name field
        if 'name' in target_lower and 'username' not in target_lower:
            return "input[name*='name'], input[id*='name'], input[placeholder*='name' i], [data-testid*='name']"
        
        # Phone field
        if 'phone' in target_lower or 'mobile' in target_lower:
            return "input[type='tel'], input[name*='phone'], input[name*='mobile'], input[id*='phone'], input[placeholder*='phone' i], input[autocomplete='tel']"
        
        # Address field
        if 'address' in target_lower:
            return "input[name*='address'], input[id*='address'], textarea[name*='address'], input[placeholder*='address' i], input[autocomplete*='address']"
        
        # Dropdown/Select
        if 'dropdown' in target_lower or 'select' in target_lower:
            return "select, [role='combobox'], [role='listbox'], .dropdown, [class*='select']"
        
        # ========== BUTTONS ==========
        
        # Submit/Continue/Next
        if any(word in target_lower for word in ['submit', 'sign in', 'login', 'continue', 'next', 'confirm', 'ok', 'yes']):
            return f"button:has-text('{target}'), input[type='submit'], input[type='button'], a:has-text('{target}'), [role='button']:has-text('{target}'), [type='button']:has-text('{target}'), button[name*='{target.replace(' ', '')}']"
        
        # Cancel/Close/No
        if any(word in target_lower for word in ['cancel', 'close', 'no', 'dismiss']):
            return f"button:has-text('{target}'), a:has-text('{target}'), [aria-label*='Close'], [aria-label*='Cancel'], .close, [class*='close'], [class*='cancel']"
        
        # ========== NAVIGATION ==========
        
        # Links
        if any(word in target_lower for word in ['link', 'href']):
            return f"a:has-text('{target}'), [role='link']:has-text('{target}')"
        
        # Tabs
        if 'tab' in target_lower:
            return f"[role='tab']:has-text('{target}'), .tab:has-text('{target}'), [class*='tab']:has-text('{target}')"
        
        # Menu items
        if 'menu' in target_lower or 'item' in target_lower:
            return f"[role='menuitem']:has-text('{target}'), .menu-item:has-text('{target}'), [class*='menu']:has-text('{target}')"
        
        # ========== CONTENT PATTERNS ==========
        
        # Cards/Tiles
        if any(word in target_lower for word in ['card', 'tile']):
            return f"[class*='card']:has-text('{target}'), [class*='tile']:has-text('{target}'), article:has-text('{target}'), [data-testid*='card']"
        
        # Headers/Headings
        if any(word in target_lower for word in ['heading', 'header', 'title']):
            return f"h1:has-text('{target}'), h2:has-text('{target}'), h3:has-text('{target}'), [role='heading']:has-text('{target}')"
        
        # ========== GENERIC FALLBACK (Try Everything) ==========
        
        # Create a comprehensive selector that tries multiple strategies
        target_escaped = target.replace("'", "\\'")
        target_normalized = target.replace(' ', '-').lower()
        
        return f"""
            text='{target_escaped}',
            button:has-text('{target_escaped}'),
            a:has-text('{target_escaped}'),
            input[placeholder*='{target_escaped}' i],
            [aria-label*='{target_escaped}'],
            [title*='{target_escaped}'],
            [name*='{target_normalized}'],
            [id*='{target_normalized}'],
            [data-testid*='{target_normalized}'],
            [class*='{target_normalized}'],
            [role='button']:has-text('{target_escaped}'),
            [type='button']:has-text('{target_escaped}'),
            span:has-text('{target_escaped}'),
            div:has-text('{target_escaped}')
        """.replace('\n', '').replace('  ', ' ').strip()
=======
        # Common button patterns
        if any(word in target_lower for word in ['submit', 'sign in', 'login', 'search', 'button']):
            return f"button:has-text('{target}'), input[type='submit'], a:has-text('{target}'), [role='button']:has-text('{target}')"
        
        # Search box patterns
        if 'search' in target_lower:
            return "input[name='q'], input[name='search'], input[type='search'], input[aria-label*='Search'], input[placeholder*='Search'], textarea[name='q']"
        
        # Common input patterns
        if 'email' in target_lower:
            return "input[type='email'], input[name*='email'], input[id*='email'], input[autocomplete='email']"
        
        if 'password' in target_lower:
            return "input[type='password'], input[name*='password'], input[id*='password'], input[autocomplete*='password']"
        
        if 'username' in target_lower or 'user' in target_lower:
            return "input[name*='user'], input[id*='user'], input[placeholder*='user'], input[autocomplete='username']"
        
        if 'name' in target_lower:
            return "input[name*='name'], input[id*='name'], input[placeholder*='name']"
        
        # Generic text search with multiple strategies
        return f"text='{target}', button:has-text('{target}'), a:has-text('{target}'), [aria-label*='{target}'], [placeholder*='{target}'], [name*='{target}'], [title*='{target}']"
>>>>>>> Yashaswini-branch
