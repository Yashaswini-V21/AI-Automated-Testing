"""
Error Handler Module
Categorizes, logs, and tracks errors during test execution
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import os


class ErrorCategory(Enum):
    """Error categories for classification"""
    NETWORK_ERROR = "NETWORK_ERROR"
    ELEMENT_ERROR = "ELEMENT_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    JAVASCRIPT_ERROR = "JAVASCRIPT_ERROR"
    ASSERTION_ERROR = "ASSERTION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ErrorHandler:
    """Handles error categorization, logging, and reporting"""
    
    def __init__(self, log_file: str = "error_log.json"):
        """
        Initialize the error handler
        
        Args:
            log_file: Path to JSON file for storing errors
        """
        self.log_file = log_file
        self.errors: List[Dict] = []
        self._load_existing_errors()
        
        # Configure Python logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _load_existing_errors(self):
        """Load existing errors from JSON file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.errors = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Could not load existing error log: {e}")
                self.errors = []
        else:
            self.errors = []
    
    def categorize_error(self, error: Exception, error_message: str = None) -> ErrorCategory:
        """
        Categorize an error based on its type and message
        
        Args:
            error: The exception object
            error_message: Optional error message string
            
        Returns:
            ErrorCategory enum value
        """
        error_type = type(error).__name__
        message = error_message or str(error)
        message_lower = message.lower()
        
        # Network errors
        network_keywords = ['connection', 'network', 'timeout', 'dns', 'socket', 'err_connection']
        if any(keyword in message_lower for keyword in network_keywords):
            return ErrorCategory.NETWORK_ERROR
        
        if 'timeouterror' in error_type.lower() or 'timeout' in message_lower:
            return ErrorCategory.TIMEOUT_ERROR
        
        # Element errors
        element_keywords = ['element', 'selector', 'locator', 'not found', 'cannot find']
        if any(keyword in message_lower for keyword in element_keywords):
            return ErrorCategory.ELEMENT_ERROR
        
        # JavaScript errors
        js_keywords = ['javascript', 'js error', 'console error', 'evaluation failed']
        if any(keyword in message_lower for keyword in js_keywords):
            return ErrorCategory.JAVASCRIPT_ERROR
        
        # Assertion errors
        if 'assert' in error_type.lower() or 'assertion' in message_lower:
            return ErrorCategory.ASSERTION_ERROR
        
        return ErrorCategory.UNKNOWN_ERROR
    
    def log_error(self, error: Exception, test_case_name: str, 
                  additional_context: Optional[Dict] = None):
        """
        Log an error with full context
        
        Args:
            error: The exception object
            test_case_name: Name of the test case that failed
            additional_context: Optional dictionary with additional context
        """
        category = self.categorize_error(error)
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'test_case': test_case_name,
            'category': category.value,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': additional_context or {}
        }
        
        self.errors.append(error_entry)
        
        # Log to Python logger
        self.logger.error(
            f"[{category.value}] {test_case_name}: {type(error).__name__} - {str(error)}"
        )
        
        # Save to file
        self._save_errors()
    
    def _save_errors(self):
        """Save errors to JSON file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.errors, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save error log: {e}")
    
    def get_error_summary(self) -> Dict:
        """
        Generate error summary with counts per category
        
        Returns:
            Dictionary with error counts per category
        """
        summary = {category.value: 0 for category in ErrorCategory}
        
        for error in self.errors:
            category = error.get('category', ErrorCategory.UNKNOWN_ERROR.value)
            summary[category] = summary.get(category, 0) + 1
        
        total_errors = len(self.errors)
        
        return {
            'total_errors': total_errors,
            'by_category': summary,
            'most_common': self._get_most_common_category()
        }
    
    def _get_most_common_category(self) -> str:
        """Get the most common error category"""
        if not self.errors:
            return None
        
        category_counts = {}
        for error in self.errors:
            category = error.get('category', ErrorCategory.UNKNOWN_ERROR.value)
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
    
    def get_most_common_errors(self, limit: int = 5) -> List[Dict]:
        """
        Get the most common errors by error message
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of error dictionaries with counts
        """
        error_counts = {}
        
        for error in self.errors:
            error_type = error.get('error_type', 'Unknown')
            error_msg = error.get('error_message', '')
            key = f"{error_type}: {error_msg[:100]}"  # Limit message length
            
            if key not in error_counts:
                error_counts[key] = {
                    'error_type': error_type,
                    'error_message': error_msg,
                    'category': error.get('category'),
                    'count': 0,
                    'test_cases': []
                }
            
            error_counts[key]['count'] += 1
            if error.get('test_case') not in error_counts[key]['test_cases']:
                error_counts[key]['test_cases'].append(error.get('test_case'))
        
        # Sort by count and return top N
        sorted_errors = sorted(error_counts.values(), key=lambda x: x['count'], reverse=True)
        return sorted_errors[:limit]
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[Dict]:
        """
        Get all errors of a specific category
        
        Args:
            category: ErrorCategory enum value
            
        Returns:
            List of error dictionaries
        """
        return [error for error in self.errors if error.get('category') == category.value]
    
    def clear_errors(self):
        """Clear all errors and delete log file"""
        self.errors = []
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except Exception as e:
                self.logger.warning(f"Could not delete log file: {e}")
    
    def print_summary(self):
        """Print error summary to console"""
        summary = self.get_error_summary()
        
        print("\n" + "="*60)
        print(" "*20 + "ERROR SUMMARY")
        print("="*60)
        print(f"\nTotal Errors: {summary['total_errors']}")
        
        if summary['total_errors'] > 0:
            print("\nErrors by Category:")
            for category, count in summary['by_category'].items():
                if count > 0:
                    print(f"  {category}: {count}")
            
            print(f"\nMost Common Category: {summary['most_common']}")
            
            print("\nTop 3 Most Common Errors:")
            for i, error in enumerate(self.get_most_common_errors(3), 1):
                print(f"\n  {i}. {error['error_type']} (occurred {error['count']} times)")
                print(f"     Category: {error['category']}")
                print(f"     Message: {error['error_message'][:150]}...")
                print(f"     Affected tests: {', '.join(error['test_cases'][:3])}")
        else:
            print("\n✓ No errors recorded!")
        
        print("="*60 + "\n")


# Example usage
if __name__ == "__main__":
    handler = ErrorHandler()
    
    # Simulate some errors
    try:
        raise TimeoutError("Element not found within timeout")
    except Exception as e:
        handler.log_error(e, "Test Login Flow")
    
    try:
        raise ConnectionError("Failed to connect to server")
    except Exception as e:
        handler.log_error(e, "Test API Call")
    
    # Print summary
    handler.print_summary()
