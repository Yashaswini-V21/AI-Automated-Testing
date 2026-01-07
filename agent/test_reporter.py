"""
Test Statistics Tracker Module
Tracks and reports test execution statistics
"""

from typing import Dict, List
from datetime import datetime
import time


class TestReporter:
    """Tracks test execution statistics and generates reports"""
    
    def __init__(self):
        self.test_results = []
        self.error_counts = {}
        self.start_time = None
        self.end_time = None
        
    def start_session(self):
        """Mark the start of a test session"""
        self.start_time = time.time()
        
    def end_session(self):
        """Mark the end of a test session"""
        self.end_time = time.time()
        
    def add_test_result(self, test_name: str, status: str, execution_time: float, 
                       error_message: str = None, error_type: str = None):
        """
        Add a test result
        
        Args:
            test_name: Name of the test case
            status: 'pass', 'fail', or 'skip'
            execution_time: Time taken to execute the test in seconds
            error_message: Error message if test failed
            error_type: Type of error (TimeoutError, ElementNotFound, etc.)
        """
        result = {
            'test_name': test_name,
            'status': status,
            'execution_time': execution_time,
            'error_message': error_message,
            'error_type': error_type,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Count error types
        if error_type:
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            
    def get_statistics(self) -> Dict:
        """
        Calculate and return test statistics
        
        Returns:
            Dictionary containing all test statistics
        """
        total_tests = len(self.test_results)
        if total_tests == 0:
            return {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'pass_rate': 0.0,
                'fail_rate': 0.0,
                'skip_rate': 0.0,
                'total_execution_time': 0.0,
                'average_execution_time': 0.0,
                'error_counts': {}
            }
        
        passed = sum(1 for r in self.test_results if r['status'] == 'pass')
        failed = sum(1 for r in self.test_results if r['status'] == 'fail')
        skipped = sum(1 for r in self.test_results if r['status'] == 'skip')
        
        total_time = sum(r['execution_time'] for r in self.test_results)
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'pass_rate': (passed / total_tests) * 100,
            'fail_rate': (failed / total_tests) * 100,
            'skip_rate': (skipped / total_tests) * 100,
            'total_execution_time': total_time,
            'average_execution_time': total_time / total_tests,
            'error_counts': self.error_counts.copy()
        }
        
    def display_statistics(self):
        """Display statistics in terminal with formatting"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print(" "*20 + "TEST STATISTICS")
        print("="*60)
        print(f"\nTotal Tests: {stats['total_tests']}")
        print(f"Passed:      {stats['passed']} ({stats['pass_rate']:.2f}%)")
        print(f"Failed:      {stats['failed']} ({stats['fail_rate']:.2f}%)")
        print(f"Skipped:     {stats['skipped']} ({stats['skip_rate']:.2f}%)")
        print(f"\nTotal Execution Time: {stats['total_execution_time']:.2f}s")
        print(f"Average Time per Test: {stats['average_execution_time']:.2f}s")
        
        if stats['error_counts']:
            print("\n" + "-"*60)
            print("Error Types:")
            for error_type, count in sorted(stats['error_counts'].items(), 
                                           key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count}")
        
        print("="*60 + "\n")
        
    def get_test_results(self) -> List[Dict]:
        """Return all test results"""
        return self.test_results.copy()
