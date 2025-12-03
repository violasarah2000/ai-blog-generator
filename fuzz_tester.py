#!/usr/bin/env python3
"""
Fuzz Testing Orchestrator for AI Blog Generator

Uses the fuzzing framework to test the application against various attack vectors,
fuzzing inputs, and edge cases. Generates professional JSON and HTML reports.

Simple CLI orchestrator that delegates to security/fuzzing/redteam_playbook.py
"""

import sys
import time
from pathlib import Path
import requests

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from security.fuzzing.redteam_playbook import (
    FuzzTestSuite,
    InjectionAttackTests,
    PromptInjectionTests,
    UnicodeEdgeCaseTests,
    LongInputTests,
    EdgeCaseTests,
    RateLimitTests,
)

# Configuration
BASE_URL = "http://localhost:5000"
FUZZ_REPORT_DIR = Path(__file__).parent / "fuzz_reports"


def wait_for_app(max_attempts: int = 10, timeout: float = 2) -> bool:
    """
    Wait for the application to be ready.
    
    Args:
        max_attempts: Maximum number of connection attempts
        timeout: Timeout per attempt in seconds
        
    Returns:
        True if app is ready, False if connection failed
    """
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/status", timeout=timeout)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            if attempt < max_attempts - 1:
                time.sleep(1)
    
    return False


def run_fuzz_tests(suite: FuzzTestSuite) -> None:
    """
    Execute all fuzz tests with progress reporting.
    
    Args:
        suite: Configured FuzzTestSuite instance
    """
    def progress_callback(current: int, total: int, result: dict) -> None:
        """Print test progress."""
        status_symbol = "✓" if result["status"] == "SUCCESS" else "✗"
        print(f"  {status_symbol} Test {current}/{total}: {result['status']}")
    
    suite.run_all(on_progress=progress_callback)


def main():
    """Run all fuzz tests and generate reports."""
    
    print("🔍 AI Blog Generator Fuzz Test Suite")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"Report Directory: {FUZZ_REPORT_DIR}")
    print("=" * 70)
    
    # Wait for app to be ready
    print("\n⏳ Waiting for application to be ready...")
    if not wait_for_app():
        print("✗ Cannot connect to application. Is it running on port 5000?")
        return
    
    print("✓ Application is ready!\n")
    
    # Create test suite
    suite = FuzzTestSuite(BASE_URL, FUZZ_REPORT_DIR)
    
    # Add injection attack tests
    print("Testing Injection Attacks...")
    for i, payload in enumerate(InjectionAttackTests.PAYLOADS, 1):
        suite.add_test(f"injection_attack_{i}", payload)
    run_fuzz_tests(suite)
    
    # Add prompt injection tests
    print("\nTesting Prompt Injections...")
    suite_size = len(suite.tests)
    for i, payload in enumerate(PromptInjectionTests.PAYLOADS, 1):
        suite.add_test(f"prompt_injection_{i}", payload)
    for test in suite.tests[suite_size:]:
        result = test.run(BASE_URL)
        suite.results.append(result)
        status_symbol = "✓" if result["status"] == "SUCCESS" else "✗"
        print(f"  {status_symbol} {result['test_name']}: {result['status']}")
    
    # Add Unicode fuzzing tests
    print("\nTesting Unicode Edge Cases...")
    suite_size = len(suite.tests)
    for i, payload in enumerate(UnicodeEdgeCaseTests.PAYLOADS, 1):
        suite.add_test(f"unicode_fuzz_{i}", payload)
    for test in suite.tests[suite_size:]:
        result = test.run(BASE_URL)
        suite.results.append(result)
        status_symbol = "✓" if result["status"] == "SUCCESS" else "✗"
        print(f"  {status_symbol} {result['test_name']}: {result['status']}")
    
    # Add long input tests
    print("\nTesting Long Inputs...")
    suite_size = len(suite.tests)
    for i, payload in enumerate(LongInputTests.PAYLOADS, 1):
        suite.add_test(f"long_input_{i}", payload)
    for test in suite.tests[suite_size:]:
        result = test.run(BASE_URL)
        suite.results.append(result)
        status_symbol = "✓" if result["status"] == "SUCCESS" else "✗"
        print(f"  {status_symbol} {result['test_name']}: {result['status']}")
    
    # Add edge case tests
    print("\nTesting Edge Cases...")
    suite_size = len(suite.tests)
    for i, payload in enumerate(EdgeCaseTests.PAYLOADS, 1):
        suite.add_test(f"edge_case_{i}", payload)
    for test in suite.tests[suite_size:]:
        result = test.run(BASE_URL)
        suite.results.append(result)
        status_symbol = "✓" if result["status"] == "SUCCESS" else "✗"
        print(f"  {status_symbol} {result['test_name']}: {result['status']}")
    
    # Add rate limit tests
    print("\nTesting Rate Limiting...")
    suite_size = len(suite.tests)
    for i in range(RateLimitTests.COUNT):
        suite.add_test(f"rate_limit_test_{i+1}", f"Rate limit test {i+1}")
    for test in suite.tests[suite_size:]:
        result = test.run(BASE_URL)
        suite.results.append(result)
        status_symbol = "✓" if result["status"] in ["SUCCESS", "RATE_LIMIT"] else "✗"
        print(f"  {status_symbol} {result['test_name']}: {result['status']}")
    
    # Generate reports
    print("\n📊 Generating Reports...")
    json_report = suite.generate_json_report()
    print(f"  ✓ JSON Report: {json_report}")
    
    html_report = suite.generate_html_report()
    print(f"  ✓ HTML Report: {html_report}")
    
    # Print summary
    suite.print_summary()
    
    print(f"🎉 Fuzz testing complete! Reports saved to: {FUZZ_REPORT_DIR}")
    print(f"   View results: open {html_report}")


if __name__ == "__main__":
    main()

