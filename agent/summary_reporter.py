"""
Summary Reporter Module
Generates visually appealing final test summary with colors and ASCII art
"""

import sys
from typing import Dict, List


# Check if colorama is available, use fallback if not
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Fallback: create dummy color classes
    class DummyColor:
        def __getattr__(self, name):
            return ''
    
    Fore = DummyColor()
    Back = DummyColor()
    Style = DummyColor()


def generate_final_summary(statistics: Dict, error_summary: Dict, 
                          robustness_score: int, html_report_path: str,
                          total_time: float):
    """
    Generate and print final test summary with colors and formatting
    
    Args:
        statistics: Test statistics dictionary from TestReporter
        error_summary: Error summary from ErrorHandler
        robustness_score: Website robustness score (0-100)
        html_report_path: Path to generated HTML report
        total_time: Total execution time in seconds
    """
    
    # Print ASCII banner
    _print_banner()
    
    # Print execution summary
    _print_execution_summary(statistics, total_time)
    
    # Print error summary
    if error_summary['total_errors'] > 0:
        _print_error_summary(error_summary)
    
    # Print robustness score
    _print_robustness_score(robustness_score)
    
    # Print report location
    _print_report_location(html_report_path)
    
    # Print footer
    _print_footer(statistics)


def _print_banner():
    """Print ASCII art banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     ████████╗███████╗███████╗████████╗    ██████╗  ██████╗ ███╗  ║
    ║     ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ██╔══██╗██╔═══██╗████╗ ║
    ║        ██║   █████╗  ███████╗   ██║       ██║  ██║██║   ██║██╔██╗║
    ║        ██║   ██╔══╝  ╚════██║   ██║       ██║  ██║██║   ██║██║╚██║
    ║        ██║   ███████╗███████║   ██║       ██████╔╝╚██████╔╝██║ ╚█║
    ║        ╚═╝   ╚══════╝╚══════╝   ╚═╝       ╚═════╝  ╚═════╝ ╚═╝  ╚║
    ║                                                                   ║
    ║            🎯  TEST EXECUTION COMPLETE  🎯                        ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    
    if HAS_COLORAMA:
        print(Fore.CYAN + Style.BRIGHT + banner)
    else:
        print(banner)


def _print_execution_summary(statistics: Dict, total_time: float):
    """Print execution summary with colors"""
    print("\n" + "="*70)
    
    if HAS_COLORAMA:
        print(Style.BRIGHT + "📊  EXECUTION SUMMARY")
    else:
        print("📊  EXECUTION SUMMARY")
    
    print("="*70 + "\n")
    
    # Total time
    time_str = _format_time(total_time)
    if HAS_COLORAMA:
        print(f"⏱  {Fore.CYAN}Total Execution Time:{Style.RESET_ALL} {Style.BRIGHT}{time_str}{Style.RESET_ALL}")
    else:
        print(f"⏱  Total Execution Time: {time_str}")
    
    print()
    
    # Test counts with colors
    total = statistics['total_tests']
    passed = statistics['passed']
    failed = statistics['failed']
    skipped = statistics['skipped']
    
    if HAS_COLORAMA:
        print(f"📝 Total Tests:   {Style.BRIGHT}{total}{Style.RESET_ALL}")
        print(f"✓  Passed:        {Fore.GREEN}{Style.BRIGHT}{passed}{Style.RESET_ALL} ({statistics['pass_rate']:.1f}%)")
        print(f"✗  Failed:        {Fore.RED}{Style.BRIGHT}{failed}{Style.RESET_ALL} ({statistics['fail_rate']:.1f}%)")
        print(f"○  Skipped:       {Fore.YELLOW}{Style.BRIGHT}{skipped}{Style.RESET_ALL} ({statistics['skip_rate']:.1f}%)")
    else:
        print(f"📝 Total Tests:   {total}")
        print(f"✓  Passed:        {passed} ({statistics['pass_rate']:.1f}%)")
        print(f"✗  Failed:        {failed} ({statistics['fail_rate']:.1f}%)")
        print(f"○  Skipped:       {skipped} ({statistics['skip_rate']:.1f}%)")
    
    print()
    
    # Success rate with color coding
    success_rate = statistics['pass_rate']
    if HAS_COLORAMA:
        if success_rate >= 90:
            color = Fore.GREEN
            icon = "🎉"
        elif success_rate >= 70:
            color = Fore.YELLOW
            icon = "⚠️"
        else:
            color = Fore.RED
            icon = "❌"
        
        print(f"{icon}  Success Rate:   {color}{Style.BRIGHT}{success_rate:.1f}%{Style.RESET_ALL}")
    else:
        if success_rate >= 90:
            icon = "🎉"
        elif success_rate >= 70:
            icon = "⚠️"
        else:
            icon = "❌"
        print(f"{icon}  Success Rate:   {success_rate:.1f}%")


def _print_error_summary(error_summary: Dict):
    """Print top errors"""
    print("\n" + "="*70)
    
    if HAS_COLORAMA:
        print(Style.BRIGHT + "🐛  TOP ERRORS")
    else:
        print("🐛  TOP ERRORS")
    
    print("="*70 + "\n")
    
    # Get most common errors
    most_common = error_summary.get('most_common_errors', [])
    
    if most_common:
        for i, error in enumerate(most_common[:3], 1):
            if HAS_COLORAMA:
                print(f"{Fore.RED}#{i}{Style.RESET_ALL} {error['error_type']} "
                      f"({Fore.YELLOW}{error['count']} occurrences{Style.RESET_ALL})")
            else:
                print(f"#{i} {error['error_type']} ({error['count']} occurrences)")
            
            # Print truncated message
            msg = error['error_message']
            if len(msg) > 100:
                msg = msg[:97] + "..."
            print(f"    {msg}")
            print()
    else:
        if HAS_COLORAMA:
            print(f"{Fore.GREEN}✓ No errors recorded!{Style.RESET_ALL}")
        else:
            print("✓ No errors recorded!")


def _print_robustness_score(score: int):
    """Print robustness score with visual indicator"""
    print("\n" + "="*70)
    
    if HAS_COLORAMA:
        print(Style.BRIGHT + "🎯  WEBSITE ROBUSTNESS")
    else:
        print("🎯  WEBSITE ROBUSTNESS")
    
    print("="*70 + "\n")
    
    # Determine color and rating
    if score >= 80:
        color = Fore.GREEN if HAS_COLORAMA else ''
        rating = "Excellent"
        icon = "🟢"
    elif score >= 60:
        color = Fore.YELLOW if HAS_COLORAMA else ''
        rating = "Good"
        icon = "🟡"
    elif score >= 40:
        color = Fore.LIGHTYELLOW_EX if HAS_COLORAMA else ''
        rating = "Fair"
        icon = "🟠"
    else:
        color = Fore.RED if HAS_COLORAMA else ''
        rating = "Poor"
        icon = "🔴"
    
    # Print score bar
    bar_length = 50
    filled = int(bar_length * score / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    if HAS_COLORAMA:
        print(f"{icon} Robustness Score: {color}{Style.BRIGHT}{score}/100{Style.RESET_ALL}")
        print(f"   [{color}{bar}{Style.RESET_ALL}] {rating}")
    else:
        print(f"{icon} Robustness Score: {score}/100")
        print(f"   [{bar}] {rating}")


def _print_report_location(html_path: str):
    """Print HTML report location"""
    print("\n" + "="*70)
    
    if HAS_COLORAMA:
        print(Style.BRIGHT + "📄  DETAILED REPORT")
    else:
        print("📄  DETAILED REPORT")
    
    print("="*70 + "\n")
    
    if HAS_COLORAMA:
        print(f"{Fore.CYAN}📋 HTML Report:{Style.RESET_ALL} {html_path}")
        print(f"{Fore.GREEN}💡 Tip:{Style.RESET_ALL} Open the report in your browser for detailed analysis")
    else:
        print(f"📋 HTML Report: {html_path}")
        print(f"💡 Tip: Open the report in your browser for detailed analysis")


def _print_footer(statistics: Dict):
    """Print footer with final message"""
    print("\n" + "="*70 + "\n")
    
    passed = statistics['passed']
    failed = statistics['failed']
    
    if failed == 0 and passed > 0:
        message = "🎊 All tests passed! Great job! 🎊"
        color = Fore.GREEN if HAS_COLORAMA else ''
    elif failed > 0:
        message = "⚠️  Some tests failed. Check the report for details."
        color = Fore.YELLOW if HAS_COLORAMA else ''
    else:
        message = "ℹ️  No tests executed."
        color = Fore.CYAN if HAS_COLORAMA else ''
    
    if HAS_COLORAMA:
        print(f"{color}{Style.BRIGHT}{message.center(70)}{Style.RESET_ALL}")
    else:
        print(message.center(70))
    
    print("\n" + "="*70 + "\n")


def _format_time(seconds: float) -> str:
    """Format time in human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.0f}s"


# Example usage
if __name__ == "__main__":
    # Example data
    stats = {
        'total_tests': 10,
        'passed': 8,
        'failed': 2,
        'skipped': 0,
        'pass_rate': 80.0,
        'fail_rate': 20.0,
        'skip_rate': 0.0,
        'total_execution_time': 45.5,
        'average_execution_time': 4.55
    }
    
    errors = {
        'total_errors': 2,
        'most_common_errors': [
            {
                'error_type': 'TimeoutError',
                'error_message': 'Element not found within timeout period',
                'count': 2,
                'category': 'TIMEOUT_ERROR'
            }
        ]
    }
    
    generate_final_summary(
        statistics=stats,
        error_summary=errors,
        robustness_score=75,
        html_report_path='test_report.html',
        total_time=45.5
    )
