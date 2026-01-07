"""
Progress Indicator Module
Visual progress indicator for test execution
"""

import sys
import time
from typing import Optional


class ProgressIndicator:
    """Real-time progress indicator for terminal"""
    
    def __init__(self, total_tests: int):
        """
        Initialize progress indicator
        
        Args:
            total_tests: Total number of tests to run
        """
        self.total_tests = total_tests
        self.current_test = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()
        self.current_test_name = ""
        
    def start_test(self, test_name: str):
        """
        Mark the start of a test
        
        Args:
            test_name: Name of the test being executed
        """
        self.current_test += 1
        self.current_test_name = test_name
        self._update_display()
        
    def mark_passed(self):
        """Mark current test as passed"""
        self.passed += 1
        self._update_display()
        
    def mark_failed(self):
        """Mark current test as failed"""
        self.failed += 1
        self._update_display()
        
    def mark_skipped(self):
        """Mark current test as skipped"""
        self.skipped += 1
        self._update_display()
        
    def _update_display(self):
        """Update the progress display in terminal"""
        # Calculate progress
        progress_percentage = (self.current_test / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * self.current_test / self.total_tests) if self.total_tests > 0 else 0
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Calculate elapsed time
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)
        
        # Truncate test name if too long
        display_name = self.current_test_name
        if len(display_name) > 40:
            display_name = display_name[:37] + "..."
        
        # Build progress line
        progress_line = (
            f"\r🧪 Test {self.current_test}/{self.total_tests}: {display_name:<40} | "
            f"[{bar}] {progress_percentage:.0f}% | "
            f"✓ {self.passed} ✗ {self.failed} ○ {self.skipped} | "
            f"⏱ {elapsed_str}"
        )
        
        # Write to stdout without newline
        sys.stdout.write('\033[K')  # Clear line
        sys.stdout.write(progress_line)
        sys.stdout.flush()
        
    def _format_time(self, seconds: float) -> str:
        """Format time in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def finish(self):
        """Mark progress as complete and move to new line"""
        sys.stdout.write("\n")
        sys.stdout.flush()


class SimpleProgressBar:
    """Simplified progress bar for quick use"""
    
    @staticmethod
    def show(current: int, total: int, prefix: str = '', suffix: str = '', 
             length: int = 50, fill: str = '█'):
        """
        Display a simple progress bar
        
        Args:
            current: Current iteration
            total: Total iterations
            prefix: Prefix string
            suffix: Suffix string
            length: Character length of bar
            fill: Bar fill character
        """
        percent = 100 * (current / float(total))
        filled_length = int(length * current // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        
        sys.stdout.write(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}')
        sys.stdout.flush()
        
        if current == total:
            sys.stdout.write('\n')


# Example usage
if __name__ == "__main__":
    # Example 1: ProgressIndicator
    print("Example 1: Testing ProgressIndicator\n")
    
    tests = [
        "Login Test",
        "Search Functionality",
        "Add to Cart",
        "Checkout Process",
        "Payment Gateway",
        "Order Confirmation",
        "User Profile Update",
        "Logout Test"
    ]
    
    progress = ProgressIndicator(total_tests=len(tests))
    
    for i, test_name in enumerate(tests):
        progress.start_test(test_name)
        time.sleep(0.8)  # Simulate test execution
        
        # Randomly mark as pass/fail
        import random
        outcome = random.choice(['pass', 'pass', 'pass', 'fail'])  # 75% pass rate
        
        if outcome == 'pass':
            progress.mark_passed()
        else:
            progress.mark_failed()
        
        time.sleep(0.3)
    
    progress.finish()
    
    print("\n" + "="*80)
    print("Example 2: Testing SimpleProgressBar\n")
    
    # Example 2: SimpleProgressBar
    items = 100
    for i in range(items + 1):
        time.sleep(0.02)
        SimpleProgressBar.show(i, items, prefix='Processing:', suffix='Complete', length=50)
    
    print("\nDone!")
