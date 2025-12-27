"""
Simple Instruction Parser - NO API NEEDED
Pure rule-based parsing - 100% reliable
<<<<<<< HEAD
Ultra-robust for ANY website and ANY task
=======
>>>>>>> Yashaswini-branch
"""

import re
from typing import List, Dict

class SimpleParser:
    """Rule-based parser that handles any website and any task"""
    
    def parse(self, instruction: str) -> List[Dict]:
        """Parse instruction into actions - handles complex multi-step instructions"""
        original_instruction = instruction
        instruction = instruction.lower().strip()
        actions = []
        
<<<<<<< HEAD
        # Check if this is a login/signup scenario
        is_login_scenario = any(word in instruction for word in ['login', 'log in', 'sign in', 'signin', 'signup', 'sign up', 'register', 'authenticate'])
        
        # Split by common separators to handle multi-step commands
        steps = re.split(r'\s+(?:and then|then|and|,)\s+', instruction)
        
        for step in steps:
            step = step.strip()
            if not step:
                continue
            
            # Extract URL - comprehensive pattern matching
            url_patterns = [
                r'(https?://[^\s,]+)',
                r'(?:www\.)([a-z0-9-]+\.[a-z]{2,}(?:/[^\s,]*)?)',
                r'(netflix\.com|spotify\.com|amazon\.com|youtube\.com|facebook\.com|twitter\.com|instagram\.com|linkedin\.com|github\.com|reddit\.com|wikipedia\.org|ebay\.com|walmart\.com|target\.com)(?:/[^\s,]*)?',
                r'([a-z0-9-]+\.(?:com|org|net|io|tv|fm|co\.uk|in|edu|gov))(?:/[^\s,]*)?',
            ]
            
            base_url = None
            for pattern in url_patterns:
                url_match = re.search(pattern, step, re.IGNORECASE)
                if url_match:
                    base_url = url_match.group(0)
                    if 'www.' in base_url and not base_url.startswith('http'):
                        base_url = 'https://' + base_url
                    elif not base_url.startswith('http'):
                        base_url = 'https://' + base_url
                    break
            
            # NAVIGATE - go to, open, visit, browse, navigate
            if base_url and any(word in step for word in ['navigate', 'go to', 'go', 'open', 'visit', 'browse', 'load']):
                actions.append({
                    'type': 'navigate',
                    'target': base_url,
                    'description': f'Navigate to {base_url}'
                })
                continue
            
            # WAIT - wait, pause, sleep, delay
            wait_match = re.search(r'(?:wait|pause|sleep|delay)\s+(?:for\s+)?(\d+)\s*(?:second|sec|s)?s?', step)
            if wait_match:
                seconds = wait_match.group(1)
                actions.append({
                    'type': 'wait',
                    'target': 'page',
                    'value': seconds,
                    'description': f'Wait {seconds} seconds'
                })
                continue
            
            # SEARCH/TYPE - search, type, enter text, input
            search_patterns = [
                r'(?:search|type|enter|input)\s+(?:for\s+)?["\']([^"\']+)["\']',
                r'(?:search|type|enter|input)\s+(?:for\s+)?(.+?)(?:\s+in\s+search|\s+in\s+box|\s+into|$)',
                r'look\s+for\s+["\']?([^"\']+?)["\']?(?:\s|$)',
                r'find\s+["\']?([^"\']+?)["\']?(?:\s|$)'
            ]
            
            search_found = False
            for pattern in search_patterns:
                search_match = re.search(pattern, step)
                if search_match:
                    query = search_match.group(1).strip()
                    query = re.sub(r'["\']', '', query)
                    if query and len(query) > 1:
                        actions.append({
                            'type': 'search',
                            'target': 'search_box',
                            'value': query,
                            'description': f'Search for: {query}'
                        })
                        search_found = True
                        break
            
            if search_found:
                continue
            
            # CLICK - click, press, tap, select, choose
            click_patterns = [
                (r'(?:click|press|tap)\s+(?:on\s+)?(?:the\s+)?(first|1st)\s+(.+?)(?:\s|$)', 'first'),
                (r'(?:click|press|tap)\s+(?:on\s+)?(?:the\s+)?(second|2nd)\s+(.+?)(?:\s|$)', 'second'),
                (r'(?:click|press|tap)\s+(?:on\s+)?(?:the\s+)?(third|3rd)\s+(.+?)(?:\s|$)', 'third'),
                (r'(?:click|press|tap)\s+(?:on\s+)?(?:the\s+)?(last)\s+(.+?)(?:\s|$)', 'last'),
                (r'add\s+to\s+(?:cart|basket)', 'add_to_cart'),
                (r'(?:click|press|tap|select|choose)\s+(?:on\s+)?(?:the\s+)?["\']([^"\']+)["\']', 'quoted'),
                (r'(?:click|press|tap|select|choose)\s+(?:on\s+)?(?:the\s+)?(.+?)(?:\s+button|\s+link|\s+icon|\s+menu|$)', 'general')
            ]
            
            click_found = False
            for pattern_tuple in click_patterns:
                if len(pattern_tuple) == 2:
                    pattern, click_type = pattern_tuple
                    click_match = re.search(pattern, step)
                    if click_match:
                        if click_type == 'add_to_cart':
                            target = 'add to cart'
                            description = 'Click Add to Cart button'
                        elif click_type in ['first', 'second', 'third', 'last']:
                            item_type = click_match.group(2).strip() if click_match.lastindex >= 2 else 'result'
                            target = f'{click_type} {item_type}'
                            description = f'Click on the {click_type} {item_type}'
                        elif click_type == 'quoted':
                            target = click_match.group(1).strip()
                            description = f'Click on {target}'
                        else:  # general
                            target = click_match.group(1).strip()
                            target = re.sub(r'\s+(?:button|link|icon|menu|element)$', '', target).strip()
                            description = f'Click on {target}'
                        
                        actions.append({
                            'type': 'click',
                            'target': target,
                            'description': description
                        })
                        click_found = True
                        break
            
            if click_found:
                continue
            
            # HOVER - hover, mouse over
            hover_match = re.search(r'(?:hover|mouse\s+over)\s+(?:on\s+)?(?:the\s+)?(.+?)(?:\s|$)', step)
            if hover_match:
                target = hover_match.group(1).strip()
                actions.append({
                    'type': 'hover',
                    'target': target,
                    'description': f'Hover over {target}'
                })
                continue
            
            # SCROLL - scroll up/down/to
            if any(word in step for word in ['scroll']):
                if 'down' in step or 'bottom' in step:
                    direction = 'down'
                elif 'up' in step or 'top' in step:
                    direction = 'up'
                else:
                    direction = 'down'
                
                actions.append({
                    'type': 'scroll',
                    'target': 'page',
                    'value': direction,
                    'description': f'Scroll {direction}'
                })
                continue
            
            # FILL/ENTER - fill field, enter into field
            fill_patterns = [
                r'(?:fill|enter|input|type\s+into)\s+(?:the\s+)?(.+?)\s+(?:with|as)\s+["\']([^"\']+)["\']',
                r'(?:fill|enter|input)\s+["\']([^"\']+)["\']\s+(?:into|in)\s+(?:the\s+)?(.+?)(?:\s+(?:field|box|input))?(?:\s|$)',
                r'(?:set|change)\s+(.+?)\s+to\s+["\']([^"\']+)["\']'
            ]
            
            fill_found = False
            for pattern in fill_patterns:
                fill_match = re.search(pattern, step)
                if fill_match:
                    if 'with' in step or 'as' in step or 'to' in step:
                        field = fill_match.group(1).strip()
                        value = fill_match.group(2).strip()
                    else:
                        value = fill_match.group(1).strip()
                        field = fill_match.group(2).strip()
                    
                    actions.append({
                        'type': 'fill',
                        'target': field,
                        'value': value,
                        'description': f'Fill {field} with {value}'
                    })
                    fill_found = True
                    break
            
            if fill_found:
                continue
            
            # SELECT DROPDOWN - select from dropdown
            select_patterns = [
                r'(?:select|choose)\s+["\']([^"\']+)["\']\s+from\s+(?:the\s+)?(.+?)(?:\s+dropdown|\s+menu|\s+list)?(?:\s|$)',
                r'(?:select|choose)\s+(.+?)\s+from\s+dropdown'
            ]
            
            select_found = False
            for pattern in select_patterns:
                select_match = re.search(pattern, step)
                if select_match:
                    value = select_match.group(1).strip()
                    dropdown = select_match.group(2).strip() if select_match.lastindex >= 2 else 'dropdown'
                    actions.append({
                        'type': 'select',
                        'target': dropdown,
                        'value': value,
                        'description': f'Select {value} from {dropdown}'
                    })
                    select_found = True
                    break
            
            if select_found:
                continue
            
            # VERIFY/CHECK/ASSERT - verify, check, assert, confirm, ensure
            verify_patterns = [
                r'(?:verify|check|assert|confirm|ensure)\s+(?:that\s+)?(?:the\s+)?page\s+contains?\s+["\']([^"\']+)["\']',
                r'(?:verify|check|assert)\s+["\']([^"\']+)["\']\s+(?:is\s+visible|appears?|exists?|is\s+present)',
                r'(?:make\s+sure|ensure)\s+(?:that\s+)?["\']([^"\']+)["\']\s+(?:is\s+visible|appears?|exists?|is\s+present)'
            ]
            
            verify_found = False
            for pattern in verify_patterns:
                verify_match = re.search(pattern, step)
                if verify_match:
                    text = verify_match.group(1).strip()
                    actions.append({
                        'type': 'assert_text',
                        'target': 'page',
                        'value': text,
                        'description': f'Verify page contains: {text}'
                    })
                    verify_found = True
                    break
            
            if verify_found:
                continue
            
            # SCREENSHOT - take screenshot, capture screen
            if any(word in step for word in ['screenshot', 'capture', 'snap']):
                actions.append({
                    'type': 'screenshot',
                    'target': 'page',
                    'description': 'Take screenshot'
                })
                continue
            
            # REFRESH/RELOAD
            if any(word in step for word in ['refresh', 'reload']):
                actions.append({
                    'type': 'refresh',
                    'target': 'page',
                    'description': 'Refresh page'
                })
                continue
            
            # GO BACK
            if 'back' in step or 'previous' in step:
                actions.append({
                    'type': 'back',
                    'target': 'page',
                    'description': 'Go back'
                })
                continue
            
            # If URL found but no navigate action yet, add it
            if base_url:
                actions.append({
                    'type': 'navigate',
                    'target': base_url,
                    'description': f'Navigate to {base_url}'
                })
        
        # If no actions parsed at all, try to be smart
        if not actions:
            # Check if there's a URL anywhere in original instruction
            url_in_original = re.search(r'(https?://[^\s,]+|(?:www\.)?[a-z0-9-]+\.(?:com|org|net|io))', original_instruction, re.IGNORECASE)
            if url_in_original:
                url = url_in_original.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url
                actions.append({
                    'type': 'navigate',
                    'target': url,
                    'description': f'Navigate to {url}'
                })
=======
        # Extract URL first - improved to match more formats
        url_patterns = [
            r'(https?://[^\s,]+)',  # Full URLs with protocol
            r'(?:www\.)([a-z0-9-]+\.[a-z]{2,}(?:/[^\s,]*)?)',  # www.site.com
            r'([a-z0-9-]+\.com|[a-z0-9-]+\.org|[a-z0-9-]+\.net|[a-z0-9-]+\.io)(?:/[^\s,]*)?',  # site.com
        ]
        
        base_url = None
        for pattern in url_patterns:
            url_match = re.search(pattern, original_instruction, re.IGNORECASE)
            if url_match:
                base_url = url_match.group(0)
                if 'www.' in base_url and not base_url.startswith('http'):
                    base_url = 'https://' + base_url
                elif not base_url.startswith('http'):
                    base_url = 'https://' + base_url
                break
        
        # Check for navigate/go to OR if URL is mentioned anywhere
        if base_url and (any(word in instruction for word in ['navigate', 'go to', 'open', 'visit']) or 
                         any(word in instruction for word in ['.com', '.org', '.net', '.io', 'http'])):
            actions.append({
                'type': 'navigate',
                'target': base_url,
                'description': f'Navigate to {base_url}'
            })
        
        # Check for wait
        wait_match = re.search(r'wait\s+(\d+)\s*seconds?', instruction)
        if wait_match:
            seconds = wait_match.group(1)
            actions.append({
                'type': 'wait',
                'target': 'page',
                'value': seconds,
                'description': f'Wait {seconds} seconds'
            })
        
        # Check for search/type - improved to capture the search query better
        search_patterns = [
            r'type\s+["\']([^"\']+)["\']',
            r'search\s+(?:for\s+)?["\']([^"\']+)["\']',
            r'search\s+(?:for\s+)?(.+?)(?:\s+and|\s+then|$)',
            r'type\s+(.+?)(?:\s+and|\s+then|$)'
        ]
        
        for pattern in search_patterns:
            search_match = re.search(pattern, instruction)
            if search_match:
                query = search_match.group(1).strip()
                # Clean up the query
                query = re.sub(r'\s+and\s+.*$', '', query)
                query = re.sub(r'\s+then\s+.*$', '', query)
                if query and len(query) > 2:
                    actions.append({
                        'type': 'search',
                        'target': 'search_box',
                        'value': query,
                        'description': f'Search for: {query}'
                    })
                    break
        
        # Check for click
        if 'click' in instruction:
            click_match = re.search(r'click\s+(?:on\s+)?(?:the\s+)?["\']?([^"\']+)["\']?', instruction)
            target = click_match.group(1).strip() if click_match else 'button'
            # Don't include the rest of the instruction
            target = target.split(' and ')[0].split(' then ')[0]
            actions.append({
                'type': 'click',
                'target': target,
                'description': f'Click on {target}'
            })
        
        # If no actions found but URL exists, navigate to it
        if not actions and base_url:
            actions.append({
                'type': 'navigate',
                'target': base_url,
                'description': f'Navigate to {base_url}'
            })
>>>>>>> Yashaswini-branch
        
        return actions
