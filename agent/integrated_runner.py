"""
Integrated Test Runner
Main test execution flow integrating all enhanced features
"""

import time
from typing import Dict, List, Callable
from playwright.sync_api import sync_playwright, Page
import logging

# Import all the new modules
from agent.test_reporter import TestReporter
from agent.html_reporter import generate_html_report
from agent.retry_decorator import retry_on_failure, retry_playwright_action
from agent.element_finder import find_element_robust, ElementNotFoundError
from agent.error_handler import ErrorHandler
from agent.compatibility_checker import check_website_compatibility, print_compatibility_report
from agent.popup_handler import handle_common_popups, setup_popup_blocking_context
from agent.progress_indicator import ProgressIndicator
from agent.summary_reporter import generate_final_summary


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedTestRunner:
    """Enhanced test runner with all new features"""
    
    def __init__(self, url: str, browser_type: str = 'chromium', headless: bool = True):
        """
        Initialize the integrated test runner
        
        Args:
            url: Target URL to test
            browser_type: Browser to use (chromium, firefox, webkit)
            headless: Run in headless mode
        """
        self.url = url
        self.browser_type = browser_type
        self.headless = headless
        
        # Initialize components
        self.reporter = TestReporter()
        self.error_handler = ErrorHandler()
        self.compatibility_report = None
        self.robustness_score = 0
        
    def run_test_suite(self, test_functions: List[tuple]) -> Dict:
        """
        Run a complete test suite with all features
        
        Args:
            test_functions: List of tuples (test_name, test_function)
            
        Returns:
            Dictionary with complete test results
        """
        logger.info("="*70)
        logger.info("Starting Integrated Test Suite")
        logger.info("="*70)
        
        # Start timing
        self.reporter.start_session()
        
        # Step 1: Check website compatibility
        logger.info("\n🔍 Step 1: Checking website compatibility...")
        self.compatibility_report = check_website_compatibility(
            self.url, self.browser_type, self.headless
        )
        self.robustness_score = self.compatibility_report['robustness_score']
        print_compatibility_report(self.compatibility_report)
        
        # Step 2: Initialize browser
        logger.info("\n🌐 Step 2: Launching browser...")
        
        with sync_playwright() as p:
            # Launch browser
            if self.browser_type == 'firefox':
                browser = p.firefox.launch(headless=self.headless)
            elif self.browser_type == 'webkit':
                browser = p.webkit.launch(headless=self.headless)
            else:
                browser = p.chromium.launch(headless=self.headless)
            
            # Setup context with popup blocking
            context = setup_popup_blocking_context(browser)
            page = context.new_page()
            
            # Navigate to URL
            page.goto(self.url, wait_until='networkidle', timeout=30000)
            
            # Step 3: Handle common popups
            logger.info("\n🚫 Step 3: Handling common popups...")
            handle_common_popups(page)
            
            # Step 4: Run tests with progress indicator
            logger.info(f"\n🧪 Step 4: Running {len(test_functions)} test(s)...\n")
            
            progress = ProgressIndicator(total_tests=len(test_functions))
            
            for test_name, test_func in test_functions:
                progress.start_test(test_name)
                
                # Run individual test with retry
                self._run_single_test(test_name, test_func, page, progress)
            
            progress.finish()
            
            # Close browser
            browser.close()
        
        # Step 5: Generate reports
        self.reporter.end_session()
        
        logger.info("\n📊 Step 5: Generating reports...")
        
        # Get statistics
        statistics = self.reporter.get_statistics()
        test_results = self.reporter.get_test_results()
        
        # Generate HTML report
        html_path = generate_html_report(test_results, statistics)
        logger.info(f"✓ HTML report generated: {html_path}")
        
        # Print error summary
        self.error_handler.print_summary()
        
        # Step 6: Display final summary
        logger.info("\n🎯 Step 6: Final Summary\n")
        
        error_summary = self.error_handler.get_error_summary()
        error_summary['most_common_errors'] = self.error_handler.get_most_common_errors(3)
        
        generate_final_summary(
            statistics=statistics,
            error_summary=error_summary,
            robustness_score=self.robustness_score,
            html_report_path=html_path,
            total_time=statistics['total_execution_time']
        )
        
        return {
            'statistics': statistics,
            'test_results': test_results,
            'error_summary': error_summary,
            'compatibility_report': self.compatibility_report,
            'html_report_path': html_path
        }
    
    def _run_single_test(self, test_name: str, test_func: Callable, 
                        page: Page, progress: ProgressIndicator):
        """
        Run a single test with error handling and retry
        
        Args:
            test_name: Name of the test
            test_func: Test function to execute
            page: Playwright page object
            progress: Progress indicator instance
        """
        start_time = time.time()
        
        try:
            # Wrap test function with retry decorator
            @retry_on_failure(max_retries=3, initial_wait=2.0)
            def wrapped_test():
                return test_func(page, self)
            
            # Execute test
            result = wrapped_test()
            
            # Mark as passed
            execution_time = time.time() - start_time
            self.reporter.add_test_result(
                test_name=test_name,
                status='pass',
                execution_time=execution_time
            )
            progress.mark_passed()
            
        except Exception as e:
            # Test failed
            execution_time = time.time() - start_time
            error_type = type(e).__name__
            
            # Log error
            self.error_handler.log_error(
                error=e,
                test_case_name=test_name,
                additional_context={'execution_time': execution_time}
            )
            
            # Add to reporter
            self.reporter.add_test_result(
                test_name=test_name,
                status='fail',
                execution_time=execution_time,
                error_message=str(e),
                error_type=error_type
            )
            progress.mark_failed()


# Example test functions
def example_test_google_search(page: Page, runner: IntegratedTestRunner):
    """Example test: Google search"""
    # Use robust element finder
    search_input = find_element_robust(
        page,
        'input[name="q"]',
        fallback_selectors=['textarea[name="q"]', '//input[@title="Search"]'],
        timeout=10000
    )
    
    search_input.fill("Playwright Python")
    search_input.press("Enter")
    
    # Wait for results
    page.wait_for_selector('div#search', timeout=10000)
    
    return True


def example_test_navigation(page: Page, runner: IntegratedTestRunner):
    """Example test: Navigation"""
    # Navigate to different page
    page.goto("https://www.python.org", timeout=30000)
    
    # Handle popups again
    handle_common_popups(page)
    
    # Find element robustly
    downloads = find_element_robust(
        page,
        'a:has-text("Downloads")',
        fallback_selectors=['//a[contains(text(), "Downloads")]'],
        timeout=10000
    )
    
    return True


# Main execution function
def run_integrated_tests(url: str = "https://www.google.com", 
                        browser_type: str = 'chromium',
                        headless: bool = True):
    """
    Main function to run integrated test suite
    
    Args:
        url: Target URL
        browser_type: Browser to use
        headless: Run in headless mode
        
    Returns:
        Test results dictionary
    """
    # Initialize runner
    runner = IntegratedTestRunner(url, browser_type, headless)
    
    # Define test suite
    test_suite = [
        ("Google Search Test", example_test_google_search),
        ("Navigation Test", example_test_navigation),
    ]
    
    # Run tests
    results = runner.run_test_suite(test_suite)
    
    return results


if __name__ == "__main__":
    # Example: Run the integrated test suite
    print("\n🚀 Starting Integrated Test Runner Example\n")
    
    results = run_integrated_tests(
        url="https://www.google.com",
        browser_type='chromium',
        headless=False  # Set to True for headless mode
    )
    
    print("\n✅ Test execution completed!")
    print(f"📄 View detailed report at: {results['html_report_path']}")
