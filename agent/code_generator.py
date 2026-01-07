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
            'webkit': 'webkit'
        }
        
        playwright_browser = browser_mapping.get(browser_type.lower(), 'chromium')
        browser_display_name = {
            'chromium': 'Google Chrome',
            'firefox': 'Firefox',
            'msedge': 'Microsoft Edge',
            'webkit': 'Safari (WebKit)'
        }.get(browser_type.lower(), browser_type)
        
        # For Edge, we need to specify the channel
        channel_param = ", channel='msedge'" if browser_type.lower() in ['msedge', 'edge'] else ""
        
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
            "        'steps': []",
            "    }",
            "    ",
            "    # Create screenshots directory",
            "    screenshots_dir = os.path.join('static', 'screenshots')",
            "    os.makedirs(screenshots_dir, exist_ok=True)",
            "    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')",
            "    ",
            "    with sync_playwright() as p:",
            f"        # Launch {browser_display_name} browser in {mode_text} mode",
            f"        browser = p.{playwright_browser}.launch(headless={headless}, slow_mo={slow_mo_delay}{channel_param})",
            "        context = browser.new_context(viewport={'width': 1920, 'height': 1080})",
            "        page = context.new_page()",
            "        page.set_default_timeout(30000)",
            "        ",
            f"        print('{browser_display_name} browser launched in {mode_text} mode', file=sys.stderr)",
            "        ",
            "        try:"
        ]
        
        # Generate code for each action
        for i, action in enumerate(actions):
            step_code = self._generate_action_code(action, i, target_url)
            script_lines.extend([f"            {line}" for line in step_code.split('\n')])
        
        # Add cleanup code with extended wait for visible mode
        script_lines.extend([
            "            ",
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
            code += f"    page.goto('{url}')\n"
            code += f"    page.wait_for_load_state('networkidle')\n"
            code += f"    # Take screenshot after navigation\n"
            code += f"    screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png')\n"
            code += f"    page.screenshot(path=screenshot_path, full_page=True)\n"
            code += f"    results['screenshots'].append(screenshot_path)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'navigate', 'description': '{description}', 'screenshot': screenshot_path}})\n"
        
        elif action_type == 'click':
            selector = self._smart_selector(target)
            code += f"    element = page.locator(\"{selector}\").first\n"
            code += f"    element.wait_for(state='visible', timeout=10000)\n"
            code += f"    element.scroll_into_view_if_needed()\n"
            code += f"    page.wait_for_timeout(500)\n"
            code += f"    element.click()\n"
            code += f"    page.wait_for_timeout(1000)\n"
            code += f"    # Take screenshot after click\n"
            code += f"    screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png')\n"
            code += f"    page.screenshot(path=screenshot_path, full_page=True)\n"
            code += f"    results['screenshots'].append(screenshot_path)\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'click', 'description': '{description}', 'screenshot': screenshot_path}})\n"
        
        elif action_type == 'search':
            # Enhanced search with better timeout handling
            code += f"    # Search with multiple strategies\n"
            code += f"    search_found = False\n"
            code += f"    search_selectors = [\n"
            code += f"        'textarea[name=\"q\"]',  # Google's new search (textarea)\n"
            code += f"        'input[name=\"q\"]',     # Classic Google search\n"
            code += f"        'input[type=\"search\"]', # Generic search\n"
            code += f"        'input[aria-label*=\"Search\"]',  # ARIA search\n"
            code += f"        'input[placeholder*=\"Search\"]', # Placeholder search\n"
            code += f"        '#search', '.search-input', '[role=\"searchbox\"]'\n"
            code += f"    ]\n"
            code += f"    for selector in search_selectors:\n"
            code += f"        try:\n"
            code += f"            elements = page.locator(selector)\n"
            code += f"            count = elements.count()\n"
            code += f"            if count > 0:\n"
            code += f"                element = elements.first\n"
            code += f"                element.wait_for(state='visible', timeout=3000)\n"
            code += f"                element.click()\n"
            code += f"                page.wait_for_timeout(500)\n"
            code += f"                element.fill('{value}')\n"
            code += f"                page.wait_for_timeout(800)\n"
            code += f"                page.keyboard.press('Enter')\n"
            code += f"                page.wait_for_timeout(2000)\n"
            code += f"                # Take screenshot after search\n"
            code += f"                screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png')\n"
            code += f"                page.screenshot(path=screenshot_path, full_page=True)\n"
            code += f"                results['screenshots'].append(screenshot_path)\n"
            code += f"                search_found = True\n"
            code += f"                break\n"
            code += f"        except Exception as sel_err:\n"
            code += f"            continue\n"
            code += f"    if search_found:\n"
            code += f"        screenshot_path = os.path.join(screenshots_dir, f'step_{step_num + 1}_{{timestamp}}.png') if screenshot_path else 'N/A'\n"
            code += f"        results['passed'].append({{'step': {step_num + 1}, 'action': 'search', 'description': '{description}', 'value': '{value}', 'screenshot': screenshot_path}})\n"
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
        
        else:
            code += f"    # Unknown action type: {action_type}\n"
            code += f"    results['passed'].append({{'step': {step_num + 1}, 'action': 'unknown', 'description': '{description}'}})\n"
        
        code += "except Exception as e:\n"
        code += f"    results['failed'].append({{'step': {step_num + 1}, 'action': '{action_type}', 'description': '{description}', 'error': str(e)}})\n"
        
        return code
    
    def _smart_selector(self, target: str) -> str:
        """
        Generate intelligent CSS/Playwright selector from target description
        """
        target_lower = target.lower()
        
        # If it's already a CSS selector, return it
        if any(char in target for char in ['#', '.', '[', '>']):
            return target
        
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
