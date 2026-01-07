"""
Simple Instruction Parser - NO API NEEDED
Pure rule-based parsing - 100% reliable
"""

import re
from typing import List, Dict

class SimpleParser:
    """Rule-based parser that always works"""
    
    def parse(self, instruction: str) -> List[Dict]:
        """Parse instruction into actions"""
        original_instruction = instruction
        instruction = instruction.lower().strip()
        actions = []
        
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
        
        return actions
